import hashlib
import sys
import os
import time
from colorama import Fore, Style, init

init(autoreset=True)

class HashBreaker:
    def __init__(self):
        self.banner()

    def banner(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print(rf"""{Fore.RED}
    __  __           __    ____                  __            
   / / / /___ ______/ /_  / __ )________  ____ _/ /_____  _____
  / /_/ / __ `/ ___/ __ \/ __  / ___/ _ \/ __ `/ //_/ _ \/ ___/
 / __  / /_/ (__  ) / / / /_/ / /  /  __/ /_/ / ,< /  __/ /    
/_/ /_/\__,_/____/_/ /_/_____/_/   \___/\__,_/_/|_|\___/_/     
                                                               
{Fore.WHITE}      >> OFFLINE DICTIONARY ATTACK TOOL <<
""")

    def crack(self, target_hash, wordlist_path, algo_type):
        print(f"\n{Fore.WHITE}[*] Starte Angriff auf: {Fore.YELLOW}{target_hash}")
        print(f"{Fore.WHITE}[*] Algorithmus: {Fore.CYAN}{algo_type}")
        print(f"{Fore.WHITE}[*] Wordlist: {wordlist_path}")
        
        try:
            with open(wordlist_path, "r", encoding="latin-1") as f:
                for line in f:
                    password = line.strip()
                    
                    # Hash berechnen
                    if algo_type == "md5":
                        attempt = hashlib.md5(password.encode()).hexdigest()
                    elif algo_type == "sha256":
                        attempt = hashlib.sha256(password.encode()).hexdigest()
                    elif algo_type == "sha1":
                        attempt = hashlib.sha1(password.encode()).hexdigest()
                    else:
                        print("Unbekannter Algo")
                        return

                    if attempt == target_hash:
                        print(f"\n{Fore.GREEN}SUCCESS! PASSWORT GEFUNDEN:")
                        print(f"{Fore.GREEN}>>> {password} <<<")
                        return
                        
            print(f"\n{Fore.RED}[-] Passwort nicht in der Liste gefunden.")
            
        except FileNotFoundError:
            print(f"{Fore.RED}[ERROR] Wordlist nicht gefunden.")

    def run(self):
        print(f"{Fore.WHITE}[1] MD5")
        print(f"{Fore.WHITE}[2] SHA-256")
        print(f"{Fore.WHITE}[3] SHA-1")
        algo_choice = input(f"{Fore.YELLOW}[?] Welcher Hash-Typ? ")
        
        algos = {"1": "md5", "2": "sha256", "3": "sha1"}
        algo = algos.get(algo_choice)
        
        if not algo: return

        target = input(f"{Fore.GREEN}[?] Ziel-Hash eingeben: ").strip()
        wordlist = input(f"{Fore.GREEN}[?] Pfad zur Wordlist (Default: /usr/share/wordlists/rockyou.txt): ").strip()
        
        if not wordlist:
            wordlist = "/usr/share/wordlists/rockyou.txt"
            
        self.crack(target, wordlist, algo)
        input(f"\n{Fore.WHITE}[ENTER] Zurück...")

if __name__ == "__main__":
    tool = HashBreaker()
    tool.run()
