#!/usr/bin/env python3
"""
CodeDigger - Scannt GitHub/GitLab nach API-Keys, Passwörtern, etc.
"""

import argparse
import requests
import re
import sys
import time
from colorama import Fore, init

init(autoreset=True)

class CodeDigger:
    def __init__(self, query, platform="github", token=None, output=None):
        self.query = query
        self.platform = platform
        self.token = token
        self.output = output
        self.results = []
    
    def print_banner(self):
        print(rf"""{Fore.CYAN}
   ____          _      ____  _             
  / ___|___   __| | ___|  _ \(_) __ _  __ _ 
 | |   / _ \ / _` |/ _ \ | | | |/ _` |/ _` |
 | |__| (_) | (_| |  __/ |_| | | (_| | (_| |
  \____\___/ \__,_|\___|____/|_|\__, |\__, |
                                |___/ |___/ 
{Fore.WHITE}   >> SECRET SCANNER FOR CODE REPOS v1.0 <<
{Fore.YELLOW}   NUR FÜR AUTORISIERTE TESTS!
        """)
    
    def search_github(self):
        headers = {}
        if self.token:
            headers['Authorization'] = f'token {self.token}'
        url = f"https://api.github.com/search/code?q={self.query}"
        try:
            r = requests.get(url, headers=headers)
            if r.status_code == 200:
                items = r.json().get('items', [])
                for item in items:
                    file_url = item['html_url']
                    self.results.append(file_url)
                    print(f"{Fore.GREEN}[+] {file_url}")
            else:
                print(f"{Fore.RED}[!] GitHub API Fehler: {r.status_code}")
        except Exception as e:
            print(f"{Fore.RED}[!] Fehler: {e}")
    
    def search_gitlab(self):
        # GitLab API
        url = f"https://gitlab.com/api/v4/projects?search={self.query}"
        headers = {'PRIVATE-TOKEN': self.token} if self.token else {}
        try:
            r = requests.get(url, headers=headers)
            if r.status_code == 200:
                projects = r.json()
                for proj in projects:
                    # Scanne Repository nach Dateien mit Schlüsselwörtern
                    proj_url = proj['web_url']
                    self.results.append(proj_url)
                    print(f"{Fore.GREEN}[+] {proj_url}")
            else:
                print(f"{Fore.RED}[!] GitLab API Fehler: {r.status_code}")
        except Exception as e:
            print(f"{Fore.RED}[!] Fehler: {e}")
    
    def run(self):
        self.print_banner()
        if self.platform == "github":
            self.search_github()
        else:
            self.search_gitlab()
        if self.output:
            with open(self.output, 'w') as f:
                json.dump(self.results, f, indent=2)
            print(f"{Fore.GREEN}[✓] Gespeichert: {self.output}")

def main():
    parser = argparse.ArgumentParser(description="CodeDigger")
    parser.add_argument("query", help="Suchbegriff (z.B. 'api_key', 'password')")
    parser.add_argument("--platform", choices=["github", "gitlab"], default="github")
    parser.add_argument("--token", help="GitHub/GitLab API Token")
    parser.add_argument("-o", "--output", help="JSON Output")
    args = parser.parse_args()
    
    print(f"{Fore.RED}[!] CodeDigger: Nur für autorisierte Tests!")
    confirm = input(f"{Fore.WHITE}[?] Fortfahren? (ja/NEIN): ").strip().lower()
    if confirm != "ja":
        print("Abbruch.")
        sys.exit(0)
    
    import json
    digger = CodeDigger(args.query, args.platform, args.token, args.output)
    digger.run()

if __name__ == "__main__":
    main()
