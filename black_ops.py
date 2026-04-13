#!/usr/bin/env python3
"""
Black Ops Framework - Ultimate Hacking Suite v3.0
NUR FÜR AUTORISIERTE SICHERHEITSTESTS!
"""

import os
import sys
import time
import json
import hashlib
import subprocess
import shutil
from datetime import datetime
from colorama import Fore, Style, init

init(autoreset=True)

# -------------------------------------------------------------------
# Manager-Import mit Fallback (falls Core-Module nicht existieren)
# -------------------------------------------------------------------
try:
    from core.config_manager import ConfigManager
    from core.blackops_logger import BlackOpsLogger
    from core.dependency_checker import DependencyChecker
    from core.plugin_manager import PluginManager
    MANAGER_IMPORT_OK = True
except ImportError as e:
    MANAGER_IMPORT_OK = False
    print(f"{Fore.YELLOW}[WARNUNG] Manager-Module nicht gefunden: {e}")
    print(f"{Fore.YELLOW}Verwende Basis-Modus ohne erweiterte Features...")
    
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
            print("Dependency checker nicht verfügbar. Bitte installiere fehlende Pakete manuell.")
    
    class PluginManager:
        def __init__(self, *args, **kwargs): pass
        def discover(self, *args, **kwargs): return {}
        def list_plugins(self): return []

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
        self.plugins = self.plugin_manager.discover()
        
        # Tool-Registry mit Pfaden UNTER tools/
        self.tools = {
            "1": {
                "name": "Social Hunter V7 (OSINT Framework)",
                "file": "tools/recon/social_hunter_v7.py",
                "sudo": False,
                "category": "recon",
                "description": "Findet Profile, IPs, Telefonnummern und geleakte Passwörter"
            },
            "2": {
                "name": "GhostNet (Anonymity & MAC Changer)",
                "file": "tools/stealth/ghost_net.py",
                "sudo": True,
                "category": "stealth",
                "description": "MAC-Spoofing, Tor-Routing, Identitäts-Check"
            },
            "3": {
                "name": "TraceLess (Log Wiper & Cleaner)",
                "file": "tools/stealth/traceless.py",
                "sudo": True,
                "category": "stealth",
                "description": "Löscht Logs, History und Spuren"
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
                "description": "EXIF-Daten, GPS-Koordinaten, Metadaten"
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
                "description": "GPT-4o KI für Cybersecurity-Beratung"
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
                "description": "Prüft AWS S3, Azure Blob, GCP Buckets auf öffentlichen Zugriff"
            },
            "18": {
                "name": "MobileSpy (App Security Analyzer)",
                "file": "tools/recon/mobilespy.py",
                "sudo": False,
                "category": "recon",
                "description": "APK/IPA Analyse auf Secrets, unsichere Konfigurationen"
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
                "description": ".onion Crawler & Leak Search (Tor erforderlich)"
            },
            "21": {
                "name": "CodeDigger (Secret Scanner)",
                "file": "tools/recon/codedigger.py",
                "sudo": False,
                "category": "recon",
                "description": "GitHub/GitLab nach API-Keys, Passwörtern durchsuchen"
            },
            "22": {
                "name": "MailTracker (Email Security)",
                "file": "tools/recon/mailtracker.py",
                "sudo": False,
                "category": "recon",
                "description": "SPF, DKIM, DMARC, Tracking-Pixel Analyse"
            },
            "23": {
                "name": "LogShield (Log Monitor)",
                "file": "tools/stealth/logshield.py",
                "sudo": True,
                "category": "stealth",
                "description": "Echtzeit-Log-Überwachung mit Alarmfunktion"
            },
            "24": {
                "name": "Decryptor (Encoding Toolkit)",
                "file": "tools/utils/decryptor.py",
                "sudo": False,
                "category": "utils",
                "description": "Base64, ROT13, Hashes, AES, JWT Decoding"
            },
            "13": {
                "name": "System Check & Updates",
                "file": "system_check",
                "sudo": True,
                "category": "utils",
                "description": "System-Status, Updates, Abhängigkeiten prüfen"
            },
            "14": {
                "name": "Report Generator",
                "file": "report_gen",
                "sudo": False,
                "category": "utils",
                "description": "PDF-Reports, Logs exportieren"
            },
            "99": {
                "name": "Exit / Self-Destruct",
                "file": "exit",
                "sudo": False,
                "category": "system",
                "description": "Beendet Framework sicher"
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
        print(f"{Fore.RED}║               ⚠️  WICHTIGE WARNUNG ⚠️                    ║")
        print(f"{Fore.RED}╠══════════════════════════════════════════════════════════╣")
        print(f"{Fore.YELLOW}║  1. NUR für autorisierte Sicherheitstests             ║")
        print(f"{Fore.YELLOW}║  2. NUR auf eigenen Systemen/Laboren                  ║")
        print(f"{Fore.YELLOW}║  3. Deutsche Gesetze beachten (§202a StGB)            ║")
        print(f"{Fore.YELLOW}║  4. KEINE illegalen Aktivitäten                       ║")
        print(f"{Fore.YELLOW}║  5. Verantwortungsvoll nutzen                         ║")
        print(f"{Fore.RED}╚══════════════════════════════════════════════════════════╝")
        if self.config.get("ethics", {}).get("require_confirmation", True):
            consent = input(f"\n{Fore.WHITE}[?] Verstanden und akzeptiert? (ja/NEIN): ").strip().lower()
            if consent != "ja":
                print(f"{Fore.RED}[!] Abbruch. Du musst die Bedingungen akzeptieren.")
                sys.exit(0)
        # Korrektur: info= statt log_action
        self.logger.info("ethical_warning_accepted")
        return True

    def system_check(self):
        print(f"\n{Fore.CYAN}[*] Führe System-Checks durch...")
        checks = []
        if os.geteuid() == 0:
            checks.append((f"{Fore.GREEN}[✓] Root-Privilegien", True))
        else:
            checks.append((f"{Fore.YELLOW}[!] Nicht als Root (manche Tools benötigen sudo)", False))
        python_version = sys.version_info
        if python_version.major >= 3 and python_version.minor >= 8:
            checks.append((f"{Fore.GREEN}[✓] Python {python_version.major}.{python_version.minor}.{python_version.micro}", True))
        else:
            checks.append((f"{Fore.RED}[!] Python 3.8+ benötigt (aktuell: {python_version.major}.{python_version.minor})", False))
        try:
            import requests
            response = requests.get("http://httpbin.org/ip", timeout=5)
            if response.status_code == 200:
                checks.append((f"{Fore.GREEN}[✓] Internet-Verbindung OK", True))
            else:
                checks.append((f"{Fore.YELLOW}[!] Internet-Verbindung eingeschränkt", False))
        except:
            checks.append((f"{Fore.YELLOW}[!] Keine Internet-Verbindung", False))
        missing = self.deps.check_all_dependencies()
        if not missing.get("missing", []):
            checks.append((f"{Fore.GREEN}[✓] Alle Abhängigkeiten vorhanden", True))
        else:
            checks.append((f"{Fore.YELLOW}[!] Fehlende Abhängigkeiten: {len(missing['missing'])}", False))
        print(f"\n{Fore.WHITE}┌──────────────────────────────┐")
        print(f"{Fore.WHITE}│     SYSTEM CHECK RESULTS     │")
        print(f"{Fore.WHITE}├──────────────────────────────┤")
        for check, passed in checks:
            print(f"{Fore.WHITE}│ {check:<40} │")
        print(f"{Fore.WHITE}└──────────────────────────────┘")
        if missing.get("missing"):
            print(f"\n{Fore.YELLOW}[!] Fehlende Pakete installieren:")
            for pkg in missing["missing"]:
                print(f"   - {pkg}")
            install = input(f"\n{Fore.WHITE}[?] Automatisch installieren? (y/n): ").lower()
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
        print(f"{Fore.WHITE}│ Kategorie:   {Fore.GREEN}{tool['category']:<30} {Fore.WHITE}│")
        print(f"{Fore.WHITE}│ Datei:       {Fore.CYAN}{tool['file']:<30} {Fore.WHITE}│")
        print(f"{Fore.WHITE}│ Root nötig:  {Fore.RED if tool['sudo'] else Fore.GREEN}{'Ja' if tool['sudo'] else 'Nein':<30} {Fore.WHITE}│")
        print(f"{Fore.WHITE}│ Beschreibung: {tool['description']:<30} {Fore.WHITE}│")
        print(f"{Fore.CYAN}└──────────────────────────────────────────────────┘")

    def _prompt_required(self, message):
        while True:
            value = input(f"{Fore.WHITE}[?] {message}: ").strip()
            if value:
                return value
            print(f"{Fore.RED}[!] Dieses Feld ist erforderlich.")

    def _append_optional_arg(self, cmd, flag, value):
        if value:
            cmd.extend([flag, value])

    def _build_tool_command(self, tool_id, filename):
        cmd = ["python3", filename]

        # Tools 1-12 bleiben ohne zusätzliche CLI-Argumente.
        if tool_id not in {"15", "16", "17", "18", "19", "20", "21", "22", "23", "24"}:
            return cmd

        if tool_id == "15":  # WebHunter
            target = self._prompt_required("Ziel-URL (z.B. https://example.com)")
            threads = input(f"{Fore.WHITE}[?] Threads (optional): ").strip()
            delay = input(f"{Fore.WHITE}[?] Delay in Sekunden (optional): ").strip()
            output = input(f"{Fore.WHITE}[?] Output JSON (optional): ").strip()
            cmd.append(target)
            self._append_optional_arg(cmd, "--threads", threads)
            self._append_optional_arg(cmd, "--delay", delay)
            self._append_optional_arg(cmd, "--output", output)
            return cmd

        if tool_id == "16":  # SubScout
            target = self._prompt_required("Ziel-Domain (z.B. example.com)")
            threads = input(f"{Fore.WHITE}[?] Threads (optional): ").strip()
            wordlist = input(f"{Fore.WHITE}[?] Wordlist-Pfad (optional): ").strip()
            output = input(f"{Fore.WHITE}[?] Output JSON (optional): ").strip()
            cmd.append(target)
            self._append_optional_arg(cmd, "--threads", threads)
            self._append_optional_arg(cmd, "--wordlist", wordlist)
            self._append_optional_arg(cmd, "--output", output)
            return cmd

        if tool_id == "17":  # CloudRaider
            target = self._prompt_required("Ziel (Bucket/Storage/Domain)")
            aws_profile = input(f"{Fore.WHITE}[?] AWS-Profil (optional): ").strip()
            output = input(f"{Fore.WHITE}[?] Output JSON (optional): ").strip()
            cmd.append(target)
            self._append_optional_arg(cmd, "--aws-profile", aws_profile)
            self._append_optional_arg(cmd, "--output", output)
            return cmd

        if tool_id == "18":  # MobileSpy
            app_file = self._prompt_required("Pfad zur APK/IPA")
            output = input(f"{Fore.WHITE}[?] Output JSON (optional): ").strip()
            cmd.append(app_file)
            self._append_optional_arg(cmd, "--output", output)
            return cmd

        if tool_id == "19":  # CredCannon
            target = self._prompt_required("Ziel-IP/Hostname")
            protocol = self._prompt_required("Protokoll (ssh/ftp/mysql/http)").lower()
            port = input(f"{Fore.WHITE}[?] Port (optional): ").strip()
            userlist = input(f"{Fore.WHITE}[?] Userlist-Pfad (optional): ").strip()
            passlist = input(f"{Fore.WHITE}[?] Passlist-Pfad (optional): ").strip()
            threads = input(f"{Fore.WHITE}[?] Threads (optional): ").strip()
            delay = input(f"{Fore.WHITE}[?] Delay (optional): ").strip()
            cmd.append(target)
            cmd.extend(["--protocol", protocol])
            self._append_optional_arg(cmd, "--port", port)
            self._append_optional_arg(cmd, "--userlist", userlist)
            self._append_optional_arg(cmd, "--passlist", passlist)
            self._append_optional_arg(cmd, "--threads", threads)
            self._append_optional_arg(cmd, "--delay", delay)
            return cmd

        if tool_id == "20":  # DarkWebMonitor
            start_url = self._prompt_required("Start-URL (.onion)")
            depth = input(f"{Fore.WHITE}[?] Crawl-Tiefe (optional): ").strip()
            output = input(f"{Fore.WHITE}[?] Output JSON (optional): ").strip()
            cmd.append(start_url)
            self._append_optional_arg(cmd, "--depth", depth)
            self._append_optional_arg(cmd, "--output", output)
            return cmd

        if tool_id == "21":  # CodeDigger
            query = self._prompt_required("Suchbegriff")
            platform = input(f"{Fore.WHITE}[?] Plattform github/gitlab (optional): ").strip().lower()
            token = input(f"{Fore.WHITE}[?] API-Token (optional): ").strip()
            output = input(f"{Fore.WHITE}[?] Output JSON (optional): ").strip()
            cmd.append(query)
            self._append_optional_arg(cmd, "--platform", platform)
            self._append_optional_arg(cmd, "--token", token)
            self._append_optional_arg(cmd, "--output", output)
            return cmd

        if tool_id == "22":  # MailTracker
            domain = self._prompt_required("Domain")
            header = input(f"{Fore.WHITE}[?] E-Mail-Header-Datei (optional): ").strip()
            cmd.append(domain)
            self._append_optional_arg(cmd, "--header", header)
            return cmd

        if tool_id == "23":  # LogShield
            logs = self._prompt_required("Log-Dateien (kommagetrennt)")
            patterns = input(f"{Fore.WHITE}[?] Suchmuster (kommagetrennt, optional): ").strip()
            alert_cmd = input(f"{Fore.WHITE}[?] Alert-Befehl (optional): ").strip()
            log_items = [entry.strip() for entry in logs.split(",") if entry.strip()]
            if not log_items:
                print(f"{Fore.RED}[!] Keine gültigen Log-Dateien angegeben.")
                return None
            cmd.extend(["--logs"] + log_items)
            if patterns:
                pattern_items = [entry.strip() for entry in patterns.split(",") if entry.strip()]
                if pattern_items:
                    cmd.extend(["--patterns"] + pattern_items)
            self._append_optional_arg(cmd, "--alert-cmd", alert_cmd)
            return cmd

        if tool_id == "24":  # Decryptor
            mode = self._prompt_required("Modus (b64dec/b64enc/rot13/md5/sha256/aesdec/jwt)").lower()
            data = self._prompt_required("Daten")
            key = input(f"{Fore.WHITE}[?] Key (nur für aesdec, optional): ").strip()
            cmd.extend([mode, data])
            self._append_optional_arg(cmd, "--key", key)
            return cmd

        return cmd

    def launch_tool(self, tool_id):
        tool = self.tools.get(tool_id)
        if not tool:
            print(f"{Fore.RED}[!] Ungültige Tool-ID")
            return
        self.show_tool_info(tool_id)
        if tool_id == "13":
            self.system_check()
            return
        elif tool_id == "14":
            self.generate_report()
            return
        elif tool_id == "99":
            self.safe_exit()
            return
        
        filename = tool["file"]
        if filename == "plugin":
            print(f"\n{Fore.GREEN}[*] Starte Plugin: {tool['name']}...")
            self.logger.info(f"launch_plugin: {tool['name']}")
            plugin_name = tool['name'].replace(" (Plugin)", "")
            plugin = self.plugin_manager.get_plugin(plugin_name)
            if plugin:
                params_schema = plugin.get_parameters()
                user_args = {}
                for param, config in params_schema.items():
                    val = input(f"[?] {config['description']} ({param}): ").strip()
                    if val:
                        user_args[param] = val
                
                result = plugin.run(**user_args)
                print(f"\n{Fore.CYAN}Ergebnis: {getattr(result, 'status', 'Unknown')}")
                data = getattr(result, 'data', None)
                if data: print(data)
            return

        # Special cases that aren't paths
        if filename in ["system_check", "report_gen", "exit"]:
            return

        if not os.path.exists(filename):
            print(f"{Fore.RED}[ERROR] '{filename}' nicht gefunden!")
            if not filename.startswith("tools/"):
                alt_filename = os.path.join("tools", filename)
                if os.path.exists(alt_filename):
                    filename = alt_filename
                    print(f"{Fore.YELLOW}[!] Datei gefunden unter: {filename}")
                else:
                    input(f"\n{Fore.RED}[!] Abgebrochen")
                    return
            else:
                input(f"\n{Fore.RED}[!] Abgebrochen")
                return
        
        print(f"\n{Fore.GREEN}[*] Starte {tool['name']}...")
        self.logger.info(f"launch_tool: {tool['name']} ({filename})")
        if tool["sudo"] and os.geteuid() != 0:
            print(f"{Fore.YELLOW}[WARNUNG] Tool benötigt Root-Rechte!")
            print(f"{Fore.YELLOW}[WARNUNG] Starte mit 'sudo python3 {filename}'")
            time.sleep(2)
        try:
            time.sleep(1)
            cmd = self._build_tool_command(tool_id, filename)
            if not cmd:
                return
            if tool["sudo"] and os.geteuid() != 0:
                cmd = ["sudo"] + cmd
            new_env = os.environ.copy()
            new_env["PYTHONPATH"] = os.getcwd()
            process = subprocess.Popen(cmd, env=new_env)
            return_code = process.wait()
            if return_code != 0:
                print(f"{Fore.YELLOW}[WARNUNG] Tool wurde mit Exit-Code {return_code} beendet.")
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}[!] Tool-Ausführung abgebrochen")
        except Exception as e:
            print(f"{Fore.RED}[ERROR] Konnte Tool nicht starten: {e}")
        self.update_stats(tool['name'])

    def generate_report(self):
        print(f"\n{Fore.CYAN}[*] Generiere System-Report...")
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
        report_file = f"blackops_report_{self.session_id}.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"{Fore.GREEN}[✓] Report gespeichert als: {report_file}")
        print(f"\n{Fore.WHITE}┌──────────────────────────────┐")
        print(f"{Fore.WHITE}│      REPORT SUMMARY          │")
        print(f"{Fore.WHITE}├──────────────────────────────┤")
        print(f"{Fore.WHITE}│ Session: {self.session_id:<28} │")
        print(f"{Fore.WHITE}│ Tools verfügbar: {len([k for k in self.tools if k not in ['13','14','99']]):<22} │")
        print(f"{Fore.WHITE}└──────────────────────────────┘")

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
        print(f"\n{Fore.YELLOW}[*] Beende Black Ops Framework...")
        self.logger.info("framework_exit: Session beendet")
        print(f"{Fore.GREEN}[✓] Auf Wiedersehen, @{self.author}")
        sys.exit(0)

    def show_menu(self):
        while True:
            self.print_banner()
            print(f"\n{Fore.WHITE}╔══════════════════════════════════════════════════════════╗")
            print(f"{Fore.WHITE}║                    HAUPTMENÜ                              ║")
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
            choice = input(f"\n{Fore.WHITE}[?] Auswahl: ").strip()
            if choice in self.tools:
                self.launch_tool(choice)
            else:
                print(f"{Fore.RED}[!] Ungültige Auswahl")
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
        print(f"\n{Fore.RED}[!] Abbruch durch Benutzer")
        sys.exit(0)
    except Exception as e:
        print(f"{Fore.RED}[!] Schwerer Fehler: {e}")
        sys.exit(1)
