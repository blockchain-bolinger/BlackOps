"""
Centralized tool execution service for CLI and Web paths.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, Optional

from core.process_runner import ProcessRunnerError, SafeProcessRunner
from core.tool_contract import ToolResult


class ExecutionService:
    def __init__(
        self,
        process_runner: Optional[SafeProcessRunner] = None,
        base_dir: Optional[str | Path] = None,
        tools_dir: Optional[str | Path] = None,
    ):
        self.base_dir = Path(base_dir or Path.cwd()).resolve()
        self.tools_dir = Path(tools_dir or (self.base_dir / "tools")).resolve()
        self.process_runner = process_runner or SafeProcessRunner(
            allowed_roots=[self.base_dir, self.tools_dir]
        )

    @staticmethod
    def _normalize_timeout(timeout: Optional[float], default: float = 30.0) -> Optional[float]:
        if timeout is None:
            return None
        if isinstance(timeout, (int, float)) and timeout > 0:
            return float(timeout)
        return float(default)

    @staticmethod
    def _sanitize_args(args: Optional[Iterable], max_args: int = 64) -> list[str]:
        if args is None:
            return []
        if not isinstance(args, list):
            raise ProcessRunnerError("args must be an array")
        if len(args) > max_args:
            raise ProcessRunnerError("too many args")

        safe_args: list[str] = []
        for item in args:
            if isinstance(item, (str, int, float, bool)):
                safe_args.append(str(item))
            else:
                raise ProcessRunnerError("args must contain only scalar values")
        return safe_args

    def resolve_tool_path(self, tool_path: str) -> Path:
        if not isinstance(tool_path, str) or not tool_path.strip():
            raise ProcessRunnerError("tool path is required")

        candidate = Path(tool_path.strip())
        script_path = (
            candidate.resolve()
            if candidate.is_absolute()
            else (self.base_dir / candidate).resolve()
        )
        if not script_path.exists() or not script_path.is_file():
            raise ProcessRunnerError("tool script not found")
        if script_path.suffix != ".py":
            raise ProcessRunnerError("only python scripts are allowed")
        if self.tools_dir not in script_path.parents:
            raise ProcessRunnerError("tool script must be under tools/")
        return script_path

    @staticmethod
    def _result_from_process(
        proc_result,
        *,
        capture_output: bool,
        tool_label: str,
    ) -> ToolResult:
        payload = {
            "returncode": proc_result.returncode,
            "timed_out": proc_result.timed_out,
            "command": proc_result.command,
        }
        if capture_output:
            payload["stdout"] = proc_result.stdout
            payload["stderr"] = proc_result.stderr

        if proc_result.timed_out:
            result = ToolResult.failed(
                "tool execution timed out",
                tool=tool_label,
                returncode=proc_result.returncode,
                error_type="timeout",
            )
            result.data = payload
            return result

        if proc_result.returncode != 0:
            result = ToolResult.failed(
                f"tool exited with code {proc_result.returncode}",
                tool=tool_label,
                returncode=proc_result.returncode,
            )
            result.data = payload
            return result

        return ToolResult.success(
            data=payload,
            tool=tool_label,
            returncode=proc_result.returncode,
        )

    def execute_command(
        self,
        command: list[str],
        *,
        timeout: Optional[float] = None,
        env: Optional[dict[str, str]] = None,
        cwd: Optional[str | Path] = None,
        capture_output: bool = False,
        tool_label: str = "command",
    ) -> ToolResult:
        try:
            normalized_timeout = self._normalize_timeout(timeout, default=30.0)
            if capture_output:
                proc_result = self.process_runner.run_capture(
                    command,
                    timeout=normalized_timeout,
                    env=env,
                    cwd=cwd,
                )
            else:
                proc_result = self.process_runner.run_streaming(
                    command,
                    timeout=normalized_timeout,
                    env=env,
                    cwd=cwd,
                )
            return self._result_from_process(
                proc_result,
                capture_output=capture_output,
                tool_label=tool_label,
            )
        except ProcessRunnerError as exc:
            return ToolResult.failed(str(exc), tool=tool_label, error_type="validation")
        except Exception as exc:
            return ToolResult.failed(str(exc), tool=tool_label, error_type="internal")

    def execute_tool(
        self,
        tool_path: str,
        *,
        args: Optional[list] = None,
        timeout: Optional[float] = 30.0,
        env: Optional[dict[str, str]] = None,
        cwd: Optional[str | Path] = None,
        capture_output: bool = False,
        sudo: bool = False,
    ) -> ToolResult:
        try:
            safe_args = self._sanitize_args(args)
            script_path = self.resolve_tool_path(tool_path)
        except ProcessRunnerError as exc:
            return ToolResult.failed(str(exc), tool=tool_path, error_type="validation")

        command = ["python3", str(script_path)] + safe_args
        if sudo:
            command = ["sudo"] + command

        run_cwd = cwd or self.base_dir
        return self.execute_command(
            command,
            timeout=timeout,
            env=env,
            cwd=run_cwd,
            capture_output=capture_output,
            tool_label=str(script_path),
        )

    @staticmethod
    def http_status_for_result(result: ToolResult) -> int:
        error_type = (result.meta or {}).get("error_type")
        data = result.data if isinstance(result.data, dict) else {}

        if result.status == "success":
            return 200
        if error_type == "validation":
            return 400
        if error_type == "internal":
            return 500
        if error_type == "timeout" or bool(data.get("timed_out")):
            return 504
        return 200
