#!/usr/bin/env python3
"""
Black Ops Framework - Ultimate Hacking Suite v3.0
FOR AUTHORIZED SECURITY TESTING ONLY! (NUR FÜR AUTORISIERTE SICHERHEITSTESTS!)
"""

import os
import sys
import time
import json
import hashlib
import shutil
import subprocess
from datetime import datetime
from colorama import Fore, Style, init
from utils.validation_utils import ValidationUtils

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
    from core.config_manager import ConfigManager
    from core.blackops_logger import BlackOpsLogger
    from core.dependency_checker import DependencyChecker
    from core.execution_service import ExecutionService
    from core.plugin_manager import PluginManager
    from core.process_runner import SafeProcessRunner, ProcessRunnerError
    from core.tool_contract import ToolResult, normalize_tool_result
    MANAGER_IMPORT_OK = True
except ImportError as e:
    MANAGER_IMPORT_OK = False
    print(f"{Fore.YELLOW}[WARNING] Manager modules not found (Manager-Module nicht gefunden): {e}")
    print(f"{Fore.YELLOW}Using basic mode without advanced features (Verwende Basis-Modus ohne erweiterte Features)...")
    
    class ConfigManager:
        def __init__(self, config_file="blackops_config.json"):
            self.config = {"ethics": {"show_warning": True, "require_confirmation": False}, "system": {"auto_check": True}}
        def load_config(self):
            return self.config
    
