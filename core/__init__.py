"""
Core modules for configuration, execution, presentation, policy, and runtime support.
"""

from .runtime import ConfigManager, DependencyChecker, RuntimeGuardService, ShellRuntimeService
from .execution import ExecutionService, ProcessRunnerError, SafeProcessRunner, ToolCommandBuilder, DispatchContext, ToolDispatchService
from .presentation import LauncherPresentationService, MenuService, ShellPresentationService
from .reporting import ReportGenerator, SystemReportService
from .registry import BASE_TOOL_REGISTRY, DEFAULT_CATEGORIES, build_tool_registry
from .compat import BlackOpsLogger
from .telemetry import ExecutionTelemetry, TelemetryEvent
from .job_manager import JobManager
from .metrics import MetricsCollector
from .evidence_store import EvidenceStore, EvidenceRecord
from .policy_engine import PolicyEngine, PolicyDecision
from .plugin_manager import PluginManager, PluginInterface
from .secrets_manager import SecretsManager
from .stats_service import StatsService
from .shell_action_service import ShellActionService
from .tool_contract import ToolContext, ToolResult, normalize_tool_result

__all__ = [
    "ConfigManager",
    "DependencyChecker",
    "RuntimeGuardService",
    "ShellRuntimeService",
    "ExecutionService",
    "ProcessRunnerError",
    "SafeProcessRunner",
    "ToolCommandBuilder",
    "DispatchContext",
    "ToolDispatchService",
    "LauncherPresentationService",
    "MenuService",
    "ShellPresentationService",
    "ReportGenerator",
    "SystemReportService",
    "BASE_TOOL_REGISTRY",
    "DEFAULT_CATEGORIES",
    "build_tool_registry",
    "BlackOpsLogger",
    "JobManager",
    "MetricsCollector",
    "EvidenceStore",
    "EvidenceRecord",
    "PolicyEngine",
    "PolicyDecision",
    "PluginManager",
    "PluginInterface",
    "SecretsManager",
    "StatsService",
    "ShellActionService",
    "ExecutionTelemetry",
    "TelemetryEvent",
    "ToolContext",
    "ToolResult",
    "normalize_tool_result",
]
