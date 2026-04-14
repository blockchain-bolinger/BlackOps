import tempfile
import unittest
from pathlib import Path

from core.process_runner import SafeProcessRunner, ProcessRunnerError


class TestSafeProcessRunner(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.tmp_path = Path(self.tmp)
        self.script_path = self.tmp_path / "ok.py"
        self.script_path.write_text("print('ok')\n", encoding="utf-8")
        self.sleep_script = self.tmp_path / "sleep.py"
        self.sleep_script.write_text("import time\ntime.sleep(2)\n", encoding="utf-8")
        self.runner = SafeProcessRunner(allowed_roots=[self.tmp_path], allowed_executables=["python3", "python", "sudo"])

    def test_run_capture_allows_python_script(self):
        result = self.runner.run_capture(["python3", str(self.script_path)], timeout=5)
        self.assertEqual(result.returncode, 0)
        self.assertFalse(result.timed_out)
        self.assertIn("ok", result.stdout)

    def test_rejects_inline_python_execution(self):
        with self.assertRaises(ProcessRunnerError):
            self.runner.run_capture(["python3", "-c", "print('x')"], timeout=5)

    def test_rejects_script_outside_allowed_roots(self):
        outside_script = Path("/tmp/blackops_runner_outside_test.py")
        outside_script.write_text("print('x')\n", encoding="utf-8")
        try:
            with self.assertRaises(ProcessRunnerError):
                self.runner.run_capture(["python3", str(outside_script)], timeout=5)
        finally:
            outside_script.unlink(missing_ok=True)

    def test_timeout_is_reported(self):
        result = self.runner.run_capture(["python3", str(self.sleep_script)], timeout=0.05)
        self.assertTrue(result.timed_out)
        self.assertEqual(result.returncode, 124)


if __name__ == "__main__":
    unittest.main()
