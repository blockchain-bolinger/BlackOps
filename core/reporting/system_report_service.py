"""
System report generation for the Black Ops shell.
"""

from __future__ import annotations

import getpass
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from core.redaction_utils import redact_data
from core.tool_contract import ToolResult


class SystemReportService:
    def __init__(self, output_dir: str | Path = "reports/scans"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _current_user() -> str:
        try:
            return os.getlogin()
        except Exception:
            try:
                return getpass.getuser()
            except Exception:
                return "N/A"

    def generate(
        self,
        *,
        session_id: str,
        tools: Dict[str, Dict[str, Any]],
        config: Dict[str, Any],
        tool_name: str = "Report Generator",
    ) -> ToolResult:
        try:
            report = {
                "timestamp": datetime.now().isoformat(),
                "session_id": session_id,
                "system": {
                    "platform": sys.platform,
                    "python_version": sys.version,
                    "user": self._current_user(),
                    "is_root": os.geteuid() == 0 if hasattr(os, "geteuid") else False,
                },
                "tools": {k: v["name"] for k, v in tools.items() if k not in ["13", "14", "99"]},
                "config": config,
            }
            report = redact_data(report)
            report_file = self.output_dir / f"blackops_report_{session_id}.json"
            with report_file.open("w", encoding="utf-8") as handle:
                json.dump(report, handle, indent=2, ensure_ascii=False)

            return ToolResult.success(
                data={
                    "report_file": str(report_file),
                    "session_id": session_id,
                    "tool_count": len([k for k in tools if k not in ["13", "14", "99"]]),
                },
                tool=tool_name,
            )
        except Exception as exc:
            return ToolResult.failed(str(exc), action="generate_report", tool=tool_name)
