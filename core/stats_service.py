"""
Persist simple usage statistics for the CLI.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict


class StatsService:
    def __init__(self, stats_path: str | Path = "data/sessions/blackops_stats.json"):
        self.stats_path = Path(stats_path)

    def increment(self, key: str) -> Dict[str, Any]:
        stats: Dict[str, Any] = {}
        if self.stats_path.exists():
            try:
                with self.stats_path.open("r", encoding="utf-8") as handle:
                    loaded = json.load(handle)
                    if isinstance(loaded, dict):
                        stats = loaded
            except Exception:
                stats = {}

        stats[key] = stats.get(key, 0) + 1
        stats["last_run"] = datetime.now().isoformat()

        self.stats_path.parent.mkdir(parents=True, exist_ok=True)
        with self.stats_path.open("w", encoding="utf-8") as handle:
            json.dump(stats, handle, indent=2)
        return stats
