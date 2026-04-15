import logging
import tempfile
import unittest

from core.blackops_logger import BlackOpsLogger, JsonFormatter


class TestLogger(unittest.TestCase):
    def test_correlation_id_and_json_format(self):
        with tempfile.TemporaryDirectory() as tmp:
            logger = BlackOpsLogger("test_logger", log_dir=tmp)
            correlation_id = logger.set_correlation_id("corr-123")
            self.assertEqual(correlation_id, "corr-123")

            record = logging.LogRecord(
                name="test_logger",
                level=logging.INFO,
                pathname=__file__,
                lineno=10,
                msg="hello",
                args=(),
                exc_info=None,
            )
            record.correlation_id = correlation_id
            payload = JsonFormatter().format(record)
            self.assertIn('"correlation_id": "corr-123"', payload)
            self.assertIn('"message": "hello"', payload)


if __name__ == "__main__":
    unittest.main()
