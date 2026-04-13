"""
Verwaltet Secrets getrennt von der allgemeinen Konfiguration.
Reihenfolge: Environment/.env > secrets.json.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional, Any

try:
    from dotenv import load_dotenv
except Exception:
    load_dotenv = None


class SecretsManager:
    def __init__(
        self,
        path: str = "secrets.json",
        env_prefix: str = "BLACKOPS_SECRET_",
        dotenv_path: str = ".env",
    ):
        self.path = Path(path)
        self.env_prefix = env_prefix
        self.dotenv_path = Path(dotenv_path)
        if load_dotenv is not None:
            load_dotenv(dotenv_path=self.dotenv_path, override=False)
        self._secrets = self._load_file_secrets()

    def _load_file_secrets(self) -> dict:
        if not self.path.exists():
            return {}
        try:
            with open(self.path, "r", encoding="utf-8") as handle:
                data = json.load(handle)
                if isinstance(data, dict):
                    return data
        except Exception:
            return {}
        return {}

    def _get_nested(self, data: dict, key: str, default: Any = None) -> Any:
        ref: Any = data
        for part in key.split("."):
            if isinstance(ref, dict) and part in ref:
                ref = ref[part]
            else:
                return default
        return ref

    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        normalized = key.upper().replace(".", "_")
        candidates = [
            f"{self.env_prefix}{normalized}",
            normalized,
        ]
        for env_key in candidates:
            if env_key in os.environ:
                return os.environ[env_key]
        value = self._get_nested(self._secrets, key, default=default)
        if value is default:
            value = self._secrets.get(key, default)
        return value if value is not None else default

    def set(self, key: str, value: str) -> None:
        ref = self._secrets
        parts = key.split(".")
        for part in parts[:-1]:
            if part not in ref or not isinstance(ref[part], dict):
                ref[part] = {}
            ref = ref[part]
        ref[parts[-1]] = value
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as handle:
            json.dump(self._secrets, handle, indent=2)

    def redacted(self) -> dict:
        return {key: "***REDACTED***" for key in self._secrets}
