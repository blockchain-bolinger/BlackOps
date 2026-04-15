"""
Shared shell runtime helpers for discovery and policy evaluation.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Optional

from core.plugin_manager import PluginManager
from core.policy_engine import PolicyEngine


class ShellRuntimeService:
    def __init__(
        self,
        *,
        tools_dir: str | Path = "tools",
        plugin_manager: Optional[PluginManager] = None,
        policy_engine: Optional[PolicyEngine] = None,
    ):
        self.tools_dir = Path(tools_dir)
        self.plugin_manager = plugin_manager or PluginManager()
        self.plugin_manager.discover()
        self.policy_engine = policy_engine or PolicyEngine()
        self.tools_cache = self._discover_tools()

    @staticmethod
    def infer_category(tool_path: str | None) -> str | None:
        if not tool_path:
            return None
        parts = Path(tool_path).parts
        for category in ("recon", "offensive", "stealth", "intelligence", "utils", "wireless"):
            if category in parts:
                return category
        return None

    def _discover_tools(self) -> dict[str, str]:
        tools: dict[str, str] = {}
        if not self.tools_dir.exists():
            return tools

        for root, _dirs, files in os.walk(self.tools_dir):
            for file in files:
                if file.endswith(".py") and file != "__init__.py":
                    rel_path = os.path.relpath(os.path.join(root, file), start=self.tools_dir.parent)
                    module_path = rel_path.replace(os.sep, ".")[:-3]
                    tools[rel_path] = module_path
        return tools

    def get_plugin(self, name: str):
        return self.plugin_manager.get_plugin(name)

    def list_plugin_metadata(self):
        return self.plugin_manager.list_plugin_metadata()

    def evaluate_tool_execution(
        self,
        *,
        profile_name: str,
        tool_name: str,
        tool_path: str,
        approved: bool,
        action: str = "tool_execution",
    ):
        return self.policy_engine.evaluate(
            profile_name=profile_name,
            tool_name=tool_name,
            tool_path=tool_path,
            module_category=self.infer_category(tool_path),
            action=action,
            approved=approved,
        )

    def evaluate_plugin_execution(
        self,
        *,
        profile_name: str,
        plugin_name: str,
        approved: bool,
    ):
        return self.policy_engine.evaluate(
            profile_name=profile_name,
            tool_name=plugin_name,
            tool_path=f"plugin:{plugin_name}",
            module_category="plugin",
            action="plugin_execution",
            approved=approved,
        )
