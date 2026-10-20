"""Phase 41: contested parentage remains visibly sourced, never auto-imported."""
from __future__ import annotations

import csv
import io
from pathlib import Path
import tempfile
import json
import unittest

from family_data import index_people, load_site_data, relationship_index
from genealogy_integrity import connected_components
from identity_claim_review import (load_claims, cases_for_person,
                                   claim_review_route, witness_families,
                                   conflict_report_csv)
from family_research_index import build_index
from validation import validate_site_data

ROOT = Path(__file__).resolve().parents[1]


class Phase41CompetingIdentityEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = load_site_data(ROOT / "data")
        cls.people = index_people(cls.data["people"])
        cls.links = relationship_index(cls.data["people"])
        cls.cases = load_claims()

    def test_four_fully_sourced_cases_and_person_attribution(self):
        self.assertEqual(len(self.cases), 4)
        ids = {row["id"] for row in self.cases}
        self.assertEqual(ids, {
            "rachel-surname-conflict", "josiah-si-parents",
            "nathaniel-birth-identity", "thomas-1837-deed-chronology"})
        self.assertTrue(all(not claim["original_inspected"]
                            for case in self.cases for claim in case["claims"]))
        self.assertTrue(all(len(case["claims"]) >= 2 and case["research_tasks"]
                            for case in self.cases))
        self.assertEqual({case["id"] for case in cases_for_person(
            "josiah_b_beverage_1821", self.cases)},
            {"rachel-surname-conflict", "josiah-si-parents"})
        self.assertEqual(cases_for_person("nonexistent-person", self.cases), [])

    def test_competing_rachel_names_not_counted_as_two_originals(self):
        case = next(c for c in self.cases if c["id"] == "rachel-surname-conflict")
        self.assertEqual({cl["value"] for cl in case["claims"]},
                         {"Rachel Lucy Crosby", "Rachel Luce Tarr"})
        self.assertEqual(len(witness_families(case)), 2)
        self.assertEqual(len(witness_families(case)["ancestry-contributed-family-pedigree"]), 2)
        self.assertTrue(all(not c["original_inspected"] for c in case["claims"]))

    def test_josiah_parent_claims_cannot_replace_existing_parents(self):
        current = set(self.people["josiah_b_beverage_1821"]["parents"])
        self.assertEqual(current, {"josiah_winslow_beverage_1793",
                                   "mary_dyer_1795"})
        self.assertNotIn("john_white_beverage_1774", current)
        claim = next(c for c in self.cases if c["id"] == "josiah-si-parents")
        self.assertIn("John White Beverage", claim["claims"][1]["value"])
        self.assertIn("Rachel Luce Tarr", claim["claims"][1]["value"])
        self.assertTrue(any("1821" in task for task in claim["research_tasks"]))

    def test_nathaniel_stays_outside_main_tree_until_named_original(self):
        self.assertEqual(len(connected_components(self.people, self.links)), 4)
        self.assertEqual(self.people["nathaniel_beverage_1804_rockland"]["parents"], [])
        john = self.people["john_white_beverage_1774"]
        self.assertNotIn("nathaniel_beverage_1804_rockland", john["children"])
        self.assertEqual(len(self.people), 202)
        self.assertEqual(validate_site_data(self.data).errors, [])

    def test_search_index_exposes_all_conflicts_from_exact_person_ids(self):
        index = build_index(self.people)
        found = [r for r in index if str(r["id"]).startswith("identity-dispute:")]
        self.assertEqual(len(found), 4)
        for row in found:
            self.assertEqual(row["category"], "Open identity questions")
            self.assertIn("conflict_case=", row["route"])
            self.assertTrue(all(pid in self.people for pid in row["person_ids"]))
            self.assertTrue(row["limits"])
        page = next(r for r in found if r["id"].endswith("josiah-si-parents"))
        self.assertIn("josiah_b_beverage_1821", page["person_ids"])

    def test_bookmarked_cases_and_complete_csv(self):
        self.assertEqual(claim_review_route("josiah-si-parents"),
                         "?page=collection&view=source-expedition&conflict=1&conflict_case=josiah-si-parents")
        with io.StringIO(conflict_report_csv(self.cases)) as h:
            rows = list(csv.DictReader(h))
        self.assertEqual(len(rows), 8)
        self.assertTrue(all(row["original_inspected"] == "no" for row in rows))
        self.assertTrue(all(row["research_requirements"] for row in rows))

    def test_original_claim_flag_cannot_be_fabricated(self):
        with tempfile.TemporaryDirectory() as tmp:
            modified = json.loads((ROOT / "data" /
                     "phase41_competing_identity_claims.json").read_text(encoding="utf-8"))
            modified[0]["claims"][0]["original_inspected"] = True
            path = Path(tmp) / "claims.json"
            path.write_text(json.dumps(modified), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "uninspected"):
                load_claims(path)

    def test_no_shared_password_or_ancestry_edit_in_pr(self):
        app = (ROOT / "app.py").read_text(encoding="utf-8")
        self.assertIn("LEGACY_COMPATIBILITY_PASSWORD", app)
        self.assertIn("def check_password()", app)
        profile = (ROOT / "family_exhibits.py").read_text(encoding="utf-8")
        self.assertIn("conflicting_cases_for_person(person_id)", profile)
        self.assertIn("claim_review_route(dispute[\"id\"])", profile)
        self.assertIn("render_conflict_review", (ROOT / "primary_source_expedition.py").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
