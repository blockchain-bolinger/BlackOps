"""
File Utility Functions
"""

import os
import shutil
import hashlib
import json
import yaml
import csv
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
import magic

class FileUtils:
    @staticmethod
    def read_file(file_path: str) -> str:
        """Liest Datei ein"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    @staticmethod
    def write_file(file_path: str, content: str) -> None:
        """Schreibt Datei"""
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    @staticmethod
    def read_json(file_path: str) -> Dict[str, Any]:
        """Liest JSON Datei"""
        with open(file_path, 'r') as f:
            return json.load(f)
    
    @staticmethod
    def write_json(file_path: str, data: Dict[str, Any], indent: int = 2) -> None:
        """Schreibt JSON Datei"""
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=indent)
    
    @staticmethod
    def read_yaml(file_path: str) -> Dict[str, Any]:
        """Liest YAML Datei"""
        with open(file_path, 'r') as f:
            return yaml.safe_load(f)
    
    @staticmethod
    def write_yaml(file_path: str, data: Dict[str, Any]) -> None:
        """Schreibt YAML Datei"""
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False)
    
    @staticmethod
    def calculate_hash(file_path: str, algorithm: str = "sha256") -> str:
        """Berechnet Hash einer Datei"""
        hash_func = getattr(hashlib, algorithm)()
        
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_func.update(chunk)
        
        return hash_func.hexdigest()
    
    @staticmethod
    def get_file_info(file_path: str) -> Dict[str, Any]:
        """Holt Dateiinformationen"""
        path = Path(file_path)
        stat = path.stat()
        
        return {
            'path': str(path.absolute()),
            'size': stat.st_size,
            'created': stat.st_ctime,
            'modified': stat.st_mtime,
            'type': FileUtils._get_file_type(file_path),
            'hash_sha256': FileUtils.calculate_hash(file_path),
            'permissions': oct(stat.st_mode)[-3:]
        }
    
    @staticmethod
    def _get_file_type(file_path: str) -> str:
        """Ermittelt Dateityp"""
        try:
            mime = magic.Magic(mime=True)
            return mime.from_file(file_path)
        except:
            return "unknown"
    
    @staticmethod
    def search_files(directory: str, pattern: str = "*", recursive: bool = True) -> List[str]:
        """Sucht Dateien nach Pattern"""
        path = Path(directory)
        
        if recursive:
            files = list(path.rglob(pattern))
        else:
            files = list(path.glob(pattern))
        
        return [str(f) for f in files if f.is_file()]
    
    @staticmethod
    def backup_file(file_path: str, backup_dir: str = "backups") -> str:
        """Erstellt Backup einer Datei"""
        path = Path(file_path)
        backup_path = Path(backup_dir) / f"{path.name}.backup"
        
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(file_path, backup_path)
        
        return str(backup_path)
    
    @staticmethod
    def safe_delete(file_path: str, shred_passes: int = 3) -> bool:
        """Sicheres Löschen einer Datei"""
        try:
            path = Path(file_path)
            
            if not path.exists():
                return False
            
            # Mehrfaches Überschreiben (DoD 5220.22-M Standard)
            file_size = path.stat().st_size
            
            with open(file_path, 'wb') as f:
                for i in range(shred_passes):
                    f.seek(0)
                    # Zufällige Daten schreiben
                    f.write(os.urandom(file_size))
            
            # Datei löschen
            path.unlink()
            
            return True
            
        except Exception as e:
            print(f"[-] Secure delete failed: {e}")
            return False