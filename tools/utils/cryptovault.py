import base64
import hashlib
import os
import sys
from colorama import Fore, init

init(autoreset=True)

class CryptoVault:
    def banner(self):
        os.system('clear')
        print(f"""{Fore.MAGENTA}
   ______                 __        _    __            ____ 
  / ____/________  ____  / /_____  | |  / /___ ___  __/ / /_
 / /   / ___/ __ \/ __ \/ __/ __ \ | | / / __ `/ / / / / __/
/ /___/ /  / /_/ / /_/ / /_/ /_/ / | |/ / /_/ / /_/ / / /_  
\____/_/   \__, / .___/\__/\____/  |___/\__,_/\__,_/_/\__/  
          /____/_/                                          
{Fore.WHITE}   >> ENCODING & HASHING UTILITY <<
""")

    def run(self):
        self.banner()
        print(f"{Fore.WHITE}[1] Base64 Encode")
        print(f"{Fore.WHITE}[2] Base64 Decode")
        print(f"{Fore.WHITE}[3] Generate MD5/SHA256 Hash")
        print(f"{Fore.WHITE}[4] Rot13 Cipher")
        
        c = input(f"\n{Fore.YELLOW}[?] Wahl: ")
        
        if c == '1':
            txt = input("Text: ")
            print(f"{Fore.GREEN}Result: {base64.b64encode(txt.encode()).decode()}")
        elif c == '2':
            try:
                txt = input("Base64 String: ")
                print(f"{Fore.GREEN}Result: {base64.b64decode(txt).decode()}")
            except: print(f"{Fore.RED}Fehler: Kein gültiges Base64")
        elif c == '3':
            txt = input("Text: ")
            print(f"MD5:    {hashlib.md5(txt.encode()).hexdigest()}")
            print(f"SHA256: {hashlib.sha256(txt.encode()).hexdigest()}")
        elif c == '4':
            txt = input("Text: ")
            import codecs
            print(f"{Fore.GREEN}Result: {codecs.encode(txt, 'rot_13')}")
            
        input("\n[ENTER] Zurück...")

if __name__ == "__main__":
    CryptoVault().run()
