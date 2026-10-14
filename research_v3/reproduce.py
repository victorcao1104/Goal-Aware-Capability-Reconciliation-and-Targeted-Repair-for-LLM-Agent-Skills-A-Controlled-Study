"""Verify and replay the complete adaptive v3 experiment without API access."""
import json
from research_v2.reproduce import verify_artifacts
from .run import OUT,freeze,collect,slug,schedule
from .fixtures import make_cases,public_case
from .engine import prefix,simulate_round
from .model import payload_for,INSTRUCTION,SCHEMA
from .run import feedback_history
from .analysis import summarize

def main():
    freeze();count=verify_artifacts(OUT)
    from .audit import certificates
    if json.loads((OUT/"complexity.json").read_text(encoding="utf-8"))!=certificates():raise AssertionError("Complexity certificate differs")
    if json.loads((OUT/"cases.json").read_text(encoding="utf-8"))!=make_cases():raise AssertionError("Fixtures differ")
    if json.loads((OUT/"model-spec.json").read_text(encoding="utf-8"))!={"instruction":INSTRUCTION,"schema":SCHEMA}:raise AssertionError("Prompt/schema differs")
    trials,proposals=collect()
    if summarize(trials,proposals)!=json.loads((OUT/"summary.json").read_text(encoding="utf-8")):raise AssertionError("Summary differs")
    cases={c["id"]:c for c in make_cases()};expected_requests=set()
    for t in trials:
        c=cases[t["case_id"]];runtime,blocked=prefix(c);history=[]
        for q in range(t["rounds"]):
            name=slug(c["id"],t["method"],t["repeat"],q)+".json";expected_requests.add(name)
            p=json.loads((OUT/"requests"/name).read_text(encoding="utf-8"))
            payload=payload_for(public_case(c),runtime,blocked,history,t["method"])
            if p["payload"]!=json.loads(json.dumps(payload)):raise AssertionError("Public request/feedback differs")
            result=simulate_round(runtime,c["program"],c["goals"],p["candidates"])
            runtime=result["runtime"];history.append(feedback_history(q,p,result))
    if {p.name for p in (OUT/"requests").glob("*.json")}!=expected_requests:raise AssertionError("Request inventory differs")
    expected_trials={slug(j["case_id"],j["method"],j["repeat"],0)+".json" for j in schedule()}
    if {p.name for p in (OUT/"trajectories").glob("*.json")}!=expected_trials:raise AssertionError("Trajectory inventory differs")
    print(f"Verified {count} evidence files, {len(trials)} trajectories, {len(proposals)} adaptive requests; no API calls.")
if __name__=="__main__":main()
