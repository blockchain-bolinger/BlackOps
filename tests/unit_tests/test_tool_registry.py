import unittest

from core.tool_registry import build_tool_registry


class _DummyPlugin:
    def __init__(self, description_text: str):
        self._description_text = description_text

    def description(self):
        return self._description_text


class TestToolRegistry(unittest.TestCase):
    def test_build_tool_registry_adds_plugins_and_categories(self):
        tools, categories = build_tool_registry(
            {
                "beta": _DummyPlugin("beta plugin"),
                "alpha": _DummyPlugin("alpha plugin"),
            }
        )

        self.assertIn("1", tools)
        self.assertIn("99", tools)
        self.assertEqual(tools["100"]["name"], "alpha (Plugin)")
        self.assertEqual(tools["101"]["name"], "beta (Plugin)")
        self.assertEqual(tools["100"]["description"], "alpha plugin")
        self.assertIn("recon", categories)
        self.assertIn("system", categories)


if __name__ == "__main__":
    unittest.main()
