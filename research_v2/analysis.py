"""Paired development comparisons and conservative per-attempt API accounting."""
import random
from statistics import mean

def analyze(trials,proposals):
    by_method={}
    for t in trials:by_method.setdefault(t["method"],{})[t["case_id"]]=t
    comparisons={}
    for left,right in (("GraphPlanner","Planner"),("GraphSearch","ProgramSearch"),
                       ("GraphPlanner","GraphNoSim"),("GraphPlanner","GraphShuffled")):
        if left not in by_method or right not in by_method:continue
        rows=[]
        for case_id,a in by_method[left].items():
            b=by_method[right][case_id]
            rows.append({"case_id":case_id,"family":a["family"],"blocked":a["blocked"],
                         "joint_delta":int(a["evaluation"]["joint"])-int(b["evaluation"]["joint"]),
                         "simulation_delta":a["simulated"]-b["simulated"]})
        families={f:mean(r["joint_delta"] for r in rows if r["family"]==f) for f in sorted({r["family"] for r in rows})}
        rng=random.Random(20261014);vals=list(families.values())
        bootstrap=sorted(mean(rng.choices(vals,k=len(vals)))*100 for _ in range(10000))
        key="paired_graph_minus_planner" if (left,right)==("GraphPlanner","Planner") else left+"_minus_"+right
        comparisons[key]={"n":len(rows),"joint_difference_pp":100*mean(r["joint_delta"] for r in rows),
             "blocked_joint_difference_pp":100*mean(r["joint_delta"] for r in rows if r["blocked"]) if any(r["blocked"] for r in rows) else None,
             "family_deltas":families,"descriptive_family_bootstrap_95_pp":[bootstrap[249],bootstrap[9749]],
             "warning":"Six authored development families; interval is descriptive, not evidence of equivalence or external validity.",
             "case_pairs":rows}
    usage={}
    for p in proposals:
        row=usage.setdefault(p["method"],{"logical_calls":0,"failed_logical_calls":0,"dispatch_attempts":0,
             "pending_attempts":0,"input_tokens":0,"output_tokens":0,"charged_or_reserved_usd":0.0,
             "reported_model_seconds":0.0,"returned_models":[]})
        row["logical_calls"]+=1;row["failed_logical_calls"]+=p["status"]!="ok"
        row["input_tokens"]+=p.get("usage",{}).get("input_tokens",0)
        row["output_tokens"]+=p.get("usage",{}).get("output_tokens",0)
        row["reported_model_seconds"]+=p.get("seconds",0)
        for attempt in p.get("attempts",[]):
            row["dispatch_attempts"]+=1
            row["pending_attempts"]+=attempt["status"]!="settled"
            row["charged_or_reserved_usd"]+=attempt.get("settled",attempt["reserved"])
        model=p.get("model")
        if model and model not in row["returned_models"]:row["returned_models"].append(model)
    return {**comparisons,"model_usage":usage,
            "timing_note":"Provider call timing includes cached original call durations; not an end-to-end latency benchmark.",
            "shared_proposals":"GraphNoSim uses GraphPlanner proposals; no extra model dispatch."}

