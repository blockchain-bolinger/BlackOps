"""
Hardened subprocess execution helpers.
"""

from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Optional


class ProcessRunnerError(ValueError):
    """Raised when a command violates process execution policy."""


@dataclass
class ProcessResult:
    returncode: int
    stdout: str = ""
    stderr: str = ""
    timed_out: bool = False
    command: list[str] = field(default_factory=list)


class SafeProcessRunner:
    def __init__(
        self,
        allowed_roots: Optional[Iterable[str | Path]] = None,
        allowed_executables: Optional[Iterable[str]] = None,
    ):
        base = Path.cwd().resolve()
        roots = allowed_roots or [base, base / "tools"]
        self.allowed_roots = [Path(root).resolve() for root in roots]
        self.allowed_executables = {exe.strip() for exe in (allowed_executables or ["python3", "python", "sudo"])}

    def _resolve_command(self, command: list[str]) -> list[str]:
        if not isinstance(command, (list, tuple)) or not command:
            raise ProcessRunnerError("Command must be a non-empty list.")

        resolved = []
        for item in command:
            if not isinstance(item, str):
                raise ProcessRunnerError("All command items must be strings.")
            candidate = item.strip()
            if not candidate:
                raise ProcessRunnerError("Command contains an empty argument.")
            if "\x00" in candidate:
                raise ProcessRunnerError("Command contains invalid null byte.")
            resolved.append(candidate)
        return resolved

    def _is_allowed_path(self, path: Path) -> bool:
        return any(path == root or root in path.parents for root in self.allowed_roots)

    def _validate_python_script(self, command: list[str], python_index: int) -> None:
        if len(command) <= python_index + 1:
            raise ProcessRunnerError("Python command missing script path.")

        script = command[python_index + 1]
        if script.startswith("-"):
            raise ProcessRunnerError("Inline python flags (e.g. -c/-m) are not allowed.")

        script_path = Path(script)
        if not script_path.is_absolute():
            script_path = (Path.cwd() / script_path).resolve()
        else:
            script_path = script_path.resolve()

        if not script_path.exists():
            raise ProcessRunnerError(f"Script not found: {script}")
        if not self._is_allowed_path(script_path):
            raise ProcessRunnerError(f"Script path is outside allowed roots: {script_path}")

    def _validate_command(self, command: list[str]) -> None:
        first = os.path.basename(command[0])
        if first not in self.allowed_executables:
            raise ProcessRunnerError(f"Executable not allowed: {first}")

        python_index = 0
        if first == "sudo":
            if len(command) < 2:
                raise ProcessRunnerError("sudo command missing executable.")
            second = os.path.basename(command[1])
            if second not in {"python", "python3"}:
                raise ProcessRunnerError("Only python/python3 is allowed after sudo.")
            python_index = 1
        elif first not in {"python", "python3"}:
            raise ProcessRunnerError("Only python/python3 execution is allowed.")

        self._validate_python_script(command, python_index)

    def run_capture(
        self,
        command: list[str],
        timeout: Optional[float] = 30.0,
        env: Optional[dict[str, str]] = None,
        cwd: Optional[str | Path] = None,
    ) -> ProcessResult:
        resolved = self._resolve_command(command)
        self._validate_command(resolved)
        run_cwd = str(Path(cwd).resolve()) if cwd else None
        try:
            proc = subprocess.run(
                resolved,
                capture_output=True,
                text=True,
                timeout=timeout,
                env=env,
                cwd=run_cwd,
                check=False,
            )
            return ProcessResult(
                returncode=proc.returncode,
                stdout=proc.stdout or "",
                stderr=proc.stderr or "",
                timed_out=False,
                command=resolved,
            )
        except subprocess.TimeoutExpired as exc:
            return ProcessResult(
                returncode=124,
                stdout=exc.stdout or "",
                stderr=exc.stderr or "",
                timed_out=True,
                command=resolved,
            )

    def run_streaming(
        self,
        command: list[str],
        timeout: Optional[float] = None,
        env: Optional[dict[str, str]] = None,
        cwd: Optional[str | Path] = None,
    ) -> ProcessResult:
        resolved = self._resolve_command(command)
        self._validate_command(resolved)
        run_cwd = str(Path(cwd).resolve()) if cwd else None
        proc = subprocess.Popen(resolved, env=env, cwd=run_cwd)
        try:
            returncode = proc.wait(timeout=timeout)
            return ProcessResult(returncode=returncode, timed_out=False, command=resolved)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()
            return ProcessResult(returncode=124, timed_out=True, command=resolved)
