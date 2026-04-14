#!/usr/bin/env python3
"""
Specialized OSINT tool for domain investigation.
"""

from __future__ import annotations

import argparse
import json
import re
import socket
import sys
from pathlib import Path
from typing import Dict, List

import requests

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.blackops_logger import BlackOpsLogger
from tools.recon.osint_output import failed_payload, save_csv, save_json, success_payload


class DomainOsintTool:
    DOMAIN_RE = re.compile(
        r"^(?!-)[A-Za-z0-9-]{1,63}(?<!-)"
        r"(\.(?!-)[A-Za-z0-9-]{1,63}(?<!-))+$"
    )

    def __init__(self):
        self.logger = BlackOpsLogger("DomainOsintTool")

    @classmethod
    def _valid_domain(cls, value: str) -> bool:
        return bool(cls.DOMAIN_RE.match((value or "").strip().lower()))

    @staticmethod
    def _lookup_json(url: str):
        try:
            response = requests.get(url, timeout=12)
            if response.status_code == 200:
                return response.json()
            return {"error": f"http_{response.status_code}"}
        except Exception as exc:
            return {"error": str(exc)}

    def _dns_info(self, domain: str) -> Dict:
        data: Dict[str, object] = {}
        try:
            host, aliases, ips = socket.gethostbyname_ex(domain)
            data["hostname"] = host
            data["aliases"] = aliases
            data["a_records"] = sorted(set(ips))
        except Exception as exc:
            data["dns_error"] = str(exc)
        return data

    @staticmethod
    def _extract_crtsh_subdomains(raw) -> List[str]:
        if not isinstance(raw, list):
            return []
        names = set()
        for item in raw:
            name_value = str(item.get("name_value", "")).strip()
            for entry in name_value.split("\n"):
                candidate = entry.strip().lower()
                if candidate and "*" not in candidate:
                    names.add(candidate)
        return sorted(names)

    def build_report(self, domain: str) -> Dict:
        report: Dict[str, object] = {
            "target_type": "domain",
            "domain": domain,
            "dns": self._dns_info(domain),
            "rdap": self._lookup_json(f"https://rdap.org/domain/{domain}"),
            "open_source_links": {
                "crtsh_web": f"https://crt.sh/?q=%25.{domain}",
                "securitytrails": f"https://securitytrails.com/domain/{domain}",
                "virustotal": f"https://www.virustotal.com/gui/domain/{domain}",
            },
        }
        crtsh_raw = self._lookup_json(f"https://crt.sh/?q=%25.{domain}&output=json")
        subdomains = self._extract_crtsh_subdomains(crtsh_raw)
        report["subdomains_sample"] = subdomains[:50]
        report["subdomains_count"] = len(subdomains)
        return report

    def run(self) -> None:
        parser = argparse.ArgumentParser(description="Domain OSINT Tool")
        parser.add_argument("domain", nargs="?", help="Target domain")
        parser.add_argument("-o", "--output", help="Optional output report file")
        parser.add_argument("--json", action="store_true", help="Print standardized ToolResult JSON")
        parser.add_argument("--csv", help="Export flattened data as CSV")
        args = parser.parse_args()

        domain = (args.domain or "").strip().lower()
        if not domain:
            domain = input("Domain (leer = zurück): ").strip().lower()
            if not domain:
                return
        if not self._valid_domain(domain):
            payload = failed_payload("osint_domain", "invalid domain", error_type="validation")
            print(json.dumps(payload, indent=2, ensure_ascii=False))
            return

        self.logger.print_banner()
        report = self.build_report(domain)
        payload = success_payload("osint_domain", report)
        if args.json:
            print(json.dumps(payload, indent=2, ensure_ascii=False))
        else:
            print(json.dumps(payload["data"], indent=2, ensure_ascii=False))
        if args.output:
            save_json(args.output, payload)
            print(f"Saved JSON report: {args.output}")
        if args.csv:
            save_csv(args.csv, payload, data_only=True)
            print(f"Saved CSV report: {args.csv}")


if __name__ == "__main__":
    DomainOsintTool().run()
