"""Phase 42: prove source retrieval workflow never fabricates genealogical links."""
from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from family_data import index_people, load_site_data, relationship_index
from genealogy_integrity import connected_components
from original_record_intake import (load_acquisition, acquisition_for_person,
                                    acquisition_route, researcher_packet,
                                    request_draft)
from family_research_index import build_index
from validation import validate_site_data

ROOT = Path(__file__).resolve().parents[1]


class Phase42OriginalRecordRetrievalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = load_acquisition()
        cls.targets = cls.registry["targets"]
        cls.custodians = {x["id"]: x for x in cls.registry["custodians"]}
        cls.data = load_site_data(ROOT / "data")
        cls.people = index_people(cls.data["people"])
        cls.links = relationship_index(cls.data["people"])

    def test_nine_targeted_originals_with_supported_repositories(self):
        self.assertEqual(len(self.targets), 9)
        self.assertEqual(len(self.custodians), 7)
        self.assertEqual(len({x["id"] for x in self.targets}), 9)
        self.assertEqual([x["priority"] for x in self.targets], list(range(1, 10)))
        self.assertTrue(all(x["status"] != "original_inspected"
                            for x in self.targets))
        self.assertTrue(all(x["evidence_needed"] and x["source_locator"]
                            for x in self.targets))
        self.assertTrue(all(set(x["custodian_ids"]) <= self.custodians.keys()
                            for x in self.targets))

    def test_municipal_record_context_and_specific_image_limits(self):
        lookup = {x["id"]: x for x in self.targets}
        for pid in ("nathaniel-1803", "josiah-1821", "john-rachel-1800"):
            target = lookup[pid]
            self.assertIn("Vinalhaven", target["places"])
            self.assertIn("7596929", target["source_locator"])
            self.assertIn("vinalhaven-clerk", target["custodian_ids"])
        self.assertIn("NOT established", lookup["john-rachel-1800"]["source_locator"])
        self.assertIn("UNLOCATED", lookup["nathaniel-1803"]["source_locator"])
        self.assertIn("8296915", lookup["thomas-deed-1837"]["source_locator"])
        self.assertIn("207/601", lookup["thomas-deed-1837"]["source_locator"])
        self.assertIn("North Haven", lookup["nathaniel-sarah-1838"]["places"].replace("North Fox Island", "North Haven"))

    def test_relevant_original_targets_propagate_to_exact_person_exhibit(self):
        a = {r["id"] for r in acquisition_for_person("josiah_b_beverage_1821", self.registry)}
        self.assertEqual(a, {"josiah-1821", "john-white-1839-probate", "josiah-1918-death"})
        b = {r["id"] for r in acquisition_for_person("nathaniel_beverage_1804_rockland", self.registry)}
        self.assertIn("nathaniel-1803", b)
        self.assertIn("nathaniel-sarah-1838", b)
        self.assertEqual(acquisition_for_person("someone_nonexistent", self.registry), [])
        self.assertEqual(acquisition_route("josiah-1821"),
                         "?page=collection&view=source-expedition&acquire=1&source_target=josiah-1821")

    def test_draft_is_complete_and_not_automatically_sent(self):
        target = self.targets[0]
        custodian = self.custodians["vinalhaven-clerk"]
        request = request_draft([target], custodian)
        self.assertIn("Subject:", request)
        self.assertIn(target["source_locator"], request)
        self.assertIn(target["title"], request)
        self.assertIn("noncertified", request)
        self.assertIn("reproduction", request)
        self.assertNotIn("mailto:", request)
        self.assertNotIn("send(", request)
        with self.assertRaises(ValueError):
            request_draft([], custodian)

    def test_literal_transcription_export_never_alters_family_tree(self):
        target = self.targets[1]
        before = connected_components(self.people, self.links)
        original_parents = list(self.people["nathaniel_beverage_1804_rockland"]["parents"])
        result = researcher_packet(
            target=target, institution="Sample municipal ledger", shelf="Ledger A p. 43",
            record_date="20 October 1803", transcription="Nath[aniel] ... [unclear]",
            observation="Example only; review original scan before use.",
            source_url="https://example.org/source", firsthand=True,
        )
        self.assertEqual(result["verification_status"], "researcher-submitted-unreviewed")
        self.assertFalse(result["genealogy_auto_updated"])
        self.assertFalse(result["source_file_bytes_included"])
        self.assertTrue(result["reviewer_reports_read_original"])
        self.assertEqual(self.people["nathaniel_beverage_1804_rockland"]["parents"],
                         original_parents)
        self.assertEqual(connected_components(self.people, self.links), before)
        self.assertNotIn("parents", result)
        with self.assertRaises(ValueError):
            researcher_packet(target=target, institution="", shelf="",
                              record_date="", transcription="  ", observation="")
        with self.assertRaises(ValueError):
            researcher_packet(target=target, institution="", shelf="",
                              record_date="", transcription="abc", observation="",
                              source_url="javascript:evil()")

    def test_search_workbench_indexes_all_nine_retrieval_cases_without_promoting_sources(self):
        index = build_index(self.people)
        cases = [x for x in index if x["id"].startswith("original-retrieval:")]
        self.assertEqual(len(cases), 9)
        self.assertEqual(len({x["id"] for x in cases}), 9)
        self.assertTrue(all(x["category"] == "Open identity questions"
                            for x in cases))
        self.assertTrue(all("NOT inspected" in x["status"] for x in cases))
        self.assertTrue(all("source_target=" in x["route"] for x in cases))
        self.assertTrue(all(all(pid in self.people for pid in x["person_ids"])
                            for x in cases))

    def test_archive_family_login_and_names_preserved(self):
        self.assertEqual(len(self.people), 202)
        self.assertEqual(len(connected_components(self.people, self.links)), 4)
        self.assertEqual(validate_site_data(self.data).errors, [])
        app = (ROOT / "app.py").read_text(encoding="utf-8")
        self.assertIn("LEGACY_COMPATIBILITY_PASSWORD", app)
        self.assertIn("def check_password()", app)
        expedition = (ROOT / "primary_source_expedition.py").read_text(encoding="utf-8")
        self.assertIn("render_acquisition_center(people", expedition)
        assert "def render_acquisition_center" in (ROOT / "original_record_intake.py").read_text(encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
