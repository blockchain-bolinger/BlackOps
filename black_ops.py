#!/usr/bin/env python3
"""
Black Ops Framework - Ultimate Hacking Suite v3.0
FOR AUTHORIZED SECURITY TESTING ONLY! (NUR FÜR AUTORISIERTE SICHERHEITSTESTS!)
"""

import os
import sys
import time
import hashlib
import subprocess
from colorama import Fore, Style, init
from core.registry import build_tool_registry

try:
    from core.redaction_utils import redact_data
except Exception:
    def redact_data(data):
        return data

init(autoreset=True)

# -------------------------------------------------------------------
# Manager-Import mit Fallback (falls Core-Module nicht existieren)
# -------------------------------------------------------------------
try:
    from core.runtime import ConfigManager, DependencyChecker, RuntimeGuardService, ShellRuntimeService
    from core.telemetry import BlackOpsLogger, ExecutionTelemetry
    from core.execution import ExecutionService, ProcessRunnerError, SafeProcessRunner, ToolCommandBuilder, DispatchContext, ToolDispatchService
    from core.presentation import MenuService, LauncherPresentationService
    from core.reporting import SystemReportService
    from core.policy_engine import PolicyEngine
    from core.plugin_manager import PluginManager
    from core.stats_service import StatsService
    from core.tool_contract import ToolResult
    MANAGER_IMPORT_OK = True
except ImportError as e:
    MANAGER_IMPORT_OK = False
    print(f"{Fore.YELLOW}[WARNING] Manager modules not found (Manager-Module nicht gefunden): {e}")
    print(f"{Fore.YELLOW}Using basic mode without advanced features (Verwende Basis-Modus ohne erweiterte Features)...")
    from core.compat import (
        BlackOpsLogger,
        ConfigManager,
        DependencyChecker,
        DispatchContext,
        ExecutionService,
        ExecutionTelemetry,
        LauncherPresentationService,
        MenuService,
        PluginManager,
        PolicyEngine,
        ProcessRunnerError,
        SafeProcessRunner,
        StatsService,
        SystemReportService,
        ToolCommandBuilder,
        ToolDispatchService,
        ToolResult,
        RuntimeGuardService,
        ShellRuntimeService,
    )

