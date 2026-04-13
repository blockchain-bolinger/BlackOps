
import unittest
from core.tool_contract import ToolContext, ToolResult
from tools.plugins.airstrike_plugin import AirStrikePlugin

class TestAirStrikePlugin(unittest.TestCase):
    def setUp(self):
        self.context = ToolContext(tool_path="tools.plugins.airstrike_plugin", correlation_id="test-123")
        self.plugin = AirStrikePlugin(self.context)

    def test_scan_action(self):
        # We test with a safe target (localhost) and a small range
        result = self.plugin.run("scan", target="127.0.0.1", ports=[80], scan_type="tcp")
        self.assertIsInstance(result, ToolResult)
        # Note: If no ports are open on 127.0.0.1:80, result.data will be {}
        self.assertIn("status", result.to_dict())

    def test_invalid_action(self):
        result = self.plugin.run("unknown_action")
        self.assertEqual(result.status, "failed")

if __name__ == "__main__":
    unittest.main()