# Mock removed
    
    class DependencyChecker:
        def check_all_dependencies(self):
            return {"missing": [], "outdated": [], "satisfied": [], "errors": []}
        def check_all(self):
            return self.check_all_dependencies()
        def install_missing(self):
            print("Dependency checker unavailable (Dependency checker nicht verfügbar). Please install missing packages manually (Bitte installiere fehlende Pakete manuell).")
    
    class PluginManager:
        def __init__(self, *args, **kwargs): pass
        def discover(self, *args, **kwargs): return {}
        def list_plugins(self): return []

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

    def normalize_tool_result(result, tool_path):
        if isinstance(result, ToolResult):
            return result
        if isinstance(result, dict):
            return ToolResult.success(data=result, tool_path=tool_path)
        if result is None:
            return ToolResult.success(data=None, tool_path=tool_path)
        return ToolResult.success(data={"result": result}, tool_path=tool_path)

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
        def __init__(self, process_runner=None, base_dir=None, tools_dir=None):
            self.process_runner = process_runner or SafeProcessRunner()

        def execute_command(self, command, timeout=None, env=None, cwd=None, capture_output=False, tool_label="command"):
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
        self.deps = DependencyChecker()
        self.plugin_manager = PluginManager()
        self.process_runner = SafeProcessRunner()
        self.execution_service = ExecutionService(
            process_runner=self.process_runner,
            base_dir=os.getcwd(),
            tools_dir=os.path.join(os.getcwd(), "tools"),
        )
        self.plugins = self.plugin_manager.discover()
        
        # Tool-Registry mit Pfaden UNTER tools/
        self.tools = {
            "1": {
                "name": "Social Hunter V7 (OSINT Framework)",
                "file": "tools/recon/social_hunter_v7.py",
                "sudo": False,
                "category": "recon",
                "description": "Finds profiles, IPs, phone numbers, and leaked passwords (Findet Profile, IPs, Telefonnummern und geleakte Passwörter)"
            },
            "2": {
                "name": "GhostNet (Anonymity & MAC Changer)",
                "file": "tools/stealth/ghost_net.py",
                "sudo": True,
                "category": "stealth",
                "description": "MAC spoofing, Tor routing, identity checks (MAC-Spoofing, Tor-Routing, Identitäts-Check)"
            },
            "3": {
                "name": "TraceLess (Log Wiper & Cleaner)",
                "file": "tools/stealth/traceless.py",
                "sudo": True,
                "category": "stealth",
                "description": "Removes logs, history, and traces (Löscht Logs, History und Spuren)"
            },
            "4": {
                "name": "NetScout Pro (Reconnaissance)",
                "file": "tools/recon/netscout_pro.py",
                "sudo": False,
                "category": "recon",
                "description": "Port-Scanner, DNS-Enumeration, WAF-Detection"
            },
            "5": {
                "name": "MetaSpy (Image Forensics)",
                "file": "tools/recon/metaspy.py",
                "sudo": False,
                "category": "recon",
                "description": "EXIF data, GPS coordinates, metadata (EXIF-Daten, GPS-Koordinaten, Metadaten)"
            },
            "6": {
                "name": "HashBreaker (Password Cracker)",
                "file": "tools/offensive/hashbreaker.py",
                "sudo": False,
                "category": "offensive",
                "description": "Offline Hash-Cracking (MD5, SHA1, SHA256)"
            },
            "7": {
                "name": "SilentPhish (Cloudflare Phishing)",
                "file": "tools/offensive/silent_phish.py",
                "sudo": False,
                "category": "offensive",
                "description": "Phishing-Server mit Cloudflare-Tunnel"
            },
            "8": {
                "name": "VenomMaker (Payload Generator)",
                "file": "tools/offensive/venom_maker.py",
                "sudo": False,
                "category": "offensive",
                "description": "Reverse/Bind Shells, Downloader, Backdoors"
            },
            "9": {
                "name": "NeuroLink (AI Tactical Advisor)",
                "file": "tools/intelligence/neurolink.py",
                "sudo": False,
                "category": "intelligence",
                "description": "GPT-4o AI for cybersecurity guidance (GPT-4o KI für Cybersecurity-Beratung)"
            },
            "10": {
                "name": "AirStrike (WiFi Jammer & Monitor)",
                "file": "tools/offensive/airstrike.py",
                "sudo": True,
                "category": "offensive",
                "description": "WiFi-Monitoring, Deauth-Attacken"
            },
            "11": {
                "name": "NetShark (ARP Spoofer / MITM)",
                "file": "tools/offensive/netshark.py",
                "sudo": True,
                "category": "offensive",
                "description": "ARP-Spoofing, Man-in-the-Middle"
            },
            "12": {
                "name": "CryptoVault (Decoder/Encoder)",
                "file": "tools/utils/cryptovault.py",
                "sudo": False,
                "category": "utils",
                "description": "Base64, Hashes, ROT13, Encoding/Decoding"
            },
            "15": {
                "name": "WebHunter (Web Vulnerability Scanner)",
                "file": "tools/scanner/webhunter.py",
                "sudo": False,
                "category": "offensive",
                "description": "SQLi, XSS, LFI, SSRF, Command Injection Scanner"
            },
            "16": {
                "name": "SubScout (Subdomain Enumeration)",
                "file": "tools/recon/subscout.py",
                "sudo": False,
                "category": "recon",
                "description": "Subdomain Bruteforce, CT Logs, Takeover Check"
            },
            "17": {
                "name": "CloudRaider (Cloud Security Check)",
                "file": "tools/offensive/cloudraider.py",
                "sudo": False,
                "category": "offensive",
                "description": "Checks AWS S3, Azure Blob, and GCP buckets for public access (Prüft AWS S3, Azure Blob, GCP Buckets auf öffentlichen Zugriff)"
            },
            "18": {
                "name": "MobileSpy (App Security Analyzer)",
                "file": "tools/recon/mobilespy.py",
                "sudo": False,
                "category": "recon",
                "description": "Analyzes APK/IPA for secrets and insecure configurations (APK/IPA Analyse auf Secrets, unsichere Konfigurationen)"
            },
            "19": {
                "name": "CredCannon (Brute-Force Suite)",
                "file": "tools/offensive/credcannon.py",
                "sudo": False,
                "category": "offensive",
                "description": "Multi-Protocol Brute-Force (SSH, FTP, MySQL, HTTP Basic)"
            },
            "20": {
                "name": "DarkWebMonitor (Tor Crawler)",
                "file": "tools/intelligence/darkwebmonitor.py",
                "sudo": False,
                "category": "intelligence",
                "description": ".onion crawler and leak search (Tor required / Tor erforderlich)"
            },
            "21": {
                "name": "CodeDigger (Secret Scanner)",
                "file": "tools/recon/codedigger.py",
                "sudo": False,
                "category": "recon",
                "description": "Searches GitHub/GitLab for API keys and passwords (GitHub/GitLab nach API-Keys, Passwörtern durchsuchen)"
            },
            "22": {
                "name": "MailTracker (Email Security)",
                "file": "tools/recon/mailtracker.py",
                "sudo": False,
                "category": "recon",
                "description": "SPF, DKIM, DMARC, tracking pixel analysis (SPF, DKIM, DMARC, Tracking-Pixel Analyse)"
            },
            "23": {
                "name": "LogShield (Log Monitor)",
                "file": "tools/stealth/logshield.py",
                "sudo": True,
                "category": "stealth",
                "description": "Real-time log monitoring with alerts (Echtzeit-Log-Überwachung mit Alarmfunktion)"
            },
            "24": {
                "name": "Decryptor (Encoding Toolkit)",
                "file": "tools/utils/decryptor.py",
                "sudo": False,
                "category": "utils",
                "description": "Base64, ROT13, Hashes, AES, JWT Decoding"
            },
            "25": {
                "name": "OSINT Username (Specialized)",
                "file": "tools/recon/osint_username.py",
                "sudo": False,
                "category": "recon",
                "description": "Focused lookup for username/nickname across configured social sites"
            },
            "26": {
                "name": "OSINT Email (Specialized)",
                "file": "tools/recon/osint_email.py",
                "sudo": False,
                "category": "recon",
                "description": "Focused email intelligence: breach lookup, domain context, search links"
            },
            "27": {
                "name": "OSINT Phone (Specialized)",
                "file": "tools/recon/osint_phone.py",
                "sudo": False,
                "category": "recon",
                "description": "Focused phone-number intelligence with normalized output and pivot links"
            },
            "28": {
                "name": "OSINT IP (Specialized)",
                "file": "tools/recon/osint_ip.py",
                "sudo": False,
                "category": "recon",
                "description": "Focused IP intelligence: geodata, reverse DNS, open-source pivots"
            },
            "29": {
                "name": "OSINT Domain (Specialized)",
                "file": "tools/recon/osint_domain.py",
                "sudo": False,
                "category": "recon",
                "description": "Focused domain intelligence: DNS, RDAP and certificate-based subdomains"
            },
            "30": {
                "name": "OSINT Person (First + Last Name)",
                "file": "tools/recon/osint_person.py",
                "sudo": False,
                "category": "recon",
                "description": "Focused person lookup using first and last name with pivot generation"
            },
            "13": {
                "name": "System Check & Updates",
                "file": "system_check",
                "sudo": True,
                "category": "utils",
                "description": "Checks system status, updates, and dependencies (System-Status, Updates, Abhängigkeiten prüfen)"
            },
            "14": {
                "name": "Report Generator",
                "file": "report_gen",
                "sudo": False,
                "category": "utils",
                "description": "Exports PDF reports and logs (PDF-Reports, Logs exportieren)"
            },
            "99": {
                "name": "Exit / Self-Destruct",
                "file": "exit",
                "sudo": False,
                "category": "system",
                "description": "Safely exits the framework (Beendet Framework sicher)"
            }
        }
        
        # Plugins hinzufügen
        plugin_id = 100
        for name, instance in self.plugins.items():
            self.tools[str(plugin_id)] = {
                "name": f"{name} (Plugin)",
                "file": "plugin",
                "sudo": False,
                "category": "utils",
                "description": instance.description()
            }
            plugin_id += 1
        
        self.categories = {
            "recon": "🔍 RECON & OSINT",
            "offensive": "⚔️ OFFENSIVE & NETWORK",
            "stealth": "👻 STEALTH & UTILS",
            "intelligence": "🧠 INTELLIGENCE",
            "utils": "🛠️ SYSTEM & UTILS",
            "system": "🚪 SYSTEM"
        }

    # -------------------------------------------------------------------
    # Hilfsfunktionen
    # -------------------------------------------------------------------
    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def _bilingual(self, english, german):
        return f"{english} ({german})"

    def print_banner(self):
        self.clear_screen()
        width = shutil.get_terminal_size((100, 30)).columns
        logo_lines = [
            "██████╗ ██╗      █████╗  ██████╗██╗  ██╗ ██████╗ ██████╗ ███████╗",
            "██╔══██╗██║     ██╔══██╗██╔════╝██║ ██╔╝██╔═══██╗██╔══██╗██╔════╝",
            "██████╔╝██║     ███████║██║     █████╔╝ ██║   ██║██████╔╝███████╗",
            "██╔══██╗██║     ██╔══██║██║     ██╔═██╗ ██║   ██║██╔═══╝ ╚════██║",
            "██████╔╝███████╗██║  ██║╚██████╗██║  ██╗╚██████╔╝██║     ███████║",
            "╚═════╝ ╚══════╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝ ╚═════╝ ╚═╝     ╚══════╝",
        ]

        print()
        for line in logo_lines:
            print(f"{Fore.RED}{line.center(width)}")
        print(f"{Fore.WHITE}{f'>> BLACKOPS v{self.version} <<'.center(width)}")
        print(f"{Fore.YELLOW}{('-' * 43).center(width)}")
        print(f"{Fore.CYAN}{f'Session ID: {self.session_id}'.center(width)}")
        print(f"{Fore.WHITE}{f'Operator: @{self.author}'.center(width)}")
        print(f"{Fore.YELLOW}{datetime.now().strftime('%Y-%m-%d %H:%M:%S').center(width)}")

    def ethical_warning(self):
        if not self.config.get("ethics", {}).get("show_warning", True):
            return True
        print(f"\n{Fore.RED}╔══════════════════════════════════════════════════════════╗")
        print(f"{Fore.RED}║    ⚠️  IMPORTANT WARNING (WICHTIGE WARNUNG) ⚠️          ║")
        print(f"{Fore.RED}╠══════════════════════════════════════════════════════════╣")
        print(f"{Fore.YELLOW}║  1. Authorized tests only (Nur autorisierte Tests)    ║")
        print(f"{Fore.YELLOW}║  2. Only on owned/lab systems (Nur eigene/Lab-Systeme)║")
        print(f"{Fore.YELLOW}║  3. Follow local laws (Lokale Gesetze beachten)       ║")
        print(f"{Fore.YELLOW}║  4. No illegal activity (Keine illegalen Aktivitäten) ║")
        print(f"{Fore.YELLOW}║  5. Use responsibly (Verantwortungsvoll nutzen)       ║")
        print(f"{Fore.RED}╚══════════════════════════════════════════════════════════╝")
        if self.config.get("ethics", {}).get("require_confirmation", True):
            consent = input(
                f"\n{Fore.WHITE}[?] {self._bilingual('Understood and accepted? (yes/no)', 'Verstanden und akzeptiert? (ja/nein)')}: "
            ).strip().lower()
            if consent not in {"yes", "y", "ja", "j"}:
                print(f"{Fore.RED}[!] {self._bilingual('Aborted. You must accept the terms.', 'Abbruch. Du musst die Bedingungen akzeptieren.')}")
                sys.exit(0)
        # Korrektur: info= statt log_action
        self.logger.info("ethical_warning_accepted")
        return True

    def system_check(self):
        print(f"\n{Fore.CYAN}[*] {self._bilingual('Running system checks...', 'Führe System-Checks durch...')}")
        checks = []
        if os.geteuid() == 0:
            checks.append((f"{Fore.GREEN}[✓] {self._bilingual('Root privileges', 'Root-Privilegien')}", True))
        else:
            checks.append((f"{Fore.YELLOW}[!] {self._bilingual('Not running as root (some tools need sudo)', 'Nicht als Root (manche Tools benötigen sudo)')}", False))
        python_version = sys.version_info
        if python_version.major >= 3 and python_version.minor >= 8:
            checks.append((f"{Fore.GREEN}[✓] Python {python_version.major}.{python_version.minor}.{python_version.micro}", True))
        else:
            checks.append((f"{Fore.RED}[!] {self._bilingual('Python 3.8+ required', 'Python 3.8+ benötigt')} (current/aktuell: {python_version.major}.{python_version.minor})", False))
        try:
            import requests
            response = requests.get("http://httpbin.org/ip", timeout=5)
            if response.status_code == 200:
                checks.append((f"{Fore.GREEN}[✓] {self._bilingual('Internet connection OK', 'Internet-Verbindung OK')}", True))
            else:
                checks.append((f"{Fore.YELLOW}[!] {self._bilingual('Internet connection limited', 'Internet-Verbindung eingeschränkt')}", False))
        except:
            checks.append((f"{Fore.YELLOW}[!] {self._bilingual('No internet connection', 'Keine Internet-Verbindung')}", False))
        missing = self.deps.check_all_dependencies()
        if not missing.get("missing", []):
            checks.append((f"{Fore.GREEN}[✓] {self._bilingual('All dependencies available', 'Alle Abhängigkeiten vorhanden')}", True))
        else:
            checks.append((f"{Fore.YELLOW}[!] {self._bilingual('Missing dependencies', 'Fehlende Abhängigkeiten')}: {len(missing['missing'])}", False))
        print(f"\n{Fore.WHITE}┌──────────────────────────────┐")
        print(f"{Fore.WHITE}│     SYSTEM CHECK RESULTS     │")
        print(f"{Fore.WHITE}├──────────────────────────────┤")
        for check, passed in checks:
            print(f"{Fore.WHITE}│ {check:<40} │")
        print(f"{Fore.WHITE}└──────────────────────────────┘")
        if missing.get("missing"):
            print(f"\n{Fore.YELLOW}[!] {self._bilingual('Install missing packages:', 'Fehlende Pakete installieren:')}")
            for pkg in missing["missing"]:
                print(f"   - {pkg}")
            install = input(f"\n{Fore.WHITE}[?] {self._bilingual('Install automatically? (y/n)', 'Automatisch installieren? (y/n)')}: ").lower()
            if install == 'y':
                self.deps.install_missing()
        time.sleep(1)
        return True

    def show_tool_info(self, tool_id):
        tool = self.tools.get(tool_id)
        if not tool:
            return
        print(f"\n{Fore.CYAN}┌──────────────────────────────────────────────────┐")
        print(f"{Fore.CYAN}│            TOOL INFORMATION                     │")
        print(f"{Fore.CYAN}├──────────────────────────────────────────────────┤")
        print(f"{Fore.WHITE}│ Name:        {Fore.YELLOW}{tool['name']:<30} {Fore.WHITE}│")
        print(f"{Fore.WHITE}│ Category (Kategorie): {Fore.GREEN}{tool['category']}{Fore.WHITE}")
        print(f"{Fore.WHITE}│ File (Datei): {Fore.CYAN}{tool['file']}{Fore.WHITE}")
        print(f"{Fore.WHITE}│ Root required (Root nötig): {Fore.RED if tool['sudo'] else Fore.GREEN}{'Yes (Ja)' if tool['sudo'] else 'No (Nein)'}{Fore.WHITE}")
        print(f"{Fore.WHITE}│ Description (Beschreibung): {tool['description']}")
        print(f"{Fore.CYAN}└──────────────────────────────────────────────────┘")

    def _prompt_required(self, message):
        return self._prompt_validated(
            message=message,
            validator=ValidationUtils.validate_non_empty,
            error_message=self._bilingual("This field is required.", "Dieses Feld ist erforderlich."),
        )

    def _prompt_validated(self, message, validator, error_message, normalizer=None):
        while True:
            value = input(f"{Fore.WHITE}[?] {message}: ").strip()
            candidate = normalizer(value) if normalizer else value
            if validator(candidate):
                return candidate
            print(f"{Fore.RED}[!] {error_message}")

    def _prompt_optional(self, message, validator=None, error_message=None, normalizer=None):
        while True:
            value = input(f"{Fore.WHITE}[?] {message}: ").strip()
            if not value:
                return ""
            candidate = normalizer(value) if normalizer else value
            if validator is None or validator(candidate):
                return candidate
            print(
                f"{Fore.RED}[!] "
                f"{error_message or self._bilingual('Invalid value.', 'Ungültiger Wert.')}"
            )

    def _append_optional_arg(self, cmd, flag, value):
        if value:
            cmd.extend([flag, value])

    def _build_tool_command(self, tool_id, filename):
        cmd = ["python3", filename]

        # Tools 1-12 stay without additional CLI arguments.
        if tool_id not in {"15", "16", "17", "18", "19", "20", "21", "22", "23", "24"}:
            return cmd

        if tool_id == "15":  # WebHunter
            target = self._prompt_validated(
                message=self._bilingual("Target URL (e.g. https://example.com)", "Ziel-URL (z.B. https://example.com)"),
                validator=ValidationUtils.validate_url,
                error_message=self._bilingual("Please enter a valid http/https URL.", "Bitte eine gültige http/https URL eingeben."),
            )
            threads = self._prompt_optional(
                message=self._bilingual("Threads (optional)", "Threads (optional)"),
                validator=ValidationUtils.validate_positive_int,
                error_message=self._bilingual("Threads must be a positive integer.", "Threads müssen eine positive Ganzzahl sein."),
            )
            delay = self._prompt_optional(
                message=self._bilingual("Delay in seconds (optional)", "Delay in Sekunden (optional)"),
                validator=ValidationUtils.validate_non_negative_float,
                error_message=self._bilingual("Delay must be a non-negative number.", "Delay muss eine nicht-negative Zahl sein."),
            )
            output = self._prompt_optional(self._bilingual("Output JSON (optional)", "Output JSON (optional)"))
            cmd.append(target)
            self._append_optional_arg(cmd, "--threads", threads)
            self._append_optional_arg(cmd, "--delay", delay)
            self._append_optional_arg(cmd, "--output", output)
            return cmd

        if tool_id == "16":  # SubScout
            target = self._prompt_validated(
                message=self._bilingual("Target domain (e.g. example.com)", "Ziel-Domain (z.B. example.com)"),
                validator=ValidationUtils.validate_domain,
                error_message=self._bilingual("Please enter a valid domain.", "Bitte eine gültige Domain eingeben."),
            )
            threads = self._prompt_optional(
                message=self._bilingual("Threads (optional)", "Threads (optional)"),
                validator=ValidationUtils.validate_positive_int,
                error_message=self._bilingual("Threads must be a positive integer.", "Threads müssen eine positive Ganzzahl sein."),
            )
            wordlist = self._prompt_optional(
                message=self._bilingual("Wordlist path (optional)", "Wordlist-Pfad (optional)"),
                validator=ValidationUtils.validate_optional_existing_file,
                error_message=self._bilingual("Wordlist file not found.", "Wordlist-Datei nicht gefunden."),
            )
            output = self._prompt_optional(self._bilingual("Output JSON (optional)", "Output JSON (optional)"))
            cmd.append(target)
            self._append_optional_arg(cmd, "--threads", threads)
            self._append_optional_arg(cmd, "--wordlist", wordlist)
            self._append_optional_arg(cmd, "--output", output)
            return cmd

        if tool_id == "17":  # CloudRaider
            target = self._prompt_validated(
                message=self._bilingual("Target (bucket/storage/domain)", "Ziel (Bucket/Storage/Domain)"),
                validator=ValidationUtils.validate_cloud_target,
                error_message=self._bilingual("Please enter a valid cloud target.", "Bitte ein gültiges Cloud-Target eingeben."),
            )
            aws_profile = self._prompt_optional(self._bilingual("AWS profile (optional)", "AWS-Profil (optional)"))
            output = self._prompt_optional(self._bilingual("Output JSON (optional)", "Output JSON (optional)"))
            cmd.append(target)
            self._append_optional_arg(cmd, "--aws-profile", aws_profile)
            self._append_optional_arg(cmd, "--output", output)
            return cmd

        if tool_id == "18":  # MobileSpy
            app_file = self._prompt_validated(
                message=self._bilingual("Path to APK/IPA", "Pfad zur APK/IPA"),
                validator=lambda value: ValidationUtils.validate_existing_file(value, allowed_exts=(".apk", ".ipa")),
                error_message=self._bilingual("Please provide an existing .apk or .ipa file.", "Bitte eine vorhandene .apk- oder .ipa-Datei angeben."),
            )
            output = self._prompt_optional(self._bilingual("Output JSON (optional)", "Output JSON (optional)"))
            cmd.append(app_file)
            self._append_optional_arg(cmd, "--output", output)
            return cmd

        if tool_id == "19":  # CredCannon
            target = self._prompt_validated(
                message=self._bilingual("Target IP/hostname", "Ziel-IP/Hostname"),
                validator=ValidationUtils.validate_hostname_or_ip,
                error_message=self._bilingual("Please enter a valid IP or hostname.", "Bitte eine gültige IP oder Hostname eingeben."),
            )
            protocol = self._prompt_validated(
                message=self._bilingual("Protocol (ssh/ftp/mysql/http)", "Protokoll (ssh/ftp/mysql/http)"),
                validator=lambda value: ValidationUtils.validate_choice(value, ["ssh", "ftp", "mysql", "http"]),
                error_message=self._bilingual("Allowed protocols: ssh, ftp, mysql, http.", "Erlaubte Protokolle: ssh, ftp, mysql, http."),
                normalizer=lambda value: value.lower(),
            )
            port = self._prompt_optional(
                message=self._bilingual("Port (optional)", "Port (optional)"),
                validator=ValidationUtils.validate_port,
                error_message=self._bilingual("Port must be between 1 and 65535.", "Port muss zwischen 1 und 65535 liegen."),
            )
            userlist = self._prompt_optional(
                message=self._bilingual("Userlist path (optional)", "Userlist-Pfad (optional)"),
                validator=ValidationUtils.validate_optional_existing_file,
                error_message=self._bilingual("Userlist file not found.", "Userlist-Datei nicht gefunden."),
            )
            passlist = self._prompt_optional(
                message=self._bilingual("Passlist path (optional)", "Passlist-Pfad (optional)"),
                validator=ValidationUtils.validate_optional_existing_file,
                error_message=self._bilingual("Passlist file not found.", "Passlist-Datei nicht gefunden."),
            )
            threads = self._prompt_optional(
                message=self._bilingual("Threads (optional)", "Threads (optional)"),
                validator=ValidationUtils.validate_positive_int,
                error_message=self._bilingual("Threads must be a positive integer.", "Threads müssen eine positive Ganzzahl sein."),
            )
            delay = self._prompt_optional(
                message=self._bilingual("Delay (optional)", "Delay (optional)"),
                validator=ValidationUtils.validate_non_negative_float,
                error_message=self._bilingual("Delay must be a non-negative number.", "Delay muss eine nicht-negative Zahl sein."),
            )
            cmd.append(target)
            cmd.extend(["--protocol", protocol])
            self._append_optional_arg(cmd, "--port", port)
            self._append_optional_arg(cmd, "--userlist", userlist)
            self._append_optional_arg(cmd, "--passlist", passlist)
            self._append_optional_arg(cmd, "--threads", threads)
            self._append_optional_arg(cmd, "--delay", delay)
            return cmd

        if tool_id == "20":  # DarkWebMonitor
            start_url = self._prompt_validated(
                message=self._bilingual("Start URL (.onion)", "Start-URL (.onion)"),
                validator=ValidationUtils.validate_onion_url,
                error_message=self._bilingual("Please enter a valid .onion URL.", "Bitte eine gültige .onion-URL eingeben."),
                normalizer=ValidationUtils.normalize_onion_url,
            )
            depth = self._prompt_optional(
                message=self._bilingual("Crawl depth (optional)", "Crawl-Tiefe (optional)"),
                validator=ValidationUtils.validate_positive_int,
                error_message=self._bilingual("Depth must be a positive integer.", "Tiefe muss eine positive Ganzzahl sein."),
            )
            output = self._prompt_optional(self._bilingual("Output JSON (optional)", "Output JSON (optional)"))
            cmd.append(start_url)
            self._append_optional_arg(cmd, "--depth", depth)
            self._append_optional_arg(cmd, "--output", output)
            return cmd

        if tool_id == "21":  # CodeDigger
            query = self._prompt_required(self._bilingual("Search term", "Suchbegriff"))
            platform = self._prompt_optional(
                message=self._bilingual("Platform github/gitlab (optional)", "Plattform github/gitlab (optional)"),
                validator=lambda value: ValidationUtils.validate_choice(value, ["github", "gitlab"]),
                error_message=self._bilingual("Allowed platforms: github, gitlab.", "Erlaubte Plattformen: github, gitlab."),
                normalizer=lambda value: value.lower(),
            )
            token = self._prompt_optional(self._bilingual("API token (optional)", "API-Token (optional)"))
            output = self._prompt_optional(self._bilingual("Output JSON (optional)", "Output JSON (optional)"))
            cmd.append(query)
            self._append_optional_arg(cmd, "--platform", platform)
            self._append_optional_arg(cmd, "--token", token)
            self._append_optional_arg(cmd, "--output", output)
            return cmd

        if tool_id == "22":  # MailTracker
            domain = self._prompt_validated(
                message=self._bilingual("Domain", "Domain"),
                validator=ValidationUtils.validate_domain,
                error_message=self._bilingual("Please enter a valid domain.", "Bitte eine gültige Domain eingeben."),
            )
            header = self._prompt_optional(
                message=self._bilingual("Email header file (optional)", "E-Mail-Header-Datei (optional)"),
                validator=ValidationUtils.validate_optional_existing_file,
                error_message=self._bilingual("Header file not found.", "Header-Datei nicht gefunden."),
            )
            cmd.append(domain)
            self._append_optional_arg(cmd, "--header", header)
            return cmd

        if tool_id == "23":  # LogShield
            logs = self._prompt_validated(
                message=self._bilingual("Log files (comma-separated)", "Log-Dateien (kommagetrennt)"),
                validator=ValidationUtils.validate_csv_file_list,
                error_message=self._bilingual("Please provide existing log files, comma-separated.", "Bitte vorhandene Log-Dateien kommasepariert angeben."),
            )
            patterns = self._prompt_optional(
                self._bilingual("Search patterns (comma-separated, optional)", "Suchmuster (kommagetrennt, optional)")
            )
            alert_cmd = self._prompt_optional(self._bilingual("Alert command (optional)", "Alert-Befehl (optional)"))
            log_items = ValidationUtils.parse_csv(logs)
            cmd.extend(["--logs"] + log_items)
            if patterns:
                pattern_items = ValidationUtils.parse_csv(patterns)
                if pattern_items:
                    cmd.extend(["--patterns"] + pattern_items)
            self._append_optional_arg(cmd, "--alert-cmd", alert_cmd)
            return cmd

        if tool_id == "24":  # Decryptor
            mode = self._prompt_validated(
                message=self._bilingual("Mode (b64dec/b64enc/rot13/md5/sha256/aesdec/jwt)", "Modus (b64dec/b64enc/rot13/md5/sha256/aesdec/jwt)"),
                validator=lambda value: ValidationUtils.validate_choice(
                    value,
                    ["b64dec", "b64enc", "rot13", "md5", "sha256", "aesdec", "jwt"],
                ),
                error_message=self._bilingual(
                    "Allowed modes: b64dec, b64enc, rot13, md5, sha256, aesdec, jwt.",
                    "Erlaubte Modi: b64dec, b64enc, rot13, md5, sha256, aesdec, jwt.",
                ),
                normalizer=lambda value: value.lower(),
            )
            data = self._prompt_required(self._bilingual("Data", "Daten"))
            key = self._prompt_optional(self._bilingual("Key (only for aesdec, optional)", "Key (nur für aesdec, optional)"))
            cmd.extend([mode, data])
            self._append_optional_arg(cmd, "--key", key)
            return cmd

        return cmd

    def launch_tool(self, tool_id):
        tool = self.tools.get(tool_id)
        if not tool:
            print(f"{Fore.RED}[!] {self._bilingual('Invalid tool ID', 'Ungültige Tool-ID')}")
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
            print(f"\n{Fore.GREEN}[*] {self._bilingual('Starting plugin', 'Starte Plugin')}: {tool['name']}...")
            self.logger.info(f"launch_plugin: {tool['name']}")
            plugin_name = tool['name'].replace(" (Plugin)", "")
            plugin = self.plugin_manager.get_plugin(plugin_name)
            if not plugin:
                print(f"{Fore.RED}[ERROR] {self._bilingual('Plugin not loaded', 'Plugin nicht geladen')}: {plugin_name}")
                return ToolResult.failed("Plugin not loaded", plugin=plugin_name)

            params_schema = plugin.get_parameters()
            user_args = {}
            for param, config in params_schema.items():
                val = input(f"[?] {config['description']} ({param}): ").strip()
                if val:
                    user_args[param] = val

            raw_result = plugin.run(**user_args)
            result = normalize_tool_result(raw_result, f"plugin:{plugin_name}")
            print(f"\n{Fore.CYAN}{self._bilingual('Result', 'Ergebnis')}: {result.status}")
            if result.data is not None:
                print(result.data)
            if result.status == "success":
                self.update_stats(tool['name'])
            return result

        # Special cases that aren't paths
        if filename in ["system_check", "report_gen", "exit"]:
            return

        if not os.path.exists(filename):
            print(f"{Fore.RED}[ERROR] '{filename}' {self._bilingual('not found', 'nicht gefunden')}!")
            if not filename.startswith("tools/"):
                alt_filename = os.path.join("tools", filename)
                if os.path.exists(alt_filename):
                    filename = alt_filename
                    print(f"{Fore.YELLOW}[!] {self._bilingual('File found at', 'Datei gefunden unter')}: {filename}")
                else:
                    input(f"\n{Fore.RED}[!] {self._bilingual('Aborted', 'Abgebrochen')}")
                    return ToolResult.failed("Tool file not found", file=filename)
            else:
                input(f"\n{Fore.RED}[!] {self._bilingual('Aborted', 'Abgebrochen')}")
                return ToolResult.failed("Tool file not found", file=filename)
        
        print(f"\n{Fore.GREEN}[*] {self._bilingual('Starting', 'Starte')} {tool['name']}...")
        self.logger.info(f"launch_tool: {tool['name']} ({filename})")
        if tool["sudo"] and os.geteuid() != 0:
            print(f"{Fore.YELLOW}[WARNING] {self._bilingual('Tool requires root privileges!', 'Tool benötigt Root-Rechte!')}")
            print(f"{Fore.YELLOW}[WARNING] {self._bilingual('Start with', 'Starte mit')} 'sudo python3 {filename}'")
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
            tool_result = self.execution_service.execute_command(
                cmd,
                timeout=timeout_seconds,
                env=new_env,
                cwd=os.getcwd(),
                capture_output=False,
                tool_label=tool['name'],
            )
            details = tool_result.data if isinstance(tool_result.data, dict) else {}
            if details.get("timed_out"):
                print(
                    f"{Fore.YELLOW}[WARNING] "
                    f"{self._bilingual('Tool execution timed out', 'Tool-Ausführung hat das Zeitlimit überschritten')}."
                )
            elif tool_result.status == "failed" and details.get("returncode") is not None:
                print(
                    f"{Fore.YELLOW}[WARNING] "
                    f"{self._bilingual('Tool exited with code', 'Tool wurde mit Exit-Code')} {details.get('returncode')}."
                )
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}[!] {self._bilingual('Tool execution interrupted', 'Tool-Ausführung abgebrochen')}")
            tool_result = ToolResult.failed("Tool execution interrupted", tool=tool['name'])
        except ProcessRunnerError as e:
            print(f"{Fore.RED}[ERROR] {self._bilingual('Blocked unsafe command', 'Unsicherer Befehl blockiert')}: {e}")
            tool_result = ToolResult.failed(str(e), tool=tool['name'])
        except Exception as e:
            print(f"{Fore.RED}[ERROR] {self._bilingual('Could not start tool', 'Konnte Tool nicht starten')}: {e}")
            tool_result = ToolResult.failed(str(e), tool=tool['name'])
        if tool_result.status == "success":
            self.update_stats(tool['name'])
        return tool_result

    def generate_report(self):
        print(f"\n{Fore.CYAN}[*] {self._bilingual('Generating system report...', 'Generiere System-Report...')}")
        try:
            report = {
                "timestamp": datetime.now().isoformat(),
                "session_id": self.session_id,
                "system": {
                    "platform": sys.platform,
                    "python_version": sys.version,
                    "user": os.getlogin() if hasattr(os, 'getlogin') else "N/A",
                    "is_root": os.geteuid() == 0
                },
                "tools": {k: v["name"] for k, v in self.tools.items() if k not in ["13", "14", "99"]},
                "config": self.config
            }
            report = redact_data(report)
            report_file = f"blackops_report_{self.session_id}.json"
            with open(report_file, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            print(f"{Fore.GREEN}[✓] {self._bilingual('Report saved as', 'Report gespeichert als')}: {report_file}")
            print(f"\n{Fore.WHITE}┌──────────────────────────────┐")
            print(f"{Fore.WHITE}│      REPORT SUMMARY          │")
            print(f"{Fore.WHITE}├──────────────────────────────┤")
            print(f"{Fore.WHITE}│ Session: {self.session_id:<28} │")
            print(f"{Fore.WHITE}│ Tools available (Tools verfügbar): {len([k for k in self.tools if k not in ['13','14','99']]):<4} │")
            print(f"{Fore.WHITE}└──────────────────────────────┘")
            self.update_stats("Report Generator")
            return ToolResult.success(data={"report_file": report_file, "session_id": self.session_id})
        except Exception as e:
            print(f"{Fore.RED}[ERROR] {self._bilingual('Could not generate report', 'Konnte Report nicht generieren')}: {e}")
            return ToolResult.failed(str(e), action="generate_report")

    def update_stats(self, tool_name):
        stats_file = "blackops_stats.json"
        stats = {}
        if os.path.exists(stats_file):
            with open(stats_file, "r") as f:
                stats = json.load(f)
        stats[tool_name] = stats.get(tool_name, 0) + 1
        stats["last_run"] = datetime.now().isoformat()
        with open(stats_file, "w") as f:
            json.dump(stats, f, indent=2)

    def safe_exit(self):
        print(f"\n{Fore.YELLOW}[*] {self._bilingual('Exiting Black Ops Framework...', 'Beende Black Ops Framework...')}")
        self.logger.info("framework_exit: Session ended")
        print(f"{Fore.GREEN}[✓] {self._bilingual('Goodbye', 'Auf Wiedersehen')}, @{self.author}")
        sys.exit(0)

    def show_menu(self):
        while True:
            self.print_banner()
            print(f"\n{Fore.WHITE}╔══════════════════════════════════════════════════════════╗")
            print(f"{Fore.WHITE}║            MAIN MENU (HAUPTMENÜ)                         ║")
            print(f"{Fore.WHITE}╠══════════════════════════════════════════════════════════╣")
            cats = {}
            for tid, tool in self.tools.items():
                if tid in ["13", "14", "99"]:
                    continue
                cat = tool["category"]
                cats.setdefault(cat, []).append((tid, tool))
            for cat, items in cats.items():
                print(f"{Fore.CYAN}│ {self.categories.get(cat, cat.upper())}")
                for tid, tool in items:
                    print(f"{Fore.WHITE}│   {tid}. {Fore.GREEN}{tool['name']}")
            print(f"{Fore.WHITE}│")
            print(f"{Fore.YELLOW}│ 13. System Check & Updates")
            print(f"{Fore.YELLOW}│ 14. Report Generator")
            print(f"{Fore.RED}│ 99. Exit / Self-Destruct")
            print(f"{Fore.WHITE}╚══════════════════════════════════════════════════════════╝")
            choice = input(f"\n{Fore.WHITE}[?] {self._bilingual('Selection', 'Auswahl')}: ").strip()
            if choice in self.tools:
                self.launch_tool(choice)
            else:
                print(f"{Fore.RED}[!] {self._bilingual('Invalid selection', 'Ungültige Auswahl')}")
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
