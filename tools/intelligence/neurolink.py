import os
import sys
import json
import time
from colorama import Fore, Style, init
from core.secrets_manager import SecretsManager

init(autoreset=True)

class NeuroLink:
    def __init__(self):
        self.OpenAI = None
        try:
            from openai import OpenAI
            self.OpenAI = OpenAI
        except ImportError:
            self.OpenAI = None

        self.api_key = self.load_secrets()
        self.client = None
        if self.api_key and self.validate_api_key(self.api_key) and self.OpenAI:
            self.client = self.OpenAI(api_key=self.api_key)
        
        # Das Gedächtnis der KI
        self.history = [
            {"role": "system", "content": "You are 'NeuroLink', an advanced cybersecurity AI assistant integrated into the Black Ops Framework. You provide precise, technical, and ethical hacking advice. You help with syntax for tools like Nmap, Metasploit, and Python. Keep answers concise and cool."}
        ]

    def load_secrets(self):
        manager = SecretsManager(path="secrets.json")
        return manager.get("openai_key")

    def validate_api_key(self, key):
        """Prüft ob API-Key ein Platzhalter ist"""
        if not key:
            return False
        if "DEIN-" in key or "sk-" not in key:
            return False
        if len(key) < 20:  # Minimale Länge
            return False
        return True

    def banner(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print(rf"""{Fore.GREEN}
   _   __                     __    _       __  
  / | / /__  __  ___________ / /   (_)___  / /__
 /  |/ / _ \/ / / / ___/ __ \/ /   / / __ \/ //_/
/ /|  /  __/ /_/ / /  / /_/ / /___/ / / / / ,<   
/_/ |_/\___/\__,_/_/   \____/_____/_/_/ /_/_/|_|   
                                                   
{Fore.WHITE}   >> AI TACTICAL ADVISOR (GPT-4o) <<
""")

    def chat_loop(self):
        self.banner()
        
        if not self.OpenAI:
            print("Bitte installiere erst die Library: pip install openai")
            input("\n[ENTER] Zurück...")
            return

        if not self.client or not self.validate_api_key(self.api_key):
            print(f"{Fore.RED}[ERROR] Ungültiger oder fehlender OpenAI API Key!")
            print(f"{Fore.YELLOW}Bitte trage einen gültigen Key in secrets.json ein")
            print(f"{Fore.CYAN}Format: 'openai_key': 'sk-...'")
            input("\n[ENTER] Zurück...")
            return

        print(f"{Fore.CYAN}[SYSTEM] NeuroLink Online. Waiting for input...")
        print(f"{Fore.WHITE}Tippe 'exit' oder '99' zum Beenden.\n")

        while True:
            try:
                user_input = input(f"{Fore.GREEN}Operator: {Fore.WHITE}")
                
                if user_input.lower() in ['exit', 'quit', '99']:
                    break
                
                # User Input zum Gedächtnis hinzufügen
                self.history.append({"role": "user", "content": user_input})
                
                print(f"{Fore.YELLOW}NeuroLink denkt nach...", end="\r")
                
                # Anfrage an OpenAI senden
                response = self.client.chat.completions.create(
                    model="gpt-4o",
                    messages=self.history,
                    temperature=0.7
                )
                
                ai_answer = response.choices[0].message.content
                
                # Antwort anzeigen
                print(f"\r{Fore.CYAN}NeuroLink: {Fore.WHITE}{ai_answer}\n")
                
                # Antwort zum Gedächtnis hinzufügen
                self.history.append({"role": "assistant", "content": ai_answer})

            except Exception as e:
                print(f"\n{Fore.RED}[ERROR] Verbindung unterbrochen: {e}")
                break

    def run(self):
        self.chat_loop()

if __name__ == "__main__":
    ai = NeuroLink()
    ai.chat_loop()
