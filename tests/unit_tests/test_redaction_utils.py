import unittest

from core.redaction_utils import REDACTED, redact_data, redact_text


class TestRedactionUtils(unittest.TestCase):
    def test_redact_text_key_value_and_bearer(self):
        text = "token=abc123 Authorization: Bearer abcdefghijklmnop"
        redacted = redact_text(text)
        self.assertIn(f"token={REDACTED}", redacted)
        self.assertIn(f"Bearer {REDACTED}", redacted)
        self.assertNotIn("abc123", redacted)
        self.assertNotIn("abcdefghijklmnop", redacted)

    def test_redact_data_nested(self):
        payload = {
            "api_key": "sk-123456",
            "nested": {"password": "pw123", "safe": "hello"},
            "note": "Authorization: Bearer qwerty1234567890",
        }
        redacted = redact_data(payload)
        self.assertEqual(redacted["api_key"], REDACTED)
        self.assertEqual(redacted["nested"]["password"], REDACTED)
        self.assertEqual(redacted["nested"]["safe"], "hello")
        self.assertIn(f"Bearer {REDACTED}", redacted["note"])


if __name__ == "__main__":
    unittest.main()