# -------------------------------------------------------------------
# Hauptklasse BlackOps
# -------------------------------------------------------------------
class BlackOps:
    def __init__(self):
        self.version = "3.0"
        self.author = "artur_bo91"
        self.session_id = hashlib.md5(str(time.time()).encode()).hexdigest()[:8]
        
        self.config = ConfigManager().config
        self.logger = BlackOpsLogger("black_ops_main")
        self.logger.set_correlation_id(self.session_id)
        self.deps = DependencyChecker()
        self.policy_engine = PolicyEngine(self.config)
        self.telemetry = ExecutionTelemetry()
        self.active_profile = self.config.get("policy", {}).get("default_profile", "lab")
        self.ethics_accepted = False
        self.plugin_manager = PluginManager()
        self.process_runner = SafeProcessRunner()
        self.execution_service = ExecutionService(
            process_runner=self.process_runner,
            base_dir=os.getcwd(),
            tools_dir=os.path.join(os.getcwd(), "tools"),
            policy_engine=self.policy_engine,
            telemetry=self.telemetry,
            profile_name=self.active_profile,
        )
        self.report_service = SystemReportService(output_dir=os.path.join(os.getcwd(), "reports", "scans"))
        self.stats_service = StatsService(os.path.join(os.getcwd(), "data", "sessions", "blackops_stats.json"))
        self.command_builder = ToolCommandBuilder(self._bilingual)
        self.runtime_guard = RuntimeGuardService(
            dependency_checker=self.deps,
            bilingual=self._bilingual,
            logger=self.logger,
        )
        self.menu_service = MenuService(
            bilingual=self._bilingual,
        )
        self.presentation = LauncherPresentationService(
            clear_screen=self.clear_screen,
            input_func=input,
        )
        self.plugins = self.plugin_manager.discover()
        self.tools, self.categories = build_tool_registry(self.plugins)
        self.dispatcher = ToolDispatchService(
            execution_service=self.execution_service,
            plugin_manager=self.plugin_manager,
            policy_engine=self.policy_engine,
            update_stats=self.update_stats,
            logger=self.logger,
        )

    # -------------------------------------------------------------------
    # Hilfsfunktionen
    # -------------------------------------------------------------------
    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def _bilingual(self, english, german):
        return f"{english} ({german})"

    def print_banner(self):
        self.presentation.print_banner(version=self.version, session_id=self.session_id, author=self.author)

    def ethical_warning(self):
        accepted = self.runtime_guard.ethical_warning(
            show_warning=self.config.get("ethics", {}).get("show_warning", True),
            require_confirmation=self.config.get("ethics", {}).get("require_confirmation", True),
        )
        self.ethics_accepted = bool(accepted)
        if not accepted:
            sys.exit(0)
        return True

    def system_check(self):
        return self.runtime_guard.system_check()

    def show_tool_info(self, tool_id):
        tool = self.tools.get(tool_id)
        if not tool:
            return
        self.presentation.print_tool_info(tool=tool)

    def _prompt_required(self, message):
        return self.command_builder._prompt_required(message)

    def _prompt_validated(self, message, validator, error_message, normalizer=None):
        return self.command_builder._prompt_validated(message, validator, error_message, normalizer)

    def _prompt_optional(self, message, validator=None, error_message=None, normalizer=None):
        return self.command_builder._prompt_optional(message, validator, error_message, normalizer)

    def _append_optional_arg(self, cmd, flag, value):
        self.command_builder._append_optional_arg(cmd, flag, value)

    def _build_tool_command(self, tool_id, filename):
        return self.command_builder.build_tool_command(tool_id, filename)

    def launch_tool(self, tool_id):
        tool = self.tools.get(tool_id)
        if not tool:
            self.presentation.invalid_tool_id()
            return ToolResult.failed("Invalid tool ID", tool_id=tool_id)
        self.show_tool_info(tool_id)
        if tool_id == "13":
            ok = self.system_check()
            return ToolResult.success(data={"system_check": bool(ok)}, tool_id=tool_id)
        elif tool_id == "14":
            return self.generate_report()
        elif tool_id == "99":
            self.safe_exit()
            return ToolResult.success(data={"exit": True}, tool_id=tool_id)
        
        filename = tool["file"]
        if filename == "plugin":
            self.presentation.start_plugin(name=tool["name"])
            plugin_name = tool['name'].replace(" (Plugin)", "")
            plugin = self.plugin_manager.get_plugin(plugin_name)
            if not plugin:
                self.presentation.plugin_not_loaded(plugin_name=plugin_name)
                return ToolResult.failed("Plugin not loaded", plugin=plugin_name)

            params_schema = plugin.get_parameters()
            user_args = self.presentation.prompt_plugin_args(params_schema)
            result = self.dispatcher.execute_plugin(
                plugin_name=plugin_name,
                display_name=tool["name"],
                user_args=user_args,
                profile_name=self.active_profile,
                approved=self.ethics_accepted,
            )
            if result.meta.get("error_type") == "policy":
                self.presentation.policy_error(result.errors[0])
                return result
            self.presentation.plugin_result_header(result.status)
            if result.data is not None:
                self.presentation.plugin_result(result.data)
            return result

        # Special cases that aren't paths
        if filename in ["system_check", "report_gen", "exit"]:
            return

        if not os.path.exists(filename):
            self.presentation.tool_not_found(filename)
            if not filename.startswith("tools/"):
                alt_filename = os.path.join("tools", filename)
                if os.path.exists(alt_filename):
                    filename = alt_filename
                    self.presentation.file_found_at(filename)
                else:
                    self.presentation.aborted()
                    return ToolResult.failed("Tool file not found", file=filename)
            else:
                self.presentation.aborted()
                return ToolResult.failed("Tool file not found", file=filename)
        
        self.presentation.start_tool(name=tool["name"])
        if tool["sudo"] and os.geteuid() != 0:
            self.presentation.root_required()
            self.presentation.start_with_sudo(filename)
            time.sleep(2)
        try:
            time.sleep(1)
            cmd = self._build_tool_command(tool_id, filename)
            if not cmd:
                return ToolResult.failed("Command build aborted", tool=tool['name'])
            if tool["sudo"] and os.geteuid() != 0:
                cmd = ["sudo"] + cmd
            new_env = os.environ.copy()
            new_env["PYTHONPATH"] = os.getcwd()
            timeout_seconds = self.config.get("runtime", {}).get("task_timeout_seconds", 300)
            timeout_seconds = timeout_seconds if isinstance(timeout_seconds, (int, float)) and timeout_seconds > 0 else None
            dispatch_context = DispatchContext(
                tool_id=tool_id,
                tool_name=tool["name"],
                tool_path=filename,
                category=tool.get("category", "utils"),
                sudo=bool(tool.get("sudo")),
                approved=self.ethics_accepted,
                profile_name=self.active_profile,
                correlation_id=self.session_id,
            )
            tool_result = self.dispatcher.execute_tool(
                context=dispatch_context,
                command=cmd,
                env=new_env,
                cwd=os.getcwd(),
                timeout_seconds=timeout_seconds,
            )
            details = tool_result.data if isinstance(tool_result.data, dict) else {}
            if tool_result.meta.get("error_type") in {"policy", "approval"}:
                self.presentation.policy_error(tool_result.errors[0])
                return tool_result
            if details.get("timed_out"):
                self.presentation.tool_timed_out()
            elif tool_result.status == "failed" and details.get("returncode") is not None:
                self.presentation.tool_exit_code(details.get("returncode"))
        except KeyboardInterrupt:
            self.presentation.tool_interrupted()
            tool_result = ToolResult.failed("Tool execution interrupted", tool=tool['name'])
        except ProcessRunnerError as e:
            self.presentation.blocked_unsafe_command(e)
            tool_result = ToolResult.failed(str(e), tool=tool['name'])
        except Exception as e:
            self.presentation.could_not_start_tool(e)
            tool_result = ToolResult.failed(str(e), tool=tool['name'])
        return tool_result

    def generate_report(self):
        self.presentation.report_generation_start()
        result = self.report_service.generate(
            session_id=self.session_id,
            tools=self.tools,
            config=self.config,
            tool_name="Report Generator",
        )
        if result.status == "success":
            data = result.data if isinstance(result.data, dict) else {}
            self.presentation.print_report_summary(
                session_id=self.session_id,
                report_file=data.get("report_file", ""),
                tool_count=data.get("tool_count", 0),
            )
            self.update_stats("Report Generator")
            return result
        self.presentation.report_generation_error(result.errors[0])
        return result

    def update_stats(self, tool_name):
        self.stats_service.increment(tool_name)

    def safe_exit(self):
        self.presentation.print_exit(author=self.author)
        self.logger.info("framework_exit: Session ended")
        sys.exit(0)

    def show_menu(self):
        while True:
            self.print_banner()
            self.menu_service.render(tools=self.tools, categories=self.categories)
            choice = self.presentation.prompt(f"\n{Fore.WHITE}[?] {self._bilingual('Selection', 'Auswahl')}: ").strip()
            if choice in self.tools:
                self.launch_tool(choice)
            else:
                self.presentation.invalid_selection()
                time.sleep(1)

    def run(self):
        self.ethical_warning()
        self.system_check()
        self.show_menu()

# -------------------------------------------------------------------
# Start
# -------------------------------------------------------------------
if __name__ == "__main__":
    try:
        blackops = BlackOps()
        blackops.run()
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}[!] Interrupted by user (Abbruch durch Benutzer)")
        sys.exit(0)
    except Exception as e:
        print(f"{Fore.RED}[!] Critical error (Schwerer Fehler): {e}")
        sys.exit(1)
