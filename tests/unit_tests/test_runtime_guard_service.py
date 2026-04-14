import unittest

from core.runtime_guard_service import RuntimeGuardService


class _FakeDependencyChecker:
    def __init__(self, missing=None):
        self.missing = missing or {"missing": [], "outdated": [], "satisfied": [], "errors": []}
        self.install_called = False

    def check_all_dependencies(self):
        return self.missing

    def install_missing(self):
        self.install_called = True


class _FakeLogger:
    def __init__(self):
        self.messages = []

    def info(self, message):
        self.messages.append(message)


class _FakeResponse:
    status_code = 200


class RuntimeGuardServiceTest(unittest.TestCase):
    def test_ethics_warning_accepts_confirmation(self):
        logger = _FakeLogger()
        service = RuntimeGuardService(
            dependency_checker=_FakeDependencyChecker(),
            bilingual=lambda english, german: english,
            logger=logger,
            input_func=lambda prompt: "yes",
            print_func=lambda *args, **kwargs: None,
            sleep_func=lambda seconds: None,
        )

        self.assertTrue(service.ethical_warning())
        self.assertIn("ethical_warning_accepted", logger.messages)

    def test_ethics_warning_rejects_confirmation(self):
        service = RuntimeGuardService(
            dependency_checker=_FakeDependencyChecker(),
            bilingual=lambda english, german: english,
            input_func=lambda prompt: "no",
            print_func=lambda *args, **kwargs: None,
            sleep_func=lambda seconds: None,
        )

        self.assertFalse(service.ethical_warning())

    def test_system_check_installs_missing_dependencies_when_requested(self):
        checker = _FakeDependencyChecker(missing={"missing": [("requests", "2.0", "core")], "outdated": [], "satisfied": [], "errors": []})
        service = RuntimeGuardService(
            dependency_checker=checker,
            bilingual=lambda english, german: english,
            input_func=lambda prompt: "y",
            print_func=lambda *args, **kwargs: None,
            sleep_func=lambda seconds: None,
            requests_get=lambda url, timeout=5: _FakeResponse(),
        )

        self.assertTrue(service.system_check())
        self.assertTrue(checker.install_called)


if __name__ == "__main__":
    unittest.main()
