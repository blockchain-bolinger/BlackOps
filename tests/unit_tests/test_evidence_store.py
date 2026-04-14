import tempfile
import unittest
from pathlib import Path

from core.evidence_store import EvidenceStore


class TestEvidenceStore(unittest.TestCase):
    def test_ingest_and_search(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = EvidenceStore(store_dir=Path(tmp) / "evidence")
            record = store.ingest_finding(
                source_tool="osint_domain",
                profile="osint",
                correlation_id="corr-1",
                run_id="run-1",
                finding={
                    "id": "F-1",
                    "title": "Subdomain exposure",
                    "severity": "high",
                    "category": "exposure",
                    "cwe": "CWE-200",
                    "cves": ["CVE-2024-0001"],
                    "target": "example.com",
                    "evidence": [{"subdomain": "api.example.com"}],
                },
            )
            self.assertEqual(record.severity, "high")
            self.assertTrue((Path(tmp) / "evidence" / "records.json").exists())

            stats = store.stats()
            self.assertEqual(stats["total"], 1)
            self.assertEqual(stats["high"], 1)

            search = store.search(query="subdomain")
            self.assertEqual(len(search), 1)
            self.assertEqual(search[0]["target"], "example.com")


if __name__ == "__main__":
    unittest.main()
