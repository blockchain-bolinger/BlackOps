"""
Fallback implementations used when core manager imports are unavailable.
"""

from __future__ import annotations

import json
import subprocess
import time
import uuid
from pathlib import Path
from typing import Any, Optional


class ConfigManager:
    def __init__(self, config_file: str = "blackops_config.json"):
        self.config = {
            "ethics": {"show_warning": True, "require_confirmation": False},
            "system": {"auto_check": True},
        }

    def load_config(self):
        return self.config


class BlackOpsLogger:
    def __init__(self, name: str = "BlackOps", log_dir: str = "logs"):
        self.name = name
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self._correlation_id = "-"

    def set_correlation_id(self, correlation_id: Optional[str] = None) -> str:
        self._correlation_id = correlation_id or str(uuid.uuid4())
        return self._correlation_id

    def info(self, message: str) -> None:
        print(message)

    def warning(self, message: str) -> None:
        print(message)

    def error(self, message: str) -> None:
        print(message)

    def critical(self, message: str) -> None:
        print(message)

    def debug(self, message: str) -> None:
        print(message)

    def audit(self, user: str, action: str, target: str, status: str = "SUCCESS") -> None:
        print(f"{user} {action} {target} {status}")

    def print_banner(self) -> None:
        print("BlackOps Framework v3.0")


class DependencyChecker:
    def check_all_dependencies(self):
        return {"missing": [], "outdated": [], "satisfied": [], "errors": []}

    def check_all(self):
        return self.check_all_dependencies()

    def install_missing(self):
        print(
            "Dependency checker unavailable (Dependency checker nicht verfügbar). "
            "Please install missing packages manually (Bitte installiere fehlende Pakete manuell)."
        )


class PluginManager:
    def __init__(self, *args, **kwargs):
        pass

    def discover(self, *args, **kwargs):
        return {}

    def list_plugins(self):
        return []


class PolicyEngine:
    def __init__(self, *args, **kwargs):
        pass

    def evaluate(self, *args, **kwargs):
        class _Decision:
            allowed = True
            reason = "fallback"
            approval_required = False
            effective_timeout_seconds = None
            profile = "lab"

            def to_dict(self):
                return {"allowed": True, "reason": "fallback", "profile": "lab", "approval_required": False}

        return _Decision()

    def available_profiles(self):
        return {"lab": {}, "demo": {}, "training": {}, "audit": {}, "osint": {}, "pentest": {}}


class ProcessRunnerError(ValueError):
    pass


class ToolResult:
    def __init__(self, status, data=None, errors=None, meta=None):
        self.status = status
        self.data = data
        self.errors = errors or []
        self.meta = meta or {}

    @staticmethod
    def success(data=None, **meta):
        return ToolResult(status="success", data=data, errors=[], meta=meta)

    @staticmethod
    def failed(error, **meta):
        return ToolResult(status="failed", data=None, errors=[str(error)], meta=meta)


class _FallbackProcessResult:
    def __init__(self, returncode, timed_out=False):
        self.returncode = returncode
        self.timed_out = timed_out


class SafeProcessRunner:
    def run_streaming(self, command, timeout=None, env=None, cwd=None):
        proc = subprocess.Popen(command, env=env, cwd=cwd)
        try:
            return _FallbackProcessResult(proc.wait(timeout=timeout), timed_out=False)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()
            return _FallbackProcessResult(124, timed_out=True)


class ExecutionService:
    def __init__(self, process_runner=None, base_dir=None, tools_dir=None, policy_engine=None, telemetry=None, profile_name=None):
        self.process_runner = process_runner or SafeProcessRunner()
        self.policy_engine = policy_engine
        self.telemetry = telemetry
        self.profile_name = profile_name

    def execute_command(self, command, timeout=None, env=None, cwd=None, capture_output=False, tool_label="command", **kwargs):
        try:
            result = self.process_runner.run_streaming(command, timeout=timeout, env=env, cwd=cwd)
            data = {"returncode": result.returncode, "timed_out": result.timed_out, "command": command}
            if result.timed_out:
                failed = ToolResult.failed("tool execution timed out", tool=tool_label, error_type="timeout")
                failed.data = data
                return failed
            if result.returncode != 0:
                failed = ToolResult.failed(f"tool exited with code {result.returncode}", tool=tool_label)
                failed.data = data
                return failed
            return ToolResult.success(data=data, tool=tool_label, returncode=result.returncode)
        except Exception as exc:
            return ToolResult.failed(str(exc), tool=tool_label, error_type="internal")


