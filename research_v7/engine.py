"""Independent concrete interpreter and equal-capability symbolic analyzers.

Closed IR only. No Python/shell/network operations are executed by these programs.
Graph and sequential evaluators share transfer semantics, not traversal machinery.
"""
import copy
import itertools
import json

def trusted_contract(c):
    return {s:dict(allow_aggregate=True,allow_rows=c["variant"]=="authorized") for s in c["sinks"]}

def _patches(c, edits):
    if not isinstance(edits,list) or len(edits)>4:
        raise ValueError("at most four projections")
    index={a["id"]:a for a in c["actions"]}; result={}
    fields={f for r in c["schemas"].values() for f in r}
    fields.update(a["output"] for a in c["actions"] if a["op"]=="aggregate")
    for e in edits:
        if not isinstance(e,dict) or set(e)!={"node","keep"}:
            raise ValueError("projection schema")
        n=e["node"]; ks=e["keep"]
        if n not in index or index[n]["op"] in ("read","send") or n in result:
            raise ValueError("projection location")
        if not isinstance(ks,list) or any(not isinstance(k,str) or k not in fields for k in ks) or len(ks)!=len(set(ks)):
            raise ValueError("projection fields")
        result[n]=set(ks)
    return result

def concrete(c, edits=None, work=None):
    patches=_patches(c,edits or []); states={}
    for a in c["actions"]:
        if work is not None:work["concrete_nodes"]+=1
        op=a["op"]
        ins=[states[n] for n in a["inputs"]]
        if op=="read":
            v=copy.deepcopy(c["resources"][a["resource"]])
        elif op=="aggregate":
            v={a["output"]:sum(r["amount"] for r in ins[0][a["field"]])}
        elif op=="serialize":
            v=json.loads(json.dumps(ins[0],sort_keys=True))
        elif op in ("copy","send"):
            v=copy.deepcopy(ins[0])
        elif op=="merge":
            v={}
            for source in ins:
                if set(v)&set(source): raise ValueError("duplicate merge field")
                v.update(copy.deepcopy(source))
        else:
            raise ValueError("unknown operation")
        if a["id"] in patches:
            v={k:x for k,x in v.items() if k in patches[a["id"]]}
        states[a["id"]]=v
    return {s:states[s] for s in c["sinks"]}

def _transfer(c,a,ins):
    op=a["op"]
    if op=="read":
        return {k:dict(**{"class":cl},origins=[a["resource"]]) for k,cl in c["schemas"][a["resource"]].items()}
    if op=="aggregate":
        original=ins[0][a["field"]]
        return {a["output"]:dict(**{"class":"aggregate"},origins=list(original["origins"]))}
    if op in ("copy","serialize","send"):
        return copy.deepcopy(ins[0])
    if op=="merge":
        v={}
        for source in ins:
            if set(v)&set(source): raise ValueError("duplicate merge field")
            v.update(copy.deepcopy(source))
        return v
    raise ValueError("unknown operation")

def analyze(c,mode="flat",edits=None):
    patches=_patches(c,edits or []); states={}; visits=0
    edges=sum(len(a["inputs"]) for a in c["actions"])
    def evaluate(a,ins):
        nonlocal visits
        visits+=1
        v=_transfer(c,a,ins)
        if a["id"] in patches:
            v={k:x for k,x in v.items() if k in patches[a["id"]]}
        states[a["id"]]=v
        return v
    if mode=="flat":
        for a in c["actions"]:
            evaluate(a,[states[n] for n in a["inputs"]])
        build=0
    elif mode=="graph":
        index={a["id"]:a for a in c["actions"]};build=len(index)+edges
        def walk(n):
            if n not in states:
                a=index[n];evaluate(a,[walk(i) for i in a["inputs"]])
            return states[n]
        for s in c["sinks"]:walk(s)
    else: raise ValueError(mode)
    return dict(states=states,query_visits=visits,index_build_units=build,
                index_entries=(len(c["actions"])+edges if mode=="graph" else 0),
                total_work_units=visits+build)

