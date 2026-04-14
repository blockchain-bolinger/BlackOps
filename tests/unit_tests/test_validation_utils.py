import tempfile
import unittest
from pathlib import Path

from utils.validation_utils import ValidationUtils


class TestValidationUtils(unittest.TestCase):
    def test_url_and_onion_validation(self):
        self.assertTrue(ValidationUtils.validate_url("https://example.com"))
        self.assertFalse(ValidationUtils.validate_url("ftp://example.com"))
        self.assertTrue(ValidationUtils.validate_onion_url("http://exampleonionaddress.onion"))
        self.assertTrue(
            ValidationUtils.validate_onion_url(
                ValidationUtils.normalize_onion_url("exampleonionaddress.onion")
            )
        )

    def test_domain_and_host_validation(self):
        self.assertTrue(ValidationUtils.validate_domain("example.com"))
        self.assertFalse(ValidationUtils.validate_domain("localhost"))
        self.assertTrue(ValidationUtils.validate_hostname_or_ip("localhost"))
        self.assertTrue(ValidationUtils.validate_hostname_or_ip("192.168.1.10"))
        self.assertFalse(ValidationUtils.validate_hostname_or_ip("not a host"))

    def test_numeric_and_choice_validation(self):
        self.assertTrue(ValidationUtils.validate_positive_int("4"))
        self.assertFalse(ValidationUtils.validate_positive_int("0"))
        self.assertTrue(ValidationUtils.validate_non_negative_float("0.5"))
        self.assertFalse(ValidationUtils.validate_non_negative_float("-1"))
        self.assertTrue(ValidationUtils.validate_port("443"))
        self.assertFalse(ValidationUtils.validate_port("70000"))
        self.assertTrue(ValidationUtils.validate_choice("SSH", ["ssh", "ftp"]))
        self.assertFalse(ValidationUtils.validate_choice("smtp", ["ssh", "ftp"]))

    def test_file_and_csv_validation(self):
        with tempfile.TemporaryDirectory() as tmp:
            first = Path(tmp) / "a.log"
            second = Path(tmp) / "b.log"
            first.write_text("a", encoding="utf-8")
            second.write_text("b", encoding="utf-8")

            self.assertTrue(ValidationUtils.validate_existing_file(str(first)))
            self.assertTrue(ValidationUtils.validate_optional_existing_file(""))
            self.assertFalse(ValidationUtils.validate_existing_file(str(Path(tmp) / "missing.log")))

            csv_value = f"{first},{second}"
            self.assertEqual(ValidationUtils.parse_csv(csv_value), [str(first), str(second)])
            self.assertTrue(ValidationUtils.validate_csv_file_list(csv_value))
            self.assertFalse(ValidationUtils.validate_csv_file_list(f"{first},missing.log"))


if __name__ == "__main__":
    unittest.main()
