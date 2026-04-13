import tempfile
import unittest
from pathlib import Path

from core.plugin_manager import PluginManager


class TestPluginManager(unittest.TestCase):
    def test_discovery_and_lifecycle(self):
        tmp = tempfile.mkdtemp()
        plugin_root = Path(tmp) / "tools" / "plugins" / "demo"
        plugin_root.mkdir(parents=True, exist_ok=True)
        (plugin_root / "__init__.py").write_text("", encoding="utf-8")
        (plugin_root.parent / "__init__.py").write_text("", encoding="utf-8")
        (plugin_root / "plugin.py").write_text(
            """
from core.plugin_manager import PluginInterface
class DemoPlugin(PluginInterface):
    version = "1.0.0"
    api_version = 1
    def __init__(self):
        self.loaded = False
    def name(self):
        return "demo"
    def description(self):
        return "demo plugin"
    def on_load(self, context=None):
        self.loaded = True
    def run(self, **kwargs):
        return {"ok": self.loaded, "kwargs": kwargs}
""",
            encoding="utf-8",
        )
        manager = PluginManager(plugin_dir=str(plugin_root.parent), required_api_version=1)
        plugins = manager.discover()
        self.assertIn("demo", plugins)
        result = plugins["demo"].run(a=1)
        self.assertTrue(result["ok"])


if __name__ == "__main__":
    unittest.main()

