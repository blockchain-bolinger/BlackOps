#!/usr/bin/env python3
"""
Specialized OSINT tool for IP address investigation.
"""

from __future__ import annotations

import argparse
import ipaddress
import json
import socket
import sys
from pathlib import Path
from typing import Dict, Optional

import requests

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.blackops_logger import BlackOpsLogger
from tools.recon.osint_output import failed_payload, save_csv, save_json, success_payload


class IpOsintTool:
    def __init__(self):
        self.logger = BlackOpsLogger("IpOsintTool")

    @staticmethod
    def _valid_ip(value: str) -> bool:
        try:
            ipaddress.ip_address(value)
            return True
        except Exception:
            return False

    @staticmethod
    def _lookup_json(url: str) -> Dict:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                return response.json()
            return {"error": f"http_{response.status_code}"}
        except Exception as exc:
            return {"error": str(exc)}

    def build_report(self, ip: str) -> Dict:
        report: Dict[str, object] = {"target_type": "ip", "ip": ip}
        try:
            ptr_host, _, _ = socket.gethostbyaddr(ip)
            report["reverse_dns"] = ptr_host
        except Exception as exc:
            report["reverse_dns_error"] = str(exc)

        report["ipapi"] = self._lookup_json(f"https://ipapi.co/{ip}/json/")
        report["ipinfo"] = self._lookup_json(f"https://ipinfo.io/{ip}/json")
        report["open_source_links"] = {
            "shodan": f"https://www.shodan.io/host/{ip}",
            "abuseipdb": f"https://www.abuseipdb.com/check/{ip}",
            "virustotal": f"https://www.virustotal.com/gui/ip-address/{ip}",
        }
        return report

    def run(self) -> None:
        parser = argparse.ArgumentParser(description="IP Address OSINT Tool")
        parser.add_argument("ip", nargs="?", help="IPv4 or IPv6 address")
        parser.add_argument("-o", "--output", help="Optional output report file")
        parser.add_argument("--json", action="store_true", help="Print standardized ToolResult JSON")
        parser.add_argument("--csv", help="Export flattened data as CSV")
        args = parser.parse_args()

        ip = (args.ip or "").strip()
        if not ip:
            ip = input("IP address (leer = zurück): ").strip()
            if not ip:
                return
        if not self._valid_ip(ip):
            payload = failed_payload("osint_ip", "invalid IP address", error_type="validation")
            print(json.dumps(payload, indent=2, ensure_ascii=False))
            return

        self.logger.print_banner()
        report = self.build_report(ip)
        payload = success_payload("osint_ip", report)
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
    IpOsintTool().run()
