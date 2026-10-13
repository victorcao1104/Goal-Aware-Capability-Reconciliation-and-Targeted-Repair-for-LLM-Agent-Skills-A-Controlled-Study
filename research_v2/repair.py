"""Shared bounded candidate evaluation. Graph data never supplies authority."""
from copy import deepcopy
from itertools import islice,product
from .runtime import Runtime,Rejected
from .goals import public_loss,value_satisfies
from .graph import dependency_index
from .fixtures import a

MAX_CANDIDATES=4
MAX_ACTIONS=12

def prefix(case):
    runtime=Runtime(case["config"])
    for index,action in enumerate(case["program"]):
        try:runtime.step(action)
        except Rejected as exc:return runtime,{"index":index,"reason":str(exc),"action":action}
    return runtime,None

def freshen(plan,runtime):
    mapping={};out=[]
    for action in plan:
        action=deepcopy(action);action["inputs"]=[mapping.get(x,x) for x in action["inputs"]]
        old=action["out"]
        if old:
            new=old;serial=0
            while new in runtime.handles or new in mapping.values():
                serial+=1;new=f"r{serial}_"+old
            mapping[old]=new;action["out"]=new
        out.append(action)
    return out

def execute(runtime,plan):
    if not isinstance(plan,list) or not 1<=len(plan)<=MAX_ACTIONS:raise Rejected("Plan length limit")
    for action in freshen(plan,runtime):runtime.step(action)

def repair(runtime,plans,goals,simulate=True):
    candidates=plans[:MAX_CANDIDATES];records=[];selected=None;best=None
    if not simulate:
        result=runtime.clone()
        if candidates:
            try:execute(result,candidates[0])
            except (Rejected,KeyError,TypeError):pass
        return {"runtime":result,"simulated":0,"selected":0 if candidates else None,"candidates":[]}
    for i,plan in enumerate(candidates):
        trial=runtime.clone()
        try:
            execute(trial,plan);loss=public_loss(trial,goals)
            rank=(loss,len(plan),i)
            records.append({"index":i,"valid":True,"public_loss":loss,"actions":len(plan)})
            if best is None or rank<best:best=rank;selected=i
        except (Rejected,KeyError,TypeError):
            records.append({"index":i,"valid":False})
    result=runtime.clone()
    if selected is not None:
        execute(result,candidates[selected])
    return {"runtime":result,"simulated":len(candidates),"selected":selected,"candidates":records}

def seeds(case,graph=False,limit=MAX_CANDIDATES,shuffle=False):
    program=case["program"];variants=[]
    distances=dependency_index(program,shuffle)["backward_distance"]
    for i,action in enumerate(program):
        replacements=[]
        if action["op"]=="concat" and len(action["inputs"])>1:
            for index in range(len(action["inputs"])):
                # A single-input concat is identity, not an extra list wrapper.
                replacement=deepcopy(action);replacement["op"]="project";replacement["path"]=""
                replacement["inputs"]=[action["inputs"][index]]
                replacements.append(replacement)
        if action["op"]=="project":
            # Public source structure is available to both methods; no oracle paths.
            keys=sorted({"/"+k.replace("~","~0").replace("/","~1") for f in case["config"]["files"].values()
                         if isinstance(f["data"],dict) for k in f["data"]})
            for path in keys:
                replacement=deepcopy(action);replacement["path"]=path;replacements.append(replacement)
        if action["op"] in ("send","write"):
            for goal in case["goals"]:
                if goal["effect"]==action["op"]:
                    replacement=deepcopy(action);replacement["resource"]=goal["resource"];replacements.append(replacement)
        for replacement in replacements:
            if replacement==action:continue
            plan=deepcopy(program);plan[i]=replacement
            variants.append((distances.get(i,999) if graph else i,i,len(variants),plan))
    variants.sort(key=lambda row:row[:3])
    plans=[v[-1] for v in variants]
    return plans if limit is None else plans[:limit]

def handle_plans(runtime,goals):
    # Inspect all existing handles; the simulation budget does not arbitrarily
    # truncate this cheap index lookup. Already satisfied goals need no rewrite.
    choices=[]
    for g in goals:
        if public_loss(runtime,[g])==0:continue
        allowed=set(runtime.policy["sinks"].get(g["resource"],[]))-set(runtime.policy.get("deny_labels",[]))
        eligible=[a(g["effect"],inputs=[handle],resource=g["resource"])
                  for handle,value in runtime.handles.items()
                  if value.sources and value.sources<=allowed and value_satisfies(value.data,g)]
        choices.append(eligible)
    return [list(plan) for plan in islice(product(*choices),MAX_CANDIDATES)] if choices else []

