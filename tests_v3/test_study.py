import json
import unittest
import io
import tempfile
from pathlib import Path
from contextlib import redirect_stderr
from unittest.mock import patch
from research_v3.fixtures import make_cases,public_case
from research_v3.engine import prefix,simulate_round,patch_program,MAX_CANDIDATES
from research_v3.model import payload_for,SCHEMA
from research_v3.run import replay_trajectory,schedule,parse_args,request_model,dump
from research_v3.analysis import summarize

class StudyTests(unittest.TestCase):
    def test_equal_payload_except_index(self):
        c=make_cases()[0];r,b=prefix(c);p=payload_for(public_case(c),r,b,[],"Planner")
        for method in ("GraphPlanner","GraphShuffled"):
            q=payload_for(public_case(c),r,b,[],method);q.pop("dependency_index")
            self.assertEqual(p,q)
        self.assertNotIn("oracle",json.dumps(p));self.assertNotIn("reference",p)
    def test_shuffled_control_permutates_every_node_field(self):
        c=make_cases()[0];r,b=prefix(c);n=len(c["program"])
        a=payload_for(public_case(c),r,b,[],"GraphPlanner")["dependency_index"]
        q=payload_for(public_case(c),r,b,[],"GraphShuffled")["dependency_index"]
        self.assertEqual(q["edges"],[[(s+1)%n,(t+1)%n] for s,t in a["edges"]])
        self.assertEqual(q["effect_nodes"],[(x+1)%n for x in a["effect_nodes"]])
        self.assertEqual(q["backward_distance"],{(k+1)%n:v for k,v in a["backward_distance"].items()})
    def test_multi_edit_budget_and_isolation(self):
        c=make_cases()[0];r,_=prefix(c);before=r.snapshot()
        candidate={"edits":c["fix_edits"],"moves":c["fix_moves"],"plan":[]}
        out=simulate_round(r,c["program"],c["goals"],[candidate]*6)
        self.assertEqual(out["simulated"],1)
        self.assertEqual(out["public_loss"],0)
        self.assertEqual(r.snapshot(),before)
        bad={"edits":[{"node":0,"field":"path","value":""}]*17,"moves":[],"plan":[]}
        with self.assertRaises(ValueError):patch_program(c["program"],bad)
    def test_two_round_feedback_replay_and_failure(self):
        c=make_cases()[0]
        fail={"status":"ModelIncomplete","candidates":[]}
        good={"status":"ok","candidates":[{"edits":c["fix_edits"],"moves":c["fix_moves"],"plan":[]}]}
        t=replay_trajectory(c,"Planner",0,[fail,good])
        self.assertTrue(t["evaluation"]["joint"]);self.assertEqual(t["rounds"],2)
        self.assertEqual(len(schedule()),324)
    def test_clustered_pairing_retains_repeats(self):
        c=make_cases()[0];records=[]
        for repeat in range(3):
            records.append(replay_trajectory(c,"Planner",repeat,[]))
            records.append(replay_trajectory(c,"GraphPlanner",repeat,[{"status":"ok","candidates":[{"edits":c["fix_edits"],"moves":[],"plan":[]}]}]))
        s=summarize(records,[])
        self.assertEqual(s["primary"]["attacked_case_count"],1)
        self.assertEqual(s["primary"]["paired_trajectory_count"],3)
        self.assertEqual(s["primary"]["joint_difference_pp"],100)
    def test_freeze_and_live_are_separate_invocations(self):
        with redirect_stderr(io.StringIO()),self.assertRaises(SystemExit):
            parse_args(["--freeze","--live"])
    def test_resume_reuses_saved_request_and_rejects_changed_payload(self):
        from types import SimpleNamespace
        from research_v3.run import slug
        scratch=Path(__file__).resolve().parents[1]/"work";scratch.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=scratch) as directory:
            out=Path(directory);c=make_cases()[0];payload={"public":"fixture"}
            p={"payload":payload,"status":"ok","candidates":[]}
            dump(out/"requests"/(slug(c["id"],"Planner",0,0)+".json"),p)
            with patch("research_v3.run.OUT",out):
                self.assertEqual(request_model(SimpleNamespace(),c,"Planner",0,0,payload),p)
                with self.assertRaises(RuntimeError):request_model(SimpleNamespace(),c,"Planner",0,0,{"changed":True})
    def test_live_requires_committed_manifest_and_source(self):
        import hashlib
        from research_v3.run import committed_inputs
        scratch=Path(__file__).resolve().parents[1]/"work";scratch.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=scratch) as directory:
            out=Path(directory);(out/"freeze.json").write_bytes(b"manifest")
            manifest={"files":{"source.py":hashlib.sha256(b"source").hexdigest()}}
            with patch("research_v3.run.OUT",out),patch("research_v3.run.subprocess.check_output",side_effect=[b"manifest",b"source","abc\n"]):
                self.assertEqual(committed_inputs(manifest),"abc")
            for responses in ([b"different"],[b"manifest",b"changed"]):
                with patch("research_v3.run.OUT",out),patch("research_v3.run.subprocess.check_output",side_effect=responses),self.assertRaises(RuntimeError):
                    committed_inputs(manifest)
if __name__=="__main__":unittest.main()
