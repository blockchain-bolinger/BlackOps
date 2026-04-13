import unittest

from core.metrics import MetricsCollector


class TestMetricsExport(unittest.TestCase):
    def test_prometheus_export(self):
        collector = MetricsCollector(metrics_path="tmp/test_metrics.json")
        collector.increment("tool.scan.invocations", 2)
        collector.observe_duration("tool.scan.duration", 1.5)
        collector.observe_duration("tool.scan.duration", 0.5)
        text = collector.to_prometheus(namespace="blackops")
        self.assertIn("blackops_tool_scan_invocations", text)
        self.assertIn("blackops_tool_scan_duration_seconds_count", text)
        self.assertIn("blackops_tool_scan_duration_seconds_sum", text)


if __name__ == "__main__":
    unittest.main()

