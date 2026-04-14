#!/usr/bin/env python3
"""
Specialized OSINT tool for email investigation.
"""

from __future__ import annotations

import argparse
import json
import re
import socket
import sys
from pathlib import Path
from typing import Dict, Optional

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.blackops_logger import BlackOpsLogger
from tools.recon.osint_output import failed_payload, save_csv, save_json, success_payload
from tools.recon.social_hunter_v7 import SocialHunterV7


class EmailOsintTool:
    EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

    def __init__(self):
        self.logger = BlackOpsLogger("EmailOsintTool")
        self.hunter = SocialHunterV7()

    def _email_domain_info(self, email: str) -> Dict:
        domain = email.split("@", 1)[-1].strip().lower()
        info: Dict[str, object] = {"domain": domain}
        try:
            _, _, ips = socket.gethostbyname_ex(domain)
            info["dns_ips"] = sorted(set(ips))
        except Exception as exc:
            info["dns_error"] = str(exc)
        return info

    def run_lookup(self, email: str) -> dict:
        self.logger.print_banner()
        data = {
            "target_type": "email",
            "email": email,
            "domain_info": self._email_domain_info(email),
            "breach_sources": self.hunter.search_email(email),
            "search_links": {
                "google": f"https://www.google.com/search?q=%22{email}%22",
                "bing": f"https://www.bing.com/search?q=%22{email}%22",
                "haveibeenpwned": f"https://haveibeenpwned.com/account/{email}",
            },
        }
        return success_payload("osint_email", data)

    def run(self) -> None:
        parser = argparse.ArgumentParser(description="Email OSINT Tool")
        parser.add_argument("email", nargs="?", help="Email address to investigate")
        parser.add_argument("-o", "--output", help="Optional output report file")
        parser.add_argument("--json", action="store_true", help="Print standardized ToolResult JSON")
        parser.add_argument("--csv", help="Export flattened data as CSV")
        args = parser.parse_args()

        email = (args.email or "").strip()
        if not email:
            email = input("Email address (leer = zurück): ").strip()
            if not email:
                return

        if not self.EMAIL_RE.match(email):
            payload = failed_payload("osint_email", "invalid email format", error_type="validation")
            print(json.dumps(payload, indent=2, ensure_ascii=False))
            return

        payload = self.run_lookup(email)
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
    EmailOsintTool().run()
