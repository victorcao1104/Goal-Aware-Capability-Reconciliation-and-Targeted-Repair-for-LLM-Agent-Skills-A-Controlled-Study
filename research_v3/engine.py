"""Common repair interface, capability gate, public feedback and bounded search."""
from copy import deepcopy
from research_v2.runtime import Runtime,Rejected
from research_v2.repair import freshen
from research_v2.goals import value_satisfies

MAX_ACTIONS=96
MAX_EDITS=16
MAX_CANDIDATES=4
MAX_ROUNDS=2

def prefix(case):
    r=Runtime(case["config"])
    for i,a in enumerate(case["program"]):
        try:r.step(a)
        except Rejected as exc:return r,{"node":i,"reason":str(exc),"action":a}
    return r,None

def patch_program(program,candidate):
    if set(candidate)!={"edits","moves","plan"}:raise Rejected("Candidate schema")
    if candidate["plan"]:
        if candidate["edits"] or candidate["moves"]:raise Rejected("Choose patches OR free plan")
        plan=deepcopy(candidate["plan"])
    else:
        if len(candidate["edits"])+len(candidate["moves"])>MAX_EDITS:raise Rejected("Edit limit")
        actions=deepcopy(program);seen=set()
        for e in candidate["edits"]:
            if set(e)!={"node","field","value"} or type(e["node"]) is not int or not isinstance(e["value"],str):raise Rejected("Edit schema")
            node,field=e["node"],e["field"]
            if not 0<=node<len(actions) or (node,field) in seen:raise Rejected("Duplicate/invalid edit")
            seen.add((node,field))
            if field.startswith("input") and field[5:].isdigit():
                i=int(field[5:])
                if i>=len(actions[node]["inputs"]):raise Rejected("Input position")
                actions[node]["inputs"][i]=e["value"]
            elif field in ("path","field","resource"):actions[node][field]=e["value"]
            else:raise Rejected("Unsupported editable field")
        order=list(range(len(actions)));moved=set()
        for m in candidate["moves"]:
            if set(m)!={"node","after"} or type(m["node"]) is not int or type(m["after"]) is not int:raise Rejected("Move schema")
            n,after=m["node"],m["after"]
            if n not in order or after not in order or n==after or n in moved:raise Rejected("Move target")
            moved.add(n);order.remove(n);order.insert(order.index(after)+1,n)
        plan=[actions[i] for i in order]
    if not 1<=len(plan)<=MAX_ACTIONS:raise Rejected("Action limit")
    return plan

def execute_candidate(runtime,program,candidate):
    plan=patch_program(program,candidate);q=runtime.clone()
    for action in freshen(plan,q):q.step(action)
    return q

def causal_index(runtime):
    parents={};producer={};writes={};read_version={}
    for i,event in enumerate(runtime.events):
        a=event["action"];parents[i]=[producer[x] for x in a["inputs"] if x in producer]
        if a["op"]=="read_output":
            read_version[i]=writes.get(a["resource"])
            if a["resource"] in writes:parents[i].append(writes[a["resource"]])
        if a["out"]:producer[a["out"]]=i
        if a["op"]=="write":writes[a["resource"]]=i
    return parents,writes,read_version

def receipt_satisfied(runtime,goal):
    sources=goal.get("receipt_sources",[])
    if not sources:return True
    matches=[i for i,e in enumerate(runtime.events) if e["action"]["op"]==goal["effect"] and e["action"]["resource"]==goal["resource"]]
    if not matches:return False
    parents,writes,versions=causal_index(runtime)
    def ancestors(node):
        visited=set();todo=[node]
        while todo:
            n=todo.pop()
            if n in visited:continue
            visited.add(n);todo.extend(parents[n])
        return visited
    nodes=ancestors(matches[-1])
    for source in sources:
        valid=False
        for h in nodes:
            if runtime.events[h]["action"]["op"]!="hash":continue
            for read in ancestors(h):
                a=runtime.events[read]["action"]
                if a["op"]=="read_output" and a["resource"]==source and versions.get(read)==writes.get(source) and source in writes:
                    valid=True
        if not valid:return False
    return True

def public_loss(runtime,goals):
    loss=0
    for g in goals:
        data=runtime.sends if g["effect"]=="send" else {k:v.data for k,v in runtime.writes.items()}
        if g["resource"] not in data or not value_satisfies(data[g["resource"]],g) or not receipt_satisfied(runtime,g):loss+=1
    return loss

def catalogue(public):
    paths={""};fields=set()
    def walk(value,path=""):
        if isinstance(value,dict):
            for k,v in value.items():
                fields.add(k);p=path+"/"+k.replace("~","~0").replace("/","~1");paths.add(p);walk(v,p)
        # Do not enumerate array indices as task-level selectors.
    for f in public["config"]["files"].values():walk(f["data"])
    program=public["program"];producers={a["out"]:(i,a["op"]) for i,a in enumerate(program) if a["out"]}
    edits=[]
    for i,a in enumerate(program):
        choices={}
        if a["op"]=="project":choices["path"]=sorted(paths)
        if a["op"] in ("sort","join","sum"):choices["field"]=sorted(fields|{""})
        if a["op"] in ("send","write"):
            choices["resource"]=[k for k,v in public["config"]["policy"]["operations"].items() if a["op"] in v]
        if a["op"]=="read_output":
            choices["resource"]=[k for k,v in public["config"]["policy"]["operations"].items() if "write" in v]
        for pos,handle in enumerate(a["inputs"]):
            if handle in producers:
                kind=producers[handle][1]
                choices[f"input{pos}"]=[h for h,(j,op) in producers.items() if j<i and op==kind]
        for field,values in choices.items():
            old=a["inputs"][int(field[5:])] if field.startswith("input") else a[field]
            for value in values:
                if value!=old:edits.append({"node":i,"field":field,"value":value})
    return edits

def grouped_catalogue(public):
    grouped={}
    for e in catalogue(public):grouped.setdefault((e["node"],e["field"]),[]).append(e["value"])
    return [{"node":n,"field":f,"alternatives":v} for (n,f),v in grouped.items()]

def simulate_round(runtime,program,goals,candidates):
    feedback=[];best=None;best_rank=None;used=0;selected=None
    for i,candidate in enumerate(candidates[:MAX_CANDIDATES]):
        used+=1;q=runtime.clone();steps=0
        try:
            plan=patch_program(program,candidate)
            for action in freshen(plan,q):
                q.step(action);steps+=1
            loss=public_loss(q,goals);rank=(loss,steps,i)
            row={"candidate":i,"valid":True,"public_loss":loss,"executed_actions":steps}
            if best_rank is None or rank<best_rank:best=candidate;best_rank=rank;selected=i
            feedback.append(row)
            if loss==0:break
        except (ValueError,KeyError,TypeError) as exc:
            feedback.append({"candidate":i,"valid":False,"public_loss":None,"executed_actions":steps,"reason":str(exc)[:160]})
    final=execute_candidate(runtime,program,best) if best is not None else runtime.clone()
    return {"runtime":final,"feedback":feedback,"simulated":used,"selected":selected,
            "public_loss":public_loss(final,goals),"selected_candidate":best}
