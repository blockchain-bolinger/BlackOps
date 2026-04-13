#!/usr/bin/env python3
"""
Export-Funktionen
"""
import csv
import json

def export_csv(data: list, headers: list, filepath: str):
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(data)

def export_json(data: dict, filepath: str):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)