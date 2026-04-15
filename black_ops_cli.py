#!/usr/bin/env python3
"""
BlackOps Framework - Interactive Command Line (Interaktive Kommandozeile)
"""
import cmd
import sys
import importlib
from core.runtime import ShellRuntimeService
from core.shell_action_service import ShellActionService
from core.presentation import ShellPresentationService

class BlackOpsShell(cmd.Cmd):
    intro = """
    ██████╗ ██╗      █████╗  ██████╗██╗  ██╗ ██████╗ ██████╗ ███████╗
    ██╔══██╗██║     ██╔══██╗██╔════╝██║ ██╔╝██╔═══██╗██╔══██╗██╔════╝
    ██████╔╝██║     ███████║██║     █████╔╝ ██║   ██║██████╔╝███████╗
    ██╔══██╗██║     ██╔══██║██║     ██╔═██╗ ██║   ██║██╔═══╝ ╚════██║
    ██████╔╝███████╗██║  ██║╚██████╗██║  ██╗╚██████╔╝██║     ███████║
    ╚═════╝ ╚══════╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝ ╚═════╝ ╚═╝     ╚══════╝
    BlackOps Framework v3.0 - Interactive Shell (Interaktive Shell)
    Type 'help' for help. (Gib 'help' ein fuer Hilfe.)
    """
    prompt = "BlackOps> "
    current_tool = None
    current_tool_path = None
    tool_options = {}

    def __init__(self):
        super().__init__()
        self.runtime = ShellRuntimeService()
        self.actions = ShellActionService(runtime=self.runtime, bilingual=self._bilingual)
        self.presentation = ShellPresentationService(bilingual=self._bilingual)
        self.tools_cache = self.runtime.tools_cache
        self.plugin_manager = self.runtime.plugin_manager
        self.policy_engine = self.runtime.policy_engine
        self.active_profile = self.policy_engine.default_profile

    @staticmethod
    def _bilingual(english: str, german: str) -> str:
        return f"{english} ({german})"

    def do_show(self, arg):
        """Shows available resources (Zeigt verfügbare Ressourcen): show tools"""
        if arg == "tools":
            self.presentation.show_tools(self.tools_cache)
        elif arg == "plugins":
            self.presentation.show_plugins(self.plugin_manager)
        else:
            self.presentation.syntax_show()

    def do_use(self, arg):
        """Selects a tool (Wählt ein Tool aus): use tools/recon/social_hunter_v7"""
        if not arg:
            self.presentation.tool_not_found("")
            return
        if arg not in self.tools_cache:
            self.presentation.tool_not_found(arg)
            return
        try:
            module = importlib.import_module(self.tools_cache[arg])
            self.current_tool = module
            self.current_tool_path = arg
            self.prompt = f"BlackOps({arg.split('/')[-1]})> "
            self.presentation.tool_loaded(arg)
            self.tool_options = {}
        except Exception as e:
            self.presentation.load_error(e)

    def do_set(self, arg):
        """Sets an option (Setzt eine Option): set LHOST 192.168.1.100"""
        if not self.current_tool:
            self.presentation.no_tool_selected()
            return
        parts = arg.split()
        if len(parts) != 2:
            self.presentation.syntax_show()
            return
        key, value = parts
        self.tool_options[key] = value
        self.presentation.set_option(key, value)

    def do_run(self, arg):
        """Runs the selected tool (Führt das geladene Tool aus): run [--dry-run]"""
        if not self.current_tool:
            self.presentation.no_tool_selected()
            return
        dry_run = "--dry-run" in arg
        if dry_run:
            self.presentation.run_dry_tool(self.current_tool.__name__)
            return
        try:
            self.actions.run_tool(
                tool_module=self.current_tool,
                tool_path=self.current_tool_path,
                tool_options=self.tool_options,
                profile_name=self.active_profile,
            )
        except Exception as e:
            self.presentation.execution_error(e)

    def do_plugin(self, arg):
        """Plugin-Operationen: plugin run <name> [KEY=VALUE ...] [--dry-run]"""
        parts = arg.split()
        if len(parts) < 2 or parts[0] != "run":
            self.presentation.syntax_plugin()
            return
        name = parts[1]
        dry_run = "--dry-run" in parts
        kwargs = {}
        for token in parts[2:]:
            if token == "--dry-run" or "=" not in token:
                continue
            key, value = token.split("=", 1)
            kwargs[key] = value
        if dry_run:
            self.presentation.run_dry_plugin(name, kwargs)
            return
        try:
            result = self.actions.run_plugin(
                plugin_name=name,
                kwargs=kwargs,
                profile_name=self.active_profile,
            )
            if result is None:
                return
            if name == "secrets_leak_check" and isinstance(result, dict):
                self.presentation.print_secrets_leak_result(result)
            else:
                self.presentation.plugin_result(result)
        except Exception as e:
            self.presentation.plugin_error(e)

    def do_profile(self, arg):
        """Profile management: profile show|list|use <name>"""
        parts = arg.split()
        if not parts or parts[0] == "show":
            self.presentation.show_profile(self.active_profile)
            return
        if parts[0] == "list":
            self.presentation.list_profiles(self.policy_engine.available_profiles())
            return
        if parts[0] == "use" and len(parts) == 2:
            candidate = parts[1]
            if candidate not in self.policy_engine.available_profiles():
                self.presentation.profile_not_found(candidate)
                return
            self.active_profile = candidate
            self.presentation.profile_set(candidate)
            return
        self.presentation.syntax_profile()

    def do_back(self, arg):
        """Back to main menu (Zurück zum Hauptmenü)"""
        self.current_tool = None
        self.current_tool_path = None
        self.tool_options = {}
        self.prompt = "BlackOps> "
        self.presentation.back()

    def do_exit(self, arg):
        """Exit the framework (Beendet das Framework)"""
        self.presentation.exit()
        return True

    def default(self, line):
        self.presentation.unknown_command(line)

if __name__ == "__main__":
    BlackOpsShell().cmdloop()
