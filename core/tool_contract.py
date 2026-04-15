"""
Einheitlicher Tool-Contract: Context + standardisiertes Ergebnis.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Optional


@dataclass
class ToolContext:
    tool_path: str
    correlation_id: str
    dry_run: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ToolResult:
    status: str
    data: Any = None
    errors: list[str] = field(default_factory=list)
    meta: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    @staticmethod
    def success(data: Any = None, **meta) -> "ToolResult":
        return ToolResult(status="success", data=data, errors=[], meta=meta)

    @staticmethod
    def failed(error: str, **meta) -> "ToolResult":
        return ToolResult(status="failed", data=None, errors=[error], meta=meta)

    @property
    def ok(self) -> bool:
        return self.status == "success"

    @property
    def error_type(self) -> Optional[str]:
        value = self.meta.get("error_type")
        return str(value) if value is not None else None

    def to_dict(self) -> Dict[str, Any]:
        payload = asdict(self)
        payload["meta"]["timestamp"] = self.timestamp
        return payload


def normalize_tool_result(result: Any, tool_path: str) -> ToolResult:
    if isinstance(result, ToolResult):
        return result
    if isinstance(result, dict):
        status = result.get("status")
        if status in {"success", "failed"} and "data" in result:
            return ToolResult(
                status=status,
                data=result.get("data"),
                errors=result.get("errors", []),
                meta=result.get("meta", {}),
            )
        return ToolResult.success(data=result, tool_path=tool_path)
    if result is None:
        return ToolResult.success(data=None, tool_path=tool_path)
    return ToolResult.success(data={"result": result}, tool_path=tool_path)
