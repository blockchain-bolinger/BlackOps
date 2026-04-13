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
    from pydantic import BaseModel, Field, ValidationError

    PYDANTIC_AVAILABLE = True
except Exception:
    PYDANTIC_AVAILABLE = False
    BaseModel = object
    ValidationError = ValueError
    def Field(default=None, default_factory=None):
        if default_factory is not None:
            return default_factory()
        return default


class EncryptionConfig(BaseModel):
    algorithm: str = "AES-256-GCM"
    key_rotation_days: int = 30


class NetworkConfig(BaseModel):
    timeout: int = 30
    max_retries: int = 3
    proxy: Optional[str] = None


class EthicsConfig(BaseModel):
    allowed_targets: list[str] = Field(default_factory=list)
    forbidden_actions: list[str] = Field(default_factory=list)
    require_approval: bool = True


class ObservabilityConfig(BaseModel):
    structured_logging: bool = True
    metrics_enabled: bool = True


class RuntimeConfig(BaseModel):
    worker_threads: int = 4
    task_timeout_seconds: int = 300
    task_retries: int = 1


class SecretConfig(BaseModel):
    provider: str = "file"
    file_path: str = "secrets.json"


class AppConfig(BaseModel):
    version: str = "2.2.0"
    debug: bool = False
    log_level: str = "INFO"
    encryption: EncryptionConfig = Field(default_factory=EncryptionConfig)
    network: NetworkConfig = Field(default_factory=NetworkConfig)
    ethics: EthicsConfig = Field(default_factory=EthicsConfig)
    observability: ObservabilityConfig = Field(default_factory=ObservabilityConfig)
    runtime: RuntimeConfig = Field(default_factory=RuntimeConfig)
    secrets: SecretConfig = Field(default_factory=SecretConfig)


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
            "version": "2.2.0",
            "debug": False,
            "log_level": "INFO",
            "encryption": {"algorithm": "AES-256-GCM", "key_rotation_days": 30},
            "network": {"timeout": 30, "max_retries": 3, "proxy": None},
            "ethics": {"allowed_targets": [], "forbidden_actions": [], "require_approval": True},
            "observability": {"structured_logging": True, "metrics_enabled": True},
            "runtime": {"worker_threads": 4, "task_timeout_seconds": 300, "task_retries": 1},
            "secrets": {"provider": "file", "file_path": "secrets.json"},
        }

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
        file_config = self._load_file_config()
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
