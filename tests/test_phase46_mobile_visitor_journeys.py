"""Phase 46: visitor-first phone navigation without hiding family history.

Every suggested name is an actual indexed person, not an inferred relation.
All collections remain accessible and only the selected media view renders.
"""
from __future__ import annotations

from pathlib import Path
from urllib.parse import parse_qs, urlsplit
import unittest

from family_data import index_people, load_site_data, relationship_index
from family_search import person_match
from genealogy_integrity import connected_components
from visitor_fast_paths import find_relative_suggestions, family_shortcuts
from visitor_journeys import suggested_paths, JOURNEYS
from validation import validate_site_data
from visitor_ui import MEDIA_SECTIONS

ROOT = Path(__file__).resolve().parents[1]


class Phase46VisitorFastPathsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = load_site_data(ROOT / "data")
        cls.people = index_people(cls.data["people"])
        cls.graph = relationship_index(cls.data["people"])

    def test_live_name_suggestions_are_only_real_reviewed_people(self):
        self.assertEqual(len(self.people), 202)
        names = find_relative_suggestions("Orris", self.people)
        self.assertTrue(names)
        self.assertTrue(any(row["id"] == "orris_beverage_1860" for row in names))
        self.assertTrue(all(row["id"] in self.people for row in names))
        self.assertTrue(all(row["match"] for row in names))
        self.assertEqual(find_relative_suggestions("", self.people), [])
        self.assertEqual(find_relative_suggestions("zzzzabcxyznotaperson", self.people), [])
        self.assertEqual(find_relative_suggestions("Orris", self.people, limit=0), [])
        self.assertLessEqual(len(find_relative_suggestions("Beveridge", self.people)), 7)
        self.assertEqual(len(find_relative_suggestions("Beveridge", self.people, limit=1)), 1)
        # A seven-item instant preview must never alter the complete 202-profile index.
        self.assertEqual(len(self.people), 202)

    def test_search_variant_finds_same_profiles_without_linking_an_unproved_identity(self):
        beverage = find_relative_suggestions("Beverage", self.people, limit=300)
        beveridge = find_relative_suggestions("Beveridge", self.people, limit=300)
        self.assertEqual([p["id"] for p in beverage],
                         [p["id"] for p in beveridge])
        for item in beverage:
            self.assertTrue(person_match("Beverage", self.people[item["id"]]))
            self.assertNotIn("parents", item)
            self.assertNotIn("siblings", item)

    def test_exact_person_stays_selected_in_all_four_paths(self):
        pid = "matthew_beveridge_hope_1837"
        paths = family_shortcuts(pid, self.people)
        self.assertEqual([name for name, _ in paths],
                         ["Life profile", "Family tree", "Family photos", "Original records"])
        self.assertEqual(len(paths), 4)
        urls = [parse_qs(urlsplit(url).query) for _, url in paths]
        self.assertEqual(urls[0], {"page":["people"], "profile":[pid]})
        self.assertEqual(urls[1], {"page":["tree"], "profile":[pid]})
        self.assertEqual(urls[2], {"page":["media"], "person":[pid]})
        self.assertEqual(urls[3]["view"], ["person-exhibit"])
        self.assertEqual(urls[3]["person"], [pid])
        self.assertEqual(urls[3]["section"], ["Original records"])
        self.assertEqual(family_shortcuts("invented-person", self.people), [])

    def test_old_three_way_visitor_journeys_remain_valid(self):
        for section in JOURNEYS:
            self.assertEqual(len(suggested_paths(section)), 3)
        text = (ROOT/"visitor_journeys.py").read_text(encoding="utf-8")
        self.assertIn("family_shortcuts(selected, people_by_id)", text)
        self.assertIn('with st.expander("More places to explore")', text)

    def test_selected_exhibit_section_precedes_expensive_speculative_work(self):
        text = (ROOT/"family_exhibits.py").read_text(encoding="utf-8")
        start = text.index("def render_person_exhibit(")
        text = text[start:]
        self.assertIn('st.selectbox("Explore this relative"', text)
        self.assertLess(text.index('st.selectbox("Explore this relative"'),
                        text.index("open_cases = cases_for_person(person_id)"))
        self.assertLess(text.index("    if selected == SECTIONS[0]:"),
                        text.index("open_cases = cases_for_person(person_id)"))
        self.assertIn('if st.toggle("Show deeper research, open questions', text)
        self.assertIn("render_person_exhibit", (ROOT/"family_exhibits.py").read_text())
        for tool in ("_life_section", "_records_section",
                     "_photographs_section", "_family_section",
                     "conflicting_cases_for_person", "acquisition_for_person",
                     "civic_for_candidate", "trail_for_candidate"):
            self.assertIn(tool, text)

    def test_media_loads_only_active_collection_without_external_embed_iframes(self):
        self.assertEqual(MEDIA_SECTIONS, {
            "photos": "Family photographs",
            "images": "Historical images & maps",
            "documents": "Historical documents",
            "evidence": "Original evidence & investigations",
        })
        code = (ROOT/"visitor_ui.py").read_text(encoding="utf-8")
        media = code.split("def render_media_page() -> None:",1)[1].split(
            "def render_document_page() -> None:",1)[0]
        self.assertIn('if section == "photos":', media)
        self.assertIn('elif section == "images":', media)
        self.assertIn('elif section == "documents":', media)
        self.assertIn('render_colony_photographs()', media)
        self.assertIn("render_exhibit_library()", media)
        self.assertNotIn("st.tabs(", media)
        self.assertNotIn("st.components.v1.iframe", media)
        self.assertIn("case_is_known", media)
        self.assertIn('requested_section = "evidence" if case_is_known else "photos"', media)
        self.assertIn("render_document_page()",code)

    def test_homepage_lookup_is_above_actions_and_directory_stays_continuous(self):
        code = (ROOT/"app.py").read_text(encoding="utf-8")
        home=code.split("def render_home(",1)[1].split("def related_events(",1)[0]
        self.assertLess(home.index("render_home_fast_find(dict(people_by_id))"),
                        home.index('st.subheader("Start exploring")'))
        self.assertIn('route_link("See the complete people directory"', home)
        self.assertNotIn("home_person_lookup",home)
        directory=(ROOT/"visitor_ui.py").read_text(encoding="utf-8").split(
            "def render_people_directory(",1)[1].split("def render_stories_page(",1)[0]
        self.assertIn("for person in matches:",directory)
        self.assertNotIn("Directory page",directory)
        self.assertNotIn("page_count",directory)

    def test_preserve_complete_book_legacy_login_and_canonical_genealogy(self):
        self.assertEqual(validate_site_data(self.data).errors,[])
        self.assertEqual(len(connected_components(self.people, self.graph)),4)
        self.assertEqual(self.people["nathaniel_beverage_1804_rockland"]["parents"],[])
        self.assertEqual(self.people["josiah_b_beverage_1821"]["parents"],[
            "josiah_winslow_beverage_1793","mary_dyer_1795"])
        app=(ROOT/"app.py").read_text(encoding="utf-8")
        self.assertIn("LEGACY_COMPATIBILITY_PASSWORD",app)
        self.assertIn("def check_password()",app)
        photos=(ROOT/"colony_photos.py").read_text(encoding="utf-8")
        self.assertIn("len(photos)",photos)
        self.assertIn("Load 12 more photographs",photos)
        reader=(ROOT/"family_books.py").read_text(encoding="utf-8")
        self.assertIn("Open complete 305-page PDF viewer",reader)


if __name__ == "__main__":
    unittest.main()
