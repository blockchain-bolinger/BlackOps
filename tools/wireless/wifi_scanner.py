#!/usr/bin/env python3
import subprocess
import re

class WiFiScanner:
    def __init__(self, interface="wlan0"):
        self.interface = interface

    def scan_networks(self):
        """Führt airodump-ng aus und parst die Ausgabe"""
        cmd = ["sudo", "airodump-ng", self.interface, "--write", "/tmp/airodump", "--output-format", "csv", "--background", "1"]
        proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            import time
            time.sleep(10)  # 10 Sekunden scannen
        finally:
            proc.terminate()

        networks = []
        with open("/tmp/airodump-01.csv", "r") as f:
            lines = f.readlines()
        for line in lines[2:]:
            if "Station MAC" in line:
                break
            parts = line.split(",")
            if len(parts) > 13:
                bssid = parts[0].strip()
                channel = parts[3].strip()
                essid = parts[13].strip('" \n')
                if bssid and essid:
                    networks.append({"bssid": bssid, "channel": channel, "essid": essid})
        return networks

if __name__ == "__main__":
    scanner = WiFiScanner()
    nets = scanner.scan_networks()
    for n in nets:
        print(f"ESSID: {n['essid']}, BSSID: {n['bssid']}, Kanal: {n['channel']}")