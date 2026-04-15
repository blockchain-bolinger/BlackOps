"""
Execution telemetry for runs, policies, and outcomes.
"""

from __future__ import annotations

import json
import threading
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional


@dataclass
class TelemetryEvent:
    event_type: str
    timestamp: str
    run_id: str
    correlation_id: str
    payload: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ExecutionTelemetry:
    def __init__(self, telemetry_dir: str | Path = "logs/telemetry"):
        self.telemetry_dir = Path(telemetry_dir)
        self.telemetry_dir.mkdir(parents=True, exist_ok=True)
        self.events_path = self.telemetry_dir / "events.jsonl"
        self.runs_path = self.telemetry_dir / "runs.json"
        self.lock = threading.Lock()
        self.runs: Dict[str, Dict[str, Any]] = self._load_runs()

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    def _load_runs(self) -> Dict[str, Dict[str, Any]]:
        if not self.runs_path.exists():
            return {}
        try:
            with self.runs_path.open("r", encoding="utf-8") as handle:
                payload = json.load(handle)
                if isinstance(payload, dict):
                    return payload
        except Exception:
            return {}
        return {}

    def _save_runs(self) -> None:
        with self.runs_path.open("w", encoding="utf-8") as handle:
            json.dump(self.runs, handle, indent=2)

    def record_event(
        self,
        event_type: str,
        *,
        run_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        payload: Optional[Dict[str, Any]] = None,
    ) -> TelemetryEvent:
        event = TelemetryEvent(
            event_type=event_type,
            timestamp=self._now(),
            run_id=run_id or str(uuid.uuid4()),
            correlation_id=correlation_id or "-",
            payload=payload or {},
        )
        with self.lock:
            with self.events_path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(event.to_dict(), ensure_ascii=True) + "\n")
        return event

    def start_run(self, *, correlation_id: str, profile: str, tool_label: str, context: Optional[Dict[str, Any]] = None) -> str:
        run_id = str(uuid.uuid4())
        run = {
            "run_id": run_id,
            "status": "started",
            "created_at": self._now(),
            "updated_at": self._now(),
            "correlation_id": correlation_id,
            "profile": profile,
            "tool": tool_label,
            "context": context or {},
            "events": [],
        }
        with self.lock:
            self.runs[run_id] = run
            self._save_runs()
        self.record_event(
            "run_started",
            run_id=run_id,
            correlation_id=correlation_id,
            payload={"profile": profile, "tool": tool_label, "context": context or {}},
        )
        return run_id

    def update_run(self, run_id: str, *, status: str, correlation_id: str, payload: Optional[Dict[str, Any]] = None) -> None:
        with self.lock:
            run = self.runs.get(run_id)
            if not run:
                return
            run["status"] = status
            run["updated_at"] = self._now()
            if payload:
                run.setdefault("events", []).append(payload)
            self._save_runs()
        self.record_event(
            f"run_{status}",
            run_id=run_id,
            correlation_id=correlation_id,
            payload=payload or {},
        )

    def finish_run(self, run_id: str, *, correlation_id: str, payload: Dict[str, Any]) -> None:
        with self.lock:
            run = self.runs.get(run_id)
            if not run:
                return
            run["status"] = payload.get("status", "completed")
            run["updated_at"] = self._now()
            run["result"] = payload
            run.setdefault("events", []).append(payload)
            self._save_runs()
        self.record_event(
            "run_finished",
            run_id=run_id,
            correlation_id=correlation_id,
            payload=payload,
        )

    def snapshot(self) -> Dict[str, Dict[str, Any]]:
        with self.lock:
            return json.loads(json.dumps(self.runs))

