#!/usr/bin/env python3
"""
Centralized validation helpers for user-supplied values.
"""

from __future__ import annotations

import ipaddress
import os
import re
from urllib.parse import urlparse


class ValidationUtils:
    _DOMAIN_LABEL_RE = re.compile(r"^(?!-)[A-Za-z0-9-]{1,63}(?<!-)$")
    _BUCKET_RE = re.compile(r"^[a-z0-9][a-z0-9.-]{1,61}[a-z0-9]$")

    @staticmethod
    def validate_non_empty(value: str) -> bool:
        return bool(value and value.strip())

    @staticmethod
    def validate_positive_int(value: str) -> bool:
        try:
            return int(value) > 0
        except Exception:
            return False

    @staticmethod
    def validate_non_negative_float(value: str) -> bool:
        try:
            return float(value) >= 0
        except Exception:
            return False

    @staticmethod
    def validate_port(value: str) -> bool:
        try:
            port = int(value)
            return 1 <= port <= 65535
        except Exception:
            return False

    @staticmethod
    def validate_choice(value: str, choices: list[str], case_insensitive: bool = True) -> bool:
        if case_insensitive:
            normalized = {choice.lower() for choice in choices}
            return value.lower() in normalized
        return value in set(choices)

    @staticmethod
    def validate_ip(value: str) -> bool:
        try:
            ipaddress.ip_address(value)
            return True
        except Exception:
            return False

    @staticmethod
    def validate_domain(value: str) -> bool:
        candidate = value.strip().lower().rstrip(".")
        if not candidate or len(candidate) > 253:
            return False
        parts = candidate.split(".")
        if len(parts) < 2:
            return False
        return all(ValidationUtils._DOMAIN_LABEL_RE.match(part) for part in parts)

    @staticmethod
    def validate_hostname_or_ip(value: str) -> bool:
        if not value:
            return False
        lowered = value.strip().lower()
        return lowered == "localhost" or ValidationUtils.validate_ip(lowered) or ValidationUtils.validate_domain(lowered)

    @staticmethod
    def validate_url(value: str, allow_onion: bool = False) -> bool:
        if not value:
            return False
        parsed = urlparse(value.strip())
        if parsed.scheme not in {"http", "https"}:
            return False
        host = (parsed.hostname or "").lower()
        if not host:
            return False
        if allow_onion and host.endswith(".onion"):
            return True
        return ValidationUtils.validate_hostname_or_ip(host)

    @staticmethod
    def validate_onion_url(value: str) -> bool:
        return ValidationUtils.validate_url(value, allow_onion=True) and (urlparse(value.strip()).hostname or "").lower().endswith(".onion")

    @staticmethod
    def normalize_onion_url(value: str) -> str:
        candidate = value.strip()
        if candidate.startswith("http://") or candidate.startswith("https://"):
            return candidate
        return f"http://{candidate}"

    @staticmethod
    def validate_cloud_target(value: str) -> bool:
        candidate = value.strip().lower()
        if ValidationUtils.validate_hostname_or_ip(candidate):
            return True
        return bool(ValidationUtils._BUCKET_RE.match(candidate))

    @staticmethod
    def validate_existing_file(path: str, allowed_exts: tuple[str, ...] | None = None) -> bool:
        if not path:
            return False
        if not os.path.isfile(path):
            return False
        if not allowed_exts:
            return True
        return path.lower().endswith(tuple(ext.lower() for ext in allowed_exts))

    @staticmethod
    def validate_optional_existing_file(path: str, allowed_exts: tuple[str, ...] | None = None) -> bool:
        if not path:
            return True
        return ValidationUtils.validate_existing_file(path, allowed_exts=allowed_exts)

    @staticmethod
    def parse_csv(value: str) -> list[str]:
        return [item.strip() for item in value.split(",") if item.strip()]

    @staticmethod
    def validate_csv_file_list(value: str) -> bool:
        entries = ValidationUtils.parse_csv(value)
        if not entries:
            return False
        return all(os.path.isfile(entry) for entry in entries)
