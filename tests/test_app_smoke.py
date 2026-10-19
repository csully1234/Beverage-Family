from __future__ import annotations

import os
import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest


ROOT = Path(__file__).resolve().parents[1]


class StreamlitSmokeTests(unittest.TestCase):
    def go(self, app, page):
        groups = {"Home": ("Home",), "Search": ("Search",),
                  "Family": ("People", "Explore the Tree", "Full Family Map"),
                  "History": ("Timeline", "Stories & Discoveries", "Historical Discoveries"),
                  "Places": ("Historical Places", "Historical Map"),
                  "Archive": ("Photographs & Documents", "Family Books", "Historical Sources")}
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
            "Historical Sources",
            "People",
            "Timeline",
            "Stories & Discoveries",
            "Historical Discoveries",
            "Photographs & Documents",
            "Family Books",
        ):
            with self.subTest(page=page):
                self.go(app, page)
                app.run()
                self.assertEqual(
                    len(app.exception),
                    0,
                    [exception.value for exception in app.exception],
                )

    def test_family_discoveries_are_browsable_without_technical_inventories(self) -> None:
        app = self.logged_in_app(page="collection")
        self.assertEqual(app.radio(key="nav_page").value, "Historical Discoveries")
        self.assertFalse(app.exception, [e.value for e in app.exception])
        self.assertTrue(any("57 historical discoveries" in c.value for c in app.caption))
        self.assertFalse(any(s.label == "Research inventory" for s in app.selectbox))
        app.text_input(key="family_discoveries_search").input("IsleBuilt").run()
        self.assertFalse(app.exception)
        app.text_input(key="family_discoveries_search").input("").run()
        self.assertTrue(any("57 historical discoveries" in c.value for c in app.caption))

    def test_old_search_log_link_is_a_family_discoveries_view(self) -> None:
        app = self.logged_in_app(page="collection", view="Inventories", inventory="Search Log")
        self.assertEqual(app.radio(key="nav_page").value, "Historical Discoveries")
        self.assertFalse(app.exception, [e.value for e in app.exception])
        self.assertFalse(any(s.label == "Research inventory" for s in app.selectbox))
        self.assertFalse(any("436 of 436" in c.value for c in app.caption))

    def test_family_focused_navigation_and_historical_deep_links(self) -> None:
        from app import NAV_GROUPS
        self.assertEqual(list(NAV_GROUPS), ["Home", "Search", "Family", "History", "Places", "Archive"])
        sections = {name for pages in NAV_GROUPS.values() for name in pages}
        self.assertFalse({"Research Desk", "Research Collection", "Sources & Method",
                          "Source Archive", "Research inventory"} & sections)
        self.assertTrue({"Timeline", "Stories & Discoveries", "Historical Discoveries",
                         "Family Books", "Photographs & Documents", "Historical Sources"} <= sections)
        for params, destination in (
            ({"page":"research"}, "Historical Discoveries"),
            ({"page":"sources"}, "Historical Sources"),
            ({"page":"collection", "view":"Inventories", "inventory":"Search Log"}, "Historical Discoveries"),
        ):
            with self.subTest(params=params):
                app = self.logged_in_app(**params)
                self.assertEqual(app.radio(key="nav_page").value, destination)
                self.assertFalse(app.exception, [x.value for x in app.exception])
                self.assertFalse(any(x.label == "Research inventory" for x in app.selectbox))
        document = self.logged_in_app(page="documents", doc="thomas-1786")
        self.assertFalse(document.exception, [x.value for x in document.exception])
        self.assertTrue(any("Thomas" in str(x.value) for x in document.title))
        self.assertTrue(any("1786" in str(x.value) for x in document.caption))

    def test_profile_with_unresolved_spouse_and_multiple_parents_renders_cleanly(self) -> None:
        """Regression for False text and red error on Sandra's family summary."""
        app = self.logged_in_app(page="people", profile="sandra_beverage_1947")
        self.assertFalse(app.exception, [error.value for error in app.exception])
        buttons = [button.label for button in app.button]
        self.assertIn("Eleanor Mae Sargent", buttons)
        self.assertIn("Samuel Hiram Beverage", buttons)
        notes = [caption.value for caption in app.caption]
        self.assertTrue(any("profile not yet entered" in note for note in notes))
        self.assertFalse(any(str(note).strip() == "False" for note in notes))
        self.assertFalse(any(str(element.value).strip() == "False" for element in app.markdown))

    def test_family_photo_gallery_and_event_citation_access(self):
        app = self.logged_in_app(page="media")
        self.assertFalse(app.exception, [e.value for e in app.exception])
        self.assertTrue(any("Family photographs" in tab.label for tab in app.tabs))
        self.assertTrue(any("82 cataloged photo-bearing pages" in str(x.value) for x in app.caption))
        self.assertIn("Load 12 more photographs", app.button(key="colony_photo_load_more").label)
        app.button(key="colony_photo_load_more").click().run()
        self.assertFalse(app.exception, [e.value for e in app.exception])

    def test_event_with_two_citations_shows_individual_references(self):
        app = self.logged_in_app(page="timeline", event="event_birth_hiram_stone_beverage_1886")
        self.assertFalse(app.exception, [e.value for e in app.exception])
        self.assertTrue(any("source references and available records" in x.label for x in app.expander))

    def test_authorized_book_page_route_renders_before_binary_is_uploaded(self) -> None:
        app = self.logged_in_app(page="family-books", book_page="49")
        self.assertFalse(app.exception, [e.value for e in app.exception])
        self.assertTrue(any("The Colony" in str(x.value) for x in app.markdown))
        self.assertEqual(app.number_input(key="book_selected_page").value, 49)
        self.assertTrue(any("PDF" in str(x.value) for x in app.caption))

    def test_book_next_previous_buttons_do_not_mutate_initialized_widget(self) -> None:
        """Regression for production crash at render_book_reader, Next page."""
        app = self.logged_in_app(page="family-books", book_page="49")
        self.assertEqual(app.number_input(key="book_selected_page").value, 49)
        self.assertFalse(app.exception, [e.value for e in app.exception])
        app.button(key="book_next").click().run()
        self.assertFalse(app.exception, [e.value for e in app.exception])
        self.assertEqual(app.number_input(key="book_selected_page").value, 50)
        self.assertEqual(app.query_params.get("book_page"), ["50"])
        app.button(key="book_prev").click().run()
        self.assertFalse(app.exception, [e.value for e in app.exception])
        self.assertEqual(app.number_input(key="book_selected_page").value, 49)
        app.number_input(key="book_selected_page").set_value(305).run()
        self.assertFalse(app.exception, [e.value for e in app.exception])
        self.assertEqual(app.query_params.get("book_page"), ["305"])
        self.assertTrue(app.button(key="book_next").disabled)

    def test_illustration_page_jump_works_without_pdf(self) -> None:
        app = self.logged_in_app(page="family-books")
        app.button(key="book_evidence_colony-amelia-hanson").click().run()
        self.assertFalse(app.exception, [e.value for e in app.exception])
        self.assertEqual(app.number_input(key="book_selected_page").value, 49)
        self.assertEqual(app.query_params.get("book_page"), ["49"])

    def test_research_deep_links_and_existing_profile_context(self) -> None:
        cases = (
            ({"page": "collection", "finding": "BF-R033"}, "Registration dates are not deed dates"),
            ({"page": "collection", "finding": "BF-R049"}, "Duplicate suspected"),
            ({"page": "archive", "source": "SRC118"}, "Findings citing this source"),
            ({"page": "people", "profile": "elliot_beverage_1908"}, "IsleBuilt"),
            ({"page": "collection", "target": "BF-G001"}, "Historical Discoveries"),
            ({"page": "collection", "view": "Inventories", "inventory": "Properties and Deeds"}, "Historical Discoveries"),
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
            ({"page":"archive", "source":"src_bridge_act_1848"}, "Historical Sources"),
            ({"page":"archive", "source":"nonexistent"}, "Historical Sources"),
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

    def test_runtime_source_id_reports_loaded_people_implementation(self) -> None:
        from app import runtime_source_identity
        identity, variant = runtime_source_identity()
        self.assertIn("app ", identity)
        self.assertIn("people ", identity)
        self.assertEqual(variant, "continuous")

    def test_full_family_map_person_selection_is_in_map(self) -> None:
        app = self.logged_in_app(page="full-tree")
        self.assertFalse(app.exception, [e.value for e in app.exception])
        self.assertTrue(any(s.label == "Selected relative" for s in app.selectbox))
        # The selected relative is now inside the iframe; a disconnected
        # outer dropdown is intentionally absent.
        self.assertFalse(any(s.label == "Open a profile from the full map" for s in app.selectbox))

    def test_full_map_selection_persists_into_focused_tree(self) -> None:
        target = "harold_h_beverage_1893"
        app = self.logged_in_app(page="full-tree")
        self.assertFalse(app.exception, [e.value for e in app.exception])
        app.selectbox(key="full_map_person").select(target).run()
        self.assertEqual(app.session_state["tree_person"], target)
        back = next(button for button in app.button if button.label == "Back to focused tree")
        back.click().run()
        self.assertFalse(app.exception, [e.value for e in app.exception])
        self.assertEqual(app.selectbox(key="tree_person").value, target)

    def test_full_map_bridge_updates_both_person_controls(self) -> None:
        target = "harold_h_beverage_1893"
        app = self.logged_in_app(page="full-tree")
        app.session_state["_pending_full_map_person"] = target
        app.session_state["_pending_full_map_action"] = "select"
        app.run()
        self.assertFalse(app.exception, [e.value for e in app.exception])
        self.assertEqual(app.selectbox(key="full_map_person").value, target)
        self.assertEqual(app.session_state["tree_person"], target)

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
            ({"page":"collection", "view":"Conflict review"}, "Historical Discoveries"),
            ({"page":"collection", "finding":"BF-R008"}, "CRS001"),
            ({"page":"archive", "source":"CRS003"}, "p. xli"),
            ({"page":"media"}, "Photographs & Documents"),
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

    def test_matthew_probate_branch_is_navigable_with_no_invented_mother(self):
        person_id = "matthew_beveridge_hope_1837"
        app = self.logged_in_app(page="people", profile=person_id)
        self.assertFalse(app.exception, [error.value for error in app.exception])
        text = " ".join(str(element.value)
                        for kind in ("markdown", "caption", "subheader", "info")
                        for element in getattr(app, kind))
        self.assertIn("Matthew", text)
        self.assertIn("Beveridge", text)
        app = self.logged_in_app(page="collection", view="waldo-probate", scan="9")
        self.assertFalse(app.exception, [error.value for error in app.exception])
        labels = " ".join(element.label for element in app.selectbox)
        self.assertIn("31", labels) if "31" in labels else self.assertIn(
            "Choose a source image", labels)

    def test_phase24_clarissa_origins_and_sourced_profile_are_browsable(self):
        page = self.logged_in_app(page="collection", view="family-origins")
        self.assertFalse(page.exception, [error.value for error in page.exception])
        words = " ".join(str(element.value)
                         for name in ("title", "markdown", "caption", "info", "subheader")
                         for element in getattr(page, name))
        self.assertIn("Clarissa", words)
        self.assertIn("1786", words)
        self.assertIn("Cobb", words)
        profile = self.logged_in_app(page="people",
                                     profile="clarissa_beveridge_widow_1837")
        self.assertFalse(profile.exception, [error.value for error in profile.exception])
        profile_text = " ".join(str(x.value) for kind in ("markdown", "caption", "subheader")
                                for x in getattr(profile, kind))
        self.assertIn("Clarissa", profile_text)

    def test_family_museum_exhibit_person_deep_link_and_sections(self):
        pid = "matthew_beveridge_hope_1837"
        app = self.logged_in_app(page="collection", view="person-exhibit", person=pid)
        self.assertFalse(app.exception, [error.value for error in app.exception])
        self.assertEqual(app.radio(key="exhibit_section_" + pid).value, "Life & timeline")
        self.assertTrue(any("Matthew" in str(e.value) for e in app.title))
        self.assertTrue(any("Dated entries" in e.label for e in app.metric))
        app.radio(key="exhibit_section_" + pid).set_value("Original records").run()
        self.assertFalse(app.exception, [error.value for error in app.exception])
        self.assertEqual(app.query_params.get("section"), ["Original records"])
        self.assertTrue(any("Find the actual evidence" in str(e.value)
                            for e in app.subheader))
        app.radio(key="exhibit_section_" + pid).set_value("Family connections").run()
        self.assertFalse(app.exception, [error.value for error in app.exception])
        self.assertIn("Clarissa", " ".join(b.label for b in app.button))

    def test_family_museum_book_images_and_missing_profile_are_truthful(self):
        pid = "lowell_pierson_beveridge_jr_1930"
        app = self.logged_in_app(page="collection", view="person-exhibit",
                                 person=pid, section="Photographs & book")
        self.assertFalse(app.exception, [error.value for error in app.exception])
        self.assertEqual(app.radio(key="exhibit_section_" + pid).value, "Photographs & book")
        self.assertTrue(any("original PDF page" in str(e.value) for e in app.caption))
        missing = self.logged_in_app(page="collection", view="person-exhibit",
                                     person="nonexistent_hist_person")
        self.assertFalse(missing.exception, [e.value for e in missing.exception])
        self.assertTrue(any("isn't in the reviewed family index" in str(w.message)
                            for w in missing.warning))

    def test_family_home_exhibits_and_profile_entry_point(self):
        home = self.logged_in_app(page="home")
        self.assertFalse(home.exception, [e.value for e in home.exception])
        self.assertTrue(any("Step into a family life" in str(e.value)
                            for e in home.subheader))
        self.assertTrue(any(b.label == "Explore this person's life"
                            for b in home.button))
        profile = self.logged_in_app(page="people", profile="matthew_beveridge_hope_1837")
        self.assertFalse(profile.exception, [e.value for e in profile.exception])
        self.assertTrue(any("life, documents and family photographs" in b.label
                            for b in profile.button))

    def test_original_waldo_probate_deep_links_show_reviewed_court_evidence(self):
        app = self.logged_in_app(page="collection", view="waldo-probate", scan="31")
        self.assertFalse(app.exception, [error.value for error in app.exception])
        displayed = " ".join(
            str(element.value)
            for name in ("title", "markdown", "caption", "info", "subheader", "warning")
            for element in getattr(app, name)
        )
        self.assertIn("Waldo County probate", displayed)
        self.assertIn("Ezekiel", displayed)
        self.assertIn("31", displayed)
        self.assertIn("not publicly", displayed.lower())

    def test_family_discoveries_remain_after_navigating_away(self):
        app = self.logged_in_app(page="collection")
        self.go(app, "Home")
        self.go(app, "Historical Discoveries")
        self.assertFalse(app.exception)
        self.assertFalse(any(s.label == "Research inventory" for s in app.selectbox))


    def test_shared_full_family_map_link_selects_relative_and_keeps_focus(self):
        person = "mercy_beveridge_henry_1753"
        app = self.logged_in_app(page="full-tree", profile=person)
        self.assertFalse(app.exception, [error.value for error in app.exception])
        self.assertEqual(app.selectbox(key="full_map_person").value, person)
        next(button for button in app.button
             if button.label == "Back to focused tree").click().run()
        self.assertFalse(app.exception, [error.value for error in app.exception])
        self.assertEqual(app.selectbox(key="tree_person").value, person)
        self.assertEqual(app.query_params["profile"], [person])



if __name__ == "__main__":
    unittest.main()
