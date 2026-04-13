#!/usr/bin/env python3
"""
Backup-Funktionen
"""
import os
import shutil
from datetime import datetime

def create_backup(source_dir: str, backup_root: str = "backups") -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = os.path.basename(source_dir) + f"_{timestamp}"
    backup_path = os.path.join(backup_root, backup_name)
    shutil.copytree(source_dir, backup_path)
    return backup_path

def rotate_backups(backup_root: str, keep: int = 5):
    backups = sorted(os.listdir(backup_root))
    while len(backups) > keep:
        oldest = os.path.join(backup_root, backups.pop(0))
        shutil.rmtree(oldest)