import json
import os
import tempfile
import unittest
from pathlib import Path

from core.config_manager import ConfigManager


class TestConfigManager(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.config_path = Path(self.tmp) / "config.json"
        self.secrets_path = Path(self.tmp) / "secrets.json"
        self.secrets_path.write_text('{"token": "file-token"}', encoding="utf-8")

    def tearDown(self):
        for key in list(os.environ.keys()):
            if key.startswith("BLACKOPS__") or key.startswith("BLACKOPS_SECRET_"):
                del os.environ[key]

    def test_default_and_validation(self):
        cm = ConfigManager(str(self.config_path))
        self.assertTrue(cm.validate())
        self.assertIn("runtime", cm.config)

    def test_env_override(self):
        os.environ["BLACKOPS__NETWORK__TIMEOUT"] = "99"
        cm = ConfigManager(str(self.config_path))
        self.assertEqual(cm.get("network.timeout"), 99)

    def test_secret_precedence(self):
        cm = ConfigManager(str(self.config_path))
        cm.set("secrets.file_path", str(self.secrets_path))
        cm = ConfigManager(str(self.config_path))
        self.assertEqual(cm.get_secret("token"), "file-token")
        os.environ["BLACKOPS_SECRET_TOKEN"] = "env-token"
        cm = ConfigManager(str(self.config_path))
        self.assertEqual(cm.get_secret("token"), "env-token")

    def test_lint_doctor_migrate(self):
        cm = ConfigManager(str(self.config_path))
        lint = cm.lint()
        self.assertIn("valid", lint)
        doctor = cm.doctor()
        self.assertIn("status", doctor)
        migrate = cm.migrate(target_version="2.3.0", dry_run=True)
        self.assertTrue(migrate["dry_run"])
        self.assertEqual(migrate["to_version"], "2.3.0")

    def test_legacy_layout_is_mapped(self):
        legacy = {
            "framework": {"name": "Legacy", "version": "2.2.0"},
            "logging": {"level": "WARNING"},
            "security": {"session_timeout_minutes": 45},
            "network": {"scan_timeout": 7, "max_threads": 64},
            "ethics": {"require_agreement": False},
            "modules": {"offensive": {"enabled": True, "require_confirmation": False}},
        }
        self.config_path.write_text(json.dumps(legacy), encoding="utf-8")

        cm = ConfigManager(str(self.config_path))
        self.assertEqual(cm.get("version"), "2.2.0")
        self.assertEqual(cm.get("log_level"), "WARNING")
        self.assertEqual(cm.get("network.timeout"), 7)
        self.assertEqual(cm.get("runtime.worker_threads"), 64)
        self.assertEqual(cm.get("runtime.task_timeout_seconds"), 2700)
        self.assertFalse(cm.get("ethics.require_confirmation"))
        self.assertFalse(cm.get("ethics.require_approval"))


if __name__ == "__main__":
    unittest.main()