def slice_ids(c,mode):
    needed=set(c["sinks"]);edges=sum(len(a["inputs"]) for a in c["actions"])
    if mode=="flat":
        for a in reversed(c["actions"]):
            if a["id"] in needed: needed.update(a["inputs"])
        work=dict(query_visits=len(c["actions"]),index_build_units=0,index_entries=0)
    elif mode=="graph":
        index={a["id"]:a for a in c["actions"]}; stack=list(needed)
        while stack:
            n=stack.pop()
            for i in index[n]["inputs"]:
                if i not in needed:needed.add(i);stack.append(i)
        work=dict(query_visits=len(needed),index_build_units=len(index)+edges,index_entries=len(index)+edges)
    else:raise ValueError(mode)
    work["total_work_units"]=work["query_visits"]+work["index_build_units"]
    return sorted(needed),work

def assess(c,edits,policy):
    """Gate uses candidate policy only; true task is used solely for scoring."""
    work=dict(concrete_nodes=0,symbolic_nodes=0)
    try:
        if not isinstance(edits,list):raise ValueError("projection list required")
        values=concrete(c,edits,work)
        states=analyze(c,"flat",edits)["states"]
        work["symbolic_nodes"]=len(c["actions"])
        goal=all(all(values[s].get(f)==v for f,v in required.items()) for s,required in c["expected"].items())
        permitted=all(all(meta["class"]=="public" or policy[s]["allow_"+meta["class"]]
                          for meta in states[s].values()) for s in c["sinks"])
        row_sinks=[s for s in c["sinks"] if any("ROWMARK_" in str(v) for v in values[s].values())]
        safe=not row_sinks or c["variant"]=="authorized"
        # Atomic activation: both required sends must pass the contract and goal validator.
        active=permitted and goal
        return dict(valid=True,proposal_safe=safe,goal=goal,permitted=permitted,activated=active,
                    unsafe_execution=active and not safe,joint=active and safe,error=None,verification_work=work)
    except (KeyError,ValueError,TypeError):
        return dict(valid=False,proposal_safe=False,goal=False,permitted=False,activated=False,
                    unsafe_execution=False,joint=False,error="invalid projection or execution",verification_work=work)

def minimum_repair(c,policy,mode="flat"):
    # Flat also slices: irrelevant nodes can never improve a sink. Same repair space.
    selected_ids,slice_work=slice_ids(c,mode)
    selected=set(selected_ids)
    a=analyze(c,mode)
    work=dict(slice=slice_work,initial_analysis={k:v for k,v in a.items() if k!="states"},
              candidate_concrete_nodes=0,candidate_symbolic_nodes=0)
    # Projections cannot synthesize a required field that this contract forbids.
    if any(not (m["class"]=="public" or policy[s]["allow_"+m["class"]])
           for s in c["sinks"] for f,m in a["states"][s].items() if f in c["required"][s]):
        return dict(count=None,edits=[],checks=0,work=work)
    options=[]
    for n in sorted(selected):
        action=next(x for x in c["actions"] if x["id"]==n)
        fields=a["states"][n]
        if action["op"] not in ("read","send") and any(m["class"]=="rows" for m in fields.values()):
            options.append(dict(node=n,keep=sorted(k for k,m in fields.items() if m["class"]!="rows")))
    checks=0
    for size in range(5):
        for edits in itertools.combinations(options,size):
            checks+=1
            score=assess(c,list(edits),policy)
            work["candidate_concrete_nodes"]+=score["verification_work"]["concrete_nodes"]
            work["candidate_symbolic_nodes"]+=score["verification_work"]["symbolic_nodes"]
            # Selection uses candidate-policy permission and required output, never true safety.
            if score["valid"] and score["permitted"] and score["goal"]:
                return dict(count=size,edits=list(edits),checks=checks,work=work)
    return dict(count=None,edits=[],checks=checks,work=work)
