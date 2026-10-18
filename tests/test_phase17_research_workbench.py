"""Full-archive search keeps actual source provenance and uncertainty intact."""
from __future__ import annotations

import unittest
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from family_data import index_people, load_site_data, relationship_index
from family_books import load_book_ocr_navigation, load_book_person_crosswalk
from family_research_index import (CATEGORIES, build_index, case_packet, overview,
                                   search_index)
from family_research_workbench import pages_for_terms
from relationship_evidence import audited_edges
from research_collection import CollectionIndex

ROOT = Path(__file__).resolve().parents[1]


class UnifiedArchiveWorkbenchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = load_site_data(ROOT / "data")
        cls.people = index_people(cls.data["people"])
        cls.index = build_index(cls.people)
        cls.lookup = {row["id"]: row for row in cls.index}
        cls.stats = overview(cls.index)
        cls.crosswalk = load_book_person_crosswalk()
        cls.nav = load_book_ocr_navigation()

    def test_every_collection_indexed_once_with_grounded_navigation(self):
        self.assertGreater(len(self.index), 450)
        self.assertEqual(len(self.lookup), len(self.index))
        self.assertEqual(self.stats["total"], len(self.index))
        self.assertEqual(set(self.stats["by_category"]), set(CATEGORIES))
        self.assertEqual(
            self.stats["by_category"]["Existing family profiles"], len(self.people)
        )
        for entry in self.index:
            with self.subTest(record=entry["id"]):
                self.assertTrue(entry["title"] and entry["category"] and entry["status"])
                self.assertIn(entry["category"], CATEGORIES)
                self.assertTrue(entry["route"].startswith("?page="))
                route = parse_qs(urlsplit(entry["route"]).query)
                self.assertIn(route["page"][0], {
                    "people", "timeline", "collection", "family-books", "stories", "archive"
                })
                self.assertTrue(all(pid in self.people for pid in entry["person_ids"]))
                self.assertTrue(all(1 <= page <= 305 for page in entry["pages"]))
                for source in entry["sources"]:
                    uri = urlsplit(source["url"])
                    self.assertEqual(uri.scheme, "https")
                    self.assertTrue(uri.hostname)

    def test_scanned_pages_remain_ocr_word_presence_not_verified_identity(self):
        ocr = [x for x in self.index if x["category"] == "Scanned book OCR leads"]
        self.assertEqual(len(ocr), self.stats["unique_book_pages"])
        self.assertGreater(len(ocr), 150)
        self.assertEqual(self.nav["scanned_pages"], 305)
        self.assertEqual(len(self.nav["hits"]), 35)
        for row in ocr:
            self.assertEqual(row["person_ids"], [])
            self.assertIn("NOT identity proof", row["status"])
            self.assertIn("not establish the identity", row["limits"])
            self.assertTrue(row["route"].startswith("?page=family-books&book_page="))
            self.assertEqual(len(row["pages"]), 1)

    def test_photographs_are_author_attributed_only_by_exact_reviewed_id(self):
        photos = [x for x in self.index if x["category"] == "Scanned book photographs"]
        self.assertEqual(len(photos), 82)
        self.assertGreaterEqual(self.stats["profile_ids_with_photo"], 20)
        referenced = set()
        for row in self.crosswalk["linked_people"]:
            for page in row["pdf_pages"]:
                if "photo:" + str(page) in self.lookup:
                    referenced.add((row["person_id"], page))
                    self.assertIn(row["person_id"],
                                  self.lookup["photo:" + str(page)]["person_ids"])
        self.assertTrue(referenced)
        p57 = self.lookup["photo:57"]
        self.assertIn("lowell_pierson_beveridge_jr_1930", p57["person_ids"])
        self.assertNotIn("lowell_beveridge_1905", p57["person_ids"])
        self.assertIn("not independently certified", p57["status"])

    def test_unresolved_names_never_turn_into_new_family_profiles(self):
        book = [x for x in self.index if x["id"].startswith("unresolved:")]
        self.assertEqual(len(book), 16)
        self.assertEqual(self.stats["unresolved_book_names"], 16)
        hanson = next(x for x in book if "Hanson" in x["title"])
        self.assertEqual(hanson["person_ids"], [])
        self.assertIn("unresolved", hanson["status"].lower())
        self.assertTrue(hanson["pages"])
        self.assertFalse(self.people["mercy_beveridge_henry_1753"]["parents"])
        self.assertNotIn("capt_matthew_beverage", self.people)

    def test_cross_search_intersection_and_union_are_only_page_numbers(self):
        nav = self.nav
        a = set(nav["hits"]["Orris"])
        b = set(nav["hits"]["Rose"])
        and_pages = pages_for_terms(nav, ["Orris", "Rose"])
        or_pages = pages_for_terms(nav, ["Orris", "Rose"], require_all=False)
        self.assertEqual(and_pages, sorted(a & b))
        self.assertEqual(or_pages, sorted(a | b))
        self.assertTrue(set(and_pages).issubset(or_pages))
        self.assertEqual(pages_for_terms(nav, []), [])
        self.assertEqual(pages_for_terms(nav, ["nonexistent-term"]), [])

    def test_exact_person_filter_never_attaches_ocr_surname_mentions(self):
        results = search_index(self.index, person_id="orris_beverage_1860")
        self.assertTrue(results)
        self.assertTrue(all("orris_beverage_1860" in x["person_ids"] for x in results))
        self.assertFalse(any(x["category"] == "Scanned book OCR leads" for x in results))
        self.assertEqual(search_index(self.index, person_id="no_such_person"), [])
        self.assertTrue(search_index(self.index, query="Orris"))
        without_ocr = search_index(self.index, query="Orris", show_ocr=False)
        self.assertTrue(all(x["category"] != "Scanned book OCR leads"
                            for x in without_ocr))
        self.assertEqual(search_index(self.index, query="xxyyz-unknown-family-word"), [])

    def test_open_case_and_citations_export_exact_limitations(self):
        james = self.lookup["exhibit:1749-intention-bangor-1888"]
        self.assertIn("intention", james["summary"].lower())
        self.assertIn("not proven", james["limits"].lower())
        report = case_packet(james)
        self.assertIn("Original records and links", report)
        self.assertIn("Marriage intention only", report)
        self.assertIn("archives.mainegenealogy.net", report)
        self.assertIn("not an independent verification", report)
        self.assertNotIn("confirmed wedding", report.casefold())
        case = next(x for x in self.index
                    if x["id"].startswith("ancestry:") and "nathaniel" in x["id"])
        self.assertIn("unverified", case["limits"].lower()) if "unverified" in case["limits"].lower() else self.assertIn("not", case["limits"].lower())
        self.assertTrue(case["sources"])
        self.assertEqual(len(self.lookup), len(self.index))

    def test_full_research_collection_findings_and_sources_retain_original_grades(self):
        collection = CollectionIndex.load()
        findings = [x for x in self.index if x["category"] == "Historical research findings"]
        sources = [x for x in self.index if x["category"] == "Original source register"]
        self.assertEqual(len(findings), len(collection.findings))
        self.assertEqual(len(sources), len(collection.sources))
        for rid, raw in collection.findings.items():
            item = self.lookup["finding:" + rid]
            self.assertIn(raw["Confidence"], item["status"])
            self.assertEqual(item["limits"], raw["Notes about uncertainty"])
            self.assertEqual(item["person_ids"], sorted(set(raw["Navigation"]["people_ids"])))
            self.assertEqual(item["route"], "?page=collection&finding=" + rid)
        for sid, raw in collection.sources.items():
            entry = self.lookup["register:" + sid]
            self.assertEqual(entry["route"], "?page=archive&source=" + sid)
            self.assertIn(raw.get("Viewed status") or "Unknown", entry["limits"])
        self.assertTrue(any("Possible lead" in x["status"] for x in findings))
        self.assertTrue(any("Conflict" in x["status"] for x in findings))

    def test_workbench_does_not_mutate_genealogy_or_reviewed_edges(self):
        originals = relationship_index(self.data["people"])
        before = audited_edges(self.people, originals)
        build_index(self.people)
        after = audited_edges(self.people, relationship_index(self.data["people"]))
        self.assertEqual([x["key"] for x in before], [x["key"] for x in after])
        self.assertEqual(self.people["lyford_beveridge_brother_lowell"]["parents"], [])
        self.assertEqual(self.people["mercy_beveridge_henry_1753"]["parents"], [])

if __name__ == "__main__":
    unittest.main()
