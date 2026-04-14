import json
import tempfile
import unittest

from core.stats_service import StatsService


class TestStatsService(unittest.TestCase):
    def test_increment_persists_counts(self):
        with tempfile.TemporaryDirectory() as tmp:
            service = StatsService(f"{tmp}/stats.json")
            payload = service.increment("Report Generator")
            self.assertEqual(payload["Report Generator"], 1)
            self.assertIn("last_run", payload)

            payload = service.increment("Report Generator")
            self.assertEqual(payload["Report Generator"], 2)

            with open(f"{tmp}/stats.json", "r", encoding="utf-8") as handle:
                stored = json.load(handle)
            self.assertEqual(stored["Report Generator"], 2)


if __name__ == "__main__":
    unittest.main()
