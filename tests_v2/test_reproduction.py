import json
import unittest
import tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from research_v2.fixtures import make_cases, public_case
from research_v2.repair import prefix
from research_v2.model import payload_for, SCHEMA
from research_v2.run import deterministic_trials, summarize, replay_trial
from research_v2.reproduce import verify_artifacts
from research_v2.analysis import analyze
from research_v2.run import call_one
from src.api import Budget

class ReproductionTests(unittest.TestCase):
    def test_payload_only_differs_in_index_and_seed_order(self):
        c=next(c for c in make_cases() if c["variant"]=="injected");r,b=prefix(c)
        p=payload_for(public_case(c),r,b,"Planner")
        q=payload_for(public_case(c),r,b,"GraphPlanner")
        p.pop("seed_candidates");q.pop("seed_candidates");q.pop("dependency_index")
        self.assertEqual(p,q)
        self.assertNotIn("oracle",json.dumps(p))
        self.assertNotIn("family",p)
    def test_limits_are_same_schema(self):
        self.assertEqual(SCHEMA["properties"]["plans"]["maxItems"],4)
        self.assertEqual(SCHEMA["properties"]["plans"]["items"]["maxItems"],12)
    def test_deterministic_replay_and_all_denominators(self):
        trials=deterministic_trials(make_cases())
        metrics=summarize(trials)
        self.assertEqual(len(trials),48*4)
        for row in metrics.values():self.assertEqual(row["n"],48)
        for trial in trials:self.assertEqual(replay_trial(trial)["evaluation"],trial["evaluation"])
    def test_model_failure_replay_still_counts_failed_repair(self):
        trial=next(t for t in deterministic_trials(make_cases()) if t["blocked"])
        trial["method"]="Planner";trial["model_status"]="model_incomplete";trial["plans"]=[]
        replay=replay_trial(trial)
        self.assertFalse(replay["evaluation"]["joint"])
    def test_evidence_manifest_rejects_tamper_and_path_escape(self):
        scratch=Path(__file__).resolve().parents[1]/"work"
        scratch.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=scratch) as directory:
            p=Path(directory);(p/"artifact.json").write_text("{}")
            (p/"evidence-manifest.json").write_text(json.dumps({"files":{"artifact.json":"wrong"}}))
            with self.assertRaises(ValueError):verify_artifacts(p)
            (p/"evidence-manifest.json").write_text(json.dumps({"files":{"../outside.json":"wrong"}}))
            with self.assertRaises(ValueError):verify_artifacts(p)
    def test_paired_analysis_and_failed_attempt_accounting(self):
        case=make_cases()[0]
        base={"case_id":case["id"],"family":case["family"],"blocked":True,
              "simulated":1,"evaluation":{"joint":False}}
        graph={**base,"method":"GraphPlanner","evaluation":{"joint":True}}
        plain={**base,"method":"Planner"}
        proposal={"method":"Planner","status":"RuntimeError","usage":{"input_tokens":10,"output_tokens":2},
                  "attempts":[{"status":"pending","reserved":0.01},{"status":"settled","reserved":0.01,"settled":0.001}],
                  "seconds":1.0}
        result=analyze([plain,graph],[proposal])
        self.assertEqual(result["paired_graph_minus_planner"]["joint_difference_pp"],100)
        usage=result["model_usage"]["Planner"]
        self.assertEqual(usage["dispatch_attempts"],2)
        self.assertEqual(usage["failed_logical_calls"],1)
        self.assertAlmostEqual(usage["charged_or_reserved_usd"],0.011)
    def test_failed_call_keeps_usage_and_ledger_attempts(self):
        scratch=Path(__file__).resolve().parents[1]/"work";scratch.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=scratch) as directory:
            p=Path(directory);calls=p/"cache";calls.mkdir()
            case=next(c for c in make_cases() if c["variant"]=="injected")
            key="f"*64;budget=Budget(p/"budget.json")
            budget.reserve(key+":0",0.01);budget.settle(key+":0",0.001)
            cached={"call_id":"v2-pilot-1:"+case["id"]+":Planner","fingerprint":key,
                    "status":"model_incomplete","seconds":2,
                    "response":{"model":"gpt-6-luna","usage":{"input_tokens":50,"output_tokens":10}}}
            (calls/"response.json").write_text(json.dumps(cached),encoding="utf-8")
            def fail(*args,**kwargs):raise RuntimeError("synthetic model failure")
            client=SimpleNamespace(calls=calls,budget=budget,generate=fail)
            with patch("research_v2.run.OUT",p/"out"):
                result=call_one(client,case,"Planner")
            self.assertEqual(result["status"],"RuntimeError")
            self.assertEqual(result["usage"]["output_tokens"],10)
            self.assertEqual(result["attempts"][0]["settled"],0.001)
            self.assertEqual(result["plans"],[])

if __name__=="__main__":unittest.main()

