"""
Network Monitoring System für Black Ops Framework
"""

import socket
import threading
import time
import json
from datetime import datetime
from typing import Dict, List, Optional
from collections import defaultdict
import scapy.all as scapy
from scapy.layers.inet import IP, TCP, UDP, ICMP

class NetworkMonitor:
    def __init__(self):
        self.is_monitoring = False
        self.capture_thread = None
        self.packets = []
        self.statistics = defaultdict(int)
        self.connections = {}
        self.alerts = []
        
    def start_monitoring(self, interface: str = None, filter: str = None):
        """Startet Netzwerk-Monitoring"""
        if self.is_monitoring:
            print("[!] Monitoring already running")
            return
        
        self.is_monitoring = True
        self.capture_thread = threading.Thread(
            target=self._capture_packets,
            args=(interface, filter)
        )
        self.capture_thread.daemon = True
        self.capture_thread.start()
        
        print(f"[+] Network monitoring started on {interface or 'all interfaces'}")
    
    def stop_monitoring(self):
        """Stoppt Netzwerk-Monitoring"""
        self.is_monitoring = False
        if self.capture_thread:
            self.capture_thread.join(timeout=5)
        print("[+] Network monitoring stopped")
    
    def _capture_packets(self, interface: str, filter: str):
        """Fängt Pakete ab"""
        try:
            scapy.sniff(
                iface=interface,
                prn=self._process_packet,
                store=False,
                filter=filter
            )
        except Exception as e:
            print(f"[-] Capture error: {e}")
            self.is_monitoring = False
    
    def _process_packet(self, packet):
        """Verarbeitet gefangene Pakete"""
        if not self.is_monitoring:
            return
        
        packet_info = {
            'timestamp': datetime.now().isoformat(),
            'summary': packet.summary(),
            'hexdump': scapy.hexdump(packet, dump=True),
            'layers': self._extract_layers(packet)
        }
        
        self.packets.append(packet_info)
        
        # Update statistics
        if IP in packet:
            src = packet[IP].src
            dst = packet[IP].dst
            proto = packet[IP].proto
            
            self.statistics['total_packets'] += 1
            self.statistics[f'proto_{proto}'] += 1
            
            # Track connections
            conn_key = f"{src}:{dst}:{proto}"
            if conn_key not in self.connections:
                self.connections[conn_key] = {
                    'source': src,
                    'destination': dst,
                    'protocol': proto,
                    'packet_count': 0,
                    'first_seen': datetime.now().isoformat(),
                    'last_seen': datetime.now().isoformat()
                }
            
            self.connections[conn_key]['packet_count'] += 1
            self.connections[conn_key]['last_seen'] = datetime.now().isoformat()
            
            # Check for suspicious activity
            self._check_suspicious_activity(packet)
        
        # Limit packet storage
        if len(self.packets) > 10000:
            self.packets = self.packets[-5000:]
    
    def _extract_layers(self, packet) -> Dict:
        """Extrahiert Layer-Informationen"""
        layers = {}
        
        if IP in packet:
            layers['ip'] = {
                'src': packet[IP].src,
                'dst': packet[IP].dst,
                'ttl': packet[IP].ttl
            }
        
        if TCP in packet:
            layers['tcp'] = {
                'sport': packet[TCP].sport,
                'dport': packet[TCP].dport,
                'flags': packet[TCP].flags
            }
        
        if UDP in packet:
            layers['udp'] = {
                'sport': packet[UDP].sport,
                'dport': packet[UDP].dport
            }
        
        if ICMP in packet:
            layers['icmp'] = {
                'type': packet[ICMP].type,
                'code': packet[ICMP].code
            }
        
        return layers
    
    def _check_suspicious_activity(self, packet):
        """Prüft auf verdächtige Aktivitäten"""
        # Port scanning detection
        if TCP in packet and packet[TCP].flags == 2:  # SYN flag
            src = packet[IP].src
            dst = packet[IP].dst
            
            # Check for multiple SYN packets to different ports
            syn_key = f"syn_{src}_{dst}"
            if syn_key not in self.statistics:
                self.statistics[syn_key] = 0
            
            self.statistics[syn_key] += 1
            
            if self.statistics[syn_key] > 10:  # Threshold
                alert = {
                    'type': 'port_scan',
                    'source': src,
                    'target': dst,
                    'count': self.statistics[syn_key],
                    'timestamp': datetime.now().isoformat()
                }
                self.alerts.append(alert)
                print(f"[!] Port scan detected from {src} to {dst}")
        
        # DDoS detection
        if IP in packet:
            src = packet[IP].src
            pps_key = f"pps_{src}"  # Packets per second
            
            if pps_key not in self.statistics:
                self.statistics[pps_key] = []
            
            self.statistics[pps_key].append(time.time())
            
            # Clean old timestamps
            self.statistics[pps_key] = [t for t in self.statistics[pps_key] 
                                      if time.time() - t < 1]
            
            if len(self.statistics[pps_key]) > 100:  # 100 packets per second
                alert = {
                    'type': 'ddos',
                    'source': src,
                    'pps': len(self.statistics[pps_key]),
                    'timestamp': datetime.now().isoformat()
                }
                self.alerts.append(alert)
                print(f"[!] DDoS activity detected from {src}")
    
    def get_statistics(self) -> Dict:
        """Holt Statistik"""
        return {
            'total_packets': self.statistics.get('total_packets', 0),
            'active_connections': len(self.connections),
            'alerts': len(self.alerts),
            'protocol_distribution': {
                k: v for k, v in self.statistics.items() 
                if k.startswith('proto_')
            }
        }
    
    def get_recent_packets(self, count: int = 10) -> List[Dict]:
        """Holt letzte Pakete"""
        return self.packets[-count:]
    
    def get_alerts(self) -> List[Dict]:
        """Holt Alarme"""
        return self.alerts[-20:]  # Last 20 alerts
    
    def save_capture(self, filename: str = None):
        """Speichert Capture"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"network_capture_{timestamp}.json"
        
        capture_data = {
            'metadata': {
                'capture_date': datetime.now().isoformat(),
                'total_packets': len(self.packets),
                'duration': 'N/A'
            },
            'statistics': dict(self.statistics),
            'connections': self.connections,
            'alerts': self.alerts,
            'sample_packets': self.packets[-100:] if self.packets else []
        }
        
        capture_dir = Path("reports/network_captures")
        capture_dir.mkdir(parents=True, exist_ok=True)
        
        filepath = capture_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(capture_data, f, indent=2)
        
        print(f"[+] Capture saved to {filepath}")
        return str(filepath)
    
    def analyze_traffic(self) -> Dict:
        """Analysiert Netzwerkverkehr"""
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'total_packets': len(self.packets),
            'unique_ips': len(set(
                p['layers']['ip']['src'] for p in self.packets 
                if 'ip' in p['layers']
            )),
            'top_protocols': {},
            'suspicious_activity': len(self.alerts)
        }
        
        # Count protocols
        proto_counts = defaultdict(int)
        for packet in self.packets:
            if 'ip' in packet['layers']:
                proto = packet['layers']['ip'].get('protocol', 'unknown')
                proto_counts[proto] += 1
        
        analysis['top_protocols'] = dict(
            sorted(proto_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        )
        
        return analysis