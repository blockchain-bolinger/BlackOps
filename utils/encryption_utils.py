"""
Encryption Utilities für Black Ops Framework
"""

import base64
import hashlib
import hmac
import os
from typing import Union, Optional
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend

class EncryptionUtils:
    @staticmethod
    def generate_hash(data: Union[str, bytes], algorithm: str = "sha256") -> str:
        """Generiert kryptographischen Hash."""
        if isinstance(data, str):
            data = data.encode()

        if algorithm == "md5":
            return hashlib.md5(data).hexdigest()
        if algorithm == "sha1":
            return hashlib.sha1(data).hexdigest()
        if algorithm == "sha256":
            return hashlib.sha256(data).hexdigest()
        if algorithm == "sha512":
            return hashlib.sha512(data).hexdigest()
        raise ValueError(f"Unsupported algorithm: {algorithm}")

    @staticmethod
    def generate_key_from_password(password: str, salt: bytes = None, 
                                 iterations: int = 100000) -> bytes:
        """Generiert Schlüssel aus Passwort"""
        if salt is None:
            salt = os.urandom(16)
        
        key = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode(),
            salt,
            iterations,
            dklen=32
        )
        
        return key, salt
    
    @staticmethod
    def encrypt_aes_cbc(plaintext: Union[str, bytes], key: bytes, 
                       iv: bytes = None) -> bytes:
        """Verschlüsselt mit AES-CBC"""
        if isinstance(plaintext, str):
            plaintext = plaintext.encode()
        
        if iv is None:
            iv = os.urandom(16)
        
        # Add PKCS7 padding
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(plaintext) + padder.finalize()
        
        # Create cipher
        cipher = Cipher(
            algorithms.AES(key),
            modes.CBC(iv),
            backend=default_backend()
        )
        
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()
        
        return iv + ciphertext
    
    @staticmethod
    def decrypt_aes_cbc(ciphertext: bytes, key: bytes) -> str:
        """Entschlüsselt AES-CBC"""
        iv = ciphertext[:16]
        actual_ciphertext = ciphertext[16:]
        
        cipher = Cipher(
            algorithms.AES(key),
            modes.CBC(iv),
            backend=default_backend()
        )
        
        decryptor = cipher.decryptor()
        padded_plaintext = decryptor.update(actual_ciphertext) + decryptor.finalize()
        
        # Remove PKCS7 padding
        unpadder = padding.PKCS7(128).unpadder()
        plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()
        
        return plaintext.decode()
    
    @staticmethod
    def encrypt_rsa(plaintext: Union[str, bytes], public_key) -> bytes:
        """Verschlüsselt mit RSA"""
        if isinstance(plaintext, str):
            plaintext = plaintext.encode()
        
        from cryptography.hazmat.primitives.asymmetric import padding as rsa_padding
        from cryptography.hazmat.primitives import hashes
        
        ciphertext = public_key.encrypt(
            plaintext,
            rsa_padding.OAEP(
                mgf=rsa_padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        return ciphertext
    
    @staticmethod
    def generate_hmac(data: Union[str, bytes], key: bytes, 
                     algorithm: str = "sha256") -> str:
        """Generiert HMAC"""
        if isinstance(data, str):
            data = data.encode()
        
        if algorithm == "sha256":
            h = hmac.new(key, data, hashlib.sha256)
        elif algorithm == "sha512":
            h = hmac.new(key, data, hashlib.sha512)
        elif algorithm == "md5":
            h = hmac.new(key, data, hashlib.md5)
        else:
            raise ValueError(f"Unsupported algorithm: {algorithm}")
        
        return h.hexdigest()
    
    @staticmethod
    def verify_hmac(data: Union[str, bytes], key: bytes, 
                   received_hmac: str, algorithm: str = "sha256") -> bool:
        """Verifiziert HMAC"""
        expected_hmac = EncryptionUtils.generate_hmac(data, key, algorithm)
        return hmac.compare_digest(expected_hmac, received_hmac)
    
    @staticmethod
    def generate_random_bytes(length: int = 32) -> bytes:
        """Generiert kryptographisch sichere Zufallsbytes"""
        return os.urandom(length)
    
    @staticmethod
    def base64_encode(data: Union[str, bytes]) -> str:
        """Base64 Kodierung"""
        if isinstance(data, str):
            data = data.encode()
        return base64.b64encode(data).decode()
    
    @staticmethod
    def base64_decode(data: str) -> bytes:
        """Base64 Dekodierung"""
        return base64.b64decode(data)
    
    @staticmethod
    def hex_encode(data: bytes) -> str:
        """Hex Kodierung"""
        return data.hex()
    
    @staticmethod
    def hex_decode(data: str) -> bytes:
        """Hex Dekodierung"""
        return bytes.fromhex(data)
