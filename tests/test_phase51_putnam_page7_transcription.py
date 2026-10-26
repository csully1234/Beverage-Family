"""Phase 51: conservative annotated transcription and original plan crosswalk."""
from __future__ import annotations

import unittest

from putnam_original import load_putnam_original, load_putnam_page7


class PutnamPage7TranscriptionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = load_putnam_original()
        cls.lines = load_putnam_page7()

    def test_all_three_columns_are_preserved_without_invented_headcount(self):
        self.assertEqual(len(self.lines), 94)
        self.assertEqual({row["column"] for row in self.lines},
                         {"left", "middle", "right"})
        self.assertEqual(self.data["phase51_review"]["working_rows_including_claim_annotations"], 94)
        self.assertIn("not 94 distinct claimants",
                      self.data["phase51_review"]["description"])

    def test_direct_original_thomas_says_fifteen_not_fifteen_year_old(self):
        matched = [x for x in self.lines if x["name_or_phrase_as_read"] == "Thomas Beverage"]
        self.assertEqual(len(matched), 1)
        self.assertEqual(matched[0]["time_when_settled_as_read"], "15")
        self.assertEqual(matched[0]["column"], "middle")
        self.assertEqual(matched[0]["reading_confidence"], "high")
        self.assertIn("not age", matched[0]["editorial_comment"])

    def test_map_page104_not_imagined_thomas_personal_allotment(self):
        map_data = self.data["phase51_review"]["archive_map_reference"]
        self.assertEqual(map_data["manuscript_plan_page"], 104)
        self.assertEqual(map_data["state_map_id"], "302962")
        self.assertIn("not Thomas Beverage's lot number", map_data["interpretation"])
        self.assertEqual(self.data["phase51_review"]["approximate_settlement_period"],
                         "circa 1770–1771")

    def test_two_similar_names_not_assigned_to_beveridge_or_family_tree(self):
        flags = self.data["phase51_review"]["uncertain_same_page_surnames"]
        self.assertEqual(len(flags), 2)
        self.assertTrue(all(
            x["status"] == "uncertain_surname_not_identified_as_beverage"
            for x in flags
        ))
        doubtful = [row for row in self.lines if
                    "B[e/r]verich" in row["name_or_phrase_as_read"]
                    or "Berich" in row["name_or_phrase_as_read"]]
        self.assertEqual(len(doubtful), 2)
        self.assertTrue(all(row["reading_confidence"] == "low" for row in doubtful))
        self.assertTrue(self.data["no_new_relationships"])

    def test_original_census_identity_inferences_remain_unproven(self):
        comparisons = self.data["phase51_review"]["historical_comparisons"]
        self.assertEqual([c["date"] for c in comparisons], ["1785", "1785-1786", "1790", "1819"])
        self.assertTrue(any("not proved" in row["status"] for row in comparisons))
        self.assertFalse(self.data["digital_facsimile_hosted_publicly"])


if __name__ == "__main__":
    unittest.main()
