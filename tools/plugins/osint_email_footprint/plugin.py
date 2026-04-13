import hashlib
import re
import socket

from core.plugin_manager import PluginInterface


class OsintEmailFootprintPlugin(PluginInterface):
    version = "1.0.0"
    api_version = 1

    EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

    def name(self):
        return "osint_email_footprint"

    def description(self):
        return "Erstellt ein leichtgewichtiges OSINT-Profil fuer eine E-Mail-Adresse."

    def run(self, **kwargs):
        email = (kwargs.get("email") or "").strip().lower()
        if not email or not self.EMAIL_RE.match(email):
            raise ValueError("Gueltige E-Mail erforderlich, z.B. email=user@example.com")

        local_part, domain = email.split("@", 1)
        gravatar_hash = hashlib.md5(email.encode("utf-8")).hexdigest()
        domain_ips = self._resolve_domain(domain)

        return {
            "email": email,
            "domain": domain,
            "local_part_length": len(local_part),
            "gravatar": {
                "hash": gravatar_hash,
                "profile_url": f"https://www.gravatar.com/{gravatar_hash}",
                "avatar_url": f"https://www.gravatar.com/avatar/{gravatar_hash}?d=404",
            },
            "domain_resolution": domain_ips,
        }

    @staticmethod
    def _resolve_domain(domain):
        try:
            infos = socket.getaddrinfo(domain, None)
        except socket.gaierror as exc:
            return {"addresses": [], "error": str(exc)}
        addresses = sorted({item[4][0] for item in infos if item and item[4]})
        return {"addresses": addresses}
