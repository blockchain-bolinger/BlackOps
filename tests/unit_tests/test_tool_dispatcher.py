import unittest

from core.policy_engine import PolicyEngine
from core.tool_dispatcher import DispatchContext, ToolDispatchService
from core.tool_contract import ToolResult


class _FakeExecutionService:
    def __init__(self):
        self.calls = []

    def execute_command(self, command, **kwargs):
        self.calls.append({"command": command, "kwargs": kwargs})
        return ToolResult.success(
            data={"returncode": 0, "timed_out": False, "command": command},
            tool=kwargs.get("tool_label", "command"),
            returncode=0,
        )


class _FakePlugin:
    def __init__(self, result):
        self._result = result

    def description(self):
        return "fake plugin"

    def run(self, **kwargs):
        return self._result


class _FakePluginManager:
    def __init__(self, plugins):
        self._plugins = plugins

    def get_plugin(self, name):
        return self._plugins.get(name)


class TestToolDispatchService(unittest.TestCase):
    def test_execute_plugin_updates_stats_once(self):
        stats = []
        service = ToolDispatchService(
            execution_service=_FakeExecutionService(),
            plugin_manager=_FakePluginManager({"demo": _FakePlugin({"ok": True})}),
            policy_engine=PolicyEngine(),
            update_stats=stats.append,
        )

        result = service.execute_plugin(
            plugin_name="demo",
            display_name="Demo Plugin",
            user_args={"a": "1"},
            profile_name="lab",
            approved=True,
        )

        self.assertEqual(result.status, "success")
        self.assertEqual(stats, ["Demo Plugin"])

    def test_execute_tool_forwards_context_to_execution_service(self):
        exec_service = _FakeExecutionService()
        service = ToolDispatchService(
            execution_service=exec_service,
            plugin_manager=_FakePluginManager({}),
            policy_engine=PolicyEngine(),
        )
        context = DispatchContext(
            tool_id="1",
            tool_name="Demo Tool",
            tool_path="tools/demo.py",
            category="recon",
            sudo=False,
            approved=True,
            profile_name="lab",
            correlation_id="corr-1",
        )

        result = service.execute_tool(
            context=context,
            command=["python3", "tools/demo.py"],
            env={},
            cwd=".",
            timeout_seconds=10,
        )

        self.assertEqual(result.status, "success")
        self.assertEqual(exec_service.calls[0]["kwargs"]["correlation_id"], "corr-1")
        self.assertEqual(exec_service.calls[0]["kwargs"]["tool_label"], "Demo Tool")


if __name__ == "__main__":
    unittest.main()
