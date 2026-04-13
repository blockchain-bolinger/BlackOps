#!/usr/bin/env python3
"""
System Info – Plattform- und Systeminformationen
"""
import platform
import os
import socket

class SystemInfo:
    @staticmethod
    def get_os() -> str:
        return platform.system()

    @staticmethod
    def get_hostname() -> str:
        return socket.gethostname()

    @staticmethod
    def get_ip() -> str:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
        except Exception:
            ip = '127.0.0.1'
        finally:
            s.close()
        return ip

    @staticmethod
    def get_user() -> str:
        return os.environ.get('USER', os.environ.get('USERNAME', 'unknown'))

    def run(self):
        print(f"[INFO] OS: {self.get_os()}")
        print(f"[INFO] Hostname: {self.get_hostname()}")
        print(f"[INFO] IP: {self.get_ip()}")
        print(f"[INFO] User: {self.get_user()}")
        input("\n[ENTER] Zurück...")
