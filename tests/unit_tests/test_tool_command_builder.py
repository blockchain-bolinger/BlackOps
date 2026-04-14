import unittest
from unittest.mock import patch

from core.tool_command_builder import ToolCommandBuilder


class TestToolCommandBuilder(unittest.TestCase):
    def test_build_tool_command_for_codedigger(self):
        inputs = iter(["api key", "github", "", ""])

        def fake_input(_prompt):
            return next(inputs)

        builder = ToolCommandBuilder(lambda en, de: en, input_func=fake_input)
        with patch("core.tool_command_builder.ValidationUtils.validate_non_empty", return_value=True), patch(
            "core.tool_command_builder.ValidationUtils.validate_choice", return_value=True
        ):
            cmd = builder.build_tool_command("21", "tools/recon/codedigger.py")

        self.assertEqual(cmd[:2], ["python3", "tools/recon/codedigger.py"])
        self.assertIn("api key", cmd)
        self.assertIn("--platform", cmd)
        self.assertIn("github", cmd)


if __name__ == "__main__":
    unittest.main()
