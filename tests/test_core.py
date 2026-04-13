#!/usr/bin/env python3
"""
Unit Tests für Core Module
"""

import unittest
import tempfile
import os
from pathlib import Path

from core.config_manager import ConfigManager
from core.encryption_manager import EncryptionManager
from core.ethics_enforcer import EthicsEnforcer

class TestConfigManager(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = Path(self.temp_dir) / "test_config.json"
        
    def test_default_config(self):
        """Testet Default-Konfiguration"""
        config = ConfigManager(str(self.config_path))
        self.assertIn("version", config.config)
        self.assertIn("ethics", config.config)
    
    def test_get_set(self):
        """Testet Get/Set Methoden"""
        config = ConfigManager(str(self.config_path))
        config.set("test.key", "value")
        
        self.assertEqual(config.get("test.key"), "value")
        self.assertEqual(config.get("nonexistent", "default"), "default")
    
    def test_validation(self):
        """Testet Konfigurations-Validierung"""
        config = ConfigManager(str(self.config_path))
        self.assertTrue(config.validate())

class TestEncryptionManager(unittest.TestCase):
    def test_string_encryption(self):
        """Testet String-Verschlüsselung"""
        manager = EncryptionManager("test_key")
        
        plaintext = "Secret Message"
        encrypted = manager.encrypt_string(plaintext)
        decrypted = manager.decrypt_string(encrypted)
        
        self.assertEqual(plaintext, decrypted)
        self.assertNotEqual(plaintext, encrypted)
    
    def test_hash_generation(self):
        """Testet Hash-Generierung"""
        manager = EncryptionManager()
        
        data = "test data"
        sha256_hash = manager.generate_hash(data, "sha256")
        md5_hash = manager.generate_hash(data, "md5")
        
        self.assertEqual(len(sha256_hash), 64)
        self.assertEqual(len(md5_hash), 32)

class TestEthicsEnforcer(unittest.TestCase):
    def setUp(self):
        self.ethics = EthicsEnforcer()
    
    def test_target_check(self):
        """Testet Target-Überprüfung"""
        # Erlaubte Targets
        self.assertTrue(self.ethics.check_target("example.com"))
        self.assertTrue(self.ethics.check_target("test.org"))
        
        # Verbotene Patterns sollten False zurückgeben
        # (hängt von der Konfiguration ab)
    
    def test_action_check(self):
        """Testet Aktion-Überprüfung"""
        self.assertTrue(self.ethics.check_action("penetration_testing"))
        self.assertFalse(self.ethics.check_action("data_destruction"))

if __name__ == '__main__':
    unittest.main()