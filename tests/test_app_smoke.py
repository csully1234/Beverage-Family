from __future__ import annotations

import os
import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest


ROOT = Path(__file__).resolve().parents[1]


class StreamlitSmokeTests(unittest.TestCase):
    def logged_in_app(self, **query_params: str) -> AppTest:
        os.environ["APP_PASSWORD"] = "test-family-password"
        app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=30)
        for key, value in query_params.items():
            app.query_params[key] = value
        app.run()
        app.text_input[0].input("test-family-password")
        app.button[0].click()
        app.run()
        self.assertEqual(len(app.exception), 0)
        return app

    def test_login_and_every_page_render_without_exceptions(self) -> None:
        app = self.logged_in_app()

        for page in (
            "Home",
            "Search",
            "Explore the Tree",
            "Full Family Map",
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

    def test_tree_open_profile_uses_safe_callback_navigation(self) -> None:
        app = self.logged_in_app()

        app.radio[0].set_value("Explore the Tree")
        app.run()
        target = "harold_h_beverage_1893"
        app.selectbox[0].select(target)
        app.run()

        open_button = next(button for button in app.button if button.label == "Open full profile")
        open_button.click()
        app.run()

        self.assertEqual(len(app.exception), 0, [exception.value for exception in app.exception])
        self.assertEqual(app.radio[0].value, "People")
        self.assertEqual(app.selectbox[0].value, target)

    def test_sidebar_open_profile_uses_safe_callback_navigation(self) -> None:
        app = self.logged_in_app()
        target = "harold_h_beverage_1893"

        quick_lookup = next(
            selectbox for selectbox in app.selectbox if selectbox.label == "Quick person lookup"
        )
        quick_lookup.select(target)
        app.run()

        open_button = next(button for button in app.button if button.label == "Open profile")
        open_button.click()
        app.run()

        self.assertEqual(len(app.exception), 0, [exception.value for exception in app.exception])
        self.assertEqual(app.radio[0].value, "People")
        profile_selector = next(
            selectbox for selectbox in app.selectbox if selectbox.label == "Find a person"
        )
        self.assertEqual(profile_selector.value, target)

    def test_person_profile_centers_tree_with_safe_callback(self) -> None:
        target = "harold_h_beverage_1893"
        app = self.logged_in_app(page="people", profile=target)

        center_button = next(
            button for button in app.button
            if button.label == "Center this person in the family tree"
        )
        center_button.click()
        app.run()

        self.assertEqual(len(app.exception), 0, [exception.value for exception in app.exception])
        self.assertEqual(app.radio[0].value, "Explore the Tree")
        tree_picker = next(
            selectbox for selectbox in app.selectbox if selectbox.label == "Center person"
        )
        self.assertEqual(tree_picker.value, target)

    def test_full_family_map_direct_route(self) -> None:
        app = self.logged_in_app(page="full-tree")
        self.assertEqual(app.radio[0].value, "Full Family Map")
        self.assertEqual(len(app.exception), 0, [exception.value for exception in app.exception])

    def test_major_interactions_and_direct_routes(self) -> None:
        app = self.logged_in_app()

        app.radio[0].set_value("Search")
        app.run()
        app.text_input[0].input("Harold")
        app.run()
        self.assertGreater(int(app.metric[0].value), 0)

        app.radio[0].set_value("Explore the Tree")
        app.run()
        app.selectbox[2].select("harold_h_beverage_1893")
        app.selectbox[3].select("albert_glover_beverage_1827")
        app.run()
        self.assertIn("Connected in 2 relationship step", app.success[0].value)

        app.radio[0].set_value("Timeline")
        app.run()
        app.text_input[0].input("patent")
        app.run()
        self.assertTrue(any("1 of 1 matching" in item.value for item in app.caption))

        profile = self.logged_in_app(page="people", profile="harold_h_beverage_1893")
        self.assertEqual(profile.radio[0].value, "People")
        self.assertEqual(profile.selectbox[0].value, "harold_h_beverage_1893")

        event = self.logged_in_app(page="timeline", event="event_harold_patent_1921")
        self.assertEqual(event.radio[0].value, "Timeline")
        self.assertTrue(any("Direct link opened" in item.value for item in event.info))


if __name__ == "__main__":
    unittest.main()
