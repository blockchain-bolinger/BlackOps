#!/usr/bin/env python3
"""
Shared output helpers for specialized OSINT tools.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from core.tool_contract import ToolResult


def success_payload(tool_name: str, data: Any, **meta) -> dict:
    return ToolResult.success(data=data, tool=tool_name, **meta).to_dict()


def failed_payload(tool_name: str, error: str, **meta) -> dict:
    return ToolResult.failed(error, tool=tool_name, **meta).to_dict()


def save_json(path: str, payload: dict) -> None:
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)


def _flatten(value: Any, prefix: str = "") -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    if isinstance(value, dict):
        for key, item in value.items():
            next_prefix = f"{prefix}.{key}" if prefix else str(key)
            rows.extend(_flatten(item, next_prefix))
        return rows
    if isinstance(value, list):
        for index, item in enumerate(value):
            next_prefix = f"{prefix}[{index}]"
            rows.extend(_flatten(item, next_prefix))
        return rows
    rows.append((prefix or "value", "" if value is None else str(value)))
    return rows


def save_csv(path: str, payload: dict, data_only: bool = True) -> None:
    target = payload.get("data") if data_only and isinstance(payload.get("data"), dict) else payload
    rows = _flatten(target)
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with open(output, "w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["key", "value"])
        writer.writerows(rows)
