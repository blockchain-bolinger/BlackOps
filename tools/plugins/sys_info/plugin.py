import os
import platform
from datetime import datetime, timezone

from core.plugin_manager import PluginInterface


class SysInfoPlugin(PluginInterface):
    version = "1.0.0"
    api_version = 1

    def name(self):
        return "sys_info"

    def description(self):
        return "Liefert grundlegende System- und Laufzeitinformationen."

    def run(self, **kwargs):
        env_keys = kwargs.get("env_keys", "")
        selected_env = {}
        if env_keys:
            for key in [k.strip() for k in env_keys.split(",") if k.strip()]:
                selected_env[key] = os.environ.get(key)

        return {
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "hostname": platform.node(),
            "cwd": os.getcwd(),
            "selected_env": selected_env,
        }

