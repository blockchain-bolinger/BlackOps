#!/usr/bin/env python3
import subprocess
import time
import os

class HandshakeCapture:
    def __init__(self, interface, bssid, channel, output="handshake"):
        self.interface = interface
        self.bssid = bssid
        self.channel = channel
        self.output = output

    def capture(self, timeout=30):
        # Interface in Monitor-Modus
        subprocess.run(["sudo", "airmon-ng", "start", self.interface], check=True)
        mon = self.interface + "mon"

        # Kanal setzen
        subprocess.run(["sudo", "iwconfig", mon, "channel", str(self.channel)], check=True)

        # airodump-ng starten
        cmd = [
            "sudo", "airodump-ng",
            "-c", str(self.channel),
            "--bssid", self.bssid,
            "-w", self.output,
            mon
        ]
        proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"[*] Capture läuft für {timeout} Sekunden...")
        time.sleep(timeout)
        proc.terminate()
        subprocess.run(["sudo", "airmon-ng", "stop", mon])
        cap_file = f"{self.output}-01.cap"
        if os.path.exists(cap_file):
            print(f"[+] Handshake gespeichert: {cap_file}")
            return cap_file
        else:
            print("[-] Kein Handshake aufgezeichnet.")
            return None

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 4:
        print(f"Usage: {sys.argv[0]} <interface> <bssid> <channel>")
        sys.exit(1)
    hc = HandshakeCapture(sys.argv[1], sys.argv[2], sys.argv[3])
    hc.capture(20)