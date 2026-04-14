import csv
import json
import tempfile
import unittest
from pathlib import Path

from tools.recon.osint_output import failed_payload, save_csv, save_json, success_payload


class TestOsintOutputHelpers(unittest.TestCase):
    def test_success_payload_shape(self):
        payload = success_payload("osint_email", {"target": "alice@example.com"}, target_type="email")
        self.assertEqual(payload["status"], "success")
        self.assertEqual(payload["errors"], [])
        self.assertEqual(payload["data"]["target"], "alice@example.com")
        self.assertEqual(payload["meta"]["tool"], "osint_email")
        self.assertEqual(payload["meta"]["target_type"], "email")
        self.assertIn("timestamp", payload["meta"])

    def test_failed_payload_shape(self):
        payload = failed_payload("osint_phone", "invalid phone", error_type="validation")
        self.assertEqual(payload["status"], "failed")
        self.assertTrue(payload["errors"])
        self.assertEqual(payload["meta"]["tool"], "osint_phone")
        self.assertEqual(payload["meta"]["error_type"], "validation")

    def test_save_json_and_csv(self):
        payload = success_payload(
            "osint_domain",
            {
                "domain": "example.com",
                "dns": {"a_records": ["1.2.3.4"]},
                "subdomains": ["a.example.com", "b.example.com"],
            },
        )
        with tempfile.TemporaryDirectory() as tmp:
            json_path = Path(tmp) / "report.json"
            csv_path = Path(tmp) / "report.csv"
            save_json(str(json_path), payload)
            save_csv(str(csv_path), payload, data_only=True)

            loaded = json.loads(json_path.read_text(encoding="utf-8"))
            self.assertEqual(loaded["status"], "success")

            with open(csv_path, newline="", encoding="utf-8") as handle:
                rows = list(csv.reader(handle))
            self.assertEqual(rows[0], ["key", "value"])
            flat_keys = {row[0] for row in rows[1:]}
            self.assertIn("domain", flat_keys)
            self.assertIn("dns.a_records[0]", flat_keys)
            self.assertIn("subdomains[1]", flat_keys)


if __name__ == "__main__":
    unittest.main()