class ExecutionTelemetry:
    def __init__(self, *args, **kwargs):
        pass

    def start_run(self, *args, **kwargs):
        return "fallback-run"

    def finish_run(self, *args, **kwargs):
        return None

    def record_event(self, *args, **kwargs):
        return None


class StatsService:
    def __init__(self, stats_file: str = "data/sessions/blackops_stats.json"):
        self.stats_file = Path(stats_file)
        if not self.stats_file.exists():
            self.stats_file.write_text("{}", encoding="utf-8")

    def increment(self, tool_name: str):
        try:
            data = json.loads(self.stats_file.read_text(encoding="utf-8") or "{}")
        except Exception:
            data = {}
        data[tool_name] = int(data.get(tool_name, 0)) + 1
        self.stats_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
        return data


class RuntimeGuardService:
    def __init__(self, *args, **kwargs):
        self.dependency_checker = kwargs.get("dependency_checker")
        self._bilingual = kwargs.get("bilingual", lambda e, g: e)
        self.logger = kwargs.get("logger")
        self._input = kwargs.get("input_func", input)
        self._print = kwargs.get("print_func", print)
        self._sleep = kwargs.get("sleep_func", time.sleep)

    def ethical_warning(self, *, show_warning=True, require_confirmation=True):
        if not show_warning:
            return True
        self._print(f"[!] {self._bilingual('Ethics warning accepted', 'Ethik-Warnung akzeptiert')}")
        return True

    def system_check(self):
        self._print(f"[!] {self._bilingual('System check unavailable in fallback mode', 'System-Check im Fallback-Modus nicht verfuegbar')}")
        self._sleep(0)
        return True


class MenuService:
    def __init__(self, *args, **kwargs):
        self._bilingual = kwargs.get("bilingual", lambda e, g: e)
        self._print = kwargs.get("print_func", print)

    def render(self, *, tools, categories):
        self._print("\nMAIN MENU")


class LauncherPresentationService:
    def __init__(self, *args, **kwargs):
        self._print = kwargs.get("print_func", print)

    def print_banner(self, *, version, session_id, author):
        self._print("BLACKOPS")

    def print_tool_info(self, *, tool):
        self._print(tool["name"])

    def invalid_tool_id(self):
        self._print("INVALID TOOL")

    def start_plugin(self, *, name):
        self._print(name)

    def plugin_not_loaded(self, *, plugin_name):
        self._print(plugin_name)

    def policy_error(self, message: str):
        self._print(message)

    def plugin_result_header(self, status):
        self._print(status)

    def report_generation_start(self):
        self._print("REPORT")

    def report_generation_error(self, error):
        self._print(error)

    def tool_not_found(self, filename):
        self._print(filename)

    def file_found_at(self, filename):
        self._print(filename)

    def aborted(self):
        self._print("ABORTED")

    def start_tool(self, *, name):
        self._print(name)

    def root_required(self):
        self._print("ROOT")

    def start_with_sudo(self, filename):
        self._print(filename)

    def tool_timed_out(self):
        self._print("TIMEOUT")

    def tool_exit_code(self, code):
        self._print(code)

    def tool_interrupted(self):
        self._print("INTERRUPTED")

    def blocked_unsafe_command(self, error):
        self._print(error)

    def could_not_start_tool(self, error):
        self._print(error)

    def print_report_summary(self, *, session_id, report_file, tool_count):
        self._print(report_file)

    def print_exit(self, *, author):
        self._print(author)

    def prompt(self, message):
        return self._input(message)

    def prompt_plugin_args(self, params_schema):
        user_args = {}
        for param, config in params_schema.items():
            val = self._input(f"[?] {config['description']} ({param}): ").strip()
            if val:
                user_args[param] = val
        return user_args

    def invalid_selection(self):
        self._print("INVALID")


