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

    def test_1749_complete_timeline_tells_intention_not_certified_marriage(self):
        historic = next(entry for entry in self.data["events"]
                      if entry["id"] == "event_marriage_james_jr_jean_white_1749")
        reviewed = next(entry for entry in self.timeline
                        if entry["type"] == "Timeline event"
                        and entry["id"] == historic["id"])
        self.assertIn("intention to marry", reviewed["title"])
        self.assertIn("ceremony unverified", reviewed["title"])
        self.assertIn("not proof", reviewed["description"])
        self.assertIn("Documented marriage intention", reviewed["certainty"])
        self.assertTrue(historic["title"].startswith("Marriage of "))
        self.assertEqual(reviewed["url"], "?page=timeline&event=" + historic["id"])
        birth = next(row for row in self.timeline
                     if row["type"] == "Timeline event"
                     and row["id"] == "event_birth_james_beveridge_jr_1724")
        self.assertIn("later identity uncertain", birth["title"])
        self.assertIn("town birth entry", birth["certainty"])
        marriage = next(row for row in self.timeline
                        if row["type"] == "Timeline event"
                        and row["id"] == "event_marriage_james_sr_sarah_bennett_1723")
        self.assertIn("town marriage entry", marriage["certainty"])

    def test_no_research_evidence_level_disappears(self):
        findings=[t for t in self.timeline if t["type"]=="Research finding"]
        self.assertEqual({t["id"] for t in findings},set(self.collection.findings))
        self.assertIn("Probable",{t["certainty"] for t in findings})
        self.assertIn("Conflict",{t["certainty"] for t in findings})
        self.assertIn("Possible lead",{t["certainty"] for t in findings})

    def test_photos_places_and_documents_included(self):
        kinds={t["type"] for t in self.timeline}
        self.assertTrue({"Photo / scan / object","Place / property connection",
                         "Research finding","Family story","Historical document"}<=kinds)
        self.assertTrue(any(t["id"]=="thomas-1786" for t in self.timeline))

    def test_internal_research_activity_is_not_a_family_history_event(self):
        kinds = {entry["type"] for entry in self.timeline}
        self.assertNotIn("Research source", kinds)
        self.assertNotIn("Unresolved research question", kinds)
        self.assertNotIn("Research note", kinds)
        self.assertFalse(any(name.startswith("Research inventory") for name in kinds))
        self.assertNotIn("Historical source", kinds)
        self.assertTrue(any(row["type"]=="Research finding" for row in self.timeline))

    def test_1786_sworn_testimony_is_dated_and_linked(self):
        testimony = next(t for t in self.timeline if t["id"]=="thomas-1786")
        self.assertEqual(testimony["year"], 1786)
        self.assertEqual(testimony["type"], "Historical document")
        self.assertIn("sworn testimony", testimony["title"])
        self.assertEqual(testimony["url"], "?page=documents&doc=thomas-1786")
        self.assertIn("1786", testimony["date"])

    def test_every_record_is_available_without_a_pagination_cap(self):
        from pathlib import Path
        code = (ROOT / "unified_timeline.py").read_text()
        self.assertNotIn('Entries per page', code)
        self.assertNotIn('Records shown', code)
        self.assertIn('ordered_items = dated_results + undated_results', code)
        self.assertIn('st.dataframe(', code)

    def test_family_history_book_and_undated_images_are_not_dropped(self):
        book = next(row for row in self.timeline if row["id"]=="colony-book-2016")
        self.assertEqual(book["year"],2016)
        self.assertEqual(book["date_kind"],"Book publication year")
        leads=[row for row in self.timeline if row["type"]=="Book photograph or illustration"]
        self.assertGreaterEqual(len(leads),100)
        self.assertTrue(all(row["year"] is None for row in leads))
        self.assertTrue(any(row["url"]=="?page=family-books&book_page=49" for row in leads))
        cited=next(row for row in self.timeline if row["id"]=="colony-lowell-1925")
        self.assertEqual(cited["year"],1925)
        self.assertIn("PDF page 245",cited["extra"])

    def test_imprecise_dates_are_not_invented(self):
        self.assertIsNone(historical_year("Nineteenth century"))
        self.assertIsNone(historical_year("1700s–1900s records"))
        self.assertEqual(historical_year("1781; 1786-06-01"),1781)

    def test_every_entry_has_a_destination_and_status(self):
        self.assertTrue(all(t["url"].startswith("?page=") and t["certainty"] for t in self.timeline))


if __name__=="__main__":
    unittest.main()
