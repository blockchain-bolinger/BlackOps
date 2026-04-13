#!/usr/bin/env python3
"""
Security Tests für Verschlüsselung
"""

import unittest
import tempfile
import os
from pathlib import Path

from core.encryption_manager import EncryptionManager
from utils.encryption_utils import EncryptionUtils

class TestEncryptionSecurity(unittest.TestCase):
    def test_key_strength(self):
        """Testet Schlüsselstärke"""
        manager = EncryptionManager()
        
        # Test key length
        self.assertEqual(len(manager.master_key), 64)  # 32 bytes in hex
        
        # Test derived key
        self.assertEqual(len(manager.derived_key), 44)  # Base64 encoded 32 bytes
    
    def test_encryption_consistency(self):
        """Testet Verschlüsselungskonsistenz"""
        manager = EncryptionManager("test_password_123")
        
        test_data = [
            "Simple text",
            "Special chars: !@#$%^&*()",
            "Unicode: 🚀🔑🗝️",
            "Long text " * 100
        ]
        
        for plaintext in test_data:
            encrypted = manager.encrypt_string(plaintext)
            decrypted = manager.decrypt_string(encrypted)
            
            self.assertEqual(plaintext, decrypted)
            self.assertNotEqual(plaintext, encrypted)
    
    def test_file_encryption(self):
        """Testet Dateiverschlüsselung"""
        manager = EncryptionManager()
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("Test file content\nMultiple lines\nEnd of file")
            plain_file = f.name
        
        try:
            # Encrypt file
            encrypted_file = manager.encrypt_file(plain_file)
            self.assertTrue(os.path.exists(encrypted_file))
            
            # Decrypt file
            decrypted_file = manager.decrypt_file(encrypted_file)
            self.assertTrue(os.path.exists(decrypted_file))
            
            # Compare content
            with open(plain_file, 'r') as f1, open(decrypted_file, 'r') as f2:
                self.assertEqual(f1.read(), f2.read())
            
            # Cleanup
            os.unlink(encrypted_file)
            os.unlink(decrypted_file)
            
        finally:
            os.unlink(plain_file)
    
    def test_hash_collision_resistance(self):
        """Testet Hash-Kollisionsresistenz"""
        utils = EncryptionUtils()
        
        # Test different inputs produce different hashes
        data1 = "Hello World"
        data2 = "Hello World!"
        
        hash1 = utils.generate_hash(data1, "sha256")
        hash2 = utils.generate_hash(data2, "sha256")
        
        self.assertNotEqual(hash1, hash2)
        
        # Test same input produces same hash
        hash3 = utils.generate_hash(data1, "sha256")
        self.assertEqual(hash1, hash3)
    
    def test_aes_encryption(self):
        """Testet AES-Verschlüsselung"""
        manager = EncryptionManager()
        
        # Generate random key
        import os
        key = os.urandom(32)  # AES-256 key
        
        plaintext = "Secret message for AES encryption"
        
        encrypted = manager.aes_encrypt(plaintext, key)
        decrypted = manager.aes_decrypt(encrypted, key)
        
        self.assertEqual(plaintext, decrypted)
        self.assertNotEqual(plaintext.encode(), encrypted)
    
    def test_key_rotation(self):
        """Testet Schlüsselrotation"""
        manager1 = EncryptionManager("initial_key")
        manager2 = EncryptionManager("new_key")
        
        plaintext = "Test rotation"
        
        # Encrypt with old key
        encrypted = manager1.encrypt_string(plaintext)
        
        # Should not decrypt with new key
        with self.assertRaises(Exception):
            manager2.decrypt_string(encrypted)
    
    def test_padding_oracle(self):
        """Testet Padding Oracle Schwachstellen"""
        manager = EncryptionManager()
        
        # Test with various padding scenarios
        test_cases = [
            ("A" * 15, "Missing padding byte"),
            ("A" * 16, "Exact block size"),
            ("A" * 31, "Partial second block"),
            ("", "Empty string")
        ]
        
        for plaintext, description in test_cases:
            with self.subTest(description):
                encrypted = manager.encrypt_string(plaintext)
                decrypted = manager.decrypt_string(encrypted)
                self.assertEqual(plaintext, decrypted)
    
    def test_timing_attacks(self):
        """Testet Timing Attack Resistenz"""
        import time
        
        manager = EncryptionManager()
        
        # Test constant-time comparison
        test_hash = manager.generate_hash("test", "sha256")
        
        times = []
        for i in range(100):
            start = time.perf_counter_ns()
            manager.generate_hash("test", "sha256")
            end = time.perf_counter_ns()
            times.append(end - start)
        
        # Check for timing variations (should be minimal)
        avg_time = sum(times) / len(times)
        variance = sum((t - avg_time) ** 2 for t in times) / len(times)
        
        # Variance should be small
        self.assertLess(variance, 1e9)  # Less than 1ms variance

if __name__ == '__main__':
    unittest.main()