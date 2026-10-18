"""Full-book OCR index stays unverified; curated source cards never rewrite the tree."""
from __future__ import annotations

from pathlib import Path
import unittest

from colony_source_review import (
    EXPANDED_FILE, load_book_page_reviews, load_expanded_ocr_navigation,
    pages_for_book_terms, reviews_for_book_page
)
from family_data import index_people, load_site_data, relationship_index
from family_books import load_book_ocr_navigation
from validation import validate_site_data

ROOT=Path(__file__).resolve().parents[1]


class CompleteBookEvidenceReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=load_site_data(ROOT/"data")
        cls.people=index_people(cls.data["people"])
        cls.cards=load_book_page_reviews()

    def test_thirteen_book_source_cards_cover_early_history_and_appendix(self):
        self.assertEqual(len(self.cards),13)
        pages={r["pdf_page"] for r in self.cards}
        self.assertEqual(len(pages),12)
        self.assertTrue({13,15,16,17,18,19,22,288,291,296,297,298} <= pages)
        for r in self.cards:
            with self.subTest(page=r["pdf_page"],title=r["title"]):
                self.assertTrue(1<=r["pdf_page"]<=305)
                self.assertTrue(r["title"] and r["observation"] and r["status"])
                self.assertTrue(r["verification"] and r["why_it_matters"])
                self.assertGreaterEqual(len(r["next_originals"]),2)
                self.assertTrue(all(task.strip() for task in r["next_originals"]))
                self.assertTrue(all(pid in self.people for pid in r["people_ids"]))
                self.assertIn(r,reviews_for_book_page(r["pdf_page"]))
        self.assertEqual(reviews_for_book_page(305),[])

    def test_opposing_matthew_reports_remain_an_identity_problem(self):
        matthews=[r for r in reviews_for_book_page(17)
                  if "Matthew's first and second wives" in r["title"]]
        self.assertEqual(len(matthews),1)
        r=matthews[0]
        self.assertIn("Abigail Dyer",r["observation"])
        self.assertIn("Clarissa Cobb",r["observation"])
        self.assertIn("Abigail Dyer first and Clarissa Cobb second",r["observation"])
        self.assertIn("around 1801", " ".join(r["next_originals"]))
        self.assertIn("original book page",r["verification"].lower())
        # A case entry must not silently create either identity in our tree.
        self.assertNotIn("capt_matthew_beverage",self.people)
        self.assertNotIn("abigail_dyer",self.people)

    def test_boston_tea_party_tradition_is_attributed_not_deleted(self):
        r=reviews_for_book_page(16)[0]
        self.assertIn("Tea Party",r["title"])
        self.assertIn("family tradition",r["status"].lower())
        self.assertIn("unverified",r["status"].lower())
        self.assertIn("Preserve",r["why_it_matters"])
        self.assertIn("marriage return", " ".join(r["next_originals"]))
        self.assertEqual(self.people["thomas_beverage_1750"]["id"],
                         "thomas_beverage_1750")

    def test_visual_review_status_is_distinct_from_independent_proof(self):
        cards=[r for r in self.cards if "visually" in r["verification"].lower()]
        self.assertTrue(cards)
        for r in cards:
            self.assertFalse("independently proven" in r["status"].lower())
        # Duplicate source cards for PDF p17 describe two *different* questions.
        self.assertEqual(len(reviews_for_book_page(17)),2)
        self.assertEqual(validate_site_data(self.data).errors,[])

    def test_full_page_index_or_legacy_fallback_has_explicit_unverified_flags(self):
        raw=load_expanded_ocr_navigation()
        self.assertEqual(raw["scanned_pages"],305)
        self.assertTrue(raw["no_identifying_person_ids"])
        self.assertFalse(raw["contains_full_original_text"])
        terms=raw["terms"]
        self.assertTrue(terms)
        if EXPANDED_FILE.is_file():
            self.assertGreater(len(terms),75)
            self.assertEqual(raw["pdf_sha256"],
                "2eaefbb79aaa7039aab1fb7d493ec5c44792f7a88d32f005b1e67cff2db576ac")
            self.assertEqual(len(raw["page_word_counts"]),305)
            self.assertIn("machine",raw["review_status"].lower())
        else:
            old=load_book_ocr_navigation()
            self.assertEqual(terms,old["hits"])
        for label,pages in terms.items():
            self.assertTrue(label.strip())
            self.assertEqual(pages,sorted(set(pages)))
            self.assertTrue(all(isinstance(p,int) and 1<=p<=305 for p in pages))

    def test_ocr_query_is_page_navigation_only(self):
        nav=load_expanded_ocr_navigation()
        terms=nav["terms"]
        names=[key for key in ("Thomas Beverage","Orris","Rose") if key in terms]
        self.assertTrue(names)
        for key in names:
            self.assertEqual(pages_for_book_terms(nav,[key],both=True),terms[key])
        if "Orris" in terms and "Rose" in terms:
            a,b=set(terms["Orris"]),set(terms["Rose"])
            self.assertEqual(pages_for_book_terms(nav,["Orris","Rose"],both=True),sorted(a&b))
            self.assertEqual(pages_for_book_terms(nav,["Orris","Rose"],both=False),sorted(a|b))
        self.assertEqual(pages_for_book_terms(nav,["unindexed nonexistent term"],both=True),[])

    def test_original_relationship_graph_unchanged(self):
        relations=relationship_index(self.data["people"])
        self.assertFalse(self.people["mercy_beveridge_henry_1753"]["parents"])
        self.assertFalse(self.people["lyford_beveridge_brother_lowell"]["parents"])
        self.assertFalse(relations["parents"].get("nathaniel_beverage_1804_rockland"))
        self.assertNotIn("capt_matthew_beverage",self.people)


if __name__=="__main__":
    unittest.main()
