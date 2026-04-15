import json
import tempfile
import unittest

from core.system_report_service import SystemReportService


class TestSystemReportService(unittest.TestCase):
    def test_generate_writes_report_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            service = SystemReportService(output_dir=tmp)
            result = service.generate(
                session_id="sess-1",
                tools={
                    "1": {"name": "Tool A"},
                    "13": {"name": "System Check & Updates"},
                    "14": {"name": "Report Generator"},
                    "99": {"name": "Exit"},
                },
                config={"ethics": {"show_warning": True}},
            )

            self.assertTrue(result.ok)
            report_file = result.data["report_file"]
            with open(report_file, "r", encoding="utf-8") as handle:
                payload = json.load(handle)
            self.assertEqual(payload["session_id"], "***REDACTED***")
            self.assertIn("Tool A", payload["tools"]["1"])


if __name__ == "__main__":
    unittest.main()
