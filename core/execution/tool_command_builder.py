"""
Interactive command construction for tool-specific CLI flows.
"""

from __future__ import annotations

from typing import Callable, Optional

from utils.validation_utils import ValidationUtils


class ToolCommandBuilder:
    def __init__(self, bilingual: Callable[[str, str], str], input_func: Callable[[str], str] = input):
        self._bilingual = bilingual
        self._input = input_func

    def _prompt_required(self, message: str) -> str:
        return self._prompt_validated(
            message=message,
            validator=ValidationUtils.validate_non_empty,
            error_message=self._bilingual("This field is required.", "Dieses Feld ist erforderlich."),
        )

    def _prompt_validated(
        self,
        message: str,
        validator: Callable[[str], bool],
        error_message: str,
        normalizer: Optional[Callable[[str], str]] = None,
    ) -> str:
        while True:
            value = self._input(f"[?] {message}: ").strip()
            candidate = normalizer(value) if normalizer else value
            if validator(candidate):
                return candidate
            print(f"[!] {error_message}")

    def _prompt_optional(
        self,
        message: str,
        validator: Optional[Callable[[str], bool]] = None,
        error_message: Optional[str] = None,
        normalizer: Optional[Callable[[str], str]] = None,
    ) -> str:
        while True:
            value = self._input(f"[?] {message}: ").strip()
            if not value:
                return ""
            candidate = normalizer(value) if normalizer else value
            if validator is None or validator(candidate):
                return candidate
            print(f"[!] {error_message or self._bilingual('Invalid value.', 'Ungültiger Wert.')}")

    @staticmethod
    def _append_optional_arg(cmd: list[str], flag: str, value: str) -> None:
        if value:
            cmd.extend([flag, value])

    def build_tool_command(self, tool_id: str, filename: str) -> list[str]:
        cmd = ["python3", filename]

        if tool_id not in {"15", "16", "17", "18", "19", "20", "21", "22", "23", "24"}:
            return cmd

        if tool_id == "15":
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

        if tool_id == "16":
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

        if tool_id == "17":
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

        if tool_id == "18":
            app_file = self._prompt_validated(
                message=self._bilingual("Path to APK/IPA", "Pfad zur APK/IPA"),
                validator=lambda value: ValidationUtils.validate_existing_file(value, allowed_exts=(".apk", ".ipa")),
                error_message=self._bilingual("Please provide an existing .apk or .ipa file.", "Bitte eine vorhandene .apk- oder .ipa-Datei angeben."),
            )
            output = self._prompt_optional(self._bilingual("Output JSON (optional)", "Output JSON (optional)"))
            cmd.append(app_file)
            self._append_optional_arg(cmd, "--output", output)
            return cmd

        if tool_id == "19":
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

        if tool_id == "20":
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

        if tool_id == "21":
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

        if tool_id == "22":
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

        if tool_id == "23":
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

        if tool_id == "24":
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
