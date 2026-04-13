import fnmatch
import hashlib
import json
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from core.plugin_manager import PluginInterface


class SecretsLeakCheckPlugin(PluginInterface):
    version = "1.0.0"
    api_version = 1

    DEFAULT_EXCLUDES = {
        ".git",
        "venv",
        "__pycache__",
        ".pytest_cache",
        "node_modules",
        "logs",
        "reports",
        "tmp",
        "backups",
        "data",
    }

    DEFAULT_INCLUDE_GLOBS = (
        "*.py",
        "*.sh",
        "*.ps1",
        "*.env",
        "*.yaml",
        "*.yml",
        "*.json",
        "*.toml",
        "*.ini",
        "*.cfg",
        "*.txt",
        "*.md",
    )

    BASE_PATTERNS = [
        ("private_key_block", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")),
        ("aws_access_key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
        ("openai_like_key", re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b")),
        (
            "generic_secret_assignment",
            re.compile(r"(?i)\b(api[_-]?key|token|secret|password)\b\s*[:=]\s*['\"][^'\"]{8,}['\"]"),
        ),
        ("bearer_token", re.compile(r"(?i)\bbearer\s+[A-Za-z0-9._-]{16,}")),
        ("github_pat", re.compile(r"\bghp_[A-Za-z0-9]{30,}\b")),
    ]
    STRICT_PATTERNS = [
        ("slack_token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b")),
        ("google_api_key", re.compile(r"\bAIza[0-9A-Za-z\-_]{35}\b")),
        ("generic_long_secret", re.compile(r"(?i)\b(secret|token|key)\b[^=\n]{0,20}=\s*['\"][A-Za-z0-9_\-\/+=]{24,}['\"]")),
    ]

    def name(self):
        return "secrets_leak_check"

    def description(self):
        return "Scannt Dateien auf mögliche Secret-Leaks anhand typischer Muster."

    def run(self, **kwargs):
        scan_path = Path(kwargs.get("path", ".")).resolve()
        if not scan_path.exists():
            raise FileNotFoundError(f"Pfad nicht gefunden: {scan_path}")

        max_file_size_kb = int(kwargs.get("max_file_size_kb", 256))
        max_files = int(kwargs.get("max_files", 2000))
        workers = max(1, int(kwargs.get("workers", 1)))
        include_globs = self._split_csv(kwargs.get("include", "")) or list(self.DEFAULT_INCLUDE_GLOBS)
        exclude_names = set(self.DEFAULT_EXCLUDES)
        exclude_names.update(self._split_csv(kwargs.get("exclude", "")))
        respect_gitignore = self._to_bool(kwargs.get("respect_gitignore", "false"))
        fail_on_findings = self._to_bool(kwargs.get("fail_on_findings", "false"))
        exit_code = int(kwargs.get("exit_code", 2))
        rules = self._split_csv(kwargs.get("rules", "default")) or ["default"]
        rules_file = kwargs.get("rules_file")
        baseline_path = kwargs.get("baseline")

        patterns, rules_load_errors = self._resolve_patterns(rules=rules, rules_file=rules_file)
        gitignore_rules = self._load_gitignore(scan_path) if respect_gitignore else []
        files = self._collect_files(
            scan_path=scan_path,
            include_globs=include_globs,
            exclude_names=exclude_names,
            gitignore_rules=gitignore_rules,
            max_files=max_files,
        )

        findings = self._scan_files(
            scan_path=scan_path,
            files=files,
            patterns=patterns,
            max_file_size_kb=max_file_size_kb,
            workers=workers,
        )

        baseline_fingerprints = self._load_baseline(baseline_path)
        filtered_findings = []
        suppressed_count = 0
        for finding in findings:
            if finding["fingerprint"] in baseline_fingerprints:
                suppressed_count += 1
                continue
            filtered_findings.append(finding)

        findings_count = len(filtered_findings)
        ci_failed = bool(fail_on_findings and findings_count > 0)

        result = {
            "path": str(scan_path),
            "scanned_files": len(files),
            "findings_count": findings_count,
            "suppressed_by_baseline": suppressed_count,
            "findings": filtered_findings,
            "limits": {"max_files": max_files, "max_file_size_kb": max_file_size_kb},
            "runtime": {"workers": workers, "respect_gitignore": respect_gitignore},
            "rules": {"selected": rules, "rules_file": rules_file or "", "load_errors": rules_load_errors},
            "ci": {"fail_on_findings": fail_on_findings, "failed": ci_failed, "exit_code": exit_code},
        }

        if self._to_bool(kwargs.get("write_baseline", "false")) and baseline_path:
            all_fingerprints = sorted({f["fingerprint"] for f in findings})
            self._write_baseline(Path(baseline_path), all_fingerprints)
            result["baseline_written"] = str(Path(baseline_path))

        return result

    @staticmethod
    def _split_csv(raw):
        if not raw:
            return []
        return [item.strip() for item in str(raw).split(",") if item.strip()]

    @staticmethod
    def _to_bool(raw):
        return str(raw).strip().lower() in {"1", "true", "yes", "on"}

    @staticmethod
    def _redact(text):
        if len(text) <= 20:
            return "***REDACTED***"
        return f"{text[:8]}***REDACTED***{text[-4:]}"

    def _resolve_patterns(self, rules, rules_file):
        selected = []
        errors = []
        for name in rules:
            lowered = name.lower()
            if lowered == "default":
                selected.extend(self.BASE_PATTERNS)
            elif lowered == "strict":
                selected.extend(self.BASE_PATTERNS)
                selected.extend(self.STRICT_PATTERNS)
            else:
                errors.append(f"Unknown rule set: {name}")

        if rules_file:
            try:
                with Path(rules_file).open("r", encoding="utf-8") as handle:
                    payload = json.load(handle)
                if isinstance(payload, dict):
                    payload = payload.get("rules", [])
                for item in payload:
                    pattern_name = str(item.get("name", "custom_rule"))
                    regex = str(item.get("pattern", ""))
                    flags_raw = str(item.get("flags", ""))
                    flags = re.IGNORECASE if "i" in flags_raw.lower() else 0
                    selected.append((pattern_name, re.compile(regex, flags)))
            except Exception as exc:
                errors.append(f"rules_file_error: {exc}")

        # dedupe by name + regex source
        deduped = []
        seen = set()
        for rule_name, pattern in selected:
            key = (rule_name, pattern.pattern)
            if key in seen:
                continue
            seen.add(key)
            deduped.append((rule_name, pattern))
        return deduped, errors

    @staticmethod
    def _collect_files(scan_path, include_globs, exclude_names, gitignore_rules, max_files):
        collected = []
        for path in scan_path.rglob("*"):
            if len(collected) >= max_files:
                break
            if not path.is_file():
                continue
            rel_path = path.relative_to(scan_path)
            if any(part in exclude_names for part in rel_path.parts):
                continue
            rel_str = str(rel_path)
            if gitignore_rules and any(fnmatch.fnmatch(rel_str, pat) for pat in gitignore_rules):
                continue
            if include_globs and not any(fnmatch.fnmatch(path.name, pat) for pat in include_globs):
                continue
            collected.append(path)
        return collected

    @staticmethod
    def _scan_files(scan_path, files, patterns, max_file_size_kb, workers):
        findings = []

        def scan_one(file_path):
            if file_path.stat().st_size > max_file_size_kb * 1024:
                return []
            try:
                content = file_path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                return []

            local = []
            for line_no, line in enumerate(content.splitlines(), start=1):
                for rule_name, pattern in patterns:
                    if pattern.search(line):
                        line_text = line.strip()
                        fingerprint = hashlib.sha1(
                            f"{file_path}:{line_no}:{rule_name}:{line_text}".encode("utf-8", errors="ignore")
                        ).hexdigest()
                        local.append(
                            {
                                "file": str(file_path.relative_to(scan_path)),
                                "line": line_no,
                                "rule": rule_name,
                                "match_preview": SecretsLeakCheckPlugin._redact(line_text),
                                "fingerprint": fingerprint,
                            }
                        )
                        break
            return local

        if workers == 1:
            for file_path in files:
                findings.extend(scan_one(file_path))
            return findings

        with ThreadPoolExecutor(max_workers=workers) as executor:
            future_to_file = {executor.submit(scan_one, file_path): file_path for file_path in files}
            for future in as_completed(future_to_file):
                findings.extend(future.result())
        return findings

    @staticmethod
    def _load_gitignore(scan_path):
        gitignore = scan_path / ".gitignore"
        if not gitignore.exists():
            return []
        rules = []
        try:
            lines = gitignore.read_text(encoding="utf-8", errors="ignore").splitlines()
        except OSError:
            return []
        for line in lines:
            value = line.strip()
            if not value or value.startswith("#") or value.startswith("!"):
                continue
            if value.endswith("/"):
                rules.append(f"{value}*")
                rules.append(f"*/{value}*")
            else:
                rules.append(value)
                rules.append(f"*/{value}")
        return rules

    @staticmethod
    def _load_baseline(baseline_path):
        if not baseline_path:
            return set()
        path = Path(baseline_path)
        if not path.exists():
            return set()
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return set()
        if isinstance(payload, dict):
            payload = payload.get("fingerprints", [])
        if not isinstance(payload, list):
            return set()
        return {str(item) for item in payload if item}

    @staticmethod
    def _write_baseline(path, fingerprints):
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"fingerprints": fingerprints}
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
