#!/usr/bin/env python3
"""
Specialized OSINT tool for person lookup by first/last name.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.blackops_logger import BlackOpsLogger
from tools.recon.osint_output import failed_payload, save_csv, save_json, success_payload
from tools.recon.social_hunter_v7 import SocialHunterV7


class PersonOsintTool:
    def __init__(self):
        self.logger = BlackOpsLogger("PersonOsintTool")
        self.hunter = SocialHunterV7()

    @staticmethod
    def _username_permutations(first_name: str, last_name: str) -> List[str]:
        f = first_name.strip().lower()
        l = last_name.strip().lower()
        if not f or not l:
            return []
        seeds = [
            f"{f}{l}",
            f"{f}.{l}",
            f"{f}_{l}",
            f"{f}-{l}",
            f"{f[0]}{l}",
            f"{f}{l[0]}",
            f"{l}{f}",
            f"{l}.{f}",
            f"{f}{l}1",
            f"{f}{l}123",
        ]
        return list(dict.fromkeys(seeds))

    def build_report(
        self,
        first_name: str,
        last_name: str,
        city: str = "",
        country: str = "",
        scan_usernames: bool = False,
    ) -> Dict:
        full_name = f"{first_name.strip()} {last_name.strip()}".strip()
        query_parts = [full_name]
        if city:
            query_parts.append(city.strip())
        if country:
            query_parts.append(country.strip())
        query = " ".join(part for part in query_parts if part)
        username_candidates = self._username_permutations(first_name, last_name)
        report: Dict[str, object] = {
            "target_type": "person",
            "person": {
                "first_name": first_name.strip(),
                "last_name": last_name.strip(),
                "city": city.strip(),
                "country": country.strip(),
            },
            "query": query,
            "search_links": {
                "google": f"https://www.google.com/search?q=%22{query}%22",
                "bing": f"https://www.bing.com/search?q=%22{query}%22",
                "linkedin": f"https://www.linkedin.com/search/results/people/?keywords={query}",
                "facebook": f"https://www.facebook.com/search/people/?q={query}",
            },
            "username_candidates": username_candidates,
        }
        if scan_usernames:
            social_hits = {}
            for username in username_candidates[:5]:
                found = self.hunter.search_username(username)
                if found:
                    social_hits[username] = sorted(found.keys())
            report["username_social_hits"] = social_hits
        return report

    def run(self) -> None:
        parser = argparse.ArgumentParser(description="Person OSINT Tool (first/last name)")
        parser.add_argument("first_name", nargs="?", help="First name")
        parser.add_argument("last_name", nargs="?", help="Last name")
        parser.add_argument("--city", help="Optional city hint")
        parser.add_argument("--country", help="Optional country hint")
        parser.add_argument("--scan-usernames", action="store_true", help="Run SocialHunter checks for top username candidates")
        parser.add_argument("-o", "--output", help="Optional output report file")
        parser.add_argument("--json", action="store_true", help="Print standardized ToolResult JSON")
        parser.add_argument("--csv", help="Export flattened data as CSV")
        args = parser.parse_args()

        first_name = (args.first_name or "").strip()
        last_name = (args.last_name or "").strip()
        if not first_name:
            first_name = input("First name (Vorname, leer = zurück): ").strip()
        if not first_name:
            payload = failed_payload("osint_person", "first_name is required", error_type="validation")
            print(json.dumps(payload, indent=2, ensure_ascii=False))
            return
        if not last_name:
            last_name = input("Last name (Nachname, leer = zurück): ").strip()
        if not last_name:
            payload = failed_payload("osint_person", "last_name is required", error_type="validation")
            print(json.dumps(payload, indent=2, ensure_ascii=False))
            return

        self.logger.print_banner()
        report = self.build_report(
            first_name=first_name,
            last_name=last_name,
            city=args.city or "",
            country=args.country or "",
            scan_usernames=bool(args.scan_usernames),
        )
        payload = success_payload("osint_person", report)
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
    PersonOsintTool().run()