class ShellPresentationService:
    def __init__(self, *args, **kwargs):
        self._bilingual = kwargs.get("bilingual", lambda e, g: e)
        self._print = kwargs.get("print_func", print)

    def show_tools(self, tools_cache):
        self._print("TOOLS")

    def show_plugins(self, plugin_manager):
        self._print("PLUGINS")

    def syntax_show(self):
        self._print("SYNTAX")

    def tool_not_found(self, arg):
        self._print(arg)

    def tool_loaded(self, arg):
        self._print(arg)

    def load_error(self, error):
        self._print(error)

    def no_tool_selected(self):
        self._print("NO TOOL")

    def set_option(self, key, value):
        self._print(key)

    def run_dry_tool(self, tool_name):
        self._print(tool_name)

    def execution_error(self, error):
        self._print(error)

    def syntax_plugin(self):
        self._print("PLUGIN SYNTAX")

    def run_dry_plugin(self, name, kwargs):
        self._print(name)

    def plugin_result(self, result):
        self._print(result)

    def plugin_error(self, error):
        self._print(error)

    def show_profile(self, profile_name):
        self._print(profile_name)

    def list_profiles(self, profiles):
        self._print("PROFILES")

    def profile_not_found(self, candidate):
        self._print(candidate)

    def profile_set(self, candidate):
        self._print(candidate)

    def syntax_profile(self):
        self._print("PROFILE SYNTAX")

    def print_secrets_leak_result(self, result):
        self._print(result)

    def back(self):
        self._print("BACK")

    def exit(self):
        self._print("EXIT")

    def unknown_command(self, line):
        self._print(line)


class ShellRuntimeService:
    def __init__(self, *args, **kwargs):
        self.tools_cache = {}
        self.plugin_manager = PluginManager()
        self.policy_engine = PolicyEngine()

    @staticmethod
    def infer_category(tool_path: str | None) -> str | None:
        return None

    def get_plugin(self, name: str):
        return None

    def list_plugin_metadata(self):
        return {}

    def evaluate_tool_execution(self, **kwargs):
        return self.policy_engine.evaluate(**kwargs)

    def evaluate_plugin_execution(self, **kwargs):
        return self.policy_engine.evaluate(**kwargs)


class ShellActionService:
    def __init__(self, *args, **kwargs):
        self.runtime = kwargs.get("runtime")
        self._bilingual = kwargs.get("bilingual", lambda e, g: e)
        self._input = kwargs.get("input_func", input)
        self._print = kwargs.get("print_func", print)

    def run_tool(self, *, tool_module: Any, tool_path: str | None, tool_options: dict[str, Any], profile_name: str):
        return None

    def run_plugin(self, *, plugin_name: str, kwargs: dict[str, Any], profile_name: str):
        return None


class DispatchContext:
    def __init__(self, *args, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


class ToolDispatchService:
    def __init__(self, *args, **kwargs):
        self.execution_service = kwargs.get("execution_service")
        self.plugin_manager = kwargs.get("plugin_manager")
        self.policy_engine = kwargs.get("policy_engine")
        self.update_stats = kwargs.get("update_stats")
        self.logger = kwargs.get("logger")

    def execute_plugin(self, **kwargs):
        return ToolResult.failed("plugin execution unavailable in fallback mode", error_type="fallback")

    def execute_tool(self, **kwargs):
        return ToolResult.failed("tool execution unavailable in fallback mode", error_type="fallback")


class SystemReportService:
    def __init__(self, output_dir: str | Path = "reports/scans"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate(self, *, session_id: str, tools: dict[str, Any], config: dict[str, Any], tool_name: str = "Report Generator"):
        report_file = self.output_dir / f"blackops_report_{session_id}.json"
        with report_file.open("w", encoding="utf-8") as handle:
            json.dump({"session_id": session_id, "tools": list(tools.keys()), "config": config}, handle)
        return ToolResult.success(data={"report_file": str(report_file), "session_id": session_id, "tool_count": len(tools)}, tool=tool_name)


class ToolCommandBuilder:
    def __init__(self, bilingual, input_func=input):
        self._bilingual = bilingual
        self._input = input_func

    def _prompt_required(self, message):
        return self._input(message)

    def _prompt_validated(self, message, validator, error_message, normalizer=None):
        return self._input(message)

    def _prompt_optional(self, message, validator=None, error_message=None, normalizer=None):
        return self._input(message)

    def _append_optional_arg(self, cmd, flag, value):
        if value:
            cmd.extend([flag, value])

    def build_tool_command(self, tool_id, filename):
        return ["python3", filename]
