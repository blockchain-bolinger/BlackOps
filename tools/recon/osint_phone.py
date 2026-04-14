#!/usr/bin/env python3
"""
Specialized OSINT tool for phone number investigation.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, Optional

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.blackops_logger import BlackOpsLogger
from tools.recon.osint_output import failed_payload, save_csv, save_json, success_payload


class PhoneOsintTool:
    PHONE_RE = re.compile(r"^\+?[0-9][0-9\s().-]{5,24}$")

    COUNTRY_HINTS = {
        "1": "North America",
        "44": "United Kingdom",
        "49": "Germany",
        "33": "France",
        "34": "Spain",
        "39": "Italy",
        "41": "Switzerland",
        "43": "Austria",
        "90": "Turkey",
    }

    def __init__(self):
        self.logger = BlackOpsLogger("PhoneOsintTool")

    @staticmethod
    def _normalize(phone: str) -> str:
        digits = re.sub(r"[^\d+]", "", phone)
        if digits.startswith("00"):
            digits = "+" + digits[2:]
        return digits

    def _country_guess(self, normalized: str) -> str:
        value = normalized.lstrip("+")
        for prefix in sorted(self.COUNTRY_HINTS.keys(), key=len, reverse=True):
            if value.startswith(prefix):
                return self.COUNTRY_HINTS[prefix]
        return "unknown"

    def build_report(self, phone: str) -> Dict:
        normalized = self._normalize(phone)
        country_guess = self._country_guess(normalized)
        return {
            "target_type": "phone",
            "input": phone,
            "normalized": normalized,
            "country_guess": country_guess,
            "open_source_links": {
                "google": f"https://www.google.com/search?q=%22{normalized}%22",
                "bing": f"https://www.bing.com/search?q=%22{normalized}%22",
                "sync_me": f"https://sync.me/search/?number={normalized}",
                "truecaller": f"https://www.truecaller.com/search/{normalized}",
            },
            "notes": [
                "Use only authorized and lawful investigation contexts.",
                "Cross-check multiple sources before concluding ownership.",
            ],
        }

    def run(self) -> None:
        parser = argparse.ArgumentParser(description="Phone Number OSINT Tool")
        parser.add_argument("phone", nargs="?", help="Phone number")
        parser.add_argument("-o", "--output", help="Optional output report file")
        parser.add_argument("--json", action="store_true", help="Print standardized ToolResult JSON")
        parser.add_argument("--csv", help="Export flattened data as CSV")
        args = parser.parse_args()

        phone = (args.phone or "").strip()
        if not phone:
            phone = input("Phone number (leer = zurück): ").strip()
            if not phone:
                return
        if not self.PHONE_RE.match(phone):
            payload = failed_payload("osint_phone", "invalid phone number format", error_type="validation")
            print(json.dumps(payload, indent=2, ensure_ascii=False))
            return

        self.logger.print_banner()
        report = self.build_report(phone)
        payload = success_payload("osint_phone", report)
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
    PhoneOsintTool().run()
