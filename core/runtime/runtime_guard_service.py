"""
Runtime guard helpers for ethics prompts and environment checks.
"""

from __future__ import annotations

import os
import sys
import time
from typing import Any, Callable, Optional

from colorama import Fore


class RuntimeGuardService:
    def __init__(
        self,
        *,
        dependency_checker: Any,
        bilingual: Callable[[str, str], str],
        logger: Any = None,
        input_func: Callable[[str], str] = input,
        print_func: Callable[..., None] = print,
        sleep_func: Callable[[float], None] = time.sleep,
        requests_get: Optional[Callable[..., Any]] = None,
    ):
        self.dependency_checker = dependency_checker
        self._bilingual = bilingual
        self.logger = logger
        self._input = input_func
        self._print = print_func
        self._sleep = sleep_func
        self._requests_get = requests_get

    def ethical_warning(self, *, show_warning: bool = True, require_confirmation: bool = True) -> bool:
        if not show_warning:
            return True

        self._print(f"\n{Fore.RED}╔══════════════════════════════════════════════════════════╗")
        self._print(f"{Fore.RED}║    ⚠️  IMPORTANT WARNING (WICHTIGE WARNUNG) ⚠️          ║")
        self._print(f"{Fore.RED}╠══════════════════════════════════════════════════════════╣")
        self._print(f"{Fore.YELLOW}║  1. Authorized tests only (Nur autorisierte Tests)    ║")
        self._print(f"{Fore.YELLOW}║  2. Only on owned/lab systems (Nur eigene/Lab-Systeme)║")
        self._print(f"{Fore.YELLOW}║  3. Follow local laws (Lokale Gesetze beachten)       ║")
        self._print(f"{Fore.YELLOW}║  4. No illegal activity (Keine illegalen Aktivitäten) ║")
        self._print(f"{Fore.YELLOW}║  5. Use responsibly (Verantwortungsvoll nutzen)       ║")
        self._print(f"{Fore.RED}╚══════════════════════════════════════════════════════════╝")

        if require_confirmation:
            consent = self._input(
                f"\n{Fore.WHITE}[?] {self._bilingual('Understood and accepted? (yes/no)', 'Verstanden und akzeptiert? (ja/nein)')}: "
            ).strip().lower()
            if consent not in {"yes", "y", "ja", "j"}:
                self._print(
                    f"{Fore.RED}[!] {self._bilingual('Aborted. You must accept the terms.', 'Abbruch. Du musst die Bedingungen akzeptieren.')}"
                )
                return False

        if self.logger is not None and hasattr(self.logger, "info"):
            self.logger.info("ethical_warning_accepted")
        return True

    def system_check(self) -> bool:
        self._print(f"\n{Fore.CYAN}[*] {self._bilingual('Running system checks...', 'Führe System-Checks durch...')}")
        checks: list[tuple[str, bool]] = []

        if hasattr(os, "geteuid") and os.geteuid() == 0:
            checks.append((f"{Fore.GREEN}[✓] {self._bilingual('Root privileges', 'Root-Privilegien')}", True))
        else:
            checks.append(
                (
                    f"{Fore.YELLOW}[!] {self._bilingual('Not running as root (some tools need sudo)', 'Nicht als Root (manche Tools benötigen sudo)')}",
                    False,
                )
            )

        python_version = sys.version_info
        if python_version.major >= 3 and python_version.minor >= 8:
            checks.append((f"{Fore.GREEN}[✓] Python {python_version.major}.{python_version.minor}.{python_version.micro}", True))
        else:
            checks.append(
                (
                    f"{Fore.RED}[!] {self._bilingual('Python 3.8+ required', 'Python 3.8+ benötigt')} (current/aktuell: {python_version.major}.{python_version.minor})",
                    False,
                )
            )

        try:
            if self._requests_get is not None:
                response = self._requests_get("http://httpbin.org/ip", timeout=5)
            else:
                import requests

                response = requests.get("http://httpbin.org/ip", timeout=5)

            if getattr(response, "status_code", None) == 200:
                checks.append((f"{Fore.GREEN}[✓] {self._bilingual('Internet connection OK', 'Internet-Verbindung OK')}", True))
            else:
                checks.append((f"{Fore.YELLOW}[!] {self._bilingual('Internet connection limited', 'Internet-Verbindung eingeschränkt')}", False))
        except Exception:
            checks.append((f"{Fore.YELLOW}[!] {self._bilingual('No internet connection', 'Keine Internet-Verbindung')}", False))

        missing = self.dependency_checker.check_all_dependencies()
        if not missing.get("missing", []):
            checks.append((f"{Fore.GREEN}[✓] {self._bilingual('All dependencies available', 'Alle Abhängigkeiten vorhanden')}", True))
        else:
            checks.append((f"{Fore.YELLOW}[!] {self._bilingual('Missing dependencies', 'Fehlende Abhängigkeiten')}: {len(missing['missing'])}", False))

        self._print(f"\n{Fore.WHITE}┌──────────────────────────────┐")
        self._print(f"{Fore.WHITE}│     SYSTEM CHECK RESULTS     │")
        self._print(f"{Fore.WHITE}├──────────────────────────────┤")
        for check, _passed in checks:
            self._print(f"{Fore.WHITE}│ {check:<40} │")
        self._print(f"{Fore.WHITE}└──────────────────────────────┘")

        if missing.get("missing"):
            self._print(f"\n{Fore.YELLOW}[!] {self._bilingual('Install missing packages:', 'Fehlende Pakete installieren:')}")
            for pkg in missing["missing"]:
                self._print(f"   - {pkg}")
            install = self._input(
                f"\n{Fore.WHITE}[?] {self._bilingual('Install automatically? (y/n)', 'Automatisch installieren? (y/n)')}: "
            ).strip().lower()
            if install == "y":
                self.dependency_checker.install_missing()

        self._sleep(1)
        return True
