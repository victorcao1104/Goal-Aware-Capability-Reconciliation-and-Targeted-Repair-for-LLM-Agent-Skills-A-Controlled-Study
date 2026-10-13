"""Closed deterministic effects. No host filesystem, network, eval or shell tools."""
from copy import deepcopy
from dataclasses import dataclass
import hashlib
import json
import re

class Rejected(ValueError):
    pass

def canonical(value):
    return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(",",":"),allow_nan=False)

def leaves(data, prefix=()):
    if isinstance(data,dict) and data:
        return {p:v for k,x in data.items() for p,v in leaves(x,prefix+(str(k),)).items()}
    if isinstance(data,list) and data:
        return {p:v for i,x in enumerate(data) for p,v in leaves(x,prefix+(str(i),)).items()}
    return {prefix:data}

def pointer(path):
    if not path:return ()
    if not isinstance(path,str) or not path.startswith("/"):raise Rejected("Invalid JSON pointer")
    return tuple(x.replace("~1","/").replace("~0","~") for x in path[1:].split("/"))

@dataclass
class Value:
    data: object
    origins: dict
    @property
    def sources(self):
        return set().union(*self.origins.values()) if self.origins else set()
    def export(self):
        return {"data":deepcopy(self.data),"origins":{
            ("/"+"/".join(x.replace("~","~0").replace("/","~1") for x in p) if p else ""):sorted(s)
            for p,s in self.origins.items()}}

def opaque(data, inputs):
    sources=set().union(*(v.sources for v in inputs))
    return Value(data,{p:set(sources) for p in leaves(data)})

def project(value,path):
    parts=pointer(path);data=value.data
    for part in parts:
        data=data[int(part)] if isinstance(data,list) else data[part]
    origins={p[len(parts):]:set(s) for p,s in value.origins.items() if p[:len(parts)]==parts}
    if not origins:raise Rejected("Missing provenance")
    return Value(deepcopy(data),origins)

OPS=("read","project","concat","render","sum","sort","unique","join","hash","write","read_output","send")
FIELDS={"op","out","inputs","resource","path","field"}

class Runtime:
    def __init__(self,config):
        self.config=deepcopy(config);self.policy=deepcopy(config["policy"])
        if set(self.policy.get("deny_destinations",[])) & set(self.policy["sinks"]):
            raise Rejected("Unresolved allow/deny destination conflict")
        self.handles={};self.writes={};self.sends={};self.events=[]
    def clone(self):return deepcopy(self)
    def snapshot(self):
        return {"handles":{k:v.export() for k,v in self.handles.items()},
                "writes":{k:v.export() for k,v in self.writes.items()},
                "sends":deepcopy(self.sends),"events":deepcopy(self.events)}
    def step(self,action):
        try:return self._step(action)
        except Rejected:raise
        except (KeyError,TypeError,ValueError,IndexError,OverflowError) as exc:
            raise Rejected("Malformed action or invalid tool input") from exc
    def _step(self,a):
        if not isinstance(a,dict) or set(a)!=FIELDS:raise Rejected("Invalid action schema")
        op=a["op"];out=a["out"]
        if op not in OPS or not all(isinstance(a[k],str) for k in FIELDS-{"inputs"}):raise Rejected("Unknown tool/schema")
        if not isinstance(a["inputs"],list) or len(a["inputs"])>12 or not all(isinstance(x,str) for x in a["inputs"]):
            raise Rejected("Invalid inputs")
        effects=op in ("write","send")
        if not effects and (not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]{0,39}",out) or out in self.handles):
            raise Rejected("Invalid or reused handle")
        vs=[self.handles[x] for x in a["inputs"]]
        arity={"read":0,"read_output":0,"project":1,"render":1,"sum":1,"sort":1,
               "unique":1,"join":2,"hash":1,"write":1,"send":1}
        if (op in arity and len(vs)!=arity[op]) or (op=="concat" and not vs):
            raise Rejected("Wrong arity")
        if op=="read":
            resource=a["resource"]
            if resource not in self.policy["read"]:raise Rejected("Read denied")
            f=self.config["files"][resource];labels={pointer(p):s for p,s in f["labels"].items()}
            origins={}
            for p in leaves(f["data"]):
                matches=[q for q in labels if p[:len(q)]==q]
                if not matches:raise Rejected("Unlabelled input")
                origins[p]={labels[max(matches,key=len)]}
            value=Value(deepcopy(f["data"]),origins)
        elif op=="read_output":value=deepcopy(self.writes[a["resource"]])
        elif op=="project":value=project(vs[0],a["path"])
        elif op=="concat":
            if all(isinstance(v.data,list) for v in vs):
                if any(not v.data for v in vs):
                    return self._store(a,opaque([x for v in vs for x in v.data],vs))
                data=[];origins={}
                for v in vs:
                    offset=len(data);data.extend(deepcopy(v.data))
                    for p,s in v.origins.items():origins[(str(int(p[0])+offset),)+p[1:]]=set(s)
                value=Value(data,origins)
            else:value=opaque([v.data for v in vs],vs)
        elif op=="render":value=opaque(canonical(vs[0].data),vs)
        elif op=="hash":
            data=vs[0].data
            value=opaque(hashlib.sha256((data if isinstance(data,str) else canonical(data)).encode()).hexdigest(),vs)
        elif op=="sum":
            data=vs[0].data
            nums=[row[a["field"]] for row in data] if a["field"] else data
            if not all(type(n) in (int,float) for n in nums):raise Rejected("Numeric sum required")
            value=opaque(sum(nums),vs)
        elif op=="sort":
            data=vs[0].data
            if not isinstance(data,list):raise Rejected("List required")
            value=opaque(sorted(data,key=(lambda x:x[a["field"]]) if a["field"] else None),vs)
        elif op=="unique":
            data=vs[0].data
            if not isinstance(data,list):raise Rejected("List required")
            seen=set();unique=[]
            for item in data:
                key=canonical(item)
                if key not in seen:seen.add(key);unique.append(item)
            value=opaque(unique,vs)
        elif op=="join":
            key=a["field"]
            left,right=(v.data for v in vs)
            if not isinstance(left,list) or not isinstance(right,list):raise Rejected("Lists required")
            if len(left)*len(right)>256:raise Rejected("Join work limit")
            value=opaque([{**x,**y} for x in left for y in right if x[key]==y[key]],vs)
        elif effects:
            value=vs[0];allowed=set(self.policy["sinks"].get(a["resource"],[]))-set(self.policy.get("deny_labels",[]))
            if op not in self.policy.get("operations",{}).get(a["resource"],["write","send"]):
                raise Rejected("Operation scope denied")
            if a["resource"] not in self.policy["sinks"] or not value.sources or not value.sources<=allowed:
                raise Rejected("Destination or source scope denied")
            if op=="write":self.writes[a["resource"]]=deepcopy(value)
            else:self.sends[a["resource"]]=deepcopy(value.data)
            self.events.append({"action":deepcopy(a),"sources":sorted(value.sources),"committed":True,
                                "data":deepcopy(value.data)})
            return
        return self._store(a,value)
    def _store(self,a,value):
        if len(canonical(value.data).encode())>65536:raise Rejected("Value size limit")
        self.handles[a["out"]]=value
        self.events.append({"action":deepcopy(a),"sources":sorted(value.sources),"committed":True})

