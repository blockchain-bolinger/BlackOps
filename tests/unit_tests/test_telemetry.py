import tempfile
import unittest
from pathlib import Path

from core.telemetry import ExecutionTelemetry


class TestExecutionTelemetry(unittest.TestCase):
    def test_start_and_finish_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            telemetry = ExecutionTelemetry(telemetry_dir=Path(tmp) / "telemetry")
            run_id = telemetry.start_run(
                correlation_id="corr-1",
                profile="lab",
                tool_label="demo-tool",
                context={"module_category": "recon"},
            )
            telemetry.finish_run(
                run_id,
                correlation_id="corr-1",
                payload={"status": "success", "tool": "demo-tool"},
            )
            snapshot = telemetry.snapshot()
            self.assertIn(run_id, snapshot)
            self.assertEqual(snapshot[run_id]["status"], "success")
            self.assertTrue((Path(tmp) / "telemetry" / "events.jsonl").exists())
            self.assertTrue((Path(tmp) / "telemetry" / "runs.json").exists())


if __name__ == "__main__":
    unittest.main()
