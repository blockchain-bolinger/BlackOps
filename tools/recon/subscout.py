#!/usr/bin/env python3
"""
SubScout - Subdomain Enumeration
NUR FÜR AUTORISIERTE TESTS!
"""

import argparse
import concurrent.futures
import json
import os
from datetime import datetime

import dns.resolver
from colorama import Fore, init

init(autoreset=True)


class SubScout:
    def __init__(self, target, threads=20, wordlist=None, output=None):
        self.target = target.replace("https://", "").replace("http://", "").split("/")[0]
        self.threads = threads
        self.wordlist = wordlist or "data/wordlists/subdomains.txt"
        self.output = output
        self.results = {
            "target": self.target,
            "scan_time": datetime.now().isoformat(),
            "found": []
        }

    def load_wordlist(self):
        if os.path.exists(self.wordlist):
            with open(self.wordlist, "r", encoding="utf-8", errors="ignore") as f:
                return [line.strip() for line in f if line.strip() and not line.startswith("#")]
        return ["www", "mail", "api", "dev", "test", "admin", "blog", "shop"]

    def resolve_subdomain(self, sub):
        fqdn = f"{sub}.{self.target}"
        try:
            answers = dns.resolver.resolve(fqdn, "A")
            ips = sorted({str(rdata) for rdata in answers})
            return {"host": fqdn, "ips": ips}
        except Exception:
            return None

    def run(self):
        print(f"{Fore.CYAN}[*] SubScout startet für: {Fore.YELLOW}{self.target}")
        subdomains = self.load_wordlist()
        print(f"{Fore.CYAN}[*] Prüfe {len(subdomains)} Subdomains mit {self.threads} Threads...")

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.threads) as executor:
            futures = [executor.submit(self.resolve_subdomain, sub) for sub in subdomains]
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result:
                    self.results["found"].append(result)
                    print(f"{Fore.GREEN}[+] Gefunden: {result['host']} -> {', '.join(result['ips'])}")

        self.results["found"] = sorted(self.results["found"], key=lambda item: item["host"])
        print(f"{Fore.CYAN}[*] Fertig. Gefunden: {len(self.results['found'])}")

        if self.output:
            with open(self.output, "w", encoding="utf-8") as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False)
            print(f"{Fore.GREEN}[+] Ergebnis gespeichert: {self.output}")


def main():
    parser = argparse.ArgumentParser(description="SubScout - Subdomain Enumeration")
    parser.add_argument("target", help="Ziel-Domain (z.B. example.com)")
    parser.add_argument("-t", "--threads", type=int, default=20, help="Anzahl Threads")
    parser.add_argument("-w", "--wordlist", help="Pfad zur Subdomain-Wordlist")
    parser.add_argument("-o", "--output", help="JSON-Output Datei")
    args = parser.parse_args()

    print(f"{Fore.RED}[!] SubScout: Nur für autorisierte Tests!")
    confirm = input(f"{Fore.WHITE}[?] Fortfahren? (ja/NEIN): ").strip().lower()
    if confirm != "ja":
        print("Abbruch.")
        return

    scout = SubScout(args.target, threads=args.threads, wordlist=args.wordlist, output=args.output)
    scout.run()


if __name__ == "__main__":
    main()
