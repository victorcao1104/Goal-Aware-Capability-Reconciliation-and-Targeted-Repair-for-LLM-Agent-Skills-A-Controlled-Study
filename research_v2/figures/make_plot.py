"""Optional scientific figure; requires the repository's pinned matplotlib."""
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

def main():
    root=Path(__file__).resolve().parents[1]
    summary=json.loads((root/"results/summary.json").read_text(encoding="utf-8"))
    methods=["Gate","HandleSearch","ProgramSearch","GraphSearch","Planner","GraphPlanner","GraphShuffled","GraphNoSim"]
    fig,ax=plt.subplots(figsize=(8,4.4),layout="constrained")
    values=[100*summary[m]["recovered"]/summary[m]["blocked"] for m in methods]
    bars=ax.barh(methods,values,color=["#818998","#818998","#4e789b","#4e789b","#277d73","#277d73","#277d73","#277d73"])
    for bar,m in zip(bars,methods):
        n=summary[m]["recovered"];d=summary[m]["blocked"]
        ax.text(max(bar.get_width()-2,2),bar.get_y()+bar.get_height()/2,f"{n}/{d}",
                ha="right" if n else "left",va="center",color="white" if n else "#333333")
    ax.invert_yaxis();ax.set_xlim(0,105);ax.set_xticks([0,25,50,75,100])
    ax.set_xlabel("Exact task recovery after a scripted block (%)")
    ax.set_title("Upstream repair helps; the graph adds no observed recovery\nSix development families, 24 blocked cases; not a native attack benchmark",fontsize=11)
    ax.spines[["top","right"]].set_visible(False)
    fig.savefig(root/"figures/recovery.png",dpi=180)
    fig.savefig(root/"figures/recovery.pdf")
    print("Wrote v2 recovery figure from archived summary.")
if __name__=="__main__":main()

