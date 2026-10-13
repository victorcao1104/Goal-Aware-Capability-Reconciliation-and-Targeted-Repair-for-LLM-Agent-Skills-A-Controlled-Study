"""Public necessary conditions only; intentionally not the exact-output oracle."""
import re

def public_loss(runtime,goals):
    loss=0
    for goal in goals:
        values=runtime.sends if goal["effect"]=="send" else {k:v.data for k,v in runtime.writes.items()}
        if goal["resource"] not in values:
            loss+=1;continue
        value=values[goal["resource"]]
        types={"str":str,"list":list,"dict":dict,"int":int}
        ok=type(value) is types[goal["type"]]
        if ok and goal.get("sha256"):ok=bool(re.fullmatch("[0-9a-f]{64}",value))
        if ok and "length" in goal:ok=len(value)==goal["length"]
        if ok and "keys" in goal:ok=set(value)==set(goal["keys"])
        loss+=int(not ok)
    return loss

