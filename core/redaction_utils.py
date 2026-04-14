"""
Secret redaction helpers for logs, reports, and API responses.
"""

from __future__ import annotations

import re
from typing import Any


REDACTED = "***REDACTED***"
SENSITIVE_KEY_PARTS = {
    "password",
    "passwd",
    "pass",
    "token",
    "secret",
    "api_key",
    "apikey",
    "auth",
    "authorization",
    "cookie",
    "session",
    "private_key",
    "client_secret",
    "key",
}

_KV_PATTERN = re.compile(
    r"(?i)\b(api[_-]?key|token|secret|password|passwd|client[_-]?secret)\b"
    r"(\s*[:=]\s*)(['\"]?)([^'\"\s,;]+)\3"
)
_AUTH_BEARER_HEADER_PATTERN = re.compile(
    r"(?i)\bAuthorization\s*:\s*Bearer\s+[A-Za-z0-9._\-+/=]{8,}"
)
_BEARER_PATTERN = re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._\-+/=]{8,}")


def is_sensitive_key(key: str) -> bool:
    lowered = str(key).strip().lower()
    if not lowered:
        return False
    normalized = lowered.replace("-", "_")
    return any(part in normalized for part in SENSITIVE_KEY_PARTS)


def redact_text(value: str) -> str:
    if not isinstance(value, str):
        return value

    redacted = _AUTH_BEARER_HEADER_PATTERN.sub(f"Authorization: Bearer {REDACTED}", value)
    redacted = _BEARER_PATTERN.sub(f"Bearer {REDACTED}", redacted)
    redacted = _KV_PATTERN.sub(lambda m: f"{m.group(1)}{m.group(2)}{m.group(3)}{REDACTED}{m.group(3)}", redacted)
    return redacted


def redact_data(data: Any) -> Any:
    if isinstance(data, dict):
        sanitized = {}
        for key, value in data.items():
            if is_sensitive_key(str(key)):
                sanitized[key] = REDACTED
            else:
                sanitized[key] = redact_data(value)
        return sanitized
    if isinstance(data, list):
        return [redact_data(item) for item in data]
    if isinstance(data, tuple):
        return tuple(redact_data(item) for item in data)
    if isinstance(data, str):
        return redact_text(data)
    return data
