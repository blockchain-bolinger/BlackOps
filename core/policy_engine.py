"""
Policy and profile evaluation for BlackOps execution.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from fnmatch import fnmatch
from pathlib import Path
from typing import Any, Dict, Iterable, Optional


DEFAULT_PROFILES: Dict[str, Dict[str, Any]] = {
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
}


def _normalize_patterns(values: Iterable[str]) -> list[str]:
    return [str(value).strip() for value in values if str(value).strip()]


@dataclass
class PolicyDecision:
    allowed: bool
    profile: str
    reason: str
    risk_level: str = "medium"
    approval_required: bool = False
    effective_timeout_seconds: Optional[float] = None
    matched_rules: list[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class PolicyEngine:
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.default_profile = str(
            self.config.get("policy", {}).get("default_profile")
            or "lab"
        )

    def available_profiles(self) -> Dict[str, Dict[str, Any]]:
        profiles = dict(DEFAULT_PROFILES)
        for name, profile in (self.config.get("profiles") or {}).items():
            if isinstance(profile, dict):
                profiles[str(name)] = profile
        return profiles

    def get_profile(self, profile_name: Optional[str] = None) -> Dict[str, Any]:
        profiles = self.available_profiles()
        selected = str(profile_name or self.default_profile)
        profile = profiles.get(selected, profiles["lab"])
        return {
            "name": selected if selected in profiles else "lab",
            **profile,
        }

    @staticmethod
    def classify_risk(module_category: Optional[str], sudo: bool) -> str:
        category = str(module_category or "").lower()
        if category in {"offensive", "stealth"} or sudo:
            return "high"
        if category in {"recon", "plugin"}:
            return "medium"
        return "low"

    @staticmethod
    def _matches_any(value: Optional[str], patterns: Iterable[str]) -> bool:
        if not value:
            return False
        candidate = str(value).strip().lower()
        return any(fnmatch(candidate, pattern.strip().lower()) for pattern in _normalize_patterns(patterns))

    def evaluate(
        self,
        *,
        profile_name: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_path: Optional[str] = None,
        module_category: Optional[str] = None,
        target: Optional[str] = None,
        action: Optional[str] = None,
        sudo: bool = False,
        timeout_seconds: Optional[float] = None,
        approved: Optional[bool] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> PolicyDecision:
        profile = self.get_profile(profile_name)
        matched_rules: list[str] = []
        metadata: Dict[str, Any] = {
            "tool_name": tool_name,
            "tool_path": tool_path,
            "module_category": module_category,
            "target": target,
            "action": action,
            "sudo": sudo,
            "context": context or {},
        }

        risk_level = self.classify_risk(module_category, sudo)
        approval_required = bool(profile.get("require_approval")) or (
            bool(self.config.get("policy", {}).get("require_approval_on_high_risk", True))
            and risk_level == "high"
        )

        allowed_modules = [str(item).lower() for item in profile.get("allowed_modules", [])]
        if allowed_modules and module_category and str(module_category).lower() not in allowed_modules:
            return PolicyDecision(
                allowed=False,
                profile=profile["name"],
                reason=f"module category '{module_category}' is not allowed in profile '{profile['name']}'",
                risk_level=risk_level,
                approval_required=approval_required,
                matched_rules=["module_not_allowed"],
                metadata=metadata,
            )

        if sudo and not bool(profile.get("allow_sudo")):
            return PolicyDecision(
                allowed=False,
                profile=profile["name"],
                reason=f"sudo execution is not allowed in profile '{profile['name']}'",
                risk_level=risk_level,
                approval_required=approval_required,
                matched_rules=["sudo_not_allowed"],
                metadata=metadata,
            )

        forbidden_actions = _normalize_patterns(profile.get("forbidden_actions", []))
        if action and any(str(action).lower() == rule.lower() for rule in forbidden_actions):
            return PolicyDecision(
                allowed=False,
                profile=profile["name"],
                reason=f"action '{action}' is forbidden in profile '{profile['name']}'",
                risk_level=risk_level,
                approval_required=approval_required,
                matched_rules=["action_forbidden"],
                metadata=metadata,
            )

        forbidden_targets = _normalize_patterns(profile.get("forbidden_targets", []))
        if target and self._matches_any(target, forbidden_targets):
            return PolicyDecision(
                allowed=False,
                profile=profile["name"],
                reason=f"target '{target}' is forbidden in profile '{profile['name']}'",
                risk_level=risk_level,
                approval_required=approval_required,
                matched_rules=["target_forbidden"],
                metadata=metadata,
            )

        effective_timeout = timeout_seconds
        max_timeout = profile.get("max_timeout_seconds")
        if isinstance(timeout_seconds, (int, float)) and isinstance(max_timeout, (int, float)) and timeout_seconds > max_timeout:
            effective_timeout = float(max_timeout)
            matched_rules.append("timeout_capped")
        elif timeout_seconds is not None:
            effective_timeout = float(timeout_seconds)

        if approved is False and approval_required:
            return PolicyDecision(
                allowed=False,
                profile=profile["name"],
                reason=f"approval is required for profile '{profile['name']}'",
                risk_level=risk_level,
                approval_required=True,
                effective_timeout_seconds=effective_timeout,
                matched_rules=matched_rules or ["approval_required"],
                metadata=metadata,
            )

        reason = f"profile '{profile['name']}' accepted"
        if "timeout_capped" in matched_rules:
            reason = f"profile '{profile['name']}' accepted; timeout capped to {effective_timeout}s"

        return PolicyDecision(
            allowed=True,
            profile=profile["name"],
            reason=reason,
            risk_level=risk_level,
            approval_required=approval_required,
            effective_timeout_seconds=effective_timeout,
            matched_rules=matched_rules,
            metadata=metadata,
        )

