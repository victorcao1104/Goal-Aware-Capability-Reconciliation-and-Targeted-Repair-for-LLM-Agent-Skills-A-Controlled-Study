"""Freeze and execute the v2 DEVELOPMENT pilot. No changes to v1 artifacts."""
import argparse
from concurrent.futures import ThreadPoolExecutor,as_completed
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import random

from .fixtures import make_cases,public_case
from .repair import prefix,repair,seeds,handle_plans
from .oracle import evaluate
from .model import payload_for,INSTRUCTION,SCHEMA
from .analysis import analyze

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"research_v2/results"
METHODS=("Gate","HandleSearch","ProgramSearch","GraphSearch")
LIVE=("Planner","GraphPlanner","GraphShuffled")

def dump(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

def fingerprint(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def seal_evidence():
    files={p.relative_to(OUT).as_posix():fingerprint(p) for p in sorted(OUT.rglob("*.json"))
           if p.name!="evidence-manifest.json"}
    dump(OUT/"evidence-manifest.json",{"files":files})

def freeze():
    paths=sorted((ROOT/"research_v2").glob("*.py"))+sorted((ROOT/"tests_v2").glob("*.py"))
    paths += [ROOT/"docs/protocol/upstream-repair-v2-design.md"]
    manifest={"files":{p.relative_to(ROOT).as_posix():fingerprint(p) for p in paths},
              "fixture_sha256":hashlib.sha256(json.dumps(make_cases(),sort_keys=True).encode()).hexdigest(),
              "model":"gpt-6-luna","repeat":1,"seed":20261014,"max_output_tokens":6000,
              "kind":"development mechanism pilot","v1_cost_before":1.013328125}
    path=OUT/"freeze.json"
    if path.exists():
        if json.loads(path.read_text(encoding="utf-8"))!=manifest:raise RuntimeError("v2 frozen inputs changed")
    else:
        dump(path,manifest);dump(OUT/"cases.json",make_cases())
        dump(OUT/"model-spec.json",{"instruction":INSTRUCTION,"schema":SCHEMA})
    return manifest

def trial(case,method,plans=None,model_status=None):
    runtime,blocked=prefix(case)
    if plans is None:
        public=public_case(case)
        if method=="Gate":plans=[]
        elif method=="HandleSearch":plans=handle_plans(runtime,case["goals"])
        else:plans=seeds(public,method=="GraphSearch")
    result=repair(runtime,plans,case["goals"],simulate=method!="GraphNoSim") if blocked else {
        "runtime":runtime,"simulated":0,"selected":None,"candidates":[]}
    return {"case_id":case["id"],"family":case["family"],"variant":case["variant"],"method":method,
            "blocked":blocked is not None,"plans":plans if blocked else [],"model_status":model_status,
            "evaluation":evaluate(case,result["runtime"]),"simulated":result["simulated"],
            "selected":result["selected"],"candidate_checks":result["candidates"],
            "executed_actions":len(result["runtime"].events)-len(runtime.events),
            "snapshot":result["runtime"].snapshot()}

def deterministic_trials(cases):
    return [trial(c,m) for c in cases for m in METHODS]

def replay_trial(record):
    c=next(c for c in make_cases() if c["id"]==record["case_id"])
    return trial(c,record["method"],record["plans"],record.get("model_status"))

def summarize(trials):
    result={}
    for t in trials:
        r=result.setdefault(t["method"],{"n":0,"joint":0,"task_success":0,"unsafe_trials":0,
                     "blocked":0,"recovered":0,"simulated":0,"executed_actions":0,"by_family":{}})
        r["n"]+=1
        for key in ("joint","task_success"):r[key]+=int(t["evaluation"][key])
        r["unsafe_trials"]+=int(t["evaluation"]["unsafe_effects"]>0)
        r["blocked"]+=int(t["blocked"]);r["recovered"]+=int(t["blocked"] and t["evaluation"]["joint"])
        r["simulated"]+=t["simulated"];r["executed_actions"]+=t["executed_actions"]
        family=r["by_family"].setdefault(t["family"],{"n":0,"joint":0})
        family["n"]+=1;family["joint"]+=int(t["evaluation"]["joint"])
    return result

def call_one(client,case,method):
    runtime,blocked=prefix(case);payload=payload_for(public_case(case),runtime,blocked,method)
    output={"case_id":case["id"],"method":method,"payload":payload,"request_model":"gpt-6-luna"}
    call_id="v2-pilot-1:"+case["id"]+":"+method
    try:
        record=client.generate("v2_repair",INSTRUCTION,payload,SCHEMA,call_id,max_output=6000)
        output.update(status="ok",plans=record["value"]["plans"],model=record["response"]["model"],
                      usage=record["response"].get("usage",{}),seconds=record["seconds"],
                      cost_usd=record.get("conservative_usage_usd"),fingerprint=record["fingerprint"])
    except Exception as exc:
        # Keep model refusals/incompletes in the denominator. Local full details remain in ignored cache.
        output.update(status=type(exc).__name__,plans=[])
    # Retain costs/usage even for refusal/incomplete/HTTP failures. The original client
    # may retry transient errors up to three dispatch attempts per logical request.
    for path in client.calls.glob("*.json"):
        try:cached=json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:continue  # another worker may still be writing
        if cached.get("call_id")!=call_id:continue
        key=cached["fingerprint"]
        with client.budget.transaction():
            attempts=[{"id":k,**v} for k,v in client.budget.records.items() if k.startswith(key+":")]
        output.update(fingerprint=key,attempts=attempts,usage=cached.get("response",{}).get("usage",{}),
                      seconds=cached.get("seconds",0),model=cached.get("response",{}).get("model"),
                      private_record_status=cached["status"])
        break
    if "attempts" not in output:raise RuntimeError("Missing auditable API record; stop instead of losing cost attribution")
    dump(OUT/"proposals"/(case["id"]+"-"+method+".json"),output)
    return output

def main():
    parser=argparse.ArgumentParser();parser.add_argument("--live",action="store_true");parser.add_argument("--freeze-only",action="store_true")
    args=parser.parse_args();freeze()
    if args.freeze_only:
        print("Frozen development protocol, code, fixture and prompt hashes.");return
    cases=make_cases();trials=deterministic_trials(cases)
    if args.live:
        from src.api import Client
        client=Client(ROOT);before=client.budget.total()
        client.calls=ROOT/"results/raw_runs/v2_calls"
        client.calls.mkdir(parents=True,exist_ok=True)
        jobs=[(c,m) for c in cases if prefix(c)[1] is not None for m in LIVE]
        random.Random(20261014).shuffle(jobs)
        with ThreadPoolExecutor(max_workers=3) as pool:
            futures={pool.submit(call_one,client,c,m):(c["id"],m) for c,m in jobs}
            for i,future in enumerate(as_completed(futures),1):
                result=future.result();print(f"{i}/{len(jobs)} {result['case_id']} {result['method']} {result['status']}",flush=True)
        dump(OUT/"accounting.json",{"ledger_before_invocation":before,"ledger_after":client.budget.total(),
             "v1_baseline_usd":1.013328125,"study_limit_usd":20,"utc":datetime.now(timezone.utc).isoformat()})
    proposals={}
    for path in sorted((OUT/"proposals").glob("*.json")):
        p=json.loads(path.read_text(encoding="utf-8"));proposals[(p["case_id"],p["method"])]=p
    if proposals:
        for c in cases:
            blocked=prefix(c)[1] is not None
            for method in (*LIVE,"GraphNoSim"):
                source="GraphPlanner" if method=="GraphNoSim" else method
                proposal=proposals.get((c["id"],source))
                if blocked and proposal is None:raise RuntimeError("Incomplete proposal matrix")
                trials.append(trial(c,method,proposal["plans"] if proposal else [],proposal["status"] if proposal else "not_needed"))
    dump(OUT/"trials.json",trials);dump(OUT/"summary.json",summarize(trials))
    dump(OUT/"analysis.json",analyze(trials,list(proposals.values())))
    seal_evidence()
    print(json.dumps({m:{k:v for k,v in x.items() if k!="by_family"} for m,x in summarize(trials).items()},indent=2))

if __name__=="__main__":main()

