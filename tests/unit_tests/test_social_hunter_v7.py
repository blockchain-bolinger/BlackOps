import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


try:
    from tools.recon.social_hunter_v7 import SocialHunterV7
    SOCIAL_HUNTER_IMPORT_OK = True
except Exception:
    SOCIAL_HUNTER_IMPORT_OK = False
    SocialHunterV7 = None


@unittest.skipUnless(SOCIAL_HUNTER_IMPORT_OK, "social_hunter_v7 dependencies not available")
class TestSocialHunterV7(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.config_path = Path(self.temp_dir.name) / "social_sites.json"
        self.config_path.write_text(
            json.dumps(
                {
                    "social_media": {
                        "github": {"url": "https://github.com/{}"}
                    }
                }
            ),
            encoding="utf-8",
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def _new_hunter(self):
        with patch.object(SocialHunterV7, "CONFIG_PATH", self.config_path):
            hunter = SocialHunterV7()
        hunter.CONFIG_PATH = self.config_path
        return hunter

    def test_email_alias_and_auto_detection(self):
        self.assertEqual(SocialHunterV7.normalize_search_type("emal", "target"), "email")
        self.assertEqual(SocialHunterV7.normalize_search_type("auto", "alice@example.com"), "email")
        self.assertEqual(SocialHunterV7.normalize_search_type("auto", "alice_user"), "username")

    def test_site_defaults_and_management(self):
        hunter = self._new_hunter()
        sites = hunter.list_social_sites()
        self.assertIn("github", sites)
        self.assertTrue(sites["github"].get("enabled", True))

        added = hunter.add_social_site("mastodon", "https://mastodon.social/@{}")
        self.assertTrue(added)
        self.assertIn("mastodon", hunter.list_social_sites())

        disabled = hunter.set_site_enabled("mastodon", False)
        self.assertTrue(disabled)
        self.assertFalse(hunter.list_social_sites()["mastodon"]["enabled"])

        removed = hunter.remove_social_site("mastodon")
        self.assertTrue(removed)
        self.assertNotIn("mastodon", hunter.list_social_sites())


if __name__ == "__main__":
    unittest.main()
