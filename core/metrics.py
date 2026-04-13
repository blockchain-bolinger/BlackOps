"""
Einfache Laufzeitmetriken für Module/Tools.
"""

from __future__ import annotations

import json
from pathlib import Path
import threading
import time
from typing import Dict


class MetricsCollector:
    def __init__(self, metrics_path: str = "logs/metrics.json"):
        self.metrics_path = Path(metrics_path)
        self.metrics_path.parent.mkdir(parents=True, exist_ok=True)
        self.lock = threading.Lock()
        self.metrics = {
            "counters": {},
            "timers": {},
        }

    def increment(self, key: str, amount: int = 1) -> None:
        with self.lock:
            self.metrics["counters"][key] = self.metrics["counters"].get(key, 0) + amount

    def observe_duration(self, key: str, duration_seconds: float) -> None:
        with self.lock:
            timer = self.metrics["timers"].setdefault(key, {"count": 0, "total": 0.0, "avg": 0.0})
            timer["count"] += 1
            timer["total"] += duration_seconds
            timer["avg"] = timer["total"] / timer["count"]

    def timed(self, key: str):
        start = time.perf_counter()

        class _Timer:
            def __enter__(_self):
                return _self

            def __exit__(_self, exc_type, exc, tb):
                self.observe_duration(key, time.perf_counter() - start)

        return _Timer()

    def flush(self) -> None:
        with self.lock:
            with open(self.metrics_path, "w", encoding="utf-8") as handle:
                json.dump(self.metrics, handle, indent=2)

    def snapshot(self) -> Dict:
        with self.lock:
            return json.loads(json.dumps(self.metrics))

    def to_prometheus(self, namespace: str = "blackops") -> str:
        """Exportiert Metriken im Prometheus-Textformat."""
        snapshot = self.snapshot()
        lines = []

        for key, value in sorted(snapshot.get("counters", {}).items()):
            metric = f"{namespace}_{key}".replace(".", "_").replace("-", "_")
            lines.append(f"# TYPE {metric} counter")
            lines.append(f"{metric} {value}")

        for key, value in sorted(snapshot.get("timers", {}).items()):
            metric_base = f"{namespace}_{key}".replace(".", "_").replace("-", "_")
            lines.append(f"# TYPE {metric_base}_seconds summary")
            lines.append(f"{metric_base}_seconds_count {value.get('count', 0)}")
            lines.append(f"{metric_base}_seconds_sum {value.get('total', 0.0)}")
            lines.append(f"{metric_base}_seconds_avg {value.get('avg', 0.0)}")

        return "\n".join(lines) + ("\n" if lines else "")
