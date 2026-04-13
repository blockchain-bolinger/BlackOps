import time
import unittest

from core.job_manager import JobManager


class TestJobManager(unittest.TestCase):
    def test_job_success_and_status(self):
        manager = JobManager(max_workers=2)
        job_id = manager.submit(lambda: "ok", retries=0, timeout_seconds=2)
        result = manager.wait(job_id)
        self.assertEqual(result.status, "completed")
        self.assertEqual(result.result, "ok")

    def test_job_retry_and_failure(self):
        manager = JobManager(max_workers=1)

        def _fail():
            raise RuntimeError("boom")

        job_id = manager.submit(_fail, retries=1, timeout_seconds=2)
        result = manager.wait(job_id)
        self.assertEqual(result.status, "failed")
        self.assertIn("boom", result.error)

    def test_cancel(self):
        manager = JobManager(max_workers=1)

        def _sleep():
            time.sleep(1)
            return "done"

        job_id = manager.submit(_sleep, retries=0, timeout_seconds=5)
        cancelled = manager.cancel(job_id)
        self.assertTrue(cancelled)
        status = manager.status(job_id)
        self.assertEqual(status["status"], "cancelled")


if __name__ == "__main__":
    unittest.main()

