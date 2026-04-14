"""
Configuration Manager für Black Ops Framework.
Layering: defaults -> file -> env. Secrets separat über SecretsManager.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

from core.secrets_manager import SecretsManager

try:
    from pydantic import BaseModel, ConfigDict, Field, ValidationError

    PYDANTIC_AVAILABLE = True
except Exception:
    PYDANTIC_AVAILABLE = False
    BaseModel = object
    ConfigDict = None
    ValidationError = ValueError
    def Field(default=None, default_factory=None):
        if default_factory is not None:
            return default_factory()
        return default


class ConfigBaseModel(BaseModel):
    if PYDANTIC_AVAILABLE:
        model_config = ConfigDict(extra="allow")


class EncryptionConfig(ConfigBaseModel):
    algorithm: str = "AES-256-GCM"
    key_rotation_days: int = 30


class FrameworkConfig(ConfigBaseModel):
    name: str = "Black Ops Framework v3.0"
    version: str = "3.0.0"
    author: str = "Security Team"
    license: str = "MIT - For Authorized Testing Only"


class LoggingConfig(ConfigBaseModel):
    level: str = "INFO"
    file: str = "logs/framework/blackops_main.log"
    max_size_mb: int = 100
    backup_count: int = 5
    audit_log: str = "logs/audit/audit.log"


class SecurityConfig(ConfigBaseModel):
    encryption_enabled: bool = True
    audit_trail: bool = True
    auto_delete_temp: bool = True
    session_timeout_minutes: int = 30


class NetworkConfig(ConfigBaseModel):
    timeout: int = 30
    max_retries: int = 3
    proxy: Optional[str] = None
    # Legacy-compatible fields still used by existing configs.
    default_ports: str = "1-1000"
    scan_timeout: int = 5
    max_threads: int = 100
    rate_limit_requests_per_second: int = 10


class EthicsConfig(ConfigBaseModel):
    show_warning: bool = True
    require_confirmation: bool = True
    require_agreement: bool = True
    check_target_authorization: bool = True
    log_all_actions: bool = True
    max_scan_duration_hours: int = 24
    allowed_targets: list[str] = Field(default_factory=list)
    forbidden_actions: list[str] = Field(default_factory=list)
    require_approval: bool = True


class ObservabilityConfig(ConfigBaseModel):
    structured_logging: bool = True
    metrics_enabled: bool = True


class RuntimeConfig(ConfigBaseModel):
    worker_threads: int = 4
    task_timeout_seconds: int = 300
    task_retries: int = 1


class SecretConfig(ConfigBaseModel):
    provider: str = "file"
    file_path: str = "secrets.json"


class ReportingConfig(ConfigBaseModel):
    default_format: str = "pdf"
    auto_generate: bool = True
    template: str = "data/templates/report_templates/pentest_report.md"


class ModuleConfig(ConfigBaseModel):
    enabled: bool = True
    require_confirmation: bool = False


class OffensiveModuleConfig(ModuleConfig):
    require_confirmation: bool = True


class ModulesConfig(ConfigBaseModel):
    recon: ModuleConfig = Field(default_factory=ModuleConfig)
    offensive: ModuleConfig = Field(default_factory=OffensiveModuleConfig)
    stealth: ModuleConfig = Field(default_factory=ModuleConfig)
    intelligence: ModuleConfig = Field(default_factory=ModuleConfig)


class AppConfig(ConfigBaseModel):
    version: str = "3.0.0"
    debug: bool = False
    log_level: str = "INFO"
    framework: FrameworkConfig = Field(default_factory=FrameworkConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)
    encryption: EncryptionConfig = Field(default_factory=EncryptionConfig)
    network: NetworkConfig = Field(default_factory=NetworkConfig)
    ethics: EthicsConfig = Field(default_factory=EthicsConfig)
    reporting: ReportingConfig = Field(default_factory=ReportingConfig)
    modules: ModulesConfig = Field(default_factory=ModulesConfig)
    observability: ObservabilityConfig = Field(default_factory=ObservabilityConfig)
    runtime: RuntimeConfig = Field(default_factory=RuntimeConfig)
    secrets: SecretConfig = Field(default_factory=SecretConfig)
    # Policy/profile data is intentionally left extensible so profile presets can evolve
    # without forcing a schema migration on every iteration.
    policy: dict = Field(default_factory=dict)
    profiles: dict = Field(default_factory=dict)


class ConfigManager:
    def __init__(self, config_path: str = "blackops_config.json", env_prefix: str = "BLACKOPS__"):
        self.config_path = Path(config_path)
        self.env_prefix = env_prefix
        self.errors: list[str] = []
        self.config = self._load_config()
        secret_path = self.get("secrets.file_path", "secrets.json")
        self.secrets = SecretsManager(path=secret_path)

    def _default_config(self) -> Dict[str, Any]:
        if PYDANTIC_AVAILABLE:
            return AppConfig().model_dump()
        return {
            "version": "3.0.0",
            "debug": False,
            "log_level": "INFO",
            "framework": {
                "name": "Black Ops Framework v3.0",
                "version": "3.0.0",
                "author": "Security Team",
                "license": "MIT - For Authorized Testing Only",
            },
            "logging": {
                "level": "INFO",
                "file": "logs/framework/blackops_main.log",
                "max_size_mb": 100,
                "backup_count": 5,
                "audit_log": "logs/audit/audit.log",
            },
            "security": {
                "encryption_enabled": True,
                "audit_trail": True,
                "auto_delete_temp": True,
                "session_timeout_minutes": 30,
            },
            "encryption": {"algorithm": "AES-256-GCM", "key_rotation_days": 30},
            "network": {
                "timeout": 30,
                "max_retries": 3,
                "proxy": None,
                "default_ports": "1-1000",
                "scan_timeout": 5,
                "max_threads": 100,
                "rate_limit_requests_per_second": 10,
            },
            "ethics": {
                "show_warning": True,
                "require_confirmation": True,
                "require_agreement": True,
                "check_target_authorization": True,
                "log_all_actions": True,
                "max_scan_duration_hours": 24,
                "allowed_targets": [],
                "forbidden_actions": [],
                "require_approval": True,
            },
            "reporting": {
                "default_format": "pdf",
                "auto_generate": True,
                "template": "data/templates/report_templates/pentest_report.md",
            },
            "modules": {
                "recon": {"enabled": True, "require_confirmation": False},
                "offensive": {"enabled": True, "require_confirmation": True},
                "stealth": {"enabled": True, "require_confirmation": False},
                "intelligence": {"enabled": True, "require_confirmation": False},
            },
            "observability": {"structured_logging": True, "metrics_enabled": True},
            "runtime": {"worker_threads": 4, "task_timeout_seconds": 300, "task_retries": 1},
            "secrets": {"provider": "file", "file_path": "secrets.json"},
            "policy": {
                "default_profile": "lab",
                "telemetry_enabled": True,
                "require_approval_on_high_risk": True,
            },
            "profiles": {
                "lab": {
                    "description": "Unrestricted local lab profile for controlled test systems.",
                    "allowed_modules": ["recon", "intelligence", "utils", "offensive", "stealth", "web", "plugin"],
                    "allow_sudo": True,
                    "require_approval": False,
                    "max_timeout_seconds": 600,
                    "forbidden_targets": [],
                    "forbidden_actions": [],
                },
                "osint": {
                    "description": "Restricted collection profile for passive reconnaissance and intelligence gathering.",
                    "allowed_modules": ["recon", "intelligence", "utils", "plugin"],
                    "allow_sudo": False,
                    "require_approval": True,
                    "max_timeout_seconds": 300,
                    "forbidden_targets": ["*.gov", "*.mil"],
                    "forbidden_actions": ["service_disruption", "credential_attack"],
                },
                "pentest": {
                    "description": "Authorized pentest profile with higher scrutiny and explicit approval.",
                    "allowed_modules": ["recon", "offensive", "stealth", "utils", "plugin"],
                    "allow_sudo": True,
                    "require_approval": True,
                    "max_timeout_seconds": 300,
                    "forbidden_targets": ["*.gov", "*.mil"],
                    "forbidden_actions": ["data_destruction", "ransomware", "identity_theft"],
                },
                "audit": {
                    "description": "Evidence-focused audit and validation profile.",
                    "allowed_modules": ["recon", "utils", "plugin"],
                    "allow_sudo": False,
                    "require_approval": True,
                    "max_timeout_seconds": 180,
                    "forbidden_targets": ["*.gov", "*.mil"],
                    "forbidden_actions": ["service_disruption", "credential_attack", "data_destruction"],
                },
                "training": {
                    "description": "Training and demo profile for guided exercises.",
                    "allowed_modules": ["recon", "intelligence", "utils", "plugin"],
                    "allow_sudo": False,
                    "require_approval": False,
                    "max_timeout_seconds": 120,
                    "forbidden_targets": ["*.gov", "*.mil"],
                    "forbidden_actions": ["service_disruption", "credential_attack", "data_destruction"],
                },
                "demo": {
                    "description": "Low-risk demo profile for presentations and walkthroughs.",
                    "allowed_modules": ["recon", "intelligence", "utils", "plugin"],
                    "allow_sudo": False,
                    "require_approval": False,
                    "max_timeout_seconds": 90,
                    "forbidden_targets": ["*.gov", "*.mil"],
                    "forbidden_actions": ["service_disruption", "credential_attack", "data_destruction"],
                },
            },
        }

    def _normalize_legacy_config(self, file_config: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(file_config, dict):
            return {}

        normalized = dict(file_config)

        framework = normalized.get("framework")
        if isinstance(framework, dict):
            if "version" not in normalized and framework.get("version"):
                normalized["version"] = framework["version"]

        logging_cfg = normalized.get("logging")
        if isinstance(logging_cfg, dict):
            if "log_level" not in normalized and logging_cfg.get("level"):
                normalized["log_level"] = logging_cfg["level"]

        security_cfg = normalized.get("security")
        network_cfg = normalized.get("network")
        if not isinstance(network_cfg, dict):
            network_cfg = {}
        if "timeout" not in network_cfg and "scan_timeout" in network_cfg:
            network_cfg["timeout"] = network_cfg["scan_timeout"]
        if "max_retries" not in network_cfg:
            network_cfg["max_retries"] = 3
        normalized["network"] = network_cfg

        runtime_cfg = normalized.get("runtime")
        if not isinstance(runtime_cfg, dict):
            runtime_cfg = {}
        if "worker_threads" not in runtime_cfg and isinstance(network_cfg.get("max_threads"), int):
            runtime_cfg["worker_threads"] = network_cfg["max_threads"]
        if (
            "task_timeout_seconds" not in runtime_cfg
            and isinstance(security_cfg, dict)
            and isinstance(security_cfg.get("session_timeout_minutes"), int)
        ):
            runtime_cfg["task_timeout_seconds"] = security_cfg["session_timeout_minutes"] * 60
        normalized["runtime"] = runtime_cfg

        ethics_cfg = normalized.get("ethics")
        if not isinstance(ethics_cfg, dict):
            ethics_cfg = {}
        modules_cfg = normalized.get("modules")
        if isinstance(modules_cfg, dict):
            offensive_cfg = modules_cfg.get("offensive")
            if isinstance(offensive_cfg, dict) and "require_confirmation" in offensive_cfg:
                ethics_cfg.setdefault("require_confirmation", offensive_cfg["require_confirmation"])
        if "require_approval" not in ethics_cfg and "require_agreement" in ethics_cfg:
            ethics_cfg["require_approval"] = bool(ethics_cfg["require_agreement"])
        normalized["ethics"] = ethics_cfg

        return normalized

    def _load_file_config(self) -> Dict[str, Any]:
        if not self.config_path.exists():
            return {}
        with open(self.config_path, "r", encoding="utf-8") as handle:
            if self.config_path.suffix == ".json":
                return json.load(handle)
            if self.config_path.suffix in [".yaml", ".yml"]:
                return yaml.safe_load(handle) or {}
        return {}

    def _parse_env_value(self, value: str) -> Any:
        low = value.lower()
        if low == "true":
            return True
        if low == "false":
            return False
        if low == "null":
            return None
        try:
            if "." in value:
                return float(value)
            return int(value)
        except ValueError:
            pass
        try:
            return json.loads(value)
        except Exception:
            return value

    def _load_env_overrides(self) -> Dict[str, Any]:
        env_config: Dict[str, Any] = {}
        for key, value in os.environ.items():
            if not key.startswith(self.env_prefix):
                continue
            rel_key = key[len(self.env_prefix):].lower()
            path = rel_key.split("__")
            ref = env_config
            for part in path[:-1]:
                ref = ref.setdefault(part, {})
            ref[path[-1]] = self._parse_env_value(value)
        return env_config

    def _merge_dicts(self, base: Dict[str, Any], incoming: Dict[str, Any]) -> Dict[str, Any]:
        result = dict(base)
        for key, value in incoming.items():
            if isinstance(value, dict) and isinstance(result.get(key), dict):
                result[key] = self._merge_dicts(result[key], value)
            else:
                result[key] = value
        return result

    def _validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        self.errors = []
        if PYDANTIC_AVAILABLE:
            try:
                return AppConfig.model_validate(data).model_dump()
            except ValidationError as exc:
                self.errors = [str(exc)]
                return data
        required_keys = ["version", "ethics", "network"]
        missing = [key for key in required_keys if key not in data]
        if missing:
            self.errors.append(f"Missing required keys: {', '.join(missing)}")
        return data

    def _load_config(self) -> Dict[str, Any]:
        defaults = self._default_config()
        file_config = self._normalize_legacy_config(self._load_file_config())
        env_config = self._load_env_overrides()
        merged = self._merge_dicts(defaults, file_config)
        merged = self._merge_dicts(merged, env_config)
        return self._validate(merged)

    def get(self, key: str, default: Any = None) -> Any:
        keys = key.split(".")
        value: Any = self.config
        for item in keys:
            if isinstance(value, dict) and item in value:
                value = value[item]
            else:
                return default
        return value

    def set(self, key: str, value: Any) -> None:
        keys = key.split(".")
        ref = self.config
        for item in keys[:-1]:
            if item not in ref or not isinstance(ref[item], dict):
                ref[item] = {}
            ref = ref[item]
        ref[keys[-1]] = value
        self.config = self._validate(self.config)
        self._save_config()

    def get_secret(self, key: str, default: Optional[str] = None) -> Optional[str]:
        return self.secrets.get(key, default=default)

    def validate(self) -> bool:
        _ = self._validate(self.config)
        return len(self.errors) == 0

    def as_model(self) -> AppConfig | Dict[str, Any]:
        if PYDANTIC_AVAILABLE:
            return AppConfig.model_validate(self.config)
        return dict(self.config)

    def snapshot(self) -> Dict[str, Any]:
        return json.loads(json.dumps(self.config))

    def lint(self) -> Dict[str, Any]:
        """Strikte Konfigurationsprüfung mit Warnungen."""
        valid = self.validate()
        warnings: list[str] = []

        timeout = self.get("network.timeout", 30)
        retries = self.get("network.max_retries", 3)
        workers = self.get("runtime.worker_threads", 4)
        log_level = str(self.get("log_level", "INFO")).upper()

        if isinstance(timeout, (int, float)) and timeout > 120:
            warnings.append("network.timeout is high (>120s)")
        if isinstance(retries, int) and retries > 10:
            warnings.append("network.max_retries is high (>10)")
        if isinstance(workers, int) and workers > 32:
            warnings.append("runtime.worker_threads is high (>32)")
        if log_level not in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}:
            warnings.append(f"log_level '{log_level}' is non-standard")

        return {"valid": valid, "errors": list(self.errors), "warnings": warnings}

    def doctor(self) -> Dict[str, Any]:
        """Umgebungsdiagnose für Konfiguration/Secrets/Dateisystem."""
        checks = {}
        checks["config_file_exists"] = self.config_path.exists()
        checks["config_file_writable"] = os.access(self.config_path.parent if self.config_path.exists() else ".", os.W_OK)

        secrets_path = Path(self.get("secrets.file_path", "secrets.json"))
        checks["secrets_file_exists"] = secrets_path.exists()

        openai = self.get_secret("openai_key")
        checks["openai_key_configured"] = bool(openai and "SET_" not in str(openai))
        checks["config_valid"] = self.validate()

        status = "ok" if all(bool(v) for v in checks.values()) else "warn"
        return {"status": status, "checks": checks, "errors": list(self.errors)}

    def migrate(self, target_version: Optional[str] = None, dry_run: bool = False) -> Dict[str, Any]:
        """
        Migriert Konfiguration auf aktuelles Defaults-Schema.
        - ergänzt fehlende Keys
        - aktualisiert Versionsfeld
        """
        current = dict(self.config)
        defaults = self._default_config()
        merged = self._merge_dicts(defaults, current)

        to_version = target_version or defaults.get("version", current.get("version", "2.2.0"))
        merged["version"] = to_version

        changed = merged != current
        result = {
            "changed": changed,
            "from_version": current.get("version"),
            "to_version": to_version,
            "dry_run": dry_run,
        }
        if changed and not dry_run:
            self.config = self._validate(merged)
            self._save_config()
        return result

    def _save_config(self) -> None:
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, "w", encoding="utf-8") as handle:
            if self.config_path.suffix == ".json":
                json.dump(self.config, handle, indent=2)
            elif self.config_path.suffix in [".yaml", ".yml"]:
                yaml.safe_dump(self.config, handle, default_flow_style=False)
