"""Frozen, paired two-round Luna study with the original cumulative budget."""
import argparse
from concurrent.futures import ThreadPoolExecutor,as_completed
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import random
import re
import os
import subprocess
import tempfile

from research_v2.run import freeze as verify_v2
from scripts.reproduce import verify_frozen
from .fixtures import make_cases,public_case
from .engine import prefix,simulate_round,execute_candidate,public_loss,MAX_ROUNDS
from .oracle import evaluate
from .model import payload_for,INSTRUCTION,SCHEMA
from .analysis import summarize

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"research_v3/results"
METHODS=("Planner","GraphPlanner","GraphShuffled")
REPEATS=3

def dump(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    data=(json.dumps(value,ensure_ascii=False,indent=2)+"\n").encode("utf-8")
    with tempfile.NamedTemporaryFile(dir=path.parent,delete=False) as stream:
        temporary=Path(stream.name);stream.write(data)
    try:os.replace(temporary,path)
    finally:temporary.unlink(missing_ok=True)
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def schedule():
    return [{"case_id":c["id"],"method":m,"repeat":r} for c in make_cases() for r in range(REPEATS) for m in METHODS]

def freeze(create=False):
    verify_frozen(ROOT);verify_v2()
    paths=sorted((ROOT/"research_v3").glob("*.py"))+sorted((ROOT/"tests_v3").glob("*.py"))
    paths += [ROOT/"src/api.py",ROOT/"docs/protocol/dependency-repair-v3.md",ROOT/"research_v2/results/freeze.json",ROOT/"configs/frozen-study.json"]
    value={"files":{p.relative_to(ROOT).as_posix():sha(p) for p in paths},
           "fixtures_sha256":hashlib.sha256(json.dumps(make_cases(),sort_keys=True).encode()).hexdigest(),
           "schedule":schedule(),"model":"gpt-6-luna","max_output_tokens":8000,"seed":314159,
           "kind":"authored multi-site mechanism study","prior_study_cost_usd":1.034103375}
    path=OUT/"freeze.json"
    if path.exists():
        if json.loads(path.read_text(encoding="utf-8"))!=value:raise RuntimeError("Frozen v3 inputs changed")
    elif create:
        from .audit import certificates
        audit=certificates()
        dump(path,value);dump(OUT/"cases.json",make_cases());dump(OUT/"complexity.json",audit)
        dump(OUT/"model-spec.json",{"instruction":INSTRUCTION,"schema":SCHEMA})
    else:raise RuntimeError("Freeze before execution")
    return value

def slug(cid,method,repeat,round_index):
    return f"{cid}-{method}-r{repeat}-q{round_index}"

def feedback_history(round_index,proposal,result):
    return {"round":round_index,"candidates":proposal["candidates"],"model_status":proposal["status"],
            "feedback":result["feedback"],"selected":result["selected"],"public_loss":result["public_loss"]}

def replay_trajectory(case,method,repeat,proposals):
    runtime,blocked=prefix(case);history=[];simulated=0;steps=0;first=None
    if blocked:
        for round_index,p in enumerate(proposals[:MAX_ROUNDS]):
            if round_index==0 and p["candidates"]:
                try:first=evaluate(case,execute_candidate(runtime,case["program"],p["candidates"][0]))["joint"]
                except (ValueError,KeyError,TypeError):first=False
            result=simulate_round(runtime,case["program"],case["goals"],p["candidates"])
            runtime=result["runtime"];simulated+=result["simulated"]
            steps+=sum(x["executed_actions"] for x in result["feedback"])
            history.append(feedback_history(round_index,p,result))
            if result["public_loss"]==0:break
    return {"case_id":case["id"],"method":method,"repeat":repeat,"family":case["family"],"width":case["width"],
            "variant":case["variant"],"blocked":blocked is not None,"rounds":len(history),"simulated":simulated,
            "simulation_actions":steps,"history":history,"first_candidate_joint":first,
            "public_loss":public_loss(runtime,case["goals"]),"evaluation":evaluate(case,runtime),"snapshot":runtime.snapshot()}

def request_model(client,case,method,repeat,round_index,payload):
    from src.api import BudgetExceeded
    name=slug(case["id"],method,repeat,round_index);path=OUT/"requests"/(name+".json")
    if path.exists():
        old=json.loads(path.read_text(encoding="utf-8"))
        if old["payload"]!=json.loads(json.dumps(payload)):raise RuntimeError("Cached public request differs")
        return old
    call_id="v3:"+name
    p={"case_id":case["id"],"method":method,"repeat":repeat,"round":round_index,"request_model":"gpt-6-luna","payload":payload}
    cached=None
    try:
        cached=client.generate("v3_repair",INSTRUCTION,payload,SCHEMA,call_id,max_output=8000)
        p.update(status="ok",candidates=cached["value"]["candidates"],notes=cached["value"]["notes"])
    except BudgetExceeded:raise
    except Exception as exc:
        p.update(status=type(exc).__name__,candidates=[],notes="")
        matches=re.findall(r"[0-9a-f]{64}",str(exc))
        for match in matches:
            source=client.calls/(match+".json")
            if source.exists():cached=json.loads(source.read_text(encoding="utf-8"));break
        if cached is None:
            for source in client.calls.glob("*.json"):
                try:record=json.loads(source.read_text(encoding="utf-8"))
                except json.JSONDecodeError:continue
                if record.get("call_id")==call_id:cached=record;break
    if cached is None:raise RuntimeError("Missing auditable API record")
    key=cached["fingerprint"]
    with client.budget.transaction():
        attempts=[{"id":k,**v} for k,v in client.budget.records.items() if k.startswith(key+":")]
    p.update(fingerprint=key,attempts=attempts,usage=cached.get("response",{}).get("usage",{}),
             model=cached.get("response",{}).get("model"),seconds=cached.get("seconds",0),
             provider_status=cached["status"])
    dump(path,p);return p

def live_trajectory(client,case,method,repeat):
    runtime,blocked=prefix(case);history=[];proposals=[]
    if blocked:
        for round_index in range(MAX_ROUNDS):
            payload=payload_for(public_case(case),runtime,blocked,history,method)
            p=request_model(client,case,method,repeat,round_index,payload);proposals.append(p)
            result=simulate_round(runtime,case["program"],case["goals"],p["candidates"])
            runtime=result["runtime"];history.append(feedback_history(round_index,p,result))
            if result["public_loss"]==0:break
    trial=replay_trajectory(case,method,repeat,proposals)
    dump(OUT/"trajectories"/(slug(case["id"],method,repeat,0)+".json"),trial)
    return trial

def collect():
    cases={c["id"]:c for c in make_cases()};trials=[];proposals=[]
    for job in schedule():
        c=cases[job["case_id"]];ps=[]
        for q in range(MAX_ROUNDS):
            path=OUT/"requests"/(slug(c["id"],job["method"],job["repeat"],q)+".json")
            if path.exists():ps.append(json.loads(path.read_text(encoding="utf-8")))
        t=replay_trajectory(c,job["method"],job["repeat"],ps)
        saved=OUT/"trajectories"/(slug(c["id"],job["method"],job["repeat"],0)+".json")
        if not saved.exists() or json.loads(saved.read_text(encoding="utf-8"))!=t:raise RuntimeError("Missing or inconsistent trajectory")
        if c["variant"]=="attack" and (not ps or len(ps)!=t["rounds"] or (t["public_loss"]!=0 and len(ps)<MAX_ROUNDS)):
            raise RuntimeError("Incomplete adaptive schedule")
        trials.append(t);proposals.extend(ps)
    return trials,proposals

def seal():
    dump(OUT/"evidence-manifest.json",{"files":{p.relative_to(OUT).as_posix():sha(p) for p in sorted(OUT.rglob("*.json")) if p.name!="evidence-manifest.json"}})

def parse_args(argv=None):
    parser=argparse.ArgumentParser();mode=parser.add_mutually_exclusive_group()
    mode.add_argument("--freeze",action="store_true");mode.add_argument("--live",action="store_true")
    return parser.parse_args(argv)

def committed_inputs(manifest):
    def committed(name):
        return subprocess.check_output(["git","show","HEAD:"+name],cwd=ROOT,stderr=subprocess.DEVNULL)
    if committed("research_v3/results/freeze.json")!=(OUT/"freeze.json").read_bytes():
        raise RuntimeError("Commit the frozen manifest before paid execution")
    for name,digest in manifest["files"].items():
        if hashlib.sha256(committed(name)).hexdigest()!=digest:
            raise RuntimeError("Commit all frozen source files before paid execution")
    return subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip()

def main():
    args=parse_args();manifest=freeze(create=args.freeze)
    if args.freeze and not args.live:
        print("Frozen v3 inputs, prompts, schedule and complexity certificates.");return
    if args.live:
        source_commit=committed_inputs(manifest)
        from src.api import Client
        client=Client(ROOT);client.calls=ROOT/"results/raw_runs/v3_calls";client.calls.mkdir(parents=True,exist_ok=True)
        before=client.budget.total();jobs=schedule();random.Random(314159).shuffle(jobs)
        cases={c["id"]:c for c in make_cases()}
        with ThreadPoolExecutor(max_workers=4) as pool:
            futures=[pool.submit(live_trajectory,client,cases[j["case_id"]],j["method"],j["repeat"]) for j in jobs]
            for count,future in enumerate(as_completed(futures),1):
                t=future.result()
                if count%10==0 or count==len(jobs):print(f"{count}/{len(jobs)} trajectories complete",flush=True)
        dump(OUT/"accounting.json",{"before_invocation_usd":before,"after_usd":client.budget.total(),
                 "prior_study_usd":1.034103375,"ceiling_usd":20,"source_commit":source_commit,"utc":datetime.now(timezone.utc).isoformat()})
    trials,proposals=collect();dump(OUT/"summary.json",summarize(trials,proposals));seal()
    print(json.dumps({m:{k:v for k,v in s.items() if k not in ("by_family","by_width")} for m,s in summarize(trials,proposals)["methods"].items()},indent=2))

if __name__=="__main__":main()
