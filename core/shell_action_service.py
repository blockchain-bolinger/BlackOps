"""
Shared command execution helpers for the interactive shell.
"""

from __future__ import annotations

from typing import Any, Callable


class ShellActionService:
    def __init__(
        self,
        *,
        runtime,
        bilingual: Callable[[str, str], str],
        input_func: Callable[[str], str] = input,
        print_func: Callable[..., None] = print,
    ):
        self.runtime = runtime
        self._bilingual = bilingual
        self._input = input_func
        self._print = print_func

    def run_tool(self, *, tool_module: Any, tool_path: str | None, tool_options: dict[str, Any], profile_name: str):
        if not tool_module:
            return None
        decision = self.runtime.evaluate_tool_execution(
            profile_name=profile_name,
            tool_name=tool_module.__name__,
            tool_path=tool_path,
            approved=True,
        )
        if not decision.allowed:
            self._print(f"[-] {self._bilingual('Blocked by profile policy', 'Durch Profilrichtlinie blockiert')}: {decision.reason}")
            return None
        if decision.approval_required:
            consent = self._input(
                f"[?] {self._bilingual('Profile approval required. Continue? (yes/no)', 'Profilgenehmigung erforderlich. Fortfahren? (ja/nein)')}: "
            ).strip().lower()
            if consent not in {"yes", "y", "ja", "j"}:
                self._print(f"[-] {self._bilingual('Execution cancelled by policy', 'Ausführung durch Richtlinie abgebrochen')}")
                return None
        if hasattr(tool_module, "main"):
            return tool_module.main(tool_options)
        self._print(f"[-] {self._bilingual('The tool has no main() function.', 'Das Tool hat keine main()-Funktion.')}")
        return None

    def run_plugin(self, *, plugin_name: str, kwargs: dict[str, Any], profile_name: str):
        plugin = self.runtime.get_plugin(plugin_name)
        if not plugin:
            self._print(f"[-] {self._bilingual('Plugin not loaded', 'Plugin nicht geladen')}: {plugin_name}")
            return None

        decision = self.runtime.evaluate_plugin_execution(
            profile_name=profile_name,
            plugin_name=plugin_name,
            approved=True,
        )
        if not decision.allowed:
            self._print(f"[-] {self._bilingual('Blocked by profile policy', 'Durch Profilrichtlinie blockiert')}: {decision.reason}")
            return None

        return plugin.run(**kwargs)
