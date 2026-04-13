import argparse
import requests
import socket
import dns.resolver
import sys
import json
import concurrent.futures
from datetime import datetime
from colorama import Fore, Style, init

# Init Colorama
init(autoreset=True)

class NetScoutPro:
    def __init__(self, target=None, threads=20, output_file=None):
        self.target = None
        self.domain = None
        self.threads = threads
        self.output_file = output_file
        self.results = {
            "target": "",
            "scan_time": str(datetime.now()),
            "headers": {},
            "dns": [],
            "open_ports": [],
            "subdomains": []
        }

        if target:
            self._configure_target(target, threads, output_file)

    def _configure_target(self, target, threads=None, output_file=None):
        self.target = target
        if threads is not None:
            self.threads = threads
        if output_file is not None:
            self.output_file = output_file
        self.domain = target.replace("https://", "").replace("http://", "").split("/")[0]
        self.results["target"] = self.domain
        self.results["scan_time"] = str(datetime.now())

        print(f"\n{Fore.CYAN}╔════════════════════════════════════════════════╗")
        print(f"{Fore.CYAN}║    NETSCOUT PRO - ADVANCED THREAT INTEL        ║")
        print(f"{Fore.CYAN}╚════════════════════════════════════════════════╝")
        print(f"{Fore.WHITE}[*] Ziel: {Fore.YELLOW}{self.domain}")
        print(f"{Fore.WHITE}[*] Threads: {Fore.YELLOW}{self.threads}")

    def check_http_headers(self):
        """Erweiterter Header Scan mit WAF-Detection"""
        print(f"\n{Fore.BLUE}[INFO] Analysiere Web-Technologie...")
        url = f"https://{self.domain}"
        try:
            res = requests.get(url, timeout=3)
            self.results["headers"] = dict(res.headers)
            
            server = res.headers.get("Server", "Unknown")
            print(f"{Fore.GREEN}  [+] Server: {server}")
            
            # WAF Detection (Simpel)
            waf_signatures = ["cloudflare", "cloudfront", "akamai"]
            for waf in waf_signatures:
                if waf in str(res.headers).lower():
                    print(f"{Fore.MAGENTA}  [!] WAF Erkannt: {waf.capitalize()}")
                    self.results["waf_detected"] = waf
                    
        except Exception:
            print(f"{Fore.RED}  [-] Webserver nicht erreichbar.")

    def scan_single_port(self, port):
        """Scannt einen Port und holt den Banner (Dienst-Version)"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1.5)
            result = sock.connect_ex((self.domain, port))
            
            if result == 0:
                # Versuch Banner zu grabben (Was antwortet der Server?)
                try:
                    sock.send(b"HEAD / HTTP/1.0\r\n\r\n")
                    banner = sock.recv(1024).decode().strip().split('\n')[0]
                except:
                    banner = "Unknown Service"
                
                sock.close()
                return port, banner
            sock.close()
        except:
            pass
        return None

    def run_port_scan(self):
        """Multithreaded Port Scan"""
        print(f"\n{Fore.BLUE}[INFO] Starte Turbo-Portscan (Top 100 Ports)...")
        
        # Top 100 Ports (verkürzt für Übersicht)
        common_ports = [21, 22, 23, 25, 53, 80, 110, 135, 139, 143, 443, 445, 993, 995, 1433, 3306, 3389, 5432, 5900, 6379, 8000, 8080, 8443]
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.threads) as executor:
            # Startet alle Scans gleichzeitig
            futures = {executor.submit(self.scan_single_port, port): port for port in common_ports}
            
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result:
                    port, banner = result
                    print(f"{Fore.GREEN}  [+] Port {port:<5} OPEN  >> {Fore.WHITE}{banner[:40]}")
                    self.results["open_ports"].append({"port": port, "banner": banner})

    def check_subdomain(self, sub):
        """Prüft ob eine Subdomain existiert"""
        full_domain = f"{sub}.{self.domain}"
        try:
            dns.resolver.resolve(full_domain, "A")
            return full_domain
        except:
            return None

    def run_subdomain_enum(self):
        """Sucht nach versteckten Subdomains"""
        print(f"\n{Fore.BLUE}[INFO] Brute-Force Subdomains...")
        # Kleine Liste für Demo-Zwecke (In echt nimmt man riesige Textdateien)
        subs = ["www", "mail", "ftp", "localhost", "webmail", "smtp", "pop", "ns1", "web", "test", "dev", "admin", "api", "vpn", "blog", "shop"]
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.threads) as executor:
            futures = {executor.submit(self.check_subdomain, sub): sub for sub in subs}
            
            for future in concurrent.futures.as_completed(futures):
                res = future.result()
                if res:
                    print(f"{Fore.GREEN}  [+] Subdomain gefunden: {res}")
                    self.results["subdomains"].append(res)

    def save_json(self):
        if self.output_file:
            with open(self.output_file, 'w') as f:
                json.dump(self.results, f, indent=4)
            print(f"\n{Fore.YELLOW}[SAVE] Bericht gespeichert in: {self.output_file}")

    def run(self):
        target = input(f"{Fore.GREEN}[?] Ziel Domain/URL: {Fore.WHITE}").strip()
        if not target:
            print(f"{Fore.RED}[ERROR] Kein Ziel angegeben.")
            return
        threads_raw = input(f"{Fore.GREEN}[?] Threads (default {self.threads}): {Fore.WHITE}").strip()
        output_file = input(f"{Fore.GREEN}[?] Output JSON (optional): {Fore.WHITE}").strip()

        threads = self.threads
        if threads_raw:
            try:
                threads = int(threads_raw)
            except ValueError:
                print(f"{Fore.YELLOW}[WARN] Ungültige Thread-Anzahl, nutze Default.")

        self._configure_target(target, threads=threads, output_file=output_file or None)

        # Workflow
        self.check_http_headers()
        self.run_subdomain_enum()
        self.run_port_scan()
        self.save_json()

def main():
    parser = argparse.ArgumentParser(description="NetScout Pro - High End Recon")
    parser.add_argument("target", help="Ziel Domain")
    parser.add_argument("-t", "--threads", type=int, default=20, help="Anzahl der Threads (Speed)")
    parser.add_argument("-o", "--output", help="Ergebnis als JSON speichern")
    
    args = parser.parse_args()

    scout = NetScoutPro(args.target, threads=args.threads, output_file=args.output)
    
    # Workflow
    scout.check_http_headers()
    scout.run_subdomain_enum()
    scout.run_port_scan()
    scout.save_json()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}[!] Abbruch.")
