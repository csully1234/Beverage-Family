"""Phase 38 — visitor journeys between exact people, photo pages and originals.

No original relationships, identities, copyright permission, source files,
password settings or questionable OCR matches are changed by navigation.
"""
from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit
import unittest

from colony_photos import (
    load_colony_photo_catalog, _photo_person_changed,
    reset_photograph_count,
)
from family_photo_navigation import (
    photo_gallery_route, exact_photo_pages, photo_matches, selected_photo,
)
from family_books import load_book_person_crosswalk, book_pages_for_person
from family_data import index_people, load_site_data, relationship_index
from visitor_journeys import current_person
from validation import validate_site_data

ROOT = Path(__file__).resolve().parents[1]


class Phase38PhotographsNavigationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = load_site_data(ROOT / "data")
        cls.people = index_people(cls.data["people"])
        cls.links = relationship_index(cls.data["people"])
        cls.catalog = load_colony_photo_catalog()
        cls.photos = cls.catalog["photos"]
        cls.crosswalk = load_book_person_crosswalk()
        cls.pages = exact_photo_pages(cls.crosswalk, set(cls.people))

    def test_every_cataloged_book_photo_page_remains_in_complete_gallery(self):
        self.assertEqual(len(self.photos), 82)
        self.assertEqual(len({int(photo["pdf_page"]) for photo in self.photos}),
                         len(self.photos))
        rows = photo_matches(self.photos, self.crosswalk)
        self.assertEqual(len(rows), len(self.photos))
        self.assertEqual({int(photo["pdf_page"]) for photo in rows},
                         {int(photo["pdf_page"]) for photo in self.photos})
        self.assertEqual(rows, sorted(rows, key=lambda p: p["pdf_page"]))
        reverse = photo_matches(self.photos, self.crosswalk,
                                order="Book order (last first)")
        self.assertEqual(list(reversed(rows)), reverse)
        by_subject = photo_matches(self.photos, self.crosswalk, order="Subject A–Z")
        self.assertEqual({p["pdf_page"] for p in rows},
                         {p["pdf_page"] for p in by_subject})

    def test_selected_person_pages_use_exact_crosswalk_not_ocr_name_guess(self):
        pid = "orris_beverage_1860"
        self.assertIn(pid, self.pages)
        expected = set(book_pages_for_person(pid, self.crosswalk))
        self.assertEqual(self.pages[pid], expected)
        actual_photos = photo_matches(self.photos, self.crosswalk, person_id=pid)
        self.assertEqual({p["pdf_page"] for p in actual_photos},
                         expected & {p["pdf_page"] for p in self.photos})
        self.assertTrue(actual_photos)
        self.assertEqual(photo_matches(
            self.photos, self.crosswalk, person_id="entirely_nonexistent_person"), [])
        # A person's book crosswalk is not a portrait authentication database.
        self.assertNotIn("matched_person", actual_photos[0])
        self.assertNotIn("verified_portrait", actual_photos[0])

    def test_text_search_is_human_readable_but_not_identity_attribution(self):
        fake = [
            {"pdf_page": 22, "title": "Orris Beverage portrait?",
             "caption_summary": "No original identification", "section": "Portrait"},
            {"pdf_page": 55, "title": "Unlabeled seaside cottage",
             "caption_summary": "Orris was never mentioned here", "section": "Places"},
        ]
        empty_crosswalk = {"linked_people": []}
        self.assertEqual(len(photo_matches(fake, empty_crosswalk, search="Orris")), 2)
        self.assertEqual(photo_matches(
            fake, empty_crosswalk, person_id="orris_beverage_1860"), [])
        self.assertEqual(
            photo_matches(fake, {"linked_people": [
                {"person_id": "orris_beverage_1860", "pdf_pages": [22]}
            ]}, person_id="orris_beverage_1860", category="Portrait"),
            [fake[0]])

    def test_shareable_links_are_exact_and_reject_invented_gallery_items(self):
        self.assertEqual(photo_gallery_route(), "?page=media")
        self.assertEqual(photo_gallery_route(person_id="orris_beverage_1860"),
                         "?page=media&person=orris_beverage_1860")
        self.assertEqual(photo_gallery_route(pdf_page=49),
                         "?page=media&photo_page=49")
        complex_id = "some id&related=other"
        route = photo_gallery_route(person_id=complex_id, pdf_page=49)
        values = parse_qs(urlsplit(route).query)
        self.assertEqual(values, {"page": ["media"], "person": [complex_id],
                                  "photo_page": ["49"]})
        self.assertIsNone(selected_photo(self.photos, "not-a-page"))
        self.assertIsNone(selected_photo(self.photos, 9999))
        sample = self.photos[0]
        self.assertIs(selected_photo(self.photos, sample["pdf_page"]), sample)
        self.assertIsNone(selected_photo(self.photos, -1))

    def test_invalid_crosswalk_ids_and_nonpositive_pages_are_not_added(self):
        fake = {"linked_people": [
            {"person_id": "known", "pdf_pages": [20, "20", "junk", 0, -4]},
            {"person_id": "not_indexed", "pdf_pages": [31]},
        ]}
        self.assertEqual(exact_photo_pages(fake, {"known"}), {"known": {20}})
        self.assertEqual(exact_photo_pages({}, {"known"}), {})

    def test_photo_relative_permalink_beats_previous_tree_selection(self):
        earlier = "matthew_beveridge_hope_1837"
        pid = "orris_beverage_1860"
        fake = SimpleNamespace(session_state={"_active_person": earlier,
                                              "tree_person": earlier},
                               query_params={"page": "media", "person": pid})
        with patch("visitor_journeys.st", fake):
            self.assertEqual(current_person(self.people, "Photographs & Documents"),
                             pid)
            self.assertEqual(current_person(self.people, "Timeline"), pid)
            self.assertEqual(current_person(self.people, "Family Books"), pid)
            # Pages not intended to read the photo's person query retain the
            # last valid viewer selection.
            self.assertEqual(current_person(self.people, "Explore the Tree"), earlier)
            fake.query_params["person"] = "not-indexed"
            self.assertEqual(current_person(self.people, "Photographs & Documents"),
                             earlier)

    def test_switching_photo_relative_removes_stale_pinned_page_and_search(self):
        pid = "orris_beverage_1860"
        fake = SimpleNamespace(session_state={
            "colony_photo_person": pid, "colony_photo_visible": 82,
            "colony_photo_search": "stale text",
            "colony_photo_category": "Places",
        }, query_params={"page": "media", "photo_page": "49", "person": "old"})
        with patch("colony_photos.st", fake):
            _photo_person_changed()
            self.assertEqual(fake.query_params["person"], pid)
            self.assertNotIn("photo_page", fake.query_params)
            self.assertEqual(fake.session_state["colony_photo_visible"], 12)
            self.assertEqual(fake.session_state["colony_photo_search"], "")
            self.assertEqual(fake.session_state["colony_photo_category"],
                             "All photographs")
            fake.session_state["colony_photo_person"] = ""
            _photo_person_changed()
            self.assertNotIn("person", fake.query_params)

    def test_pinned_photo_is_shown_before_batch_and_source_scan_first(self):
        gallery = (ROOT / "colony_photos.py").read_text(encoding="utf-8")
        book = (ROOT / "family_books.py").read_text(encoding="utf-8")
        self.assertLess(gallery.index("if target is not None:"),
                        gallery.index("remaining = [photo for photo in matches"))
        self.assertLess(book.index("    render_scanned_page(book, int(selected), width=1080)"),
                        book.index("        if st.toggle(\"Open complete 305-page PDF viewer\""))
        self.assertIn("photo_gallery_route(pdf_page=int(selected))", book)
        self.assertIn("photo_gallery_route(person_id=overview[\"id\"])",
                      (ROOT / "family_exhibits.py").read_text(encoding="utf-8"))
        self.assertIn("photo_gallery_route(person_id=person_id)",
                      (ROOT / "app.py").read_text(encoding="utf-8"))
        self.assertIn("render_colony_photographs()", (ROOT / "visitor_ui.py").read_text(encoding="utf-8"))
        self.assertNotIn("full_book_url(", book)

    def test_genealogy_and_shared_password_are_not_modified(self):
        self.assertEqual(validate_site_data(self.data).errors, [])
        self.assertEqual(len(self.people), 202)
        self.assertEqual(self.people["matthew_beveridge_hope_1837"]["parents"], [])
        self.assertEqual(self.people["clarissa_beveridge_widow_1837"]["children"], [])
        app = (ROOT / "app.py").read_text(encoding="utf-8")
        self.assertIn("LEGACY_COMPATIBILITY_PASSWORD", app)
        self.assertIn("def check_password()", app)
        self.assertIn("check_password()", app)


if __name__ == "__main__":
    unittest.main()
