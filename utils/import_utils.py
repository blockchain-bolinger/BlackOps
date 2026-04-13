#!/usr/bin/env python3
"""
Import-Funktionen
"""
import csv
import json

def import_csv(filepath: str) -> list:
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        return list(reader)

def import_json(filepath: str) -> dict:
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)