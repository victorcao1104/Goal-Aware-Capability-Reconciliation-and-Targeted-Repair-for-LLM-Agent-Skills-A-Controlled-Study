"""Paired case-level estimates; repeated responses are not independent families."""
import random
from statistics import mean
from research_v2.analysis import analyze as usage_analyze

def summarize(trials,proposals):
    methods={}
    for t in trials:
        row=methods.setdefault(t["method"],{"n":0,"joint":0,"attacked_n":0,"attacked_joint":0,
            "unsafe_trials":0,"simulated":0,"simulation_actions":0,"rounds":0,"exhausted_failures":0,"by_width":{},"by_family":{}})
        row["n"]+=1;row["joint"]+=int(t["evaluation"]["joint"])
        row["unsafe_trials"]+=int(t["evaluation"]["unsafe_effects"]>0)
        row["simulated"]+=t["simulated"];row["simulation_actions"]+=t["simulation_actions"];row["rounds"]+=t["rounds"]
        if t["variant"]=="attack":
            row["attacked_n"]+=1;row["attacked_joint"]+=int(t["evaluation"]["joint"])
            row["exhausted_failures"]+=int(t["rounds"]==2 and not t["evaluation"]["joint"])
            for group,key in (("by_width",str(t["width"])),("by_family",t["family"])):
                s=row[group].setdefault(key,{"n":0,"joint":0});s["n"]+=1;s["joint"]+=int(t["evaluation"]["joint"])
    lookup={(t["case_id"],t["repeat"],t["method"]):t for t in trials if t["variant"]=="attack"}
    comparisons={}
    for target in ("Planner","GraphShuffled"):
        pairs=[]
        for (cid,rep,method),a in lookup.items():
            if method!="GraphPlanner" or (cid,rep,target) not in lookup:continue
            b=lookup[(cid,rep,target)]
            pairs.append({"case_id":cid,"repeat":rep,"family":a["family"],"width":a["width"],
                 "joint_delta":int(a["evaluation"]["joint"])-int(b["evaluation"]["joint"]),
                 "simulation_action_delta":a["simulation_actions"]-b["simulation_actions"],
                 "round_delta":a["rounds"]-b["rounds"]})
        if not pairs:continue
        case_deltas={cid:mean(p["joint_delta"] for p in pairs if p["case_id"]==cid) for cid in sorted({p["case_id"] for p in pairs})}
        families={f:mean(case_deltas[c] for c in case_deltas if any(p["case_id"]==c and p["family"]==f for p in pairs))
                  for f in sorted({p["family"] for p in pairs})}
        rng=random.Random(314159);vals=list(families.values())
        bootstrap=sorted(100*mean(rng.choices(vals,k=len(vals))) for _ in range(10000))
        comparisons["primary" if target=="Planner" else "shuffled_control"]={
            "attacked_case_count":len(case_deltas),"paired_trajectory_count":len(pairs),
            "joint_difference_pp":100*mean(vals),"case_deltas":case_deltas,"family_deltas":families,
            "descriptive_family_bootstrap_95_pp":[bootstrap[249],bootstrap[9749]],
            "graph_wins":sum(p["joint_delta"]==1 for p in pairs),"graph_losses":sum(p["joint_delta"]==-1 for p in pairs),
            "mean_simulation_action_difference":mean(p["simulation_action_delta"] for p in pairs),
            "pairs":pairs}
    usage=usage_analyze([],proposals)["model_usage"]
    return {"methods":methods,**comparisons,"model_usage":usage,
            "warning":"Authored six-topology mechanism study. Repeats are averaged within cases; intervals are descriptive, not equivalence tests.",
            "first_candidate_success":{m:sum(t["first_candidate_joint"] is True for t in trials if t["method"]==m and t["variant"]=="attack")
                                       for m in methods}}
