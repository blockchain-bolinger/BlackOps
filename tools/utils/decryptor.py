#!/usr/bin/env python3
"""
Decryptor - Vielseitiges Encoding/Decoding Tool
"""

import argparse
import base64
import hashlib
import codecs
import json
import sys
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from colorama import Fore, init

init(autoreset=True)

class Decryptor:
    def __init__(self):
        pass
    
    def print_banner(self):
        print(rf"""{Fore.CYAN}
   ____            _            __       
  |  _ \  ___  ___| |_ _ __ ___ / _| ___  
  | | | |/ _ \/ __| __| '__/ _ \ |_ / _ \ 
  | |_| |  __/ (__| |_| | | (_) |  _| (_) |
  |____/ \___|\___|\__|_|  \___/|_|  \___/ 
{Fore.WHITE}   >> ENCODING / DECODING SUITE v1.0 <<
        """)
    
    def base64_decode(self, data):
        return base64.b64decode(data).decode('utf-8')
    
    def base64_encode(self, data):
        return base64.b64encode(data.encode()).decode()
    
    def rot13(self, data):
        return codecs.encode(data, 'rot_13')
    
    def md5(self, data):
        return hashlib.md5(data.encode()).hexdigest()
    
    def sha256(self, data):
        return hashlib.sha256(data.encode()).hexdigest()
    
    def aes_decrypt(self, data, key):
        # Einfache AES-256-CBC Entschlüsselung (Base64 Input)
        data = base64.b64decode(data)
        key = hashlib.sha256(key.encode()).digest()
        cipher = AES.new(key, AES.MODE_CBC, iv=data[:16])
        decrypted = cipher.decrypt(data[16:])
        return decrypted.rstrip(b'\x00').decode('utf-8')
    
    def jwt_decode(self, token):
        import jwt
        return jwt.decode(token, options={"verify_signature": False})
    
    def run(self, mode, input_data, key=None):
        if mode == "b64dec":
            result = self.base64_decode(input_data)
        elif mode == "b64enc":
            result = self.base64_encode(input_data)
        elif mode == "rot13":
            result = self.rot13(input_data)
        elif mode == "md5":
            result = self.md5(input_data)
        elif mode == "sha256":
            result = self.sha256(input_data)
        elif mode == "aesdec":
            if not key:
                print(f"{Fore.RED}[!] AES benötigt --key")
                return
            result = self.aes_decrypt(input_data, key)
        elif mode == "jwt":
            result = self.jwt_decode(input_data)
        else:
            print(f"{Fore.RED}[!] Unbekannter Modus")
            return
        print(f"{Fore.GREEN}Ergebnis:\n{result}")

def main():
    parser = argparse.ArgumentParser(description="Decryptor")
    parser.add_argument("mode", choices=["b64dec", "b64enc", "rot13", "md5", "sha256", "aesdec", "jwt"])
    parser.add_argument("data", help="Eingabedaten")
    parser.add_argument("--key", help="Schlüssel für AES")
    args = parser.parse_args()
    
    dec = Decryptor()
    dec.print_banner()
    dec.run(args.mode, args.data, args.key)

if __name__ == "__main__":
    main()
