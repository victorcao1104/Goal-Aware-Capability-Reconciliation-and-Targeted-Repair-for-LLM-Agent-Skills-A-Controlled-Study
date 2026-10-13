import json
import unittest
from research_v2.fixtures import make_cases, public_case
from research_v2.runtime import Runtime, Rejected
from research_v2.repair import prefix, repair, seeds, handle_plans
from research_v2.graph import dependency_index
from research_v2.oracle import evaluate

class RepairTests(unittest.TestCase):
    def test_balanced_fixtures_and_clean_authorized_controls(self):
        cases=make_cases()
        self.assertEqual(len(cases),48)
        self.assertEqual(len({c["family"] for c in cases}),6)
        for c in cases:
            r,blocked=prefix(c)
            self.assertEqual(blocked is None,c["variant"] in ("clean","authorized"),c["id"])
            if blocked is None:self.assertTrue(evaluate(c,r)["joint"],c["id"])
    def test_oracle_not_in_defense_payload(self):
        for c in make_cases():
            p=public_case(c)
            self.assertNotIn("oracle",p)
            self.assertNotIn("expected",json.dumps(p))
    def test_correct_recomputation_recovers_all_blocked_cases(self):
        for c in make_cases():
            r,blocked=prefix(c)
            if blocked is None:continue
            clean=next(x for x in make_cases() if x["family"]==c["family"] and x["instance"]==c["instance"] and x["variant"]=="clean")
            before=r.snapshot()
            result=repair(r,[clean["program"]],c["goals"])
            self.assertEqual(r.snapshot(),before)
            self.assertTrue(evaluate(c,result["runtime"])["joint"],c["id"])
    def test_wrong_but_safe_value_fails_oracle(self):
        c=make_cases()[0];r,_=prefix(c)
        r.sends["approved"]="wrong"
        self.assertFalse(evaluate(c,r)["task_success"])
    def test_budget_and_candidate_isolation(self):
        c=next(c for c in make_cases() if c["variant"]=="injected")
        r,_=prefix(c);result=repair(r,[c["program"]]*9,c["goals"])
        self.assertEqual(result["simulated"],4)
        self.assertEqual(result["runtime"].sends,{})
    def test_graph_cycle_rejected_and_seed_pools_equal(self):
        with self.assertRaises(ValueError):
            dependency_index([{"out":"a","inputs":["b"]},{"out":"b","inputs":["a"]}])
        for c in make_cases():
            plain=seeds(c,False,limit=None);graph=seeds(c,True,limit=None)
            self.assertEqual({json.dumps(p,sort_keys=True) for p in plain},{json.dumps(p,sort_keys=True) for p in graph})
    def test_handle_baseline_searches_all_existing_handles(self):
        for c in make_cases():
            if c["variant"]!="unauthorized":continue
            r,_=prefix(c);plans=handle_plans(r,c["goals"])
            result=repair(r,plans,c["goals"])
            self.assertTrue(evaluate(c,result["runtime"])["joint"],c["id"])

if __name__=="__main__":unittest.main()
