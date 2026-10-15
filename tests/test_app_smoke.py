from __future__ import annotations

import os
import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest


ROOT = Path(__file__).resolve().parents[1]


class StreamlitSmokeTests(unittest.TestCase):
    def go(self, app, page):
        groups = {"Home": ("Home",), "Search": ("Search",),
                  "Family": ("People", "Explore the Tree", "Full Family Map", "Timeline"),
                  "Places": ("Historical Places", "Historical Map"),
                  "Archive": ("Source Archive", "Sources & Method"),
                  "Research": ("Research Collection", "Research Desk")}
        group = next(k for k, v in groups.items() if page in v)
        if app.radio(key="nav_group").value != group:
            app.radio(key="nav_group").set_value(group).run()
        app.radio(key="nav_page").set_value(page).run()
        return app

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
            "Historical Map",
            "Historical Places",
            "Source Archive",
            "People",
            "Timeline",
            "Research Desk",
            "Research Collection",
            "Sources & Method",
        ):
            with self.subTest(page=page):
                self.go(app, page)
                app.run()
                self.assertEqual(
                    len(app.exception),
                    0,
                    [exception.value for exception in app.exception],
                )

    def test_research_collection_views_filters_and_reset(self) -> None:
        app = self.logged_in_app(page="collection", person="elliot_beverage_1908")
        self.assertEqual(app.radio(key="nav_page").value, "Research Collection")
        self.assertEqual(app.selectbox(key="collection_person").value, "elliot_beverage_1908")
        app.text_input(key="collection_query").input("IsleBuilt").run()
        self.assertTrue(any("BF-R028" in caption.value for caption in app.caption))
        next(b for b in app.button if b.label == "Clear research filters").click().run()
        self.assertEqual(app.text_input(key="collection_query").value, "")
        self.assertEqual(app.selectbox(key="collection_person").value, "")
        self.assertTrue(any("57 of 57 findings" in caption.value for caption in app.caption))
        for view in ("Chronology", "Sources", "Retrieval plan", "Inventories", "Images", "Conflict review", "Reports"):
            with self.subTest(view=view):
                app.selectbox(key="collection_view").select(view).run()
                self.assertFalse(app.exception, [e.value for e in app.exception])
        app.selectbox(key="dossier_section").select(7).run()
        self.assertFalse(app.exception)

    def test_research_deep_links_and_existing_profile_context(self) -> None:
        cases = (
            ({"page": "collection", "finding": "BF-R033"}, "Registration dates are not deed dates"),
            ({"page": "collection", "finding": "BF-R049"}, "Duplicate suspected"),
            ({"page": "archive", "source": "SRC118"}, "Findings citing this source"),
            ({"page": "people", "profile": "elliot_beverage_1908"}, "IsleBuilt"),
            ({"page": "collection", "target": "BF-G001"}, "Family Bible pages"),
            ({"page": "collection", "view": "Inventories", "inventory": "Properties and Deeds"}, "Snapshot of the supplied workbook"),
        )
        for params, expected in cases:
            with self.subTest(params=params):
                app = self.logged_in_app(**params)
                self.assertFalse(app.exception, [e.value for e in app.exception])
                text = " ".join(str(e.value) for kind in ("markdown", "caption", "subheader", "info") for e in getattr(app, kind))
                text += " " + " ".join(b.label for b in app.button)
                self.assertIn(expected, text)
                self.go(app, "Home")
                for key in ("finding", "target", "view", "inventory", "person", "source"):
                    self.assertNotIn(key, app.query_params)

    def test_research_conflicts_and_missing_ids_are_explicit(self) -> None:
        app = self.logged_in_app(page="collection", finding="BF-R049")
        self.assertTrue(any("review" in str(item.value).lower() for kind in ("caption", "markdown", "info") for item in getattr(app, kind)))
        app = self.logged_in_app(page="collection", finding="nonexistent")
        self.assertTrue(any("not found" in item.value for item in app.warning))
        self.assertFalse(app.exception)

    def test_tree_open_profile_uses_safe_callback_navigation(self) -> None:
        app = self.logged_in_app()

        self.go(app, "Explore the Tree")
        app.run()
        target = "harold_h_beverage_1893"
        app.selectbox(key="tree_person").select(target)
        app.run()

        open_button = next(button for button in app.button if button.label == "Open full profile")
        open_button.click()
        app.run()

        self.assertEqual(len(app.exception), 0, [exception.value for exception in app.exception])
        self.assertEqual(app.radio(key="nav_page").value, "People")
        self.assertEqual(app.selectbox(key="profile_selector").value, target)

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
        self.assertEqual(app.radio(key="nav_page").value, "People")
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
        self.assertEqual(app.radio(key="nav_page").value, "Explore the Tree")
        tree_picker = next(
            selectbox for selectbox in app.selectbox if selectbox.label == "Center person"
        )
        self.assertEqual(tree_picker.value, target)

    def test_full_family_map_direct_route(self) -> None:
        app = self.logged_in_app(page="full-tree")
        self.assertEqual(app.radio(key="nav_page").value, "Full Family Map")
        self.assertEqual(len(app.exception), 0, [exception.value for exception in app.exception])

    def test_historical_map_and_archive_direct_routes(self) -> None:
        for params, page in (
            ({"page":"map", "person":"harold_h_beverage_1893"}, "Historical Map"),
            ({"page":"map", "event":"event_north_haven_bridge_act_1848"}, "Historical Map"),
            ({"page":"places", "place":"pulpit_harbor_me"}, "Historical Places"),
            ({"page":"archive", "source":"src_bridge_act_1848"}, "Source Archive"),
            ({"page":"archive", "source":"nonexistent"}, "Source Archive"),
        ):
            with self.subTest(params=params):
                app = self.logged_in_app(**params)
                self.assertEqual(app.radio(key="nav_page").value, page)
                self.assertEqual(len(app.exception), 0)

    def test_source_search_and_place_selection(self) -> None:
        app = self.logged_in_app(page="archive")
        app.text_input(key="archive_search").input("Pulpit").run()
        self.assertTrue(any("source records" in c.value for c in app.caption))
        self.assertFalse(app.exception)
        app = self.logged_in_app(page="places", place="pulpit_harbor_me")
        app.selectbox(key="archive_place_selector").select("guatemala").run()
        self.assertEqual(app.query_params["place"], ["guatemala"])
        self.assertTrue(any("country point" in c.value for c in app.caption))
        self.go(app, "Home")
        self.assertNotIn("place", app.query_params)

    def test_map_still_requires_family_login(self) -> None:
        os.environ["APP_PASSWORD"] = "test-family-password"
        app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=30)
        app.query_params["page"] = "map"
        app.run()
        self.assertEqual(len(app.radio), 0)
        self.assertEqual(len(app.text_input), 1)

    def test_full_family_map_person_selection_is_in_map(self) -> None:
        app = self.logged_in_app(page="full-tree")
        self.assertFalse(app.exception, [e.value for e in app.exception])
        self.assertTrue(any(s.label == "Selected relative" for s in app.selectbox))
        # The selected relative is now inside the iframe; a disconnected
        # outer dropdown is intentionally absent.
        self.assertFalse(any(s.label == "Open a profile from the full map" for s in app.selectbox))

    def test_major_interactions_and_direct_routes(self) -> None:
        app = self.logged_in_app()

        self.go(app, "Search")
        app.run()
        app.text_input[0].input("Harold")
        app.run()
        self.assertTrue(any("Harold" in b.label for b in app.button))

        self.go(app, "Explore the Tree")
        app.run()
        app.selectbox(key="relationship_start").select("harold_h_beverage_1893")
        app.selectbox(key="relationship_end").select("albert_glover_beverage_1827")
        app.run()
        self.assertIn("Connected in 2 recorded relationship step", app.success[0].value)

        self.go(app, "Timeline")
        app.run()
        app.text_input(key="whole_timeline_query").input("patent")
        app.run()
        self.assertTrue(any("matching entries" in item.value for item in app.caption))

        profile = self.logged_in_app(page="people", profile="harold_h_beverage_1893")
        self.assertEqual(profile.radio(key="nav_page").value, "People")
        self.assertEqual(profile.selectbox(key="profile_selector").value, "harold_h_beverage_1893")

        event = self.logged_in_app(page="timeline", event="event_harold_patent_1921")
        self.assertEqual(event.radio(key="nav_page").value, "Timeline")
        self.assertTrue(any("Complete Family Timeline" in item.value for item in event.title))

    def test_search_variant_pagination_return_route_and_reset(self):
        app = self.logged_in_app(page="search", q="Bevridge", where="North Haven", results_page="2")
        self.assertEqual(app.text_input(key="global_query").value, "Bevridge")
        self.assertEqual(app.selectbox(key="global_people_page").value, 2)
        self.assertGreater(len(app.selectbox(key="global_people_page").options), 3)
        # Profile controls retain callback routes; results beyond the old 30 cap are usable.
        self.assertTrue(any("Bever" in b.label for b in app.button))
        self.go(app, "Home")
        self.go(app, "Search")
        self.assertEqual(app.text_input(key="global_query").value, "Bevridge")
        self.assertEqual(app.text_input(key="global_where").value, "North Haven")
        self.assertEqual(app.selectbox(key="global_people_page").value, 2)
        app.text_input(key="global_query").input("Eliot Beveridge").run()
        self.assertEqual(app.selectbox(key="global_people_page").value, 1)
        self.assertTrue(any("Elliot" in b.label for b in app.button))
        next(b for b in app.button if b.label == "Clear search").click().run()
        self.assertEqual(app.text_input(key="global_query").value, "")
        self.assertEqual(app.text_input(key="global_where").value, "")
        self.assertFalse(app.exception)

    def test_profile_back_link_survives_connected_relatives(self):
        app = self.logged_in_app(page="people", profile="harold_h_beverage_1893",
                                 return_q="Bevridge", return_where="North Haven", return_page="2")
        # Follow a real family control, then return without logging in again.
        next(b for b in app.button if b.label == "Fremont Beverage").click().run()
        self.assertEqual(app.query_params["profile"], ["fremont_beverage_1856"])
        next(b for b in app.button if "Back to your search" in b.label).click().run()
        self.assertFalse(app.exception)
        self.assertEqual(app.selectbox(key="global_people_page").value, 2)
        self.assertEqual(app.text_input(key="global_query").value, "Bevridge")

    def test_review_routes_corrections_and_authentication(self):
        cases = (
            ({"page":"people", "profile":"diana_daggett_1780"}, "Baptized"),
            ({"page":"people", "profile":"lowell_beveridge_1905"}, "Dorchester, Massachusetts"),
            ({"page":"collection", "view":"Conflict review"}, "11 of 11 questions"),
            ({"page":"collection", "finding":"BF-R008"}, "CRS001"),
            ({"page":"archive", "source":"CRS003"}, "p. xli"),
            ({"page":"collection", "view":"Images"}, "Photographs, maps and objects"),
        )
        for params, expected in cases:
            with self.subTest(params=params):
                app = self.logged_in_app(**params)
                text = " ".join(str(e.value) for kind in ("markdown", "caption", "subheader", "info") for e in getattr(app, kind))
                text += " " + " ".join(b.label for b in app.button)
                self.assertIn(expected, text)
                self.assertFalse(app.exception, [e.value for e in app.exception])
                gated = AppTest.from_file(str(ROOT / "app.py"), default_timeout=30)
                for key, value in params.items():
                    gated.query_params[key] = value
                gated.run()
                self.assertEqual(len(gated.radio), 0)
                self.assertEqual(len(gated.text_input), 1)

    def test_research_filters_survive_leaving_and_returning(self):
        app = self.logged_in_app(page="collection", person="elliot_beverage_1908")
        self.go(app, "Home")
        self.go(app, "Research Collection")
        self.assertFalse(app.exception)
        app.selectbox(key="collection_view").select("Images").run()
        app.selectbox(key="collection_view").select("Findings").run()
        self.assertFalse(app.exception)


if __name__ == "__main__":
    unittest.main()
