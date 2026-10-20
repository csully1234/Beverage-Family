"""Phase 40 - candidate bridges are inspectable but never canonical genealogy."""
import unittest
from pathlib import Path
from family_data import load_site_data,index_people,relationship_index
from genealogy_integrity import connected_components
from family_bridge_lab import PROPOSALS,bridge_preview,proposal_worklist
from primary_source_expedition import load_expedition
from validation import validate_site_data

ROOT=Path(__file__).resolve().parents[1]

class BridgeLaboratoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=load_site_data(ROOT/"data")
        cls.people=index_people(cls.data["people"])
        cls.links=relationship_index(cls.data["people"])

    def test_preview_does_not_mutate_real_tree(self):
        before=connected_components(self.people,self.links)
        parent_before={pid:set(v) for pid,v in self.links["parents"].items()}
        result=bridge_preview(PROPOSALS,self.people,self.links,[x["id"] for x in PROPOSALS])
        after=connected_components(self.people,self.links)
        self.assertEqual(before,after)
        self.assertEqual(parent_before,self.links["parents"])
        self.assertTrue(result["unverified"])
        self.assertFalse(result["changed_canonical_data"])
        self.assertEqual(result["before"],4)
        self.assertLess(result["hypothetical_after"],result["before"])
        self.assertEqual(len(result["edges_examined"]),2)

    def test_parentage_source_family_and_proof_requirements(self):
        records=proposal_worklist(PROPOSALS,self.people)
        self.assertEqual(len(records),2)
        self.assertEqual({r["case"] for r in records},
                         {"nathaniel-rockland-parentage"})
        self.assertTrue(all("UNPROVED" in r["status"] for r in records))
        self.assertTrue(all("Original" in r["needed"] for r in records))
        expedition=load_expedition()
        self.assertTrue(any(c["id"]=="nathaniel-rockland-parentage"
                            for c in expedition["cases"]))
        self.assertEqual(len(self.people),202)
        self.assertEqual(validate_site_data(self.data).errors,[])

    def test_bogus_research_ids_ignored_and_invalid_endpoints_rejected(self):
        self.assertEqual(bridge_preview(PROPOSALS,self.people,self.links,["missing"])["hypothetical_after"],4)
        wrong=[dict(PROPOSALS[0],parent="nonexistent-id",id="invalid")]
        with self.assertRaises(ValueError):
            bridge_preview(wrong,self.people,self.links,["invalid"])

if __name__=="__main__":
    unittest.main()
