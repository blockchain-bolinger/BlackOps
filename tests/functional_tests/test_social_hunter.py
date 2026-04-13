import unittest
from tools.recon.social_hunter_v7 import SocialHunterV7

class TestSocialHunter(unittest.TestCase):
    def test_search_username(self):
        hunter = SocialHunterV7()
        result = hunter.search_username("testuser")
        self.assertIsInstance(result, dict)
