#!/usr/bin/env python3
"""
Network Scanner – Schnelle Port-Scans für Tools
"""
import socket
from concurrent.futures import ThreadPoolExecutor

class NetworkScanner:
    def __init__(self, timeout=1):
        self.timeout = timeout

    def scan_port(self, host: str, port: int) -> dict:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(self.timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return {'port': port, 'state': 'open' if result == 0 else 'closed'}

    def scan_ports(self, host: str, ports: list, threads=50) -> list:
        results = []
        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = [executor.submit(self.scan_port, host, p) for p in ports]
            for f in futures:
                results.append(f.result())
        return results

    def run(self):
        host = input("[?] Host/IP: ").strip()
        ports_raw = input("[?] Ports (e.g. 22,80,443): ").strip()
        if not host or not ports_raw:
            print("[INFO] Host/ports not provided.")
            return

        try:
            ports = [int(p.strip()) for p in ports_raw.split(",") if p.strip()]
        except ValueError:
            print("[ERROR] Invalid ports list.")
            return

        results = self.scan_ports(host, ports)
        for r in results:
            print(f"{host}:{r['port']} -> {r['state']}")
