#!/usr/bin/env python3
"""
Unit Tests für Utility Module
"""

import unittest
import tempfile
import os
from pathlib import Path

from utils.file_utils import FileUtils
from utils.network_utils import NetworkUtils

class TestFileUtils(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        
    def test_file_operations(self):
        """Testet Dateioperationen"""
        test_file = Path(self.temp_dir) / "test.txt"
        content = "Hello, World!\nTest Line 2"
        
        # Write test
        FileUtils.write_file(str(test_file), content)
        self.assertTrue(test_file.exists())
        
        # Read test
        read_content = FileUtils.read_file(str(test_file))
        self.assertEqual(content, read_content)
        
        # Hash test
        file_hash = FileUtils.calculate_hash(str(test_file))
        self.assertEqual(len(file_hash), 64)  # SHA256 length
    
    def test_json_operations(self):
        """Testet JSON Operationen"""
        test_file = Path(self.temp_dir) / "test.json"
        data = {"key": "value", "number": 123, "list": [1, 2, 3]}
        
        # Write JSON
        FileUtils.write_json(str(test_file), data)
        self.assertTrue(test_file.exists())
        
        # Read JSON
        read_data = FileUtils.read_json(str(test_file))
        self.assertEqual(data, read_data)
    
    def test_search_files(self):
        """Testet Dateisuche"""
        # Create test files
        for i in range(3):
            test_file = Path(self.temp_dir) / f"file_{i}.txt"
            test_file.write_text(f"Content {i}")
        
        # Search
        files = FileUtils.search_files(self.temp_dir, "*.txt")
        self.assertEqual(len(files), 3)

class TestNetworkUtils(unittest.TestCase):
    def test_ip_validation(self):
        """Testet IP-Validierung"""
        self.assertTrue(NetworkUtils.validate_ip("192.168.1.1"))
        self.assertTrue(NetworkUtils.validate_ip("2001:0db8:85a3:0000:0000:8a2e:0370:7334"))
        self.assertFalse(NetworkUtils.validate_ip("not.an.ip"))
    
    def test_domain_resolution(self):
        """Testet Domain-Auflösung"""
        # Teste bekannte Domain
        ips = NetworkUtils.resolve_domain("google.com")
        self.assertTrue(len(ips) > 0)
        
        # Teste nicht existierende Domain
        ips = NetworkUtils.resolve_domain("nonexistentdomain12345.test")
        self.assertEqual(len(ips), 0)

if __name__ == '__main__':
    unittest.main()