#!/usr/bin/env python3
"""
Shared output helpers for specialized OSINT tools.
"""

from __future__ import annotations

import csv
import json
import os
import uuid
from pathlib import Path
from typing import Any

from core.evidence_store import EvidenceStore
from core.tool_contract import ToolResult

_EVIDENCE_STORE = EvidenceStore()


def success_payload(tool_name: str, data: Any, **meta) -> dict:
    payload = ToolResult.success(data=data, tool=tool_name, **meta).to_dict()
    if os.getenv("BLACKOPS_EVIDENCE_AUTO_RECORD", "1").strip().lower() in {"1", "true", "yes", "on"} and isinstance(data, dict):
        try:
            target = str(
                data.get("target")
                or data.get("domain")
                or data.get("ip")
                or data.get("email")
                or data.get("username")
                or data.get("host")
                or ""
            )
            _EVIDENCE_STORE.record_snapshot(
                source_tool=tool_name,
                profile=str(meta.get("profile", "osint")),
                correlation_id=str(meta.get("correlation_id") or payload["meta"].get("correlation_id", "-")),
                run_id=str(meta.get("run_id") or payload["meta"].get("run_id") or uuid.uuid4()),
                title=f"{tool_name} snapshot",
                target=target,
                severity=str(meta.get("severity", "info")),
                category=str(meta.get("category", "snapshot")),
                cwe=str(meta.get("cwe", "")),
                cves=meta.get("cves"),
                evidence=[data.get("evidence")] if data.get("evidence") else [],
                notes=str(meta.get("notes", "")),
                metadata={"payload_keys": list(data.keys())[:50], "tool_meta": meta},
            )
        except Exception:
            pass
    return payload


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
