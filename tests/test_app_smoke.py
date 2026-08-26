from __future__ import annotations

import os
import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest


ROOT = Path(__file__).resolve().parents[1]


class StreamlitSmokeTests(unittest.TestCase):
    def test_login_and_every_page_render_without_exceptions(self) -> None:
        os.environ["APP_PASSWORD"] = "test-family-password"
        app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=30).run()

        self.assertEqual(len(app.exception), 0)
        app.text_input[0].input("test-family-password")
        app.button[0].click()
        app.run()
        self.assertEqual(len(app.exception), 0)

        for page in (
            "Home",
            "Explore the Tree",
            "People",
            "Timeline",
            "Research Desk",
            "Sources & Method",
        ):
            with self.subTest(page=page):
                app.radio[0].set_value(page)
                app.run()
                self.assertEqual(
                    len(app.exception),
                    0,
                    [exception.value for exception in app.exception],
                )


if __name__ == "__main__":
    unittest.main()
