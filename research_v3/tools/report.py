"""Derived presentation artifacts from the immutable recorded study; no API access."""
from collections import Counter
import json
from pathlib import Path
from statistics import mean

ROOT=Path(__file__).resolve().parents[1]

def main():
    source=ROOT/"results";out=ROOT/"report";out.mkdir(exist_ok=True)
    summary=json.loads((source/"summary.json").read_text(encoding="utf-8"))
    trials=[json.loads(p.read_text(encoding="utf-8")) for p in sorted((source/"trajectories").glob("*.json"))]
    requests=[json.loads(p.read_text(encoding="utf-8")) for p in sorted((source/"requests").glob("*.json"))]
    methods=("Planner","GraphPlanner","GraphShuffled");secondary={}
    for method in methods:
        ts=[t for t in trials if t["method"]==method and t["variant"]=="attack"]
        ps=[p for p in requests if p["method"]==method]
        chosen=[]
        for t in ts:
            if t["evaluation"]["joint"] and t["history"]:
                h=t["history"][-1]
                if h["selected"] is not None:chosen.append(h["candidates"][h["selected"]])
        secondary[method]={
            "returned_candidate_count_distribution":dict(Counter(len(p["candidates"]) for p in ps)),
            "chosen_successful_patch_edits_moves_distribution":dict(Counter(len(c["edits"])+len(c["moves"]) for c in chosen if not c["plan"])),
            "chosen_successful_free_plan_actions_distribution":dict(Counter(len(c["plan"]) for c in chosen if c["plan"])),
            "mean_simulations_per_attack":mean(t["simulated"] for t in ts),
            "mean_actions_per_attack":mean(t["simulation_actions"] for t in ts),
            "mean_rounds_per_attack":mean(t["rounds"] for t in ts),
            "two_round_trajectories":sum(t["rounds"]==2 for t in ts),
            "public_pass_but_exact_fail":sum(t["public_loss"]==0 and not t["evaluation"]["joint"] for t in ts)}
    (out/"secondary.json").write_bytes((json.dumps(secondary,indent=2)+"\n").encode())
    lines=["| Method | Attack joint | Control joint | Simulations | Simulated actions | Logical calls | Est. USD |",
           "| --- | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for m in methods:
        r=summary["methods"][m];u=summary["model_usage"][m]
        lines.append(f"| {m} | {r['attacked_joint']}/{r['attacked_n']} | {r['joint']-r['attacked_joint']}/{r['n']-r['attacked_n']} | {r['simulated']} | {r['simulation_actions']} | {u['logical_calls']} | {u['charged_or_reserved_usd']:.8f} |")
    (out/"comparison-tables.md").write_bytes(("\n".join(lines)+"\n").encode())
    import matplotlib
    matplotlib.use("Agg")
    matplotlib.rcParams["svg.hashsalt"]="dependency-repair-v3"
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(1,2,figsize=(9,3.7),layout="constrained")
    colors=["#3568a8","#258068","#8a6b9b"]
    labels=["No graph","Correct graph","Shuffled graph"]
    values=[100*summary["methods"][m]["attacked_joint"]/summary["methods"][m]["attacked_n"] for m in methods]
    axes[0].bar(labels,values,color=colors);axes[0].set_ylim(0,113)
    axes[0].set_ylabel("Safe exact completion (%)");axes[0].set_title("Attack trajectories (72 per arm)")
    for i,v in enumerate(values):axes[0].text(i,v+1.5,f"{v:.1f}%",ha="center")
    costs=[summary["model_usage"][m]["charged_or_reserved_usd"] for m in methods]
    axes[1].bar(labels,costs,color=colors);axes[1].set_ylabel("Estimated USD");axes[1].set_title("All accounted attempts")
    for ax in axes:
        ax.spines[["top","right"]].set_visible(False);ax.tick_params(axis="x",labelsize=9)
    for ext in ("png","svg"):
        path=out/("comparison."+ext)
        fig.savefig(path,dpi=180,metadata={"Date":None} if ext=="svg" else None)
        if ext=="svg":path.write_bytes(("\n".join(line.rstrip() for line in path.read_text(encoding="utf-8").splitlines())+"\n").encode("utf-8"))
    plt.close(fig)
    print("Generated presentation artifacts from recorded evidence; no model calls.")

if __name__=="__main__":main()
