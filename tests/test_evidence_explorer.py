"""Source-first navigation: rights, citations, identity caution and deep links."""
from __future__ import annotations

import unittest
from pathlib import Path

from evidence_explorer import (
    evidence_catalog, for_event, for_person, is_external_pdf,
    safe_document_url, source_items, source_record,
)
from family_data import load_site_data
from validation import validate_site_data

ROOT = Path(__file__).resolve().parents[1]


class EvidenceExplorerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.items = evidence_catalog()
        cls.site = load_site_data(ROOT / "data")

    def test_all_exhibits_are_unique_and_have_actual_access_links(self):
        self.assertGreaterEqual(len(self.items), 16)
        self.assertEqual(len({item["id"] for item in self.items}), len(self.items))
        for item in self.items:
            self.assertTrue(safe_document_url(item.get("url")), item["id"])
            self.assertTrue(item.get("claim"), item["id"])
            self.assertTrue(item.get("limits"), item["id"])
            self.assertTrue(item.get("rights"), item["id"])
            self.assertIn(item.get("association"), {
                "candidate", "documented_history", "context", "reported_history",
                "direct_record", "indexed_record", "historical_media", "research_target",
                "direct_document_exhibit",
            }, item["id"])
            self.assertIsInstance(item.get("people_ids"), list)
            self.assertIsInstance(item.get("event_ids"), list)

    def test_source_associations_do_not_create_unproved_genealogy(self):
        people = {person["id"]: person for person in self.site["people"]}
        events = {event["id"] for event in self.site["events"]}
        for item in self.items:
            self.assertFalse(set(item["people_ids"]) - set(people), item["id"])
            self.assertFalse(set(item["event_ids"]) - events, item["id"])
        # Nathaniel's proposed father remains research-only; legacy family is unchanged.
        self.assertEqual(people["nathaniel_beverage_1804_rockland"]["parents"], [])
        self.assertIn("candidate", {x["association"] for x in for_person(
            "john_white_beverage_1774", self.items)})
        self.assertEqual(self.site["base_people"], load_site_data(ROOT / "data")["base_people"])

    def test_primary_1883_bridge_contract_and_mill_pdf_reachable(self):
        indexed = {item["id"]: item for item in self.items}
        bridge = indexed["1883-alvin-bridge-town-contract"]
        self.assertTrue(bridge["preview_pdf"])
        self.assertTrue(is_external_pdf(bridge))
        self.assertIn("#page=8", bridge["url"])
        mill = indexed["millstream-exhibit-family-mills"]
        self.assertTrue(is_external_pdf(mill))
        self.assertIn("harrison_beverage_1825", mill["people_ids"])
        self.assertIn("identity", mill["limits"])

    def test_1749_transcriptions_do_not_pretend_to_be_two_marriages(self):
        docs = for_event("event_1749_james_jean_marriage_intention", self.items)
        self.assertEqual(len(docs), 2)
        self.assertEqual({d["association"] for d in docs}, {"candidate"})
        self.assertTrue(any("SAME" in d["limits"] for d in docs))
        self.assertEqual(next(e for e in self.site["events"] if
            e["id"] == "event_1749_james_jean_marriage_intention")["people_involved"], [])

    def test_frank_photo_and_sam_diary_cannot_masquerade_as_rehosted_images(self):
        frank = for_person("frank_beverage_1861", self.items)
        self.assertTrue(any(x["id"] == "1937-frank-may-diary" for x in frank))
        sam = for_person("samuel_hiram_beverage_1917", self.items)
        self.assertTrue(any(x["id"] == "1967-sam-calderwood-diary" for x in sam))
        self.assertTrue(all("link only" in x["rights"].lower() for x in sam
                            if "calderwood-diary" in x["id"]))

    def test_citation_merge_prefers_caveated_original_link(self):
        original = for_event("event_1883_beach_bridge_alvin_contract", self.items)
        assert original
        raw = [
            {"title": "Same exhibit", "url": original[0]["url"], "supports": "Same source"},
            {"title": "Unlinked label only"},
        ]
        merged = source_items(original, raw)
        self.assertEqual(sum(it["url"] == original[0]["url"] for it in merged), 1)
        self.assertTrue(any(it["url"] is None for it in merged))
        self.assertEqual(merged[0]["limits"], original[0]["limits"])

    def test_reject_external_script_and_credentials(self):
        for url in (
            "javascript:alert(1)", "file:///tmp/data.pdf", "https://a:b@example.com/a.pdf",
            "https://example.com/a.pdf?evil=<script>", "https://example.com/a\\b.pdf",
            "https://example.com bad.pdf", "//example.com/path.pdf",
            "https://example.com:9999/a.pdf",
        ):
            self.assertIsNone(safe_document_url(url), url)
        self.assertTrue(safe_document_url("https://archives.example.org/file.pdf#page=8"))
        self.assertFalse(is_external_pdf({"url": "https://example.org/news.html",
                                          "preview_pdf": True}))

    def test_new_events_and_existing_protection_validate(self):
        self.assertEqual(len(self.site["phase5_events"]), 2)
        self.assertEqual(validate_site_data(self.site).errors, [])
        self.assertEqual({e["id"] for e in self.site["phase5_events"]}, {
            "event_1883_beach_bridge_alvin_contract",
            "event_1888_harrison_mill_stream_dam_purchase",
        })


if __name__ == "__main__":
    unittest.main()
