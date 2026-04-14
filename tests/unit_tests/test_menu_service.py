import unittest

from core.menu_service import MenuService


class MenuServiceTest(unittest.TestCase):
    def test_render_groups_tools_without_crashing(self):
        captured = []

        service = MenuService(
            bilingual=lambda english, german: english,
            print_func=lambda *args, **kwargs: captured.append(" ".join(str(arg) for arg in args)),
        )
        service.render(
            tools={
                "01": {"category": "recon", "name": "Alpha"},
                "13": {"category": "utils", "name": "Ignore"},
                "14": {"category": "utils", "name": "Ignore"},
            },
            categories={"recon": "RECON"},
        )

        self.assertTrue(any("MAIN MENU" in line for line in captured))
        self.assertTrue(any("Alpha" in line for line in captured))


if __name__ == "__main__":
    unittest.main()
