"""
Presentation helpers for the interactive shell.
"""

from __future__ import annotations

from typing import Any, Callable

from utils.table_formatter import format_table


class ShellPresentationService:
    def __init__(
        self,
        *,
        bilingual: Callable[[str, str], str],
        print_func: Callable[..., None] = print,
    ):
        self._bilingual = bilingual
        self._print = print_func

    def show_tools(self, tools_cache: dict[str, str]) -> None:
        self._print(f"\n{self._bilingual('Available tools', 'Verfuegbare Tools')}:")
        for path in sorted(tools_cache.keys()):
            self._print(f"  {path}")

    def show_plugins(self, plugin_manager: Any) -> None:
        self._print(f"\n{self._bilingual('Plugins', 'Plugins')}:")
        for name, meta in sorted(plugin_manager.list_plugin_metadata().items()):
            state = "ok" if meta["compatible"] else f"error: {meta['error']}"
            self._print(f"  {name} ({meta['version']}) [{state}]")

    def syntax_show(self) -> None:
        self._print(self._bilingual("Syntax: show tools|plugins", "Syntax: show tools|plugins"))

    def tool_not_found(self, arg: str) -> None:
        self._print(f"[-] {self._bilingual('Tool not found', 'Tool nicht gefunden')}: {arg}")

    def tool_loaded(self, arg: str) -> None:
        self._print(f"[*] {self._bilingual('Tool loaded', 'Tool geladen')}: {arg}")

    def load_error(self, error: Exception) -> None:
        self._print(f"[-] {self._bilingual('Error while loading', 'Fehler beim Laden')}: {error}")

    def no_tool_selected(self) -> None:
        self._print(f"[-] {self._bilingual('No tool selected. use <tool>', 'Kein Tool ausgewaehlt. use <tool>')}")

    def set_option(self, key: str, value: str) -> None:
        self._print(f"[*] {key} => {value}")

    def run_dry_tool(self, tool_name: str) -> None:
        self._print(f"[DRY-RUN] {self._bilingual('Would execute tool', 'Wuerde Tool ausfuehren')}: {tool_name}")

    def execution_error(self, error: Exception) -> None:
        self._print(f"[-] {self._bilingual('Execution error', 'Fehler bei der Ausfuehrung')}: {error}")

    def syntax_plugin(self) -> None:
        self._print(self._bilingual("Syntax: plugin run <name> [KEY=VALUE ...] [--dry-run]", "Syntax: plugin run <name> [KEY=VALUE ...] [--dry-run]"))

    def run_dry_plugin(self, name: str, kwargs: dict[str, Any]) -> None:
        self._print(f"[DRY-RUN] {self._bilingual('Would execute plugin', 'Wuerde Plugin ausfuehren')}: {name} {self._bilingual('with', 'mit')} {kwargs}")

    def plugin_result(self, result: Any) -> None:
        self._print(f"[*] {self._bilingual('Plugin result', 'Plugin-Resultat')}: {result}")

    def plugin_error(self, error: Exception) -> None:
        self._print(f"[-] {self._bilingual('Plugin error', 'Plugin-Fehler')}: {error}")

    def show_profile(self, profile_name: str) -> None:
        self._print(f"[*] Active profile: {profile_name}")

    def list_profiles(self, profiles: dict[str, dict[str, Any]]) -> None:
        for name, profile in sorted(profiles.items()):
            self._print(f"  {name}: {profile.get('description', '')}")

    def profile_not_found(self, candidate: str) -> None:
        self._print(f"[-] Profile not found: {candidate}")

    def profile_set(self, candidate: str) -> None:
        self._print(f"[*] Active profile set to: {candidate}")

    def syntax_profile(self) -> None:
        self._print("Syntax: profile show|list|use <name>")

    def print_secrets_leak_result(self, result: dict[str, Any]) -> None:
        self._print(
            f"[*] {self._bilingual('Scan finished', 'Scan abgeschlossen')}: "
            f"files={result.get('scanned_files', 0)} "
            f"findings={result.get('findings_count', 0)} "
            f"suppressed={result.get('suppressed_by_baseline', 0)}"
        )
        ci = result.get("ci", {})
        if ci.get("failed"):
            self._print(f"[-] CI-Status: FAILED (exit_code={ci.get('exit_code', 2)})")
        else:
            self._print("[*] CI-Status: PASS")

        findings = result.get("findings", [])
        if not findings:
            self._print(f"[*] {self._bilingual('No findings.', 'Keine Findings.')}")
            return

        rows = []
        for item in findings[:20]:
            rows.append(
                [
                    item.get("file", ""),
                    item.get("line", ""),
                    item.get("rule", ""),
                    item.get("match_preview", ""),
                ]
            )
        self._print(format_table(["file", "line", "rule", "preview"], rows))
        if len(findings) > 20:
            self._print(f"[*] {self._bilingual('Additional findings not shown', 'Weitere Findings nicht angezeigt')}: {len(findings) - 20}")

    def back(self) -> None:
        self._print(f"[*] {self._bilingual('Back to main menu.', 'Zurueck zum Hauptmenue.')}")

    def exit(self) -> None:
        self._print(f"[+] {self._bilingual('Goodbye!', 'Auf Wiedersehen!')}")

    def unknown_command(self, line: str) -> None:
        self._print(f"{self._bilingual('Unknown command', 'Unbekannter Befehl')}: {line}. {self._bilingual('Type help.', 'Gib help ein.')}")
