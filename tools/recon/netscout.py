import argparse
import requests
import socket
import dns.resolver
import sys
from datetime import datetime
from colorama import Fore, Style, init

# Init Colorama
init(autoreset=True)

class NetScout:
    def __init__(self, target, verbose=False):
        self.target = target
        self.verbose = verbose
        # Entferne Protokoll für DNS/Socket Checks
        self.domain = target.replace("https://", "").replace("http://", "").split("/")[0]
        
        print(f"\n{Fore.CYAN}╔════════════════════════════════════════╗")
        print(f"{Fore.CYAN}║      NETSCOUT - RECONNAISSANCE TOOL    ║")
        print(f"{Fore.CYAN}╚════════════════════════════════════════╝")
        print(f"{Fore.WHITE}[*] Ziel: {Fore.YELLOW}{self.domain}")
        print(f"{Fore.WHITE}[*] Startzeit: {datetime.now().strftime('%H:%M:%S')}\n")

    def check_http_headers(self):
        """Prüft Sicherheits-Header und Server-Infos"""
        print(f"{Fore.BLUE}[INFO] Prüfe HTTP-Header...")
        url = f"https://{self.domain}"
        try:
            res = requests.get(url, timeout=5)
            server = res.headers.get("Server", "Unknown")
            x_powered = res.headers.get("X-Powered-By", "Hidden")
            
            print(f"{Fore.GREEN}  [+] Status: {res.status_code}")
            print(f"{Fore.GREEN}  [+] Server: {server}")
            
            if x_powered != "Hidden":
                print(f"{Fore.YELLOW}  [!] Backend Technologie geleakt: {x_powered}")
            
            sec_headers = ["X-Frame-Options", "Content-Security-Policy", "Strict-Transport-Security"]
            for h in sec_headers:
                if h not in res.headers:
                    print(f"{Fore.RED}  [-] Missing Security Header: {h}")
                elif self.verbose:
                    print(f"{Fore.GREEN}  [+] Header vorhanden: {h}")

        except Exception as e:
            print(f"{Fore.RED}  [ERROR] HTTP Check fehlgeschlagen: {e}")

    def get_dns_records(self):
        """Holt DNS Einträge (A, MX, NS)"""
        print(f"\n{Fore.BLUE}[INFO] Hole DNS Einträge...")
        record_types = ["A", "MX", "NS", "TXT"]
        
        for record in record_types:
            try:
                answers = dns.resolver.resolve(self.domain, record)
                for rdata in answers:
                    print(f"{Fore.GREEN}  [+] {record}: {rdata.to_text()}")
            except dns.resolver.NoAnswer:
                pass
            except dns.resolver.NXDOMAIN:
                print(f"{Fore.RED}  [-] Domain existiert nicht.")
                return
            except Exception as e:
                if self.verbose:
                    print(f"{Fore.RED}  [ERROR] DNS Fehler ({record}): {e}")

    def scan_ports(self):
        """Scannt die wichtigsten Ports"""
        print(f"\n{Fore.BLUE}[INFO] Scanne wichtige Ports (kann dauern)...")
        ports = {
            21: "FTP",
            22: "SSH",
            80: "HTTP",
            443: "HTTPS",
            3306: "MySQL"
        }
        
        for port, service in ports.items():
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((self.domain, port))
            if result == 0:
                print(f"{Fore.GREEN}  [+] Port {port} ({service}) ist OFFEN")
            else:
                if self.verbose:
                    print(f"{Fore.WHITE}  [.] Port {port} ({service}) ist geschlossen")
            sock.close()

def main():
    parser = argparse.ArgumentParser(description="NetScout - Ein einfaches Recon-Tool")
    parser.add_argument("target", help="Die Ziel-Domain (z.B. google.com)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Zeige detaillierte Ausgaben")
    parser.add_argument("--scan-ports", action="store_true", help="Aktiviere den Port-Scanner")
    
    args = parser.parse_args()

    scout = NetScout(args.target, args.verbose)
    scout.check_http_headers()
    scout.get_dns_records()
    
    if args.scan_ports:
        scout.scan_ports()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}[!] Abbruch durch Benutzer.")
