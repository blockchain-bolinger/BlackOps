import os
import subprocess
import sys
import time
import random
from colorama import Fore, Style, init

init(autoreset=True)

class TraceLess:
    def __init__(self):
        # Wichtige Log-Dateien auf Linux Systemen
        self.log_files = [
            "/var/log/auth.log",
            "/var/log/syslog",
            "/var/log/messages",
            "/var/log/wtmp",    # Login records
            "/var/log/btmp",    # Failed login records
            "/var/log/lastlog"  # Last login records
        ]
        self.user_history = os.path.expanduser("~/.bash_history")
        self.root_history = "/root/.bash_history"

    def banner(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"""{Fore.RED}
  ______                      __                
 /_  __/________ _________   / /   ___  _____ _____
  / / / ___/ __ `/ ___/ _ \ / /   / _ \/ ___// ___/
 / / / /  / /_/ / /__/  __// /___/  __(__  )(__  ) 
/_/ /_/   \__,_/\___/\___//_____/\___/____//____/  
                                                   
{Fore.WHITE}   >> SYSTEM CLEANER & LOG WIPER <<
{Fore.WHITE}   --------------------------------
""")

    def check_shred(self):
        """Prüfe ob shred verfügbar ist"""
        try:
            result = subprocess.run(["which", "shred"], capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False

    def secure_delete(self, filepath):
        """Sicheres Löschen mit Fallback"""
        if not os.path.exists(filepath):
            return False
        
        shred_available = self.check_shred()
        
        try:
            if shred_available:
                # Methode 1: shred (Linux)
                print(f"{Fore.CYAN}   -> Verwende shred...")
                subprocess.call(["shred", "-u", "-z", "-n", "3", filepath], 
                              stderr=subprocess.DEVNULL,
                              stdout=subprocess.DEVNULL)
            else:
                # Methode 2: Python-Only (plattformunabhängig)
                print(f"{Fore.YELLOW}   -> 'shred' nicht verfügbar. Verwende Python-Methode...")
                
                try:
                    file_size = os.path.getsize(filepath)
                    # Mehrfaches Überschreiben
                    patterns = [
                        b'\x00' * 1024,  # Null-Bytes
                        b'\xFF' * 1024,  # Einsen
                        bytes([random.randint(0, 255) for _ in range(1024)])  # Zufall
                    ]
                    
                    for pattern in patterns:
                        try:
                            with open(filepath, 'wb') as f:
                                for _ in range(max(1, (file_size // 1024) + 1)):
                                    f.write(pattern)
                        except:
                            pass
                    
                    # Umbenennen und löschen
                    try:
                        temp_name = filepath + ".deleted"
                        os.rename(filepath, temp_name)
                        os.remove(temp_name)
                    except:
                        os.remove(filepath)
                except Exception as e:
                    print(f"{Fore.RED}   -> Fehler: {e}")
                    return False
            
            return True
            
        except Exception as e:
            print(f"{Fore.RED}[ERROR] Löschen fehlgeschlagen: {e}")
            return False

    # --- MODUL 2: LOG WIPER ---
    def wipe_logs(self):
        print(f"\n{Fore.WHITE}[*] Starte Log-Wiper Sequenz...")
        
        count = 0
        for log in self.log_files:
            if os.path.exists(log):
                print(f"{Fore.YELLOW}   [~] Bereinige: {log}...")
                
                # Bei Systemlogs löschen wir sie nicht komplett (das crasht Dienste),
                # sondern leeren nur den Inhalt sicher.
                try:
                    # Versuche sicheres Löschen
                    if self.secure_delete(log):
                        print(f"{Fore.GREEN}       -> Bereinigt.")
                        count += 1
                    else:
                        # Fallback: Datei leeren (truncate)
                        open(log, 'w').close()
                        print(f"{Fore.YELLOW}       -> Inhalt geleert.")
                        count += 1
                except PermissionError:
                    print(f"{Fore.RED}       -> FEHLER: Keine Rechte (sudo nutzen!).")
                except Exception as e:
                    print(f"{Fore.RED}       -> Fehler: {e}")
            else:
                print(f"{Fore.WHITE}   [i] Datei nicht gefunden: {log}")
                
        print(f"\n{Fore.WHITE}[OK] {count} System-Logdateien bereinigt.")

    # --- MODUL 3: HISTORY WIPER ---
    def wipe_history(self):
        print(f"\n{Fore.WHITE}[*] Lösche Bash History...")
        
        targets = [self.user_history]
        if os.geteuid() == 0:
            targets.append(self.root_history)
            
        for hist in targets:
            if os.path.exists(hist):
                if self.secure_delete(hist):
                    print(f"{Fore.GREEN}   [+] History Datei geschreddert: {hist}")
                else:
                    print(f"{Fore.RED}   [-] Fehler beim Löschen von: {hist}")
            else:
                print(f"{Fore.WHITE}   [i] Keine History Datei gefunden: {hist}")

        # WICHTIG: Die aktuelle Session hat die History noch im RAM.
        # Wir müssen dem System sagen: "Vergiss, was gerade passiert ist"
        print(f"{Fore.GREEN}   [+] Leere aktuelle Session History...")
        try:
            os.system('history -c')
            os.system('history -w')
        except:
            pass

    # --- MAIN MENU ---
    def run(self):
        if os.geteuid() != 0:
            print(f"{Fore.RED}[CRITICAL] Dieses Tool muss mit SUDO gestartet werden!")
            print("Befehl: sudo python traceless.py")
            return

        while True:
            self.banner()
            print(f"{Fore.WHITE}[1] Wipe System Logs (auth, syslog, etc.)")
            print(f"{Fore.WHITE}[2] Wipe Bash History (Befehlsverlauf)")
            print(f"{Fore.WHITE}[3] NUCLEAR OPTION (Alles bereinigen & Exit)")
            print(f"{Fore.WHITE}[99] Exit")
            print(f"\n{Fore.CYAN}---------------------------------------------")
            
            choice = input(f"{Fore.YELLOW}[?] Auswahl: ")
            
            if choice == '1':
                self.wipe_logs()
            elif choice == '2':
                self.wipe_history()
            elif choice == '3':
                self.wipe_logs()
                self.wipe_history()
                print(f"\n{Fore.GREEN}[*] System ist sauber. Bye!")
                return
            elif choice == '99':
                return
            
            input(f"\n{Fore.WHITE}[ENTER] Zurück zum Menü...")

if __name__ == "__main__":
    tool = TraceLess()
    tool.run()
