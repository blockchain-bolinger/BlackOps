import unittest

from core.tool_contract import ToolResult, normalize_tool_result


class TestToolContract(unittest.TestCase):
    def test_tool_result_to_dict_includes_timestamp(self):
        result = ToolResult.success(data={"ok": True}, tool="demo")
        payload = result.to_dict()
        self.assertTrue(result.ok)
        self.assertIn("timestamp", payload["meta"])
        self.assertEqual(payload["meta"]["tool"], "demo")

    def test_normalize_tool_result_preserves_result_shape(self):
        result = normalize_tool_result({"status": "failed", "data": {"x": 1}, "errors": ["boom"]}, "demo")
        self.assertEqual(result.status, "failed")
        self.assertEqual(result.data, {"x": 1})
        self.assertEqual(result.errors, ["boom"])


if __name__ == "__main__":
    unittest.main()
