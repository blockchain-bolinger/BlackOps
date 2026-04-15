import unittest

from core.launcher_presentation_service import LauncherPresentationService


class LauncherPresentationServiceTest(unittest.TestCase):
    def test_print_banner_and_summary_methods(self):
        captured = []
        service = LauncherPresentationService(
            print_func=lambda *args, **kwargs: captured.append(" ".join(str(arg) for arg in args)),
            clear_screen=lambda: captured.append("[clear]"),
        )

        service.print_banner(version="3.0", session_id="abc12345", author="tester")
        service.print_tool_info(
            tool={"name": "Alpha", "category": "recon", "file": "tools/alpha.py", "sudo": False, "description": "desc"}
        )
        service.print_report_summary(session_id="abc12345", report_file="/tmp/report.json", tool_count=7)
        service.print_exit(author="tester")

        self.assertTrue(any("[clear]" in line for line in captured))
        self.assertTrue(any("Alpha" in line for line in captured))
        self.assertTrue(any("report.json" in line for line in captured))
        self.assertTrue(any("Goodbye" in line for line in captured))


if __name__ == "__main__":
    unittest.main()
