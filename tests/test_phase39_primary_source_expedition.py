"""Phase 39: hold potential ancestral bridges to a genuine original-record standard."""
from __future__ import annotations

import csv
import io
import json
from pathlib import Path
import unittest

from family_data import load_site_data, index_people, relationship_index
from family_research_index import build_index, search_index
from genealogy_integrity import connected_components
from primary_source_expedition import (
    load_expedition, branch_status, source_progress, expedition_csv,
    expedition_route,
)
from validation import validate_site_data

ROOT = Path(__file__).resolve().parents[1]


class Phase39PrimarySourceExpeditionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = load_site_data(ROOT / "data")
        cls.people = index_people(cls.data["people"])
        cls.relationships = relationship_index(cls.data["people"])
        cls.research = load_expedition()
        cls.sources = {item["id"]: item for item in cls.research["sources"]}
        cls.cases = {item["id"]: item for item in cls.research["cases"]}

    def test_all_historic_investigations_remain_visible_and_retrievable(self):
        self.assertEqual(len(self.cases), 4)
        self.assertEqual(len(self.sources), 11)
        stats = source_progress(self.research)
        self.assertEqual(stats["retrieval_targets"], 10)
        self.assertEqual(stats["originals_read_or_reviewed"], 1)
        self.assertEqual({case["priority"] for case in self.cases.values()},
                         {1, 2, 3, 4})
        for case in self.cases.values():
            self.assertTrue(case["question"])
            self.assertTrue(case["not_proved"])
            self.assertGreaterEqual(len(case["next_checks"]), 4)
            self.assertTrue(set(case["source_ids"]) <= set(self.sources))
            self.assertTrue(case["existing_route"].startswith("?page="))
            self.assertTrue(all(pid in self.people for pid in case["people_ids"]))
        self.assertIn("case=nathaniel-rockland-parentage",
                      expedition_route("nathaniel-rockland-parentage"))

    def test_nathaniel_reported_parentage_is_only_a_derivative_candidate(self):
        case = self.cases["nathaniel-rockland-parentage"]
        self.assertIn("John White", case["working_theory"])
        self.assertIn("Eaton", case["working_theory"])
        self.assertIn("NOT", case["not_proved"].upper() + " NOT")
        self.assertFalse(self.sources["nathaniel-compiled-1803"]["original_inspected"])
        self.assertEqual(self.sources["nathaniel-compiled-1803"]["class"],
                         "derivative_parentage_hypothesis")
        nathaniel = self.people["nathaniel_beverage_1804_rockland"]
        self.assertFalse(nathaniel["parents"])
        self.assertNotIn("nathaniel_beverage_1804_rockland",
                         self.people["john_white_beverage_1774"]["children"])
        status = branch_status(case, self.people, self.relationships)
        self.assertTrue(status["cross_component_lead"])
        self.assertGreater(len(status["component_numbers"]), 1)
        self.assertEqual(status["component_count"], 4)

    def test_1837_deed_must_not_be_assigned_to_captain_thomas_died_1834(self):
        deed = self.sources["deed-1837-thomas-to-james"]
        captain = self.people["thomas_beverage_1750"]
        self.assertEqual(captain["death_date"], "1834-10-04")
        self.assertEqual(deed["year"], "1837")
        self.assertIn("CHRONOLOGY CONFLICT", deed["limits"])
        self.assertIn("cannot automatically", deed["limits"])
        self.assertFalse(deed["original_inspected"])
        index = build_index(self.people)
        record = next(r for r in index
                      if r["id"] == "expedition-source:deed-1837-thomas-to-james")
        self.assertEqual(record["person_ids"], [])
        # The general Josiah case may mention the chronological conflict,
        # but the recorded deed itself must not become a source attached
        # personally to a man who, according to the effective profile,
        # had been dead for almost three years.

    def test_vinalhaven_boston_and_newspaper_locators_are_exact_but_unread(self):
        self.assertIn("7596929", self.sources["vinalhaven-josiah-1793"]["locator"])
        self.assertIn("209 of 837", self.sources["vinalhaven-josiah-1793"]["locator"])
        self.assertIn("8130800", self.sources["trinity-1774-thomas-mercy"]["locator"])
        self.assertIn("459 of 798", self.sources["trinity-1774-thomas-mercy"]["locator"])
        self.assertIn("8203644", self.sources["lewiston-josiah-1858"]["locator"])
        self.assertIn("392 of 814", self.sources["lewiston-josiah-1858"]["locator"])
        for label in ("vinalhaven-josiah-1793",
                      "trinity-1774-thomas-mercy",
                      "lewiston-josiah-1858"):
            source = self.sources[label]
            self.assertFalse(source["original_inspected"])
            self.assertEqual(source["class"], "exact_original_image_locator_uninspected"
                             if label != "lewiston-josiah-1858"
                             else "exact_newspaper_image_locator_uninspected")
        self.assertIn("omits or suppresses", self.sources["woodruff-1838-josiah"]["limits"])

    def test_hope_census_and_probate_are_not_merged_as_identity_proof(self):
        census = self.sources["hope-1820-manuscript"]
        court = self.sources["hope-1837-probate"]
        self.assertFalse(census["original_inspected"])
        self.assertTrue(court["original_inspected"])
        self.assertIn("not yet", census["limits"].lower()) if "not yet" in census["limits"].lower() else self.assertIn("Neither", census["limits"])
        self.assertIn("Does NOT identify parents", court["limits"])
        self.assertEqual(self.people["matthew_beveridge_hope_1837"]["parents"], [])
        self.assertEqual(self.people["clarissa_beveridge_widow_1837"]["children"], [])
        self.assertFalse(self.sources["fox-1785-minor"]["original_inspected"])

    def test_export_includes_every_case_source_without_unpublished_scan_bytes(self):
        export = expedition_csv(self.research)
        rows = list(csv.DictReader(io.StringIO(export)))
        expected = sum(len(case["source_ids"]) for case in self.cases.values())
        self.assertEqual(len(rows), expected)
        self.assertTrue(all(row["source_id"] in self.sources for row in rows))
        self.assertTrue(all(row["original_locator"] for row in rows))
        self.assertEqual(
            next(r for r in rows if r["source_id"] == "deed-1837-thomas-to-james")
            ["original_inspected"], "no",
        )
        self.assertNotIn("data:image", export)
        self.assertNotIn("private_scans", export)

    def test_research_index_searches_new_originals_without_ocr_identity_merges(self):
        index = build_index(self.people)
        sources = [r for r in index if r["id"].startswith("expedition-source:")]
        cases = [r for r in index if r["id"].startswith("expedition-case:")]
        self.assertEqual(len(sources), len(self.sources))
        self.assertEqual(len(cases), len(self.cases))
        self.assertTrue(all(row["route"] ==
                            "?page=collection&view=source-expedition"
                            for row in sources))
        self.assertEqual(
            {r["id"] for r in search_index(index, query="7596929")},
            {"expedition-source:vinalhaven-josiah-1793"},
        )
        rockland = search_index(index, person_id="nathaniel_beverage_1804_rockland")
        self.assertIn("expedition-case:nathaniel-rockland-parentage",
                      {r["id"] for r in rockland})
        self.assertNotIn(
            "expedition-source:hope-1820-manuscript",
            {r["id"] for r in search_index(index,
                                          person_id="matthew_beveridge_hope_1837")},
        )

    def test_unchanged_all_family_members_tree_links_and_password(self):
        self.assertEqual(validate_site_data(self.data).errors, [])
        self.assertEqual(len(self.people), 202)
        self.assertEqual(len(connected_components(self.people, self.relationships)), 4)
        app = (ROOT / "app.py").read_text(encoding="utf-8")
        self.assertIn("LEGACY_COMPATIBILITY_PASSWORD", app)
        self.assertIn("def check_password()", app)
        self.assertIn("?page=collection&view=source-expedition", app)
        collection = (ROOT / "family_discoveries.py").read_text(encoding="utf-8")
        self.assertIn('view", "") or "") == "source-expedition"', collection)
        self.assertTrue((ROOT / "data" / "phase39_primary_record_expedition.json")
                        .is_file())


if __name__ == "__main__":
    unittest.main()
