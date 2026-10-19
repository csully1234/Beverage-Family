"""Phase 34 original reel, distinct municipal ledger findings and historical limits."""
from __future__ import annotations

from datetime import date
from pathlib import Path
import unittest

from family_data import load_site_data, index_people, relationship_index
from family_research_index import build_index, search_index
from hope_census_records import load_hope_census_trail, census_evidence_counts
from hope_primary_access import load_hope_primary_access
from validation import validate_site_data

ROOT = Path(__file__).resolve().parents[1]
MATTHEW = "matthew_beveridge_hope_1837"
CLARISSA = "clarissa_beveridge_widow_1837"


class Phase34OriginalReelAndCivicVotes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.case = load_hope_primary_access()
        cls.cards = {row["id"]: row for row in cls.case["cases"]}
        cls.data = load_site_data(ROOT / "data")
        cls.people = index_people(cls.data["people"])

    def test_direct_link_to_the_correct_complete_1820_original_roll(self):
        record = self.cards["hope-1820-original-roll-36"]
        self.assertIn("M33 roll 36", record["locator"])
        self.assertIn("sheet 276", record["locator"])
        self.assertEqual(record["source_url"],
                         "https://archive.org/details/populationsc18200036unit")
        self.assertIn("Hope", record["locator"])
        self.assertIn("Heirlooms", record.get("companion_title", "Heirlooms Reunited"))
        self.assertFalse(record["original_line_inspected"])
        self.assertFalse(record["manuscript_verified"])
        self.assertIn("not", record["limits"].casefold())
        self.assertNotIn("household_counts", record)
        self.assertNotIn("birth_year", record)

    def test_1813_bondsman_claim_is_not_the_1813_clerk_signature_claim(self):
        record = self.cards["hope-1813-collector-bond-vote"]
        self.assertIn("bondsmen", record["finding"].casefold())
        self.assertIn("Almond Gushe", record["finding"])
        self.assertIn("Micah Hobbs", record["finding"])
        self.assertIn("p. 54", record["locator"])
        self.assertIn("exact", record["limits"])
        self.assertFalse(record["manuscript_verified"])

    def test_1821_clerk_vote_and_calendar_contradiction_preserved(self):
        record = self.cards["hope-1821-town-clerk-vote"]
        self.assertIn("clerk", record["finding"].casefold())
        self.assertIn("vote", record["title"].casefold())
        self.assertIn("April 2", record["limits"])
        self.assertIn("April 3", record["limits"])
        self.assertIn("first Monday", record["locator"].replace("first monday", "first Monday"))
        self.assertEqual(date(1821, 4, 2).weekday(), 0)
        self.assertEqual(date(1821, 4, 3).weekday(), 1)
        self.assertIn("unresolved", record["date_label"])
        self.assertFalse(record["manuscript_verified"])

    def test_one_town_ledger_is_not_counted_as_two_new_independent_originals(self):
        records = self.case["cases"]
        self.assertEqual(len(records), 3)
        self.assertEqual(sum(row["kind"] == "municipal_ledger_transcription"
                             for row in records), 2)
        self.assertIn("Two source families", self.case["source_family_count_note"])
        self.assertTrue(all(row["original_line_inspected"] is False for row in records))
        self.assertTrue(all(row["original_image_reproduced"] is False for row in records))
        self.assertIn("not", self.case["identity_limit"].casefold() + " not")
        old = load_hope_census_trail()
        self.assertEqual(census_evidence_counts(old)["original_person_lines_inspected"], 0)

    def test_workbench_indexes_three_new_items_without_auto_attaching_to_person(self):
        found = [x for x in build_index(self.people)
                 if x["id"].startswith("hope-original-access:")]
        self.assertEqual(len(found), 3)
        self.assertEqual(len({x["id"] for x in found}), 3)
        self.assertTrue(all(x["person_ids"] == [] for x in found))
        self.assertTrue(all(x["route"] == "?page=collection&view=hope-census"
                            for x in found))
        self.assertTrue(any("populationsc18200036unit" in source["url"]
                            for row in found for source in row["sources"]))
        self.assertTrue(any("bondsmen" in row["summary"].lower()
                            for row in search_index(found, query="bondsmen Matthew")))

    def test_archive_and_protected_history_are_not_changed(self):
        self.assertEqual(validate_site_data(self.data).errors, [])
        self.assertEqual(self.people[MATTHEW]["parents"], [])
        self.assertEqual(self.people[CLARISSA]["children"], [])
        relations = relationship_index(self.data["people"])
        self.assertFalse(relations["parents"].get(MATTHEW))
        app = (ROOT / "app.py").read_text(encoding="utf-8")
        self.assertIn("LEGACY_COMPATIBILITY_PASSWORD", app)
        self.assertNotIn("from family_access import", app)


if __name__ == "__main__":
    unittest.main()
