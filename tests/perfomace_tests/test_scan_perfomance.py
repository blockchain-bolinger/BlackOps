import unittest
import time
from tools.utils.network_scanner import NetworkScanner

class TestScanPerformance(unittest.TestCase):
    def test_scan_speed(self):
        scanner = NetworkScanner()
        start = time.time()
        scanner.scan_ports('127.0.0.1', [80,443,22], threads=1)
        duration = time.time() - start
        self.assertLess(duration, 2)