import unittest

from core.shell_action_service import ShellActionService


class _FakeDecision:
    allowed = True
    reason = "ok"
    approval_required = False


class _FakeRuntime:
    def __init__(self):
        self.tool_calls = []
        self.plugin_calls = []

    def evaluate_tool_execution(self, **kwargs):
        self.tool_calls.append(kwargs)
        return _FakeDecision()

    def evaluate_plugin_execution(self, **kwargs):
        self.plugin_calls.append(kwargs)
        return _FakeDecision()

    def get_plugin(self, name):
        if name != "demo":
            return None

        class _Plugin:
            def run(self, **kwargs):
                return {"ok": True, "kwargs": kwargs}

        return _Plugin()


class ShellActionServiceTest(unittest.TestCase):
    def test_run_tool_invokes_main(self):
        runtime = _FakeRuntime()
        service = ShellActionService(runtime=runtime, bilingual=lambda english, german: english)

        class _Tool:
            __name__ = "alpha"

            @staticmethod
            def main(options):
                return {"ran": options}

        result = service.run_tool(tool_module=_Tool, tool_path="tools/recon/alpha.py", tool_options={"x": 1}, profile_name="lab")
        self.assertEqual(result, {"ran": {"x": 1}})
        self.assertEqual(runtime.tool_calls[-1]["tool_path"], "tools/recon/alpha.py")

    def test_run_plugin_returns_plugin_result(self):
        runtime = _FakeRuntime()
        service = ShellActionService(runtime=runtime, bilingual=lambda english, german: english)
        result = service.run_plugin(plugin_name="demo", kwargs={"q": 1}, profile_name="lab")
        self.assertEqual(result["ok"], True)
        self.assertEqual(result["kwargs"], {"q": 1})


if __name__ == "__main__":
    unittest.main()
