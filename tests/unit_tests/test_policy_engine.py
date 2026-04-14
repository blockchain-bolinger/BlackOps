import unittest

from core.policy_engine import PolicyEngine


class TestPolicyEngine(unittest.TestCase):
    def setUp(self):
        self.engine = PolicyEngine()

    def test_demo_profile_blocks_offensive_module(self):
        decision = self.engine.evaluate(
            profile_name="demo",
            tool_name="venom_maker",
            module_category="offensive",
            action="tool_execution",
            sudo=False,
            approved=True,
        )
        self.assertFalse(decision.allowed)
        self.assertIn("module category", decision.reason)

    def test_pentest_profile_requires_approval(self):
        decision = self.engine.evaluate(
            profile_name="pentest",
            tool_name="netscout_pro",
            module_category="recon",
            action="tool_execution",
            sudo=False,
            approved=None,
        )
        self.assertTrue(decision.allowed)
        self.assertTrue(decision.approval_required)

    def test_timeout_is_capped_by_profile(self):
        decision = self.engine.evaluate(
            profile_name="training",
            tool_name="social_hunter_v7",
            module_category="recon",
            action="tool_execution",
            timeout_seconds=300,
            sudo=False,
            approved=True,
        )
        self.assertTrue(decision.allowed)
        self.assertEqual(decision.effective_timeout_seconds, 120)


if __name__ == "__main__":
    unittest.main()
