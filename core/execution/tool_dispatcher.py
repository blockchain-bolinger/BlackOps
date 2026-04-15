"""
Dispatch helper for running registered tools and plugins.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Optional

from core.execution_service import ExecutionService
from core.policy_engine import PolicyEngine
from core.tool_contract import ToolResult, normalize_tool_result


@dataclass
class DispatchContext:
    tool_id: str
    tool_name: str
    tool_path: str
    category: str
    sudo: bool
    approved: bool
    profile_name: str
    correlation_id: str


class ToolDispatchService:
    def __init__(
        self,
        *,
        execution_service: ExecutionService,
        plugin_manager: Any,
        policy_engine: PolicyEngine,
        update_stats: Optional[Callable[[str], None]] = None,
        logger: Any = None,
    ):
        self.execution_service = execution_service
        self.plugin_manager = plugin_manager
        self.policy_engine = policy_engine
        self.update_stats = update_stats
        self.logger = logger

    def _log_info(self, message: str) -> None:
        if self.logger is not None and hasattr(self.logger, "info"):
            self.logger.info(message)

    def execute_plugin(
        self,
        *,
        plugin_name: str,
        display_name: str,
        user_args: dict[str, Any],
        profile_name: str,
        approved: bool,
    ) -> ToolResult:
        plugin = self.plugin_manager.get_plugin(plugin_name)
        if not plugin:
            return ToolResult.failed("Plugin not loaded", plugin=plugin_name)

        decision = self.policy_engine.evaluate(
            profile_name=profile_name,
            tool_name=plugin_name,
            tool_path=f"plugin:{plugin_name}",
            module_category="plugin",
            action="plugin_execution",
            approved=approved,
        )
        if not decision.allowed:
            return ToolResult.failed(decision.reason, plugin=plugin_name, error_type="policy")

        raw_result = plugin.run(**user_args)
        result = normalize_tool_result(raw_result, f"plugin:{plugin_name}")
        if result.status == "success" and self.update_stats is not None:
            self.update_stats(display_name)
        return result

    def execute_tool(
        self,
        *,
        context: DispatchContext,
        command: list[str],
        env: dict[str, str],
        cwd: str,
        timeout_seconds: Optional[float],
    ) -> ToolResult:
        self._log_info(f"launch_tool: {context.tool_name} ({context.tool_path})")
        result = self.execution_service.execute_command(
            command,
            timeout=timeout_seconds,
            env=env,
            cwd=cwd,
            capture_output=False,
            tool_label=context.tool_name,
            profile_name=context.profile_name,
            module_category=context.category,
            action="tool_execution",
            target=context.tool_name,
            approved=context.approved,
            correlation_id=context.correlation_id,
        )
        if result.status == "success" and self.update_stats is not None:
            self.update_stats(context.tool_name)
        return result
