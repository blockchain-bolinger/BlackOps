#!/usr/bin/env python3
"""
MailTracker - E-Mail Header Analyse (SPF, DKIM, DMARC, Tracking)
"""

import argparse
import dns.resolver
import re
import sys
from colorama import Fore, init

init(autoreset=True)

class MailTracker:
    def __init__(self, domain):
        self.domain = domain
        self.results = {}
    
    def print_banner(self):
        print(rf"""{Fore.BLUE}
   __  ___       _   __             
  /  |/  /__    / | / /__  _ __ __ _
 / /|_/ / _ \  /  |/ / _ \| '__/ _` |
/ /  / /  __/ / /|  / (_) | | | (_| |
/_/  /_/\___|/_/ |_/\___/|_|  \__,_|
{Fore.WHITE}   >> EMAIL SECURITY ANALYZER v1.0 <<
        """)
    
    def check_spf(self):
        try:
            answers = dns.resolver.resolve(self.domain, 'TXT')
            for rdata in answers:
                txt = str(rdata)
                if 'v=spf1' in txt:
                    self.results['SPF'] = txt
                    print(f"{Fore.GREEN}[✓] SPF Record: {txt}")
                    return
            self.results['SPF'] = "Nicht vorhanden"
            print(f"{Fore.RED}[✗] Kein SPF Record")
        except:
            self.results['SPF'] = "Fehler"
            print(f"{Fore.RED}[✗] SPF Check fehlgeschlagen")
    
    def check_dkim(self, selector='default'):
        try:
            answers = dns.resolver.resolve(f"{selector}._domainkey.{self.domain}", 'TXT')
            for rdata in answers:
                txt = str(rdata)
                if 'v=DKIM1' in txt:
                    self.results['DKIM'] = txt
                    print(f"{Fore.GREEN}[✓] DKIM Record: {txt[:100]}...")
                    return
            self.results['DKIM'] = "Nicht vorhanden"
            print(f"{Fore.RED}[✗] Kein DKIM Record")
        except:
            self.results['DKIM'] = "Fehler"
            print(f"{Fore.RED}[✗] DKIM Check fehlgeschlagen")
    
    def check_dmarc(self):
        try:
            answers = dns.resolver.resolve(f"_dmarc.{self.domain}", 'TXT')
            for rdata in answers:
                txt = str(rdata)
                if 'v=DMARC1' in txt:
                    self.results['DMARC'] = txt
                    print(f"{Fore.GREEN}[✓] DMARC Record: {txt}")
                    return
            self.results['DMARC'] = "Nicht vorhanden"
            print(f"{Fore.RED}[✗] Kein DMARC Record")
        except:
            self.results['DMARC'] = "Fehler"
            print(f"{Fore.RED}[✗] DMARC Check fehlgeschlagen")
    
    def analyze_header(self, header_file):
        """Analysiert eine E-Mail-Header-Datei (raw)"""
        with open(header_file, 'r') as f:
            content = f.read()
        # Suche nach Tracking-Pixeln
        tracking = re.findall(r'https?://[^\s]+(?:px|pixel|track|open)[^\s]*', content, re.I)
        if tracking:
            self.results['tracking_pixels'] = tracking
            print(f"{Fore.YELLOW}[!] Tracking-Pixel gefunden: {tracking}")
        # Prüfe SPF/DKIM/DMARC Ergebnisse im Header
        spf_result = re.search(r'Authentication-Results:.*spf=(pass|fail|neutral)', content, re.I)
        if spf_result:
            self.results['spf_header'] = spf_result.group(1)
            print(f"{Fore.CYAN}[*] SPF Ergebnis im Header: {spf_result.group(1)}")
    
    def run(self, header_file=None):
        self.print_banner()
        print(f"{Fore.WHITE}[*] Domain: {self.domain}")
        self.check_spf()
        self.check_dkim()
        self.check_dmarc()
        if header_file:
            self.analyze_header(header_file)
        print(json.dumps(self.results, indent=2))

def main():
    parser = argparse.ArgumentParser(description="MailTracker")
    parser.add_argument("domain", help="Domain für SPF/DKIM/DMARC")
    parser.add_argument("--header", help="Pfad zur E-Mail-Header-Datei")
    args = parser.parse_args()
    
    import json
    tracker = MailTracker(args.domain)
    tracker.run(args.header)

if __name__ == "__main__":
    main()
