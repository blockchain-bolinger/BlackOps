"""
Evidence store for findings, observables, and cross-run correlation.
"""

from __future__ import annotations

import hashlib
import json
import threading
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, Optional


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _stable_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (dict, list, tuple, set)):
        return json.dumps(value, sort_keys=True, ensure_ascii=True, default=str)
    return str(value)


def _fingerprint(*parts: Any) -> str:
    payload = "|".join(_stable_text(part).strip().lower() for part in parts if _stable_text(part).strip())
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


@dataclass
class EvidenceRecord:
    evidence_id: str
    created_at: str
    updated_at: str
    source_tool: str
    profile: str
    correlation_id: str
    run_id: str
    target: str = ""
    title: str = ""
    severity: str = "info"
    category: str = "unknown"
    cwe: str = ""
    cves: list[str] = field(default_factory=list)
    evidence: list[Any] = field(default_factory=list)
    observables: list[str] = field(default_factory=list)
    notes: str = ""
    fingerprint: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class EvidenceStore:
    def __init__(self, store_dir: str | Path = "logs/evidence"):
        self.store_dir = Path(store_dir)
        self.store_dir.mkdir(parents=True, exist_ok=True)
        self.records_path = self.store_dir / "records.json"
        self.records_jsonl = self.store_dir / "records.jsonl"
        self.lock = threading.Lock()
        self.records: Dict[str, EvidenceRecord] = self._load_records()

    def _load_records(self) -> Dict[str, EvidenceRecord]:
        if not self.records_path.exists():
            return {}
        try:
            with self.records_path.open("r", encoding="utf-8") as handle:
                payload = json.load(handle)
        except Exception:
            return {}
        if not isinstance(payload, dict):
            return {}
        records: Dict[str, EvidenceRecord] = {}
        for key, value in payload.items():
            if isinstance(value, dict):
                try:
                    records[str(key)] = EvidenceRecord(**value)
                except Exception:
                    continue
        return records

    def _save(self) -> None:
        with self.records_path.open("w", encoding="utf-8") as handle:
            json.dump({k: v.to_dict() for k, v in self.records.items()}, handle, indent=2)

    @staticmethod
    def _extract_observables(*items: Any) -> list[str]:
        observables: set[str] = set()
        for item in items:
            if item is None:
                continue
            if isinstance(item, dict):
                for value in item.values():
                    observables.update(EvidenceStore._extract_observables(value))
                continue
            if isinstance(item, (list, tuple, set)):
                for value in item:
                    observables.update(EvidenceStore._extract_observables(value))
                continue
            text = str(item).strip()
            if text:
                observables.add(text)
        return sorted(observables)

    @staticmethod
    def _normalize_cves(cves: Any) -> list[str]:
        if isinstance(cves, str):
            cves = [cves]
        if not isinstance(cves, (list, tuple, set)):
            return []
        return [str(cve).strip() for cve in cves if str(cve).strip()]

    def ingest_finding(
        self,
        *,
        source_tool: str,
        profile: str,
        correlation_id: str,
        run_id: str,
        finding: Dict[str, Any],
        target: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> EvidenceRecord:
        created_at = _now()
        evidence_id = str(finding.get("id") or uuid.uuid4())
        title = str(finding.get("title") or finding.get("vulnerability") or finding.get("name") or "Unknown finding")
        severity = str(finding.get("severity", "info")).lower()
        category = str(finding.get("category") or finding.get("type") or "unknown")
        cwe = str(finding.get("cwe") or "")
        cves = self._normalize_cves(finding.get("cves") or finding.get("cve"))
        evidence = finding.get("evidence") or []
        record = EvidenceRecord(
            evidence_id=evidence_id,
            created_at=created_at,
            updated_at=created_at,
            source_tool=source_tool,
            profile=profile,
            correlation_id=correlation_id,
            run_id=run_id,
            target=str(target or finding.get("target") or finding.get("domain") or finding.get("host") or ""),
            title=title,
            severity=severity,
            category=category,
            cwe=cwe,
            cves=cves,
            evidence=evidence if isinstance(evidence, list) else [evidence],
            observables=self._extract_observables(
                finding.get("target"),
                finding.get("domain"),
                finding.get("host"),
                finding.get("ip"),
                finding.get("url"),
                finding.get("email"),
                finding.get("username"),
                finding.get("file"),
                finding.get("path"),
                evidence,
            ),
            notes=str(finding.get("description") or finding.get("notes") or ""),
            fingerprint=_fingerprint(source_tool, profile, evidence_id, title, target, cwe, cves),
            metadata=metadata or {},
        )
        with self.lock:
            self.records[record.evidence_id] = record
            self._save()
            with self.records_jsonl.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(record.to_dict(), ensure_ascii=True) + "\n")
        return record

    def record_snapshot(
        self,
        *,
        source_tool: str,
        profile: str,
        correlation_id: str,
        run_id: str,
        title: str,
        target: str = "",
        severity: str = "info",
        category: str = "snapshot",
        cwe: str = "",
        cves: Optional[Iterable[str]] = None,
        evidence: Optional[Iterable[Any]] = None,
        notes: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> EvidenceRecord:
        finding = {
            "id": str(uuid.uuid4()),
            "title": title,
            "severity": severity,
            "category": category,
            "cwe": cwe,
            "cves": list(cves or []),
            "evidence": list(evidence or []),
            "description": notes,
            "target": target,
        }
        return self.ingest_finding(
            source_tool=source_tool,
            profile=profile,
            correlation_id=correlation_id,
            run_id=run_id,
            finding=finding,
            target=target,
            metadata=metadata or {},
        )

    def ingest_result(
        self,
        *,
        source_tool: str,
        profile: str,
        correlation_id: str,
        run_id: str,
        result: Dict[str, Any],
        target: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> list[EvidenceRecord]:
        findings = result.get("data", {}).get("findings") if isinstance(result.get("data"), dict) else None
        if not isinstance(findings, list):
            return []
        records = []
        for finding in findings:
            if isinstance(finding, dict):
                records.append(
                    self.ingest_finding(
                        source_tool=source_tool,
                        profile=profile,
                        correlation_id=correlation_id,
                        run_id=run_id,
                        finding=finding,
                        target=target,
                        metadata=metadata or {},
                    )
                )
        return records

    def search(self, query: Optional[str] = None, severity: Optional[str] = None, category: Optional[str] = None) -> list[Dict[str, Any]]:
        query_value = str(query or "").strip().lower()
        severity_value = str(severity or "").strip().lower()
        category_value = str(category or "").strip().lower()
        results = []
        with self.lock:
            for record in self.records.values():
                if severity_value and record.severity != severity_value:
                    continue
                if category_value and record.category != category_value:
                    continue
                if query_value:
                    haystack = " ".join(
                        [
                            record.title,
                            record.target,
                            record.category,
                            record.cwe,
                            " ".join(record.cves),
                            " ".join(record.observables),
                        ]
                    ).lower()
                    if query_value not in haystack:
                        continue
                results.append(record.to_dict())
        results.sort(key=lambda item: item.get("created_at", ""), reverse=True)
        return results

    def recent(self, limit: int = 20) -> list[Dict[str, Any]]:
        with self.lock:
            records = sorted(self.records.values(), key=lambda item: item.created_at, reverse=True)
        return [record.to_dict() for record in records[:limit]]

    def stats(self) -> Dict[str, Any]:
        summary = {"total": 0, "critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0, "by_tool": {}, "by_profile": {}}
        with self.lock:
            records = list(self.records.values())
        summary["total"] = len(records)
        for record in records:
            summary[record.severity] = summary.get(record.severity, 0) + 1
            summary["by_tool"][record.source_tool] = summary["by_tool"].get(record.source_tool, 0) + 1
            summary["by_profile"][record.profile] = summary["by_profile"].get(record.profile, 0) + 1
        summary["by_tool"] = dict(sorted(summary["by_tool"].items(), key=lambda item: item[1], reverse=True))
        summary["by_profile"] = dict(sorted(summary["by_profile"].items(), key=lambda item: item[1], reverse=True))
        return summary

    def related(self, fingerprint: str) -> list[Dict[str, Any]]:
        with self.lock:
            matches = [record.to_dict() for record in self.records.values() if record.fingerprint == fingerprint]
        return matches
