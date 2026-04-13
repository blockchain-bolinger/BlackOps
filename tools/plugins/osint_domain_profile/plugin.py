import re
import socket
import ssl

import requests

from core.plugin_manager import PluginInterface


class OsintDomainProfilePlugin(PluginInterface):
    version = "1.0.0"
    api_version = 1

    SECURITY_HEADERS = (
        "strict-transport-security",
        "content-security-policy",
        "x-frame-options",
        "x-content-type-options",
        "referrer-policy",
    )

    def name(self):
        return "osint_domain_profile"

    def description(self):
        return "Erstellt ein OSINT-Profil fuer eine Domain (DNS, TLS, HTTP Header, Title)."

    def run(self, **kwargs):
        domain = (kwargs.get("domain") or "").strip()
        if not domain:
            raise ValueError("Parameter 'domain' ist erforderlich, z.B. domain=example.com")

        timeout = float(kwargs.get("timeout", 5))
        profile = {
            "domain": domain,
            "dns": self._resolve_dns(domain),
            "tls": self._fetch_tls(domain, timeout=timeout),
            "http": self._fetch_http(domain, timeout=timeout),
        }
        return profile

    @staticmethod
    def _resolve_dns(domain):
        try:
            infos = socket.getaddrinfo(domain, None)
        except socket.gaierror as exc:
            return {"addresses": [], "error": str(exc)}
        addresses = sorted({info[4][0] for info in infos if info and info[4]})
        reverse = {}
        for ip in addresses[:5]:
            try:
                reverse[ip] = socket.gethostbyaddr(ip)[0]
            except Exception:
                reverse[ip] = ""
        return {"addresses": addresses, "reverse_dns": reverse}

    @staticmethod
    def _fetch_tls(domain, timeout=5):
        try:
            context = ssl.create_default_context()
            with socket.create_connection((domain, 443), timeout=timeout) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as secure_sock:
                    cert = secure_sock.getpeercert()
            subject = dict(x[0] for x in cert.get("subject", []) if x)
            issuer = dict(x[0] for x in cert.get("issuer", []) if x)
            return {
                "ok": True,
                "subject_cn": subject.get("commonName", ""),
                "issuer_cn": issuer.get("commonName", ""),
                "not_before": cert.get("notBefore", ""),
                "not_after": cert.get("notAfter", ""),
                "san": [item[1] for item in cert.get("subjectAltName", []) if item and len(item) == 2],
            }
        except Exception as exc:
            return {"ok": False, "error": str(exc)}

    def _fetch_http(self, domain, timeout=5):
        result = {}
        for scheme in ("https", "http"):
            url = f"{scheme}://{domain}"
            try:
                resp = requests.get(url, timeout=timeout, allow_redirects=True, headers={"User-Agent": "BlackOps-OSINT/1.0"})
                title_match = re.search(r"<title[^>]*>(.*?)</title>", resp.text or "", flags=re.IGNORECASE | re.DOTALL)
                title = (title_match.group(1).strip() if title_match else "")[:200]
                lower_headers = {k.lower(): v for k, v in resp.headers.items()}
                security = {key: key in lower_headers for key in self.SECURITY_HEADERS}
                result[scheme] = {
                    "ok": True,
                    "status_code": resp.status_code,
                    "final_url": resp.url,
                    "server": resp.headers.get("Server", ""),
                    "title": title,
                    "security_headers": security,
                }
            except Exception as exc:
                result[scheme] = {"ok": False, "error": str(exc)}
        return result

