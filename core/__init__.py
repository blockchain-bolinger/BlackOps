"""
Core-Module des Frameworks.
Enthält essentielle Komponenten für Konfiguration, Logging, Ethik und Session-Management.
"""

from .config_manager import ConfigManager
from .job_manager import JobManager
from .metrics import MetricsCollector
from .plugin_manager import PluginManager, PluginInterface
from .report_generator import ReportGenerator
from .secrets_manager import SecretsManager
from .tool_contract import ToolContext, ToolResult, normalize_tool_result

__all__ = [
    "ConfigManager",
    "JobManager",
    "MetricsCollector",
    "PluginManager",
    "PluginInterface",
    "ReportGenerator",
    "SecretsManager",
    "ToolContext",
    "ToolResult",
    "normalize_tool_result",
]
