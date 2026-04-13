"""
Advanced Encryption Manager für Black Ops Framework
"""

import os
import base64
import hashlib
from typing import Optional, Union
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

class EncryptionManager:
    def __init__(self, master_key: Optional[str] = None):
        self.master_key = master_key or os.urandom(32).hex()
        self._init_crypto()
    
    def _init_crypto(self):
        """Initialisiert Kryptographie-System"""
        # Key Derivation Function
        salt = b'blackops_salt_2024'
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        
        key_material = self.master_key.encode() if isinstance(self.master_key, str) else self.master_key
        self.derived_key = base64.urlsafe_b64encode(kdf.derive(key_material))
        self.fernet = Fernet(self.derived_key)
    
    def encrypt_string(self, plaintext: str) -> str:
        """Verschlüsselt einen String"""
        return self.fernet.encrypt(plaintext.encode()).decode()
    
    def decrypt_string(self, ciphertext: str) -> str:
        """Entschlüsselt einen String"""
        return self.fernet.decrypt(ciphertext.encode()).decode()
    
    def encrypt_file(self, input_path: str, output_path: Optional[str] = None) -> str:
        """Verschlüsselt eine Datei"""
        if not output_path:
            output_path = input_path + ".enc"
        
        with open(input_path, 'rb') as f:
            data = f.read()
        
        encrypted = self.fernet.encrypt(data)
        
        with open(output_path, 'wb') as f:
            f.write(encrypted)
        
        return output_path
    
    def decrypt_file(self, input_path: str, output_path: Optional[str] = None) -> str:
        """Entschlüsselt eine Datei"""
        if not output_path:
            if input_path.endswith(".enc"):
                output_path = input_path[:-4] + ".dec"
            else:
                output_path = input_path + ".dec"
        
        with open(input_path, 'rb') as f:
            encrypted = f.read()
        
        decrypted = self.fernet.decrypt(encrypted)
        
        with open(output_path, 'wb') as f:
            f.write(decrypted)
        
        return output_path
    
    def generate_hash(self, data: Union[str, bytes], algorithm: str = "sha256") -> str:
        """Generiert Hash von Daten"""
        if isinstance(data, str):
            data = data.encode()
        
        if algorithm == "md5":
            return hashlib.md5(data).hexdigest()
        elif algorithm == "sha1":
            return hashlib.sha1(data).hexdigest()
        elif algorithm == "sha256":
            return hashlib.sha256(data).hexdigest()
        elif algorithm == "sha512":
            return hashlib.sha512(data).hexdigest()
        else:
            raise ValueError(f"Unsupported algorithm: {algorithm}")
    
    def aes_encrypt(self, plaintext: str, key: bytes) -> bytes:
        """AES-Verschlüsselung"""
        iv = os.urandom(16)
        cipher = Cipher(
            algorithms.AES(key),
            modes.GCM(iv),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(plaintext.encode()) + encryptor.finalize()
        return iv + encryptor.tag + ciphertext
    
    def aes_decrypt(self, ciphertext: bytes, key: bytes) -> str:
        """AES-Entschlüsselung"""
        iv = ciphertext[:16]
        tag = ciphertext[16:32]
        actual_ciphertext = ciphertext[32:]
        
        cipher = Cipher(
            algorithms.AES(key),
            modes.GCM(iv, tag),
            backend=default_backend()
        )
        decryptor = cipher.decryptor()
        plaintext = decryptor.update(actual_ciphertext) + decryptor.finalize()
        return plaintext.decode()
