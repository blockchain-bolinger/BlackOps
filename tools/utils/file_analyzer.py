#!/usr/bin/env python3
"""
File Analyzer – Dateianalyse-Tool
"""
import os
import hashlib
import magic

class FileAnalyzer:
    @staticmethod
    def get_hash(file_path: str, algo='sha256') -> str:
        h = hashlib.new(algo)
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                h.update(chunk)
        return h.hexdigest()

    @staticmethod
    def get_mime(file_path: str) -> str:
        return magic.from_file(file_path, mime=True)

    @staticmethod
    def get_size(file_path: str) -> int:
        return os.path.getsize(file_path)

    @staticmethod
    def is_executable(file_path: str) -> bool:
        return os.access(file_path, os.X_OK)

    def run(self):
        path = input("[?] File path: ").strip().strip("'")
        if not path:
            print("[INFO] No file provided.")
            return
        if not os.path.exists(path):
            print("[ERROR] File does not exist.")
            return

        try:
            print(f"[INFO] Size: {self.get_size(path)} bytes")
            print(f"[INFO] MIME: {self.get_mime(path)}")
            print(f"[INFO] Executable: {self.is_executable(path)}")
            print(f"[INFO] SHA256: {self.get_hash(path, 'sha256')}")
        except Exception as e:
            print(f"[ERROR] Analysis failed: {e}")
