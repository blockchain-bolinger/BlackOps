import os
import tempfile
import unittest
from pathlib import Path

from core.secrets_manager import SecretsManager


class TestSecretsManager(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.secrets_path = Path(self.tmp) / "secrets.json"
        self.dotenv_path = Path(self.tmp) / ".env"
        self.secrets_path.write_text('{"api_keys": {"haveibeenpwned": "file-hibp"}, "openai_key": "file-openai"}')

    def tearDown(self):
        for key in list(os.environ.keys()):
            if key.startswith("BLACKOPS_SECRET_") or key == "OPENAI_KEY":
                del os.environ[key]

    def test_file_lookup_nested(self):
        sm = SecretsManager(path=str(self.secrets_path), dotenv_path=str(self.dotenv_path))
        self.assertEqual(sm.get("api_keys.haveibeenpwned"), "file-hibp")

    def test_env_overrides_file(self):
        os.environ["BLACKOPS_SECRET_API_KEYS_HAVEIBEENPWNED"] = "env-hibp"
        sm = SecretsManager(path=str(self.secrets_path), dotenv_path=str(self.dotenv_path))
        self.assertEqual(sm.get("api_keys.haveibeenpwned"), "env-hibp")

    def test_plain_env_alias(self):
        os.environ["OPENAI_KEY"] = "plain-env-openai"
        sm = SecretsManager(path=str(self.secrets_path), dotenv_path=str(self.dotenv_path))
        self.assertEqual(sm.get("openai_key"), "plain-env-openai")

    def test_dotenv_loaded(self):
        self.dotenv_path.write_text("BLACKOPS_SECRET_SHODAN=dotenv-shodan\n", encoding="utf-8")
        sm = SecretsManager(path=str(self.secrets_path), dotenv_path=str(self.dotenv_path))
        self.assertEqual(sm.get("shodan"), "dotenv-shodan")


if __name__ == "__main__":
    unittest.main()

