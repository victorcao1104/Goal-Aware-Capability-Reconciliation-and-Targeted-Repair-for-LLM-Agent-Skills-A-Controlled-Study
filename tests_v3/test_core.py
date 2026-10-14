import unittest
from research_v3.fixtures import make_cases,public_case
from research_v3.engine import prefix,execute_candidate,public_loss,catalogue,patch_program
from research_v3.oracle import evaluate

class CoreTests(unittest.TestCase):
    def test_structure_reference_and_multiple_faults(self):
        cases=make_cases()
        self.assertEqual(len(cases),36)
        self.assertEqual(len({c["family"] for c in cases}),6)
        for c in cases:
            r,blocked=prefix(c)
            self.assertEqual(blocked is not None,c["variant"]=="attack",c["id"])
            repaired=execute_candidate(r,c["program"],{"edits":[],"moves":[],"plan":c["reference"]})
            self.assertTrue(evaluate(c,repaired)["joint"],c["id"])
            self.assertEqual(public_loss(repaired,c["goals"]),0,c["id"])
            if c["variant"]=="attack":self.assertGreaterEqual(len(c["faults"]),3)
    def test_oracle_and_faults_excluded(self):
        for c in make_cases():
            p=public_case(c)
            self.assertEqual(set(p),{"task","config","program","goals"})
            self.assertNotIn("reference",p);self.assertNotIn("oracle",p);self.assertNotIn("faults",p)
    def test_patches_do_not_mutate_and_moves_preserve_ids(self):
        c=next(c for c in make_cases() if c["family"]=="cache" and c["variant"]=="attack")
        original=str(c["program"])
        fixed=patch_program(c["program"],{"edits":c["fix_edits"],"moves":c["fix_moves"],"plan":[]})
        r,_=prefix(c);q=execute_candidate(r,c["program"],{"edits":c["fix_edits"],"moves":c["fix_moves"],"plan":[]})
        self.assertTrue(evaluate(c,q)["joint"])
        self.assertEqual(str(c["program"]),original)
    def test_correct_values_with_stale_reads_are_rejected(self):
        c=next(c for c in make_cases() if c["family"]=="cache" and c["variant"]=="attack")
        r,_=prefix(c)
        q=execute_candidate(r,c["program"],{"edits":c["fix_edits"],"moves":[],"plan":[]})
        self.assertGreater(public_loss(q,c["goals"]),0)
        self.assertFalse(evaluate(c,q)["joint"])
    def test_single_edit_catalogue_cannot_complete_attack(self):
        for c in make_cases():
            if c["variant"]!="attack":continue
            r,_=prefix(c)
            for edit in catalogue(public_case(c)):
                try:q=execute_candidate(r,c["program"],{"edits":[edit],"moves":[],"plan":[]})
                except ValueError:continue
                self.assertFalse(evaluate(c,q)["joint"],(c["id"],edit))
    def test_receipt_witness_survives_saved_value_roundtrip(self):
        from research_v2.fixtures import a
        from research_v3.oracle import receipt_trace_ok
        c=next(c for c in make_cases() if c["family"]=="staged" and c["variant"]=="clean")
        r,_=prefix(c)
        r.step(a("read_output","roundtrip",resource="artifact"))
        r.step(a("write",inputs=["roundtrip"],resource="artifact"))
        # This output still contains hashes of the latest committed parts.
        goal=next(g for g in c["goals"] if g["resource"]=="artifact")
        self.assertEqual(public_loss(r,[goal]),0)
        self.assertTrue(receipt_trace_ok(r,[goal]))
if __name__=="__main__":unittest.main()
