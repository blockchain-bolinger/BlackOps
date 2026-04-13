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

    @staticmethod
    def success(data: Any = None, **meta) -> "ToolResult":
        return ToolResult(status="success", data=data, errors=[], meta=meta)

    @staticmethod
    def failed(error: str, **meta) -> "ToolResult":
        return ToolResult(status="failed", data=None, errors=[error], meta=meta)

    def to_dict(self) -> Dict[str, Any]:
        payload = asdict(self)
        payload["meta"]["timestamp"] = datetime.now(timezone.utc).isoformat()
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

