import importlib
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

try:
    import flask  # noqa: F401
    web_app = importlib.import_module("web.app")
    FLASK_AVAILABLE = True
except Exception:
    web_app = None
    FLASK_AVAILABLE = False


@unittest.skipUnless(FLASK_AVAILABLE, "Flask is not installed in this test environment.")
class TestWebOverview(unittest.TestCase):
    def test_overview_and_evidence_endpoints(self):
        with tempfile.TemporaryDirectory() as tmp:
            base_dir = Path(tmp)
            with patch.object(web_app, "evidence_store") as store, patch.object(web_app, "telemetry") as telemetry:
                store.stats.return_value = {"total": 2, "high": 1, "medium": 1, "low": 0, "info": 0}
                store.recent.return_value = [
                    {"evidence_id": "E-1", "title": "Finding", "severity": "high", "target": "example.com", "profile": "osint"}
                ]
                store.search.return_value = [
                    {"evidence_id": "E-1", "title": "Finding", "severity": "high", "target": "example.com", "profile": "osint"}
                ]
                telemetry.snapshot.return_value = {"run-1": {"run_id": "run-1", "profile": "osint", "tool": "demo", "status": "completed", "updated_at": "2026-04-14T00:00:00Z"}}
                with patch.object(web_app, "base_dir", base_dir), patch.object(web_app, "tools_dir", base_dir / "tools"):
                    client = web_app.app.test_client()
                    overview = client.get("/api/v1/overview")
                    evidence = client.get("/api/v1/evidence")
                    runs = client.get("/api/v1/runs")

        self.assertEqual(overview.status_code, 200)
        self.assertEqual(overview.get_json()["evidence"]["total"], 2)
        self.assertEqual(evidence.status_code, 200)
        self.assertEqual(runs.status_code, 200)
        self.assertEqual(runs.get_json()["count"], 1)


if __name__ == "__main__":
    unittest.main()
