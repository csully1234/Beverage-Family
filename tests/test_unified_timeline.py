"""Every evidence level remains visible in the complete family chronology."""
import unittest
from pathlib import Path

from family_data import load_site_data, index_people
from research_collection import CollectionIndex
from unified_timeline import build_chronology, historical_year


ROOT=Path(__file__).resolve().parents[1]


class UnifiedTimelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=load_site_data(ROOT/"data")
        cls.people=index_people(cls.data["people"])
        cls.collection=CollectionIndex.load()
        cls.timeline=build_chronology(cls.data,cls.people,cls.collection)

    def test_all_existing_events_remain(self):
        ids={t["id"] for t in self.timeline if t["type"]=="Timeline event"}
        self.assertEqual(ids,{e["id"] for e in self.data["events"]})

    def test_no_research_evidence_level_disappears(self):
        findings=[t for t in self.timeline if t["type"]=="Research finding"]
        self.assertEqual({t["id"] for t in findings},set(self.collection.findings))
        self.assertIn("Probable",{t["certainty"] for t in findings})
        self.assertIn("Conflict",{t["certainty"] for t in findings})
        self.assertIn("Possible lead",{t["certainty"] for t in findings})

    def test_photos_places_and_documents_included(self):
        kinds={t["type"] for t in self.timeline}
        self.assertTrue({"Photo / scan / object","Place / property connection",
                         "Historical source","Family story","Historical document"}<=kinds)
        self.assertTrue(any(t["id"]=="thomas-1786" for t in self.timeline))

    def test_imprecise_dates_are_not_invented(self):
        self.assertIsNone(historical_year("Nineteenth century"))
        self.assertIsNone(historical_year("1700s–1900s records"))
        self.assertEqual(historical_year("1781; 1786-06-01"),1781)

    def test_every_entry_has_a_destination_and_status(self):
        self.assertTrue(all(t["url"].startswith("?page=") and t["certainty"] for t in self.timeline))


if __name__=="__main__":
    unittest.main()
