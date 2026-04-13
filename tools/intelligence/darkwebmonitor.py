#!/usr/bin/env python3
"""
DarkWebMonitor - .onion Crawler & Leak Search
NUR FÜR AUTORISIERTE FORSCHUNG!
"""

import argparse
import requests
import sys
import time
import re
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from colorama import Fore, init

# Tor Proxy einstellen
session = requests.Session()
session.proxies = {'http': 'socks5h://127.0.0.1:9050', 'https': 'socks5h://127.0.0.1:9050'}

init(autoreset=True)

class DarkWebMonitor:
    def __init__(self, start_url, depth=2, output=None):
        self.start_url = start_url
        self.depth = depth
        self.output = output
        self.visited = set()
        self.leaks = []
    
    def print_banner(self):
        print(rf"""{Fore.MAGENTA}
    ____            _ _    __        __                 
   |  _ \  __ _  __| | | __\ \      / /__  _ __ ___  ___
   | | | |/ _` |/ _` | |/ _ \ \ /\ / / _ \| '_ ` _ \/ __|
   | |_| | (_| | (_| | | (_) \ V  V / (_) | | | | | \__ \
   |____/ \__,_|\__,_|_|\___/ \_/\_/ \___/|_| |_| |_|___/
{Fore.WHITE}   >> DARK WEB MONITOR (TOR REQUIRED) v1.0 <<
{Fore.YELLOW}   NUR FÜR AUTORISIERTE FORSCHUNG!
        """)
    
    def check_tor(self):
        try:
            r = session.get("http://check.torproject.org", timeout=10)
            if "Congratulations" in r.text:
                print(f"{Fore.GREEN}[✓] Tor ist aktiv.")
                return True
            else:
                print(f"{Fore.RED}[!] Tor nicht aktiv. Starte: systemctl start tor")
                return False
        except:
            print(f"{Fore.RED}[!] Tor nicht erreichbar.")
            return False
    
    def crawl(self, url, current_depth):
        if current_depth > self.depth or url in self.visited:
            return
        print(f"{Fore.WHITE}[*] Crawling: {url}")
        self.visited.add(url)
        try:
            r = session.get(url, timeout=30)
            soup = BeautifulSoup(r.text, 'html.parser')
            # Suche nach potenziellen Leaks (E-Mail, Passwörter, API-Keys)
            text = r.text
            emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
            if emails:
                self.leaks.extend(emails)
                print(f"{Fore.RED}[!] Emails gefunden: {emails}")
            # Weitere Links extrahieren
            for link in soup.find_all('a', href=True):
                href = link['href']
                full_url = urljoin(url, href)
                if '.onion' in full_url:
                    self.crawl(full_url, current_depth+1)
        except Exception as e:
            print(f"{Fore.YELLOW}[!] Fehler: {e}")
        time.sleep(1)
    
    def run(self):
        self.print_banner()
        if not self.check_tor():
            return
        print(f"{Fore.CYAN}[*] Starte Crawl auf {self.start_url} (Tiefe {self.depth})")
        self.crawl(self.start_url, 0)
        print(f"{Fore.GREEN}[✓] Fertig. {len(self.leaks)} potenzielle Leaks gefunden.")
        if self.output:
            with open(self.output, 'w') as f:
                json.dump({"urls_visited": list(self.visited), "leaks": self.leaks}, f, indent=2)
            print(f"{Fore.GREEN}[✓] Gespeichert: {self.output}")

def main():
    parser = argparse.ArgumentParser(description="DarkWebMonitor")
    parser.add_argument("start_url", help="Start .onion URL")
    parser.add_argument("-d", "--depth", type=int, default=2, help="Crawl Tiefe")
    parser.add_argument("-o", "--output", help="JSON Output")
    args = parser.parse_args()
    
    print(f"{Fore.RED}[!] DarkWebMonitor: Nur für autorisierte Forschung!")
    confirm = input(f"{Fore.WHITE}[?] Fortfahren? (ja/NEIN): ").strip().lower()
    if confirm != "ja":
        print("Abbruch.")
        sys.exit(0)
    
    import json
    monitor = DarkWebMonitor(args.start_url, args.depth, args.output)
    monitor.run()

if __name__ == "__main__":
    main()
