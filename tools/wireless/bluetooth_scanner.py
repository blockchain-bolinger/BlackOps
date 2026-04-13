#!/usr/bin/env python3
import subprocess
import re

class BluetoothScanner:
    def scan(self):
        """hcitool scan ausführen"""
        result = subprocess.run(["hcitool", "scan"], capture_output=True, text=True)
        devices = []
        for line in result.stdout.split("\n")[1:]:
            if line.strip():
                parts = line.split("\t", 1)
                if len(parts) == 2:
                    mac, name = parts
                    devices.append({"mac": mac.strip(), "name": name.strip()})
        return devices

if __name__ == "__main__":
    scanner = BluetoothScanner()
    devices = scanner.scan()
    for d in devices:
        print(f"Gerät: {d['name']} ({d['mac']})")