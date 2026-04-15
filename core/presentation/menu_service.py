"""
Main menu rendering for the BlackOps launcher.
"""

from __future__ import annotations

from typing import Any, Callable, Dict

from colorama import Fore


class MenuService:
    def __init__(
        self,
        *,
        bilingual: Callable[[str, str], str],
        print_func: Callable[..., None] = print,
    ):
        self._bilingual = bilingual
        self._print = print_func

    def render(self, *, tools: Dict[str, Dict[str, Any]], categories: Dict[str, str]) -> None:
        self._print(f"\n{Fore.WHITE}╔══════════════════════════════════════════════════════════╗")
        self._print(f"{Fore.WHITE}║            MAIN MENU (HAUPTMENÜ)                         ║")
        self._print(f"{Fore.WHITE}╠══════════════════════════════════════════════════════════╣")

        grouped: dict[str, list[tuple[str, Dict[str, Any]]]] = {}
        for tid, tool in tools.items():
            if tid in ["13", "14", "99"]:
                continue
            grouped.setdefault(tool["category"], []).append((tid, tool))

        for category, items in grouped.items():
            self._print(f"{Fore.CYAN}│ {categories.get(category, category.upper())}")
            for tid, tool in items:
                self._print(f"{Fore.WHITE}│   {tid}. {Fore.GREEN}{tool['name']}")

        self._print(f"{Fore.WHITE}│")
        self._print(f"{Fore.YELLOW}│ 13. System Check & Updates")
        self._print(f"{Fore.YELLOW}│ 14. Report Generator")
        self._print(f"{Fore.RED}│ 99. Exit / Self-Destruct")
        self._print(f"{Fore.WHITE}╚══════════════════════════════════════════════════════════╝")
