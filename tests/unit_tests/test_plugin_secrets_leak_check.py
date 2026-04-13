import json
import tempfile
import unittest
from pathlib import Path

from tools.plugins.secrets_leak_check.plugin import SecretsLeakCheckPlugin


class TestSecretsLeakCheckPlugin(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.plugin = SecretsLeakCheckPlugin()

    def tearDown(self):
        self.tmp.cleanup()

    def test_detect_and_redact(self):
        (self.root / "app.py").write_text("api_key='SUPERSECRET1234567890'\n", encoding="utf-8")
        result = self.plugin.run(path=str(self.root), include="*.py")
        self.assertGreaterEqual(result["findings_count"], 1)
        preview = result["findings"][0]["match_preview"]
        self.assertIn("***REDACTED***", preview)
        self.assertNotIn("SUPERSECRET1234567890", preview)

    def test_ci_fail_on_findings_and_exit_code(self):
        (self.root / "cfg.txt").write_text("token='ABCDEF0123456789TOKEN'\n", encoding="utf-8")
        result = self.plugin.run(path=str(self.root), include="*.txt", fail_on_findings="true", exit_code="7")
        self.assertTrue(result["ci"]["failed"])
        self.assertEqual(result["ci"]["exit_code"], 7)

    def test_baseline_write_and_suppress(self):
        (self.root / "main.py").write_text("password='Secr3tPassw0rd!'\n", encoding="utf-8")
        baseline = self.root / "baseline.json"

        first = self.plugin.run(
            path=str(self.root),
            include="*.py",
            baseline=str(baseline),
            write_baseline="true",
        )
        self.assertTrue(baseline.exists())
        self.assertGreaterEqual(first["findings_count"], 1)

        second = self.plugin.run(path=str(self.root), include="*.py", baseline=str(baseline))
        self.assertEqual(second["findings_count"], 0)
        self.assertGreaterEqual(second["suppressed_by_baseline"], 1)

    def test_rules_file_gitignore_and_workers(self):
        (self.root / ".gitignore").write_text("ignored/\n", encoding="utf-8")
        ignored = self.root / "ignored"
        ignored.mkdir(parents=True, exist_ok=True)
        (ignored / "skip.txt").write_text("custom_secret='HIDDEN123456'\n", encoding="utf-8")
        (self.root / "scan.txt").write_text("custom_secret='VISIBLE123456'\n", encoding="utf-8")

        rules_file = self.root / "rules.json"
        rules_file.write_text(
            json.dumps(
                {
                    "rules": [
                        {"name": "custom_secret", "pattern": r"custom_secret\s*=\s*['\"][^'\"]+['\"]", "flags": "i"}
                    ]
                }
            ),
            encoding="utf-8",
        )

        single = self.plugin.run(
            path=str(self.root),
            include="*.txt",
            rules="",
            rules_file=str(rules_file),
            respect_gitignore="true",
            workers="1",
        )
        parallel = self.plugin.run(
            path=str(self.root),
            include="*.txt",
            rules="",
            rules_file=str(rules_file),
            respect_gitignore="true",
            workers="4",
        )

        self.assertEqual(single["findings_count"], 1)
        self.assertEqual(parallel["findings_count"], 1)
        self.assertEqual(single["findings"][0]["file"], "scan.txt")
        self.assertEqual(parallel["findings"][0]["file"], "scan.txt")


if __name__ == "__main__":
    unittest.main()
