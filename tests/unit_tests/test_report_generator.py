import json
import os
import unittest

from core.report_generator import ReportGenerator


class TestReportGenerator(unittest.TestCase):
    def test_schema_and_delta(self):
        gen = ReportGenerator()
        report_a = gen.generate_pentest_report(
            {
                "target": "a.example",
                "tester": "t1",
                "findings": [{"id": "F-1", "severity": "high", "vulnerability": "SQL injection", "cve": "CVE-2024-1111"}],
            },
            format="json",
        )
        report_b = gen.generate_pentest_report(
            {
                "target": "a.example",
                "tester": "t1",
                "findings": [
                    {"id": "F-1", "severity": "medium", "vulnerability": "SQLi"},
                    {"id": "F-2", "severity": "low", "vulnerability": "Info leak"},
                ],
            },
            format="json",
        )
        self.assertTrue(os.path.exists(report_a))
        self.assertTrue(os.path.exists(report_b))
        with open(report_a, "r", encoding="utf-8") as handle:
            data_a = json.load(handle)
        self.assertEqual(data_a["metadata"]["target"], "a.example")
        self.assertEqual(data_a["summary"]["total_findings"], 1)
        self.assertIn("average_risk_score", data_a["summary"])
        self.assertEqual(data_a["findings"][0]["cwe"], "CWE-89")
        self.assertIn("CVE-2024-1111", data_a["findings"][0]["cves"])
        self.assertGreater(data_a["findings"][0]["risk_score"], 0)
        self.assertTrue(str(data_a["findings"][0]["playbook"]).startswith("playbooks/"))
        delta = gen.generate_delta_report(report_a, report_b, format="json")
        with open(delta, "r", encoding="utf-8") as handle:
            delta_data = json.load(handle)
        self.assertEqual(delta_data["report_type"], "delta")
        self.assertEqual(delta_data["summary"]["added"], 1)


if __name__ == "__main__":
    unittest.main()
