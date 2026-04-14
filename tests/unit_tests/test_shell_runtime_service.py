import tempfile
import unittest
from pathlib import Path

from core.shell_runtime_service import ShellRuntimeService


class _FakePluginManager:
    def __init__(self):
        self.discover_called = False
        self.plugin = object()

    def discover(self):
        self.discover_called = True
        return {}

    def get_plugin(self, name):
        return self.plugin if name == "demo" else None

    def list_plugin_metadata(self):
        return {"demo": {"version": "1.0", "compatible": True, "error": None}}


class _FakePolicyDecision:
    allowed = True
    reason = "ok"
    approval_required = False


class _FakePolicyEngine:
    def __init__(self):
        self.calls = []
        self.default_profile = "lab"

    def evaluate(self, **kwargs):
        self.calls.append(kwargs)
        return _FakePolicyDecision()


class ShellRuntimeServiceTest(unittest.TestCase):
    def test_discovers_tools_and_evaluates_execution(self):
        with tempfile.TemporaryDirectory() as tmp:
            tools_dir = Path(tmp) / "tools"
            (tools_dir / "recon").mkdir(parents=True)
            (tools_dir / "recon" / "alpha.py").write_text("print('alpha')\n", encoding="utf-8")

            plugin_manager = _FakePluginManager()
            policy_engine = _FakePolicyEngine()
            service = ShellRuntimeService(
                tools_dir=tools_dir,
                plugin_manager=plugin_manager,
                policy_engine=policy_engine,
            )

            self.assertTrue(plugin_manager.discover_called)
            self.assertIn("tools/recon/alpha.py", service.tools_cache)
            decision = service.evaluate_tool_execution(
                profile_name="lab",
                tool_name="alpha",
                tool_path="tools/recon/alpha.py",
                approved=True,
            )

            self.assertTrue(decision.allowed)
            self.assertEqual(policy_engine.calls[-1]["module_category"], "recon")

    def test_plugin_helpers_delegate_to_managed_components(self):
        with tempfile.TemporaryDirectory() as tmp:
            service = ShellRuntimeService(
                tools_dir=tmp,
                plugin_manager=_FakePluginManager(),
                policy_engine=_FakePolicyEngine(),
            )

            self.assertIsNotNone(service.get_plugin("demo"))
            self.assertEqual(service.list_plugin_metadata()["demo"]["version"], "1.0")
            decision = service.evaluate_plugin_execution(
                profile_name="lab",
                plugin_name="demo",
                approved=True,
            )
            self.assertTrue(decision.allowed)


if __name__ == "__main__":
    unittest.main()
