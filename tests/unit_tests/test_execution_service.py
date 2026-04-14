import tempfile
import unittest
from pathlib import Path

from core.execution_service import ExecutionService
from core.process_runner import SafeProcessRunner
from core.tool_contract import ToolResult


class TestExecutionService(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.base_dir = Path(self.tmp)
        self.tools_dir = self.base_dir / "tools"
        self.tools_dir.mkdir(parents=True, exist_ok=True)

        self.ok_script = self.tools_dir / "ok.py"
        self.ok_script.write_text("print('ok')\n", encoding="utf-8")
        self.fail_script = self.tools_dir / "fail.py"
        self.fail_script.write_text("import sys\nsys.exit(2)\n", encoding="utf-8")
        self.sleep_script = self.tools_dir / "sleep.py"
        self.sleep_script.write_text("import time\ntime.sleep(2)\n", encoding="utf-8")

        runner = SafeProcessRunner(allowed_roots=[self.base_dir, self.tools_dir], allowed_executables=["python3", "python", "sudo"])
        self.service = ExecutionService(
            process_runner=runner,
            base_dir=self.base_dir,
            tools_dir=self.tools_dir,
        )

    def test_execute_tool_capture_success(self):
        result = self.service.execute_tool("tools/ok.py", capture_output=True, timeout=5)
        self.assertIsInstance(result, ToolResult)
        self.assertEqual(result.status, "success")
        self.assertEqual(result.data["returncode"], 0)
        self.assertIn("ok", result.data["stdout"])

    def test_execute_tool_returns_failed_for_non_zero_exit(self):
        result = self.service.execute_tool("tools/fail.py", capture_output=True, timeout=5)
        self.assertEqual(result.status, "failed")
        self.assertEqual(result.data["returncode"], 2)
        self.assertTrue(result.errors)

    def test_execute_tool_returns_validation_error_for_bad_args(self):
        result = self.service.execute_tool("tools/ok.py", args={"a": 1}, capture_output=True)
        self.assertEqual(result.status, "failed")
        self.assertEqual(result.meta.get("error_type"), "validation")

    def test_execute_tool_timeout_maps_to_504(self):
        result = self.service.execute_tool("tools/sleep.py", capture_output=True, timeout=0.05)
        self.assertEqual(result.status, "failed")
        self.assertEqual(result.meta.get("error_type"), "timeout")
        self.assertEqual(self.service.http_status_for_result(result), 504)

    def test_http_status_for_validation_error_is_400(self):
        result = ToolResult.failed("bad input", error_type="validation")
        self.assertEqual(self.service.http_status_for_result(result), 400)

    def test_http_status_for_internal_error_is_500(self):
        result = ToolResult.failed("boom", error_type="internal")
        self.assertEqual(self.service.http_status_for_result(result), 500)


if __name__ == "__main__":
    unittest.main()
