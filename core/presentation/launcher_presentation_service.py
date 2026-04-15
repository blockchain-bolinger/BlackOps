"""
Presentation helpers for the main BlackOps launcher.
"""

from __future__ import annotations

import shutil
from datetime import datetime
from typing import Any, Callable, Dict

from colorama import Fore


class LauncherPresentationService:
    def __init__(
        self,
        *,
        print_func: Callable[..., None] = print,
        clear_screen: Callable[[], None],
        input_func: Callable[[str], str] = input,
    ):
        self._print = print_func
        self._clear_screen = clear_screen
        self._input = input_func

    def print_banner(self, *, version: str, session_id: str, author: str) -> None:
        self._clear_screen()
        width = shutil.get_terminal_size((100, 30)).columns
        logo_lines = [
            "██████╗ ██╗      █████╗  ██████╗██╗  ██╗ ██████╗ ██████╗ ███████╗",
            "██╔══██╗██║     ██╔══██╗██╔════╝██║ ██╔╝██╔═══██╗██╔══██╗██╔════╝",
            "██████╔╝██║     ███████║██║     █████╔╝ ██║   ██║██████╔╝███████╗",
            "██╔══██╗██║     ██╔══██║██║     ██╔═██╗ ██║   ██║██╔═══╝ ╚════██║",
            "██████╔╝███████╗██║  ██║╚██████╗██║  ██╗╚██████╔╝██║     ███████║",
            "╚═════╝ ╚══════╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝ ╚═════╝ ╚═╝     ╚══════╝",
        ]

        self._print()
        for line in logo_lines:
            self._print(f"{Fore.RED}{line.center(width)}")
        self._print(f"{Fore.WHITE}{f'>> BLACKOPS v{version} <<'.center(width)}")
        self._print(f"{Fore.YELLOW}{('-' * 43).center(width)}")
        self._print(f"{Fore.CYAN}{f'Session ID: {session_id}'.center(width)}")
        self._print(f"{Fore.WHITE}{f'Operator: @{author}'.center(width)}")
        self._print(f"{Fore.YELLOW}{datetime.now().strftime('%Y-%m-%d %H:%M:%S').center(width)}")

    def print_tool_info(self, *, tool: Dict[str, Any]) -> None:
        self._print(f"\n{Fore.CYAN}┌──────────────────────────────────────────────────┐")
        self._print(f"{Fore.CYAN}│            TOOL INFORMATION                     │")
        self._print(f"{Fore.CYAN}├──────────────────────────────────────────────────┤")
        self._print(f"{Fore.WHITE}│ Name:        {Fore.YELLOW}{tool['name']:<30} {Fore.WHITE}│")
        self._print(f"{Fore.WHITE}│ Category (Kategorie): {Fore.GREEN}{tool['category']}{Fore.WHITE}")
        self._print(f"{Fore.WHITE}│ File (Datei): {Fore.CYAN}{tool['file']}{Fore.WHITE}")
        self._print(f"{Fore.WHITE}│ Root required (Root nötig): {Fore.RED if tool['sudo'] else Fore.GREEN}{'Yes (Ja)' if tool['sudo'] else 'No (Nein)'}{Fore.WHITE}")
        self._print(f"{Fore.WHITE}│ Description (Beschreibung): {tool['description']}")
        self._print(f"{Fore.CYAN}└──────────────────────────────────────────────────┘")

    def invalid_tool_id(self) -> None:
        self._print(f"{Fore.RED}[!] Invalid tool ID (Ungültige Tool-ID)")

    def start_plugin(self, *, name: str) -> None:
        self._print(f"\n{Fore.GREEN}[*] Starting plugin (Starte Plugin): {name}...")

    def plugin_not_loaded(self, *, plugin_name: str) -> None:
        self._print(f"{Fore.RED}[ERROR] Plugin not loaded (Plugin nicht geladen): {plugin_name}")

    def policy_error(self, message: str) -> None:
        self._print(f"{Fore.RED}[ERROR] {message}")

    def plugin_result_header(self, status: str) -> None:
        self._print(f"\n{Fore.CYAN}Result (Ergebnis): {status}")

    def report_generation_start(self) -> None:
        self._print(f"\n{Fore.CYAN}[*] Generating system report... (Generiere System-Report...)")

    def report_generation_error(self, error: str) -> None:
        self._print(f"{Fore.RED}[ERROR] Could not generate report (Konnte Report nicht generieren): {error}")

    def tool_not_found(self, filename: str) -> None:
        self._print(f"{Fore.RED}[ERROR] '{filename}' not found (nicht gefunden)!")

    def file_found_at(self, filename: str) -> None:
        self._print(f"{Fore.YELLOW}[!] File found at (Datei gefunden unter): {filename}")

    def aborted(self) -> None:
        self._print(f"\n{Fore.RED}[!] Aborted (Abgebrochen)")

    def start_tool(self, *, name: str) -> None:
        self._print(f"\n{Fore.GREEN}[*] Starting (Starte) {name}...")

    def root_required(self) -> None:
        self._print(f"{Fore.YELLOW}[WARNING] Tool requires root privileges! (Tool benötigt Root-Rechte!)")

    def start_with_sudo(self, filename: str) -> None:
        self._print(f"{Fore.YELLOW}[WARNING] Start with (Starte mit) 'sudo python3 {filename}'")

    def tool_timed_out(self) -> None:
        self._print(f"{Fore.YELLOW}[WARNING] Tool execution timed out (Tool-Ausführung hat das Zeitlimit überschritten).")

    def tool_exit_code(self, code: Any) -> None:
        self._print(f"{Fore.YELLOW}[WARNING] Tool exited with code (Tool wurde mit Exit-Code) {code}.")

    def tool_interrupted(self) -> None:
        self._print(f"\n{Fore.YELLOW}[!] Tool execution interrupted (Tool-Ausführung abgebrochen)")

    def blocked_unsafe_command(self, error: Exception) -> None:
        self._print(f"{Fore.RED}[ERROR] Blocked unsafe command (Unsicherer Befehl blockiert): {error}")

    def could_not_start_tool(self, error: Exception) -> None:
        self._print(f"{Fore.RED}[ERROR] Could not start tool (Konnte Tool nicht starten): {error}")

    def print_report_summary(self, *, session_id: str, report_file: str, tool_count: int) -> None:
        self._print(f"{Fore.GREEN}[✓] Report saved as: {report_file}")
        self._print(f"\n{Fore.WHITE}┌──────────────────────────────┐")
        self._print(f"{Fore.WHITE}│      REPORT SUMMARY          │")
        self._print(f"{Fore.WHITE}├──────────────────────────────┤")
        self._print(f"{Fore.WHITE}│ Session: {session_id:<28} │")
        self._print(f"{Fore.WHITE}│ Tools available (Tools verfügbar): {tool_count:<4} │")
        self._print(f"{Fore.WHITE}└──────────────────────────────┘")

    def print_exit(self, *, author: str) -> None:
        self._print(f"\n{Fore.YELLOW}[*] Exiting Black Ops Framework...")
        self._print(f"{Fore.GREEN}[✓] Goodbye, @{author}")

    def prompt(self, message: str) -> str:
        return self._input(message)

    def prompt_plugin_args(self, params_schema: dict[str, dict[str, Any]]) -> dict[str, str]:
        user_args: dict[str, str] = {}
        for param, config in params_schema.items():
            val = self._input(f"[?] {config['description']} ({param}): ").strip()
            if val:
                user_args[param] = val
        return user_args

    def invalid_selection(self) -> None:
        self._print(f"{Fore.RED}[!] {self._bilingual('Invalid selection', 'Ungültige Auswahl')}")
