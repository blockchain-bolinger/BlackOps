#!/usr/bin/env python3
"""
BlackOps Framework – Interaktive Kommandozeile
"""
import cmd
import os
import sys
import importlib
import pkgutil
from pathlib import Path
from core.plugin_manager import PluginManager
from utils.table_formatter import format_table

class BlackOpsShell(cmd.Cmd):
    intro = """
    ██████╗ ██╗      █████╗  ██████╗██╗  ██╗ ██████╗ ██████╗ ███████╗
    ██╔══██╗██║     ██╔══██╗██╔════╝██║ ██╔╝██╔═══██╗██╔══██╗██╔════╝
    ██████╔╝██║     ███████║██║     █████╔╝ ██║   ██║██████╔╝███████╗
    ██╔══██╗██║     ██╔══██║██║     ██╔═██╗ ██║   ██║██╔═══╝ ╚════██║
    ██████╔╝███████╗██║  ██║╚██████╗██║  ██╗╚██████╔╝██║     ███████║
    ╚═════╝ ╚══════╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝ ╚═════╝ ╚═╝     ╚══════╝
    BlackOps Framework v2.2 – Interaktive Shell
    Gib 'help' ein für Hilfe.
    """
    prompt = "BlackOps> "
    current_tool = None
    tool_options = {}

    def __init__(self):
        super().__init__()
        self.tools_cache = self._discover_tools()
        self.plugin_manager = PluginManager()
        self.plugin_manager.discover()

    def _discover_tools(self):
        """Durchsucht tools/ nach Python-Modulen mit main() Funktion."""
        tools = {}
        tools_dir = Path("tools")
        if not tools_dir.exists():
            return tools
        for root, dirs, files in os.walk(tools_dir):
            for file in files:
                if file.endswith(".py") and file != "__init__.py":
                    rel_path = os.path.relpath(os.path.join(root, file), start=".")
                    module_path = rel_path.replace(os.sep, ".")[:-3]
                    tools[rel_path] = module_path
        return tools

    def do_show(self, arg):
        """Zeigt verfügbare Ressourcen: show tools"""
        if arg == "tools":
            print("\nVerfügbare Tools:")
            for path in sorted(self.tools_cache.keys()):
                print(f"  {path}")
        elif arg == "plugins":
            print("\nPlugins:")
            for name, meta in sorted(self.plugin_manager.list_plugin_metadata().items()):
                state = "ok" if meta["compatible"] else f"error: {meta['error']}"
                print(f"  {name} ({meta['version']}) [{state}]")
        else:
            print("Syntax: show tools|plugins")

    def do_use(self, arg):
        """Wählt ein Tool aus: use tools/recon/social_hunter_v7"""
        if not arg:
            print("[-] Bitte Tool-Pfad angeben")
            return
        if arg not in self.tools_cache:
            print(f"[-] Tool '{arg}' nicht gefunden.")
            return
        try:
            module = importlib.import_module(self.tools_cache[arg])
            self.current_tool = module
            self.prompt = f"BlackOps({arg.split('/')[-1]})> "
            print(f"[*] Tool geladen: {arg}")
            self.tool_options = {}
        except Exception as e:
            print(f"[-] Fehler beim Laden: {e}")

    def do_set(self, arg):
        """Setzt eine Option: set LHOST 192.168.1.100"""
        if not self.current_tool:
            print("[-] Kein Tool ausgewählt. use <tool>")
            return
        parts = arg.split()
        if len(parts) != 2:
            print("[-] Syntax: set KEY VALUE")
            return
        key, value = parts
        self.tool_options[key] = value
        print(f"[*] {key} => {value}")

    def do_run(self, arg):
        """Führt das geladene Tool aus: run [--dry-run]"""
        if not self.current_tool:
            print("[-] Kein Tool ausgewählt.")
            return
        dry_run = "--dry-run" in arg
        if dry_run:
            print(f"[DRY-RUN] Würde Tool ausführen: {self.current_tool.__name__}")
            return
        if hasattr(self.current_tool, "main"):
            try:
                self.current_tool.main(self.tool_options)
            except Exception as e:
                print(f"[-] Fehler bei der Ausführung: {e}")
        else:
            print("[-] Das Tool hat keine main()-Funktion.")

    def do_plugin(self, arg):
        """Plugin-Operationen: plugin run <name> [KEY=VALUE ...] [--dry-run]"""
        parts = arg.split()
        if len(parts) < 2 or parts[0] != "run":
            print("Syntax: plugin run <name> [KEY=VALUE ...] [--dry-run]")
            return
        name = parts[1]
        dry_run = "--dry-run" in parts
        kwargs = {}
        for token in parts[2:]:
            if token == "--dry-run" or "=" not in token:
                continue
            key, value = token.split("=", 1)
            kwargs[key] = value
        plugin = self.plugin_manager.get_plugin(name)
        if not plugin:
            print(f"[-] Plugin '{name}' nicht geladen.")
            return
        if dry_run:
            print(f"[DRY-RUN] Würde Plugin ausführen: {name} mit {kwargs}")
            return
        try:
            result = plugin.run(**kwargs)
            if name == "secrets_leak_check" and isinstance(result, dict):
                self._print_secrets_leak_result(result)
            else:
                print(f"[*] Plugin-Resultat: {result}")
        except Exception as e:
            print(f"[-] Plugin-Fehler: {e}")

    def _print_secrets_leak_result(self, result):
        print(
            "[*] Scan abgeschlossen: "
            f"files={result.get('scanned_files', 0)} "
            f"findings={result.get('findings_count', 0)} "
            f"suppressed={result.get('suppressed_by_baseline', 0)}"
        )
        ci = result.get("ci", {})
        if ci.get("failed"):
            print(f"[-] CI-Status: FAILED (exit_code={ci.get('exit_code', 2)})")
        else:
            print("[*] CI-Status: PASS")

        findings = result.get("findings", [])
        if not findings:
            print("[*] Keine Findings.")
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
        print(format_table(["file", "line", "rule", "preview"], rows))
        if len(findings) > 20:
            print(f"[*] Weitere Findings nicht angezeigt: {len(findings) - 20}")

    def do_back(self, arg):
        """Zurück zum Hauptmenü"""
        self.current_tool = None
        self.tool_options = {}
        self.prompt = "BlackOps> "
        print("[*] Zurück zum Hauptmenü.")

    def do_exit(self, arg):
        """Beendet das Framework"""
        print("[+] Auf Wiedersehen!")
        return True

    def default(self, line):
        print(f"Unbekannter Befehl: {line}. Gib 'help' ein.")

if __name__ == "__main__":
    BlackOpsShell().cmdloop()
