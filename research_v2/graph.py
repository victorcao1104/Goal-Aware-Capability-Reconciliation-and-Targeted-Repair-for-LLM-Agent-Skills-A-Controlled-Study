"""Dependency index extracted from the untrusted, already-visible DSL program."""
def dependency_index(program,shuffle=False):
    producers={a["out"]:i for i,a in enumerate(program) if a.get("out")}
    edges=[]
    for i,a in enumerate(program):
        for handle in a["inputs"]:
            if handle in producers:
                j=producers[handle]
                if j>=i:raise ValueError("Forward reference or cycle")
                edges.append([j,i])
        if a.get("op")=="read_output":
            candidates=[j for j,b in enumerate(program[:i]) if b.get("op")=="write" and b.get("resource")==a["resource"]]
            if candidates:edges.append([candidates[-1],i])
    if shuffle and len(program)>1:
        # Deterministic negative control. Preserve edge count, not semantic correctness.
        edges=[[(s+1)%len(program),(t+1)%len(program)] for s,t in edges]
    targets=[i for i,a in enumerate(program) if a.get("op") in ("send","write")]
    distance={i:0 for i in targets};queue=list(targets)
    while queue:
        target=queue.pop(0)
        for source,dest in edges:
            if dest==target and source not in distance:
                distance[source]=distance[target]+1;queue.append(source)
    return {"edges":edges,"effect_nodes":targets,"backward_distance":distance}

