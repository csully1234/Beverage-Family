from __future__ import annotations

import copy
import json
import tempfile
import unittest
from datetime import date
from pathlib import Path

from archive import ArchiveIndex, historical_person, link_overlaps, safe_url
from family_data import load_site_data
from historical_map import build_historical_map_html
from validation import validate_site_data

ROOT = Path(__file__).resolve().parents[1]


class ArchiveTests(unittest.TestCase):
    def setUp(self):
        self.data = load_site_data(ROOT / "data")
        self.archive = ArchiveIndex(self.data)

    def errors(self, data):
        return {issue.code for issue in validate_site_data(data).errors}

    def test_archive_and_legacy_records_validate_together(self):
        self.assertEqual(self.errors(self.data), set())
        self.assertEqual(len(self.data["people"]), 180)
        self.assertEqual(len(self.data["events"]), 127)
        self.assertEqual(len(self.archive.places), 21)
        self.assertEqual(len(self.archive.sources), 28)
        self.assertEqual(sum(l["subject_type"] == "person" for l in self.archive.links), 36)
        self.assertEqual(sum(l["subject_type"] == "event" for l in self.archive.links), 24)

    def test_normalized_files_are_optional_without_changing_legacy_data(self):
        before = {p.name: p.read_bytes() for p in (ROOT / "data").glob("*.json")}
        with tempfile.TemporaryDirectory() as tmp:
            for filename in ("people.json", "events.json", "research_people.json", "research_events.json", "research.json", "date_precision.json"):
                Path(tmp, filename).write_bytes(before[filename])
            legacy = load_site_data(Path(tmp))
        for key in ("people", "events", "research", "base_people", "base_events"):
            self.assertEqual(legacy[key], self.data[key])
        self.assertEqual(legacy["places"], [])
        self.assertEqual({p.name: p.read_bytes() for p in (ROOT / "data").glob("*.json")}, before)

    def test_inverse_indexes_connect_bridge_sources_people_and_event(self):
        related = self.archive.related("pulpit_harbor_me")
        self.assertIn("james_beverage_1789", {p["id"] for p in related["people"]})
        self.assertIn("josiah_winslow_beverage_1793", {p["id"] for p in related["people"]})
        self.assertIn("event_north_haven_bridge_act_1848", {e["id"] for e in related["events"]})
        self.assertIn("src_bridge_act_1848", {s["id"] for s in related["sources"]})
        self.assertIn("pulpit_harbor_me", {p["id"] for p in self.archive.places_for("person", "james_beverage_1789")})

    def test_petition_subject_towns_do_not_imply_personal_presence(self):
        eid = "event_john_hancock_courts_memorial_1808"
        self.assertEqual({p["id"] for p in self.archive.places_for("event", eid)}, {"castine_me", "bucksport_me", "vinalhaven_me"})
        self.assertEqual({p["id"] for p in self.archive.places_for("person", "john_white_beverage_1774")}, {"vinalhaven_me"})

    def test_duplicates_missing_subjects_and_sources_fail(self):
        cases = [
            (lambda d: d["places"].append(copy.deepcopy(d["places"][0])), "archive_duplicate_id"),
            (lambda d: d["place_links"][0].update(subject_id="missing"), "archive_missing_reference"),
            (lambda d: d["place_links"][0].update(place_id="missing"), "archive_missing_reference"),
            (lambda d: d["place_links"][0].update(source_ids=["missing"]), "archive_missing_reference"),
            (lambda d: d["archive_sources"][0].update(people_ids=["missing"]), "archive_missing_reference"),
            (lambda d: d["archive_sources"][0].update(place_ids=[]), "archive_source_backlink"),
        ]
        for mutate, code in cases:
            with self.subTest(code=code):
                data = copy.deepcopy(self.data); mutate(data)
                self.assertIn(code, self.errors(data))

    def test_duplicate_assertion_with_new_id_fails(self):
        duplicate = dict(self.data["place_links"][0], id="another_id")
        self.data["place_links"].append(duplicate)
        self.assertIn("archive_duplicate_link", self.errors(self.data))

    def test_bad_types_ranges_hierarchies_and_urls_fail(self):
        cases = [
            (lambda d: d["places"][0].update(latitude=91), "archive_schema"),
            (lambda d: d["places"][0].update(latitude=None), "archive_coordinates"),
            (lambda d: d["places"][0].update(parent_place_id=d["places"][0]["id"]), "archive_parent_cycle"),
            (lambda d: d["places"][0].update(parent_place_id="missing"), "archive_missing_reference"),
            (lambda d: d["places"][0].update(type="private_home"), "archive_schema"),
            (lambda d: d["places"][0].update(public=False), "archive_schema"),
            (lambda d: d["place_links"][0].update(source_ids="bad"), "archive_schema"),
            (lambda d: d["place_links"][0].update(date_to="1700"), "archive_date_range"),
            (lambda d: d["place_links"][0].update(date_from="1790-02-30", date_precision="exact"), "archive_date"),
            (lambda d: d["archive_sources"][0].update(date="1889-01-01", date_precision="year"), "archive_date_precision"),
            (lambda d: d["archive_sources"][0].update(url="javascript:alert(1)"), "archive_url"),
        ]
        for mutate, code in cases:
            with self.subTest(code=code):
                data = copy.deepcopy(self.data); mutate(data)
                self.assertIn(code, self.errors(data))

    def test_weak_evidence_cannot_support_a_factual_link(self):
        self.data["archive_sources"][0]["evidence_level"] = "corroboration"
        self.assertIn("archive_evidence", self.errors(self.data))

    def test_possibly_living_people_are_rejected_and_omitted_at_runtime(self):
        person = next(p for p in self.data["people"] if p["id"] == "harold_h_beverage_1893")
        person.update(living=True)
        self.assertIn("archive_privacy", self.errors(self.data))
        payload = ArchiveIndex(self.data).map_payload()
        self.assertNotIn(person["id"], {p["id"] for p in payload["people"]})
        self.assertNotIn("event_harold_carpathia_wireless_1912", {e["id"] for e in payload["events"]})
        self.assertFalse(historical_person({"birth_date":"1980"}, date(2026,9,2)))
        self.assertTrue(historical_person({"birth_date":"1800"}, date(2026,9,2)))

    def test_map_payload_never_serializes_raw_profiles(self):
        for person in self.data["people"]:
            person["residences"] = [{"location":"PRIVATE_ADDRESS_SENTINEL"}]
            person["notes"] = "PRIVATE_NOTE_SENTINEL"
            person["email"] = "PRIVATE_EMAIL_SENTINEL"
        serialized = json.dumps(ArchiveIndex(self.data).map_payload())
        for word in ("PRIVATE_ADDRESS_SENTINEL", "PRIVATE_NOTE_SENTINEL", "PRIVATE_EMAIL_SENTINEL", '"residences"'):
            self.assertNotIn(word, serialized)

    def test_time_ranges_include_clerk_tenure_and_handle_unknown_dates(self):
        clerk = self.archive.links[0]
        self.assertTrue(link_overlaps(clerk, 1794, 1794))
        self.assertFalse(link_overlaps(clerk, 1800, 1800))
        unknown = {"date_from":None,"date_to":None}
        self.assertTrue(link_overlaps(unknown, 1900, 2000))
        self.assertFalse(link_overlaps(unknown, 1900, 2000, False))
        self.assertTrue(link_overlaps({"date_from":"1953", "date_to":None}, 1960, 1970))

    def test_precision_and_unproven_locations_remain_explicit(self):
        self.assertEqual(self.archive.sources["src_bridge_act_1848"]["date"], "1848-08-08")
        self.assertEqual(self.archive.events["event_north_haven_bridge_act_1848"]["date"], "1848")
        self.assertEqual(self.archive.sources["src_pulpit_auction_1927"]["date"], "1927-07-30")
        self.assertEqual(self.archive.sources["src_samuel_obituary"]["date_precision"], "unknown")
        self.assertEqual(self.archive.places["guatemala"]["coordinate_precision"], "country")
        self.assertEqual(self.archive.sources["src_fuller_index"]["evidence_level"], "corroboration")

    def test_html_embeds_local_leaflet_and_escapes_untrusted_data(self):
        self.archive.places["pulpit_harbor_me"]["name"] = '</script><script>alert("x")</script>'
        html = build_historical_map_html(self.archive, place_id="pulpit_harbor_me")
        self.assertNotIn('</script><script>alert("x")', html)
        self.assertIn('\\u003c/script', html)
        self.assertNotIn('<script src=', html)
        self.assertIn("OpenStreetMap contributors", html)
        self.assertIn('id="place-list"', html)

    def test_urls_are_http_and_credential_free(self):
        for bad in ("javascript:alert(1)", "//example.com", "https://u:p@example.com", "https://example.com/a b", "https://[broken"):
            self.assertFalse(safe_url(bad))
        self.assertTrue(safe_url("https://example.com/page?id=123"))


if __name__ == "__main__":
    unittest.main()
