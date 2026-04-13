#!/usr/bin/env python3
"""
MobileSpy - Mobile App Security Analyzer (APK/IPA)
NUR FÜR AUTORISIERTE TESTS!
"""

import argparse
import os
import subprocess
import zipfile
import re
import json
import sys
from colorama import Fore, init
from pathlib import Path

init(autoreset=True)

class MobileSpy:
    def __init__(self, app_file, output=None):
        self.app_file = app_file
        self.output = output
        self.results = {"findings": [], "info": {}, "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")}
    
    def print_banner(self):
        print(rf"""{Fore.MAGENTA}
   __  ___     _     _    ___              
  /  |/  /__  (_)___| |  / _ \___ _  _____ 
 / /|_/ / _ \/ / __| | / /_\/ _ \ \/ / _ \\
/ /  / /  __/ /\__ \ |/ /_\\\\  __/>  <  __/
/_/  /_/\___/_/|___/|_/ \____/\___/_/\_\___|
{Fore.WHITE}   >> MOBILE APP SECURITY SCANNER v1.0 <<
{Fore.YELLOW}   NUR FÜR AUTORISIERTE TESTS!
        """)
    
    def analyze_apk(self):
        """Analysiert APK-Datei mit jadx, strings, etc."""
        print(f"{Fore.CYAN}[*] Analysiere APK: {self.app_file}")
        # Prüfe auf jadx
        jadx_path = shutil.which("jadx")
        if not jadx_path:
            print(f"{Fore.RED}[!] jadx nicht gefunden. Installiere: https://github.com/skylot/jadx")
            return
        
        # Dekompiliere APK in temporären Ordner
        output_dir = f"/tmp/mobilespy_{int(time.time())}"
        try:
            subprocess.run(["jadx", "-d", output_dir, self.app_file], check=True, capture_output=True)
            print(f"{Fore.GREEN}[✓] Dekompilierung erfolgreich.")
            
            # Suche nach hartkodierten Secrets
            secrets_patterns = [
                (r'api[_-]?key[\s]*=[\s]*["\']([a-zA-Z0-9]+)["\']', "API Key"),
                (r'secret[\s]*=[\s]*["\']([a-zA-Z0-9]+)["\']', "Secret"),
                (r'password[\s]*=[\s]*["\']([^"\']+)["\']', "Password"),
                (r'token[\s]*=[\s]*["\']([a-zA-Z0-9_\-]+)["\']', "Token"),
                (r'endpoint[\s]*=[\s]*["\'](https?://[^"\']+)["\']', "Endpoint")
            ]
            for root, dirs, files in os.walk(output_dir):
                for file in files:
                    if file.endswith(".java"):
                        path = os.path.join(root, file)
                        with open(path, 'r', errors='ignore') as f:
                            content = f.read()
                            for pattern, desc in secrets_patterns:
                                matches = re.findall(pattern, content, re.IGNORECASE)
                                for match in matches:
                                    self.results["findings"].append({
                                        "type": desc,
                                        "value": match,
                                        "file": path,
                                        "severity": "HIGH"
                                    })
                                    print(f"{Fore.RED}[!] Gefunden: {desc} = {match} in {file}")
        except Exception as e:
            print(f"{Fore.RED}[!] Fehler: {e}")
        finally:
            # Cleanup
            subprocess.run(["rm", "-rf", output_dir])
    
    def analyze_ipa(self):
        """Analysiert IPA-Datei (iOS)"""
        print(f"{Fore.CYAN}[*] Analysiere IPA: {self.app_file}")
        # IPA ist ZIP-Datei mit Payload
        with zipfile.ZipFile(self.app_file, 'r') as zip_ref:
            extract_dir = f"/tmp/mobilespy_ipa_{int(time.time())}"
            zip_ref.extractall(extract_dir)
            # Suche nach Info.plist und Binaries
            for root, dirs, files in os.walk(extract_dir):
                for file in files:
                    if file == "Info.plist":
                        path = os.path.join(root, file)
                        # Mit plistlib parsen
                        import plistlib
                        with open(path, 'rb') as f:
                            plist = plistlib.load(f)
                            self.results["info"]["bundle_id"] = plist.get('CFBundleIdentifier')
                            self.results["info"]["version"] = plist.get('CFBundleVersion')
                            # Prüfe auf unsichere Einstellungen
                            if plist.get('NSAppTransportSecurity', {}).get('NSAllowsArbitraryLoads') == True:
                                self.results["findings"].append({
                                    "type": "Insecure App Transport Security",
                                    "severity": "MEDIUM",
                                    "detail": "ATS deaktiviert"
                                })
                                print(f"{Fore.YELLOW}[!] ATS deaktiviert (erlaubt HTTP)")
                    elif file.endswith(".app") and os.path.isdir(os.path.join(root, file)):
                        binary_path = os.path.join(root, file, file.replace(".app", ""))
                        if os.path.exists(binary_path):
                            # Strings auf Secrets durchsuchen
                            result = subprocess.run(["strings", binary_path], capture_output=True, text=True)
                            for line in result.stdout.splitlines():
                                for pattern, desc in secrets_patterns:
                                    match = re.search(pattern, line, re.IGNORECASE)
                                    if match:
                                        self.results["findings"].append({
                                            "type": desc,
                                            "value": match.group(1),
                                            "severity": "HIGH"
                                        })
                                        print(f"{Fore.RED}[!] {desc} in Binary: {match.group(1)}")
            subprocess.run(["rm", "-rf", extract_dir])
    
    def run(self):
        self.print_banner()
        if self.app_file.endswith(".apk"):
            self.analyze_apk()
        elif self.app_file.endswith(".ipa"):
            self.analyze_ipa()
        else:
            print(f"{Fore.RED}[!] Nicht unterstützter Dateityp. Nur .apk oder .ipa")
            return
        
        if self.output:
            with open(self.output, 'w') as f:
                json.dump(self.results, f, indent=2)
            print(f"{Fore.GREEN}[✓] Bericht gespeichert: {self.output}")
        else:
            print(json.dumps(self.results, indent=2))

def main():
    parser = argparse.ArgumentParser(description="MobileSpy - Mobile App Security Analyzer")
    parser.add_argument("app_file", help="Pfad zur APK oder IPA Datei")
    parser.add_argument("-o", "--output", help="JSON Output Datei")
    args = parser.parse_args()
    
    print(f"{Fore.RED}[!] MobileSpy: Nur für autorisierte Tests!")
    confirm = input(f"{Fore.WHITE}[?] Fortfahren? (ja/NEIN): ").strip().lower()
    if confirm != "ja":
        print("Abbruch.")
        sys.exit(0)
    
    spy = MobileSpy(args.app_file, args.output)
    spy.run()

if __name__ == "__main__":
    import time
    import shutil
    main()
