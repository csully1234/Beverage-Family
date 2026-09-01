from __future__ import annotations

import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from family_data import index_people, load_site_data
from validation import validate_site_data


class HistoricalLifeTimelineExpansionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = load_site_data(ROOT / "data")
        cls.people = index_people(cls.data["people"])
        cls.events = {event["id"]: event for event in cls.data["events"]}

    def test_no_new_people_were_added(self):
        self.assertEqual(len(self.people), 180)

    def test_timeline_is_substantially_expanded(self):
        self.assertGreaterEqual(len(self.events), 126)
        self.assertGreaterEqual(len(self.data["research"]), 16)

    def test_early_civic_generation_is_enriched(self):
        self.assertIn("Vinalhaven town clerk, 1790–1798", self.people["thomas_beverage_1750"].get("civic_offices", []))
        self.assertIn("Vinalhaven town clerk, 1799–1812", self.people["john_white_beverage_1774"].get("civic_offices", []))
        self.assertTrue(any("Constitutional Convention" in item for item in self.people["benjamin_kent_beverage_1779"].get("civic_offices", [])))

    def test_benjamin_state_history_events_exist(self):
        for event_id in (
            "event_benjamin_maine_constitutional_convention_1819",
            "event_benjamin_vinalhaven_history_manuscript_1819",
            "event_benjamin_maine_house_1823",
        ):
            self.assertIn(event_id, self.events)

    def test_bridge_event_is_conservative_and_connected(self):
        event = self.events["event_north_haven_bridge_act_1848"]
        self.assertEqual(set(event["people_involved"]), {"james_beverage_1789", "josiah_winslow_beverage_1793"})
        self.assertIn("does not by itself prove", event["description"])

    def test_working_life_profiles_are_enriched(self):
        self.assertIn("Lobsterman", self.people["raymond_albert_beverage"].get("occupations", []))
        self.assertIn("Missionary in Guatemala", self.people["john_miller_beverage_1927"].get("occupations", []))
        self.assertTrue(self.people["gerald_gibson_beverage_1914"].get("military_service"))
        self.assertTrue(self.people["hartley_george_beverage_sr_1927"].get("occupations"))

    def test_mercury_claim_is_explicitly_unverified(self):
        for event_id in (
            "event_birth_lucy_c_beverage_1830",
            "event_death_jemima_crabtree_1837",
            "event_death_james_beverage_1850",
            "event_death_lucy_c_beverage_1850",
        ):
            status = self.events[event_id].get("evidence_status", "")
            self.assertIn("Research lead", status)
            self.assertIn("unverified", status.lower())

    def test_new_timeline_sources_are_structured(self):
        new_ids = [eid for eid in self.events if eid.startswith((
            "event_james_topsham_", "event_thomas_vinalhaven_", "event_john_vinalhaven_",
            "event_john_hancock_", "event_benjamin_maine_", "event_benjamin_vinalhaven_",
            "event_nathaniel_maine_", "event_north_haven_bridge_", "event_orris_colby_",
            "event_frank_", "event_harold_carpathia_", "event_samuel_signal_",
            "event_gerald_navy_", "event_john_miller_", "event_samuel_north_haven_",
            "event_norwood_beveridge_covid_"
        ))]
        self.assertGreaterEqual(len(new_ids), 18)
        for eid in new_ids:
            sources = self.events[eid].get("sources", [])
            self.assertTrue(any(isinstance(src, dict) and str(src.get("url", "")).startswith("http") for src in sources), eid)

    def test_all_new_event_people_resolve(self):
        for event in self.data["events"]:
            for pid in event.get("people_involved", []):
                if pid in self.people:
                    continue
                # Existing baseline unresolved event participants are tolerated by the validator;
                # no event introduced by this pass may add a new unresolved ID.
                if event["id"].startswith(("event_james_topsham_", "event_thomas_vinalhaven_", "event_john_", "event_benjamin_", "event_nathaniel_", "event_north_haven_bridge_", "event_orris_", "event_frank_", "event_harold_carpathia_", "event_samuel_", "event_gerald_", "event_norwood_")):
                    self.fail(f"new event {event['id']} has unresolved person {pid}")

    def test_validator_has_no_blocking_errors(self):
        self.assertEqual(validate_site_data(self.data).errors, [])


if __name__ == "__main__":
    unittest.main()
