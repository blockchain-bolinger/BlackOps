import json
import tempfile
import unittest
from pathlib import Path

from core.ethics_enforcer import EthicsEnforcer


class TestEthicsEnforcerApprovalFlow(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.config_path = Path(self.tmp) / "ethics_config.json"
        self.config_path.write_text(
            json.dumps(
                {
                    "rules": {},
                    "restrictions": {
                        "forbidden_targets": [],
                        "allowed_actions": ["penetration_testing"],
                        "forbidden_actions": [],
                    },
                    "approval_required": True,
                    "logging_level": "DETAILED",
                }
            ),
            encoding="utf-8",
        )

    def test_non_interactive_denies_when_approval_required(self):
        enforcer = EthicsEnforcer(config_path=str(self.config_path), interactive=False)
        approvals = []
        violations = []
        enforcer._log_approval = lambda *args, **kwargs: approvals.append(args)
        enforcer._log_violation = lambda *args, **kwargs: violations.append(args)

        approved = enforcer.get_approval("example.com", "port_scan", "unit-test")
        self.assertFalse(approved)
        self.assertEqual(len(approvals), 0)
        self.assertEqual(len(violations), 1)

    def test_explicit_approval_bypasses_prompt(self):
        enforcer = EthicsEnforcer(config_path=str(self.config_path), interactive=False)
        approvals = []
        violations = []
        enforcer._log_approval = lambda *args, **kwargs: approvals.append(args)
        enforcer._log_violation = lambda *args, **kwargs: violations.append(args)

        approved = enforcer.get_approval("example.com", "port_scan", "unit-test", approved=True)
        self.assertTrue(approved)
        self.assertEqual(len(approvals), 1)
        self.assertEqual(len(violations), 0)

    def test_decision_provider_is_used(self):
        enforcer = EthicsEnforcer(
            config_path=str(self.config_path),
            interactive=False,
            decision_provider=lambda ctx: ctx["target"] == "example.com",
        )
        approvals = []
        violations = []
        enforcer._log_approval = lambda *args, **kwargs: approvals.append(args)
        enforcer._log_violation = lambda *args, **kwargs: violations.append(args)

        approved = enforcer.get_approval("example.com", "port_scan", "unit-test")
        self.assertTrue(approved)
        self.assertEqual(len(approvals), 1)
        self.assertEqual(len(violations), 0)


if __name__ == "__main__":
    unittest.main()
