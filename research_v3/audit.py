"""Pre-measurement complexity certificates. Never called by a defense/model."""
from itertools import combinations
from research_v2.graph import dependency_index
from .fixtures import make_cases,public_case
from .engine import prefix,execute_candidate,catalogue
from .oracle import evaluate

def certificates():
    rows=[]
    for c in make_cases():
        r,blocked=prefix(c);single=catalogue(public_case(c));successes=0
        if c["variant"]=="attack":
            for edit in single:
                try:q=execute_candidate(r,c["program"],{"edits":[edit],"moves":[],"plan":[]})
                except ValueError:continue
                successes+=int(evaluate(c,q)["joint"])
            if successes:raise AssertionError("Single-parameter edit solves attack: "+c["id"])
            corrections=[("edit",x) for x in c["fix_edits"]]+[("move",x) for x in c["fix_moves"]]
            minimum=None;tested=0
            for size in range(len(corrections)+1):
                for subset in combinations(corrections,size):
                    tested+=1
                    candidate={"edits":[x for k,x in subset if k=="edit"],"moves":[x for k,x in subset if k=="move"],"plan":[]}
                    try:q=execute_candidate(r,c["program"],candidate)
                    except ValueError:continue
                    if evaluate(c,q)["joint"]:minimum=size;break
                if minimum is not None:break
            if minimum is None or minimum<3:raise AssertionError("Insufficient multi-site challenge")
        else:minimum=0;tested=0
        graph=dependency_index(c["reference"]);depth=[1]*len(c["reference"])
        for target in range(len(depth)):
            sources=[s for s,t in graph["edges"] if t==target]
            if sources:depth[target]=1+max(depth[s] for s in sources)
        rows.append({"case_id":c["id"],"family":c["family"],"width":c["width"],"variant":c["variant"],
                     "program_actions":len(c["program"]),"reference_dependency_depth":max(depth),
                     "single_parameter_catalogue_size":len(single),"successful_single_parameter_edits":successes,
                     "known_correction_subset_minimum":minimum,"known_subsets_tested":tested,
                     "caveat":"Minimum is within the authored correction-set subsets, not all possible programs."})
    return rows
