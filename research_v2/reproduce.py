"""Verify and replay all archived v2 trials offline, without loading API credentials."""
import json
from pathlib import PurePosixPath
from .run import OUT,freeze,replay_trial,summarize,fingerprint,METHODS,LIVE
from .fixtures import make_cases
from .model import INSTRUCTION,SCHEMA
from .analysis import analyze

def verify_artifacts(directory):
    manifest=json.loads((directory/"evidence-manifest.json").read_text(encoding="utf-8"))
    for name,expected in manifest["files"].items():
        relative=PurePosixPath(name)
        if relative.is_absolute() or ".." in relative.parts or "\\" in name or ":" in name:
            raise ValueError("Unsafe evidence path")
        path=directory/name
        if not path.resolve().is_relative_to(directory.resolve()) or not path.is_file() or fingerprint(path)!=expected:
            raise ValueError("Evidence hash mismatch: "+name)
    actual={p.relative_to(directory).as_posix() for p in directory.rglob("*.json") if p.name!="evidence-manifest.json"}
    if actual!=set(manifest["files"]):raise ValueError("Evidence file inventory differs")
    return len(actual)

def main():
    freeze()
    count=verify_artifacts(OUT)
    if json.loads((OUT/"cases.json").read_text(encoding="utf-8"))!=make_cases():
        raise AssertionError("Archived fixtures differ")
    if json.loads((OUT/"model-spec.json").read_text(encoding="utf-8"))!={"instruction":INSTRUCTION,"schema":SCHEMA}:
        raise AssertionError("Archived model specification differs")
    recorded=json.loads((OUT/"trials.json").read_text(encoding="utf-8"))
    methods=(*METHODS,*LIVE,"GraphNoSim") if (OUT/"proposals").exists() else METHODS
    expected={(c["id"],m) for c in make_cases() for m in methods}
    keys=[(t["case_id"],t["method"]) for t in recorded]
    if len(keys)!=len(expected) or set(keys)!=expected:raise AssertionError("Incomplete/duplicate trial matrix")
    for t in recorded:
        if t["blocked"] and t["method"] in (*LIVE,"GraphNoSim"):
            method="GraphPlanner" if t["method"]=="GraphNoSim" else t["method"]
            proposal=json.loads((OUT/"proposals"/(t["case_id"]+"-"+method+".json")).read_text(encoding="utf-8"))
            if proposal["plans"]!=t["plans"] or proposal["status"]!=t["model_status"]:
                raise AssertionError("Proposal/trial mismatch")
    replayed=[replay_trial(t) for t in recorded]
    if replayed!=recorded:raise AssertionError("Trial replay differs from archived evidence")
    summary=json.loads((OUT/"summary.json").read_text(encoding="utf-8"))
    if summarize(replayed)!=summary:raise AssertionError("Summary differs")
    proposals=[json.loads(p.read_text(encoding="utf-8")) for p in sorted((OUT/"proposals").glob("*.json"))]
    if analyze(replayed,proposals)!=json.loads((OUT/"analysis.json").read_text(encoding="utf-8")):
        raise AssertionError("Paired comparisons or usage totals differ")
    print(f"Verified frozen inputs, {count} evidence hashes and exactly replayed {len(recorded)} trials; no API calls.")

if __name__=="__main__":main()

