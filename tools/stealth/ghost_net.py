"""
Ghost Net - Advanced Stealth & Anonymity Tool
"""

import requests
import socks
import socket
import random
import time
import sys
from typing import List, Dict, Optional
from core.blackops_logger import BlackOpsLogger
from core.ethics_enforcer import EthicsEnforcer

class GhostNet:
    def __init__(self):
        self.logger = BlackOpsLogger("GhostNet")
        self.ethics = EthicsEnforcer()
        self.proxies = []
        self.tor_controller = None
        self.current_ip = None
    
    def enable_tor(self, control_port: int = 9051, password: str = None):
        """Aktiviert Tor Proxy"""
        try:
            try:
                from stem import Signal
                from stem.control import Controller
            except ImportError:
                self.logger.error("Missing dependency: stem. Install with: pip install stem")
                return False

            self.tor_controller = Controller.from_port(port=control_port)
            
            if password:
                self.tor_controller.authenticate(password=password)
            else:
                self.tor_controller.authenticate()
            
            # Set SOCKS proxy
            socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", 9050)
            socket.socket = socks.socksocket
            
            self.logger.info("Tor proxy enabled")
            
            # Get current IP
            self.current_ip = self.get_current_ip()
            self.logger.info(f"Current IP: {self.current_ip}")
            
            return True
        except Exception as e:
            self.logger.error(f"Failed to enable Tor: {e}")
            return False
    
    def renew_tor_identity(self):
        """Erneuert Tor Identity"""
        if self.tor_controller:
            try:
                from stem import Signal
                self.tor_controller.signal(Signal.NEWNYM)
                time.sleep(5)  # Wait for new circuit
                
                self.current_ip = self.get_current_ip()
                self.logger.info(f"New IP: {self.current_ip}")
                
                return True
            except Exception as e:
                self.logger.error(f"Failed to renew Tor identity: {e}")
        
        return False
    
    def get_current_ip(self) -> Optional[str]:
        """Holt aktuelle IP Adresse"""
        try:
            # Use Tor if enabled
            if self.tor_controller:
                session = requests.Session()
                session.proxies = {
                    'http': 'socks5://127.0.0.1:9050',
                    'https': 'socks5://127.0.0.1:9050'
                }
                response = session.get('https://api.ipify.org', timeout=10)
            else:
                response = requests.get('https://api.ipify.org', timeout=10)
            
            return response.text.strip()
        except Exception as e:
            self.logger.error(f"Failed to get IP: {e}")
            return None
    
    def load_proxy_list(self, filepath: str = "data/configs/proxies.txt"):
        """Lädt Proxy Liste"""
        try:
            with open(filepath, 'r') as f:
                proxies = [line.strip() for line in f if line.strip()]
                self.proxies = proxies
            
            self.logger.info(f"Loaded {len(self.proxies)} proxies")
            return True
        except Exception as e:
            self.logger.error(f"Failed to load proxy list: {e}")
            return False
    
    def get_random_proxy(self) -> Optional[Dict]:
        """Wählt zufälligen Proxy aus"""
        if not self.proxies:
            return None
        
        proxy = random.choice(self.proxies)
        
        if '://' in proxy:
            # Format: protocol://ip:port
            protocol, address = proxy.split('://')
        else:
            # Format: ip:port (default to http)
            protocol = 'http'
            address = proxy
        
        return {
            'http': f"{protocol}://{address}",
            'https': f"{protocol}://{address}"
        }
    
    def test_proxy(self, proxy: Dict) -> bool:
        """Testet Proxy"""
        try:
            response = requests.get(
                'https://api.ipify.org',
                proxies=proxy,
                timeout=10
            )
            
            ip = response.text.strip()
            self.logger.debug(f"Proxy IP: {ip}")
            return True
        except:
            return False
    
    def rotate_proxy(self, max_attempts: int = 10) -> Optional[Dict]:
        """Rotiert durch Proxies bis einer funktioniert"""
        attempts = 0
        
        while attempts < max_attempts and self.proxies:
            proxy = self.get_random_proxy()
            
            if self.test_proxy(proxy):
                # Set as default
                import requests
                requests.Session().proxies = proxy
                
                self.logger.info(f"Using proxy: {proxy}")
                return proxy
            
            attempts += 1
            time.sleep(1)
        
        self.logger.error("No working proxies found")
        return None
    
    def spoof_user_agent(self) -> str:
        """Generiert zufälligen User-Agent"""
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (X11; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0'
        ]
        
        return random.choice(user_agents)
    
    def create_stealth_session(self, use_tor: bool = True, 
                              use_proxy: bool = False) -> requests.Session:
        """Erstellt Stealth Session"""
        session = requests.Session()
        
        # Spoof headers
        session.headers.update({
            'User-Agent': self.spoof_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',  # Do Not Track
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        # Use Tor
        if use_tor and self.tor_controller:
            session.proxies = {
                'http': 'socks5://127.0.0.1:9050',
                'https': 'socks5://127.0.0.1:9050'
            }
        
        # Use random proxy
        elif use_proxy and self.proxies:
            proxy = self.rotate_proxy()
            if proxy:
                session.proxies = proxy
        
        return session
    
    def stealth_request(self, url: str, method: str = "GET", 
                       data: Dict = None, headers: Dict = None,
                       delay: float = 0) -> Optional[requests.Response]:
        """Führt Stealth Request durch"""
        if not self.ethics.check_target(url):
            return None
        
        session = self.create_stealth_session()
        
        # Add custom headers
        if headers:
            session.headers.update(headers)
        
        # Random delay to avoid rate limiting
        if delay:
            time.sleep(delay + random.uniform(0, 2))
        
        try:
            if method.upper() == "GET":
                response = session.get(url, timeout=30)
            elif method.upper() == "POST":
                response = session.post(url, data=data, timeout=30)
            else:
                self.logger.error(f"Unsupported method: {method}")
                return None
            
            self.logger.debug(f"Request to {url}: {response.status_code}")
            return response
            
        except Exception as e:
            self.logger.error(f"Stealth request failed: {e}")
            return None
    
    def check_fingerprint(self) -> Dict:
        """Prüft Browser/System Fingerprint"""
        # This would normally use JavaScript in a browser
        # For Python, we can check some basic indicators
        
        fingerprint = {
            'user_agent': self.spoof_user_agent(),
            'timezone': time.tzname[0],
            'screen_resolution': '1920x1080',  # Common
            'plugins': ['PDF Viewer', 'Chrome PDF Viewer'],
            'fonts': ['Arial', 'Times New Roman', 'Courier New'],
            'webgl_vendor': 'Google Inc.',
            'webgl_renderer': 'ANGLE (Intel(R) UHD Graphics Direct3D11 vs_5_0 ps_5_0)',
            'canvas_hash': 'fake_canvas_hash',
            'webgl_hash': 'fake_webgl_hash'
        }
        
        return fingerprint
    
    def _run_interactive(self):
        """Interaktiver Menü-Modus für Aufruf aus dem Hauptmenü"""
        print("\n--- GHOST NET ---")
        print("1. Check Current IP")
        print("2. Test Proxy List")
        print("3. Stealth Request")
        print("4. Back")

        choice = input("Select option: ").strip()
        if choice == "1":
            use_tor = input("Use Tor? (y/N): ").strip().lower() == "y"
            if use_tor and not self.enable_tor():
                return
            ip = self.get_current_ip()
            print(f"Current IP: {ip}")
        elif choice == "2":
            proxy_file = input("Proxy file [data/configs/proxies.txt]: ").strip() or "data/configs/proxies.txt"
            if self.load_proxy_list(proxy_file):
                proxy = self.rotate_proxy()
                if proxy:
                    print(f"Working proxy: {proxy}")
        elif choice == "3":
            url = input("Target URL: ").strip()
            if not url:
                return
            method = input("HTTP method [GET]: ").strip().upper() or "GET"
            delay_raw = input("Delay seconds [0]: ").strip() or "0"
            use_tor = input("Use Tor? (y/N): ").strip().lower() == "y"
            try:
                delay = float(delay_raw)
            except ValueError:
                delay = 0
            if use_tor:
                self.enable_tor()
            response = self.stealth_request(url, method=method, delay=delay)
            if response:
                print(f"Status: {response.status_code}")
                print(f"Headers: {dict(response.headers)}")
                print(f"\nContent (first 500 chars):\n{response.text[:500]}")

    def run(self):
        """Hauptfunktion für CLI"""
        import argparse
        
        parser = argparse.ArgumentParser(description="Ghost Net - Stealth Tool")
        subparsers = parser.add_subparsers(dest='command', help='Command')
        
        # IP check command
        ip_parser = subparsers.add_parser('ip', help='Check current IP')
        ip_parser.add_argument("-t", "--tor", action="store_true", 
                             help="Use Tor")
        
        # Proxy test command
        proxy_parser = subparsers.add_parser('proxy', help='Test proxies')
        proxy_parser.add_argument("-f", "--file", default="data/configs/proxies.txt",
                                help="Proxy list file")
        
        # Request command
        req_parser = subparsers.add_parser('request', help='Make stealth request')
        req_parser.add_argument("url", help="Target URL")
        req_parser.add_argument("-m", "--method", default="GET", 
                              help="HTTP method")
        req_parser.add_argument("-d", "--delay", type=float, default=0,
                              help="Delay between requests")
        req_parser.add_argument("-t", "--tor", action="store_true",
                              help="Use Tor")
        
        known_commands = {"ip", "proxy", "request"}
        if not any(arg in known_commands for arg in sys.argv[1:]):
            self.logger.print_banner()
            self._run_interactive()
            return

        args, _unknown = parser.parse_known_args()
        
        self.logger.print_banner()
        
        if args.command == 'ip':
            if args.tor:
                if not self.enable_tor():
                    return
            ip = self.get_current_ip()
            print(f"Current IP: {ip}")
        
        elif args.command == 'proxy':
            if self.load_proxy_list(args.file):
                proxy = self.rotate_proxy()
                if proxy:
                    print(f"Working proxy: {proxy}")
        
        elif args.command == 'request':
            if args.tor:
                self.enable_tor()
            
            response = self.stealth_request(args.url, args.method, delay=args.delay)
            
            if response:
                print(f"Status: {response.status_code}")
                print(f"Headers: {dict(response.headers)}")
                print(f"\nContent (first 500 chars):\n{response.text[:500]}")

if __name__ == '__main__':
    GhostNet().run()
