#!/usr/bin/env python3
"""
Specialized OSINT tool for username/nickname lookup.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.blackops_logger import BlackOpsLogger
from tools.recon.osint_output import failed_payload, save_csv, save_json, success_payload
from tools.recon.social_hunter_v7 import SocialHunterV7


class UsernameOsintTool:
    def __init__(self):
        self.logger = BlackOpsLogger("UsernameOsintTool")
        self.hunter = SocialHunterV7()

    def run_lookup(self, username: str) -> dict:
        self.logger.print_banner()
        print(f"Target username (Ziel-Username): {username}")
        results = self.hunter.search_username(username)
        report = self.hunter.generate_report(username, results)
        data = {
            "target_type": "username",
            "target": username,
            "site_count": len(results),
            "sites_found": sorted(results.keys()),
            "results": results,
            "report_text": report,
        }
        return success_payload("osint_username", data)

    def run(self) -> None:
        parser = argparse.ArgumentParser(description="Username/Nickname OSINT Tool")
        parser.add_argument("username", nargs="?", help="Username or nickname")
        parser.add_argument("-o", "--output", help="Optional output report file")
        parser.add_argument("--json", action="store_true", help="Print standardized ToolResult JSON")
        parser.add_argument("--csv", help="Export flattened data as CSV")
        parser.add_argument("--list-sites", action="store_true", help="List configured social sites")
        args = parser.parse_args()

        if args.list_sites:
            self.hunter._print_sites()
            return

        username = args.username
        if not username:
            username = input("Username/Nickname (leer = zurück): ").strip()
            if not username:
                return
        if not username.strip():
            payload = failed_payload("osint_username", "username is required", error_type="validation")
            print(json.dumps(payload, indent=2, ensure_ascii=False))
            return

        payload = self.run_lookup(username.strip())
        if args.json:
            print(json.dumps(payload, indent=2, ensure_ascii=False))
        else:
            print(payload["data"]["report_text"])

        if args.output:
            save_json(args.output, payload)
            print(f"Saved JSON report: {args.output}")
        if args.csv:
            save_csv(args.csv, payload, data_only=True)
            print(f"Saved CSV report: {args.csv}")


if __name__ == "__main__":
    UsernameOsintTool().run()
