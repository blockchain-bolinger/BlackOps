import importlib
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from core.process_runner import ProcessResult

try:
    import flask  # noqa: F401
    web_app = importlib.import_module("web.app")
    FLASK_AVAILABLE = True
except Exception:
    web_app = None
    FLASK_AVAILABLE = False


@unittest.skipUnless(FLASK_AVAILABLE, "Flask is not installed in this test environment.")
class TestWebRunToolContract(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.base_dir = Path(self.temp_dir.name)
        self.tools_dir = self.base_dir / "tools"
        self.tools_dir.mkdir(parents=True, exist_ok=True)
        self.script_rel = Path("tools") / "dummy_tool.py"
        (self.tools_dir / "dummy_tool.py").write_text("print('ok')\n", encoding="utf-8")
        self.client = web_app.app.test_client()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_run_tool_success_returns_tool_result_shape(self):
        fake_result = ProcessResult(
            returncode=0,
            stdout="ok\n",
            stderr="",
            timed_out=False,
            command=["python3", str((self.tools_dir / "dummy_tool.py").resolve())],
        )
        with patch.object(web_app, "base_dir", self.base_dir), patch.object(web_app, "tools_dir", self.tools_dir), patch.object(web_app, "process_runner") as runner:
            runner.run_capture.return_value = fake_result
            response = self.client.post("/api/v1/run", json={"tool": str(self.script_rel), "args": []})

        self.assertEqual(response.status_code, 200)
        body = response.get_json()
        self.assertEqual(body["status"], "success")
        self.assertEqual(body["errors"], [])
        self.assertEqual(body["data"]["returncode"], 0)
        self.assertIn("timestamp", body["meta"])

    def test_run_tool_invalid_args_returns_failed_status(self):
        response = self.client.post("/api/v1/run", json={"tool": str(self.script_rel), "args": {"x": 1}})
        self.assertEqual(response.status_code, 400)
        body = response.get_json()
        self.assertEqual(body["status"], "failed")
        self.assertTrue(body["errors"])
        self.assertIn("timestamp", body["meta"])

    def test_run_tool_non_zero_exit_returns_failed_status(self):
        fake_result = ProcessResult(
            returncode=2,
            stdout="",
            stderr="boom",
            timed_out=False,
            command=["python3", str((self.tools_dir / "dummy_tool.py").resolve())],
        )
        with patch.object(web_app, "base_dir", self.base_dir), patch.object(web_app, "tools_dir", self.tools_dir), patch.object(web_app, "process_runner") as runner:
            runner.run_capture.return_value = fake_result
            response = self.client.post("/api/v1/run", json={"tool": str(self.script_rel), "args": []})

        self.assertEqual(response.status_code, 200)
        body = response.get_json()
        self.assertEqual(body["status"], "failed")
        self.assertEqual(body["data"]["returncode"], 2)
        self.assertTrue(body["errors"])


if __name__ == "__main__":
    unittest.main()
