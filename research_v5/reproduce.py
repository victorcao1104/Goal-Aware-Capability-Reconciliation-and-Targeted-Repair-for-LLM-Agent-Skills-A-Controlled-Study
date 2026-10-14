"""Offline verification of all v5 evidence without credentials or model calls."""
import argparse
import json
from research_v2.reproduce import verify_artifacts
from .run import OUT,freeze,collect
from .fixtures import make_cases
from .model import PROMPTS,SCHEMAS,LIMITS
from .analysis import summarize
from .core import reference,simulate,mechanism_controls

def prepared():
    freeze()
    if json.loads((OUT/'mechanism-controls.json').read_text(encoding='utf-8'))!=mechanism_controls():raise RuntimeError('Mechanism control mismatch')
    if json.loads((OUT/'cases.json').read_text(encoding='utf-8'))!=make_cases():raise RuntimeError('Fixture mismatch')
    if json.loads((OUT/'model-spec.json').read_text(encoding='utf-8'))!={'prompts':PROMPTS,'schemas':SCHEMAS,'limits':LIMITS}:raise RuntimeError('Model interface mismatch')
    for c in make_cases():
        expected={'attack':'block','neutral':'block','clean':'allow','authorized':'allow','undecided':'uncertain'}[c['variant']]
        if reference(c)!=expected:raise RuntimeError('Reference fixture mismatch')
        result=simulate(c,c['oracle']['policy'],'allow')
        if result['unauthorized'] or result['unresolved'] or not result['required_complete']:raise RuntimeError('Reference execution mismatch')
    return len(make_cases())

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--prepared',action='store_true');args=parser.parse_args()
    cases=prepared()
    if args.prepared:print(json.dumps({'cases':cases,'model_calls':0,'note':'Deterministic fixture checks, not model outcomes'}));return
    count=verify_artifacts(OUT);rows,updates,requests=collect()
    summary=summarize(rows,updates,requests)
    if summary!=json.loads((OUT/'summary.json').read_text(encoding='utf-8')):raise RuntimeError('Summary mismatch')
    accounting=json.loads((OUT/'accounting.json').read_text(encoding='utf-8'))
    start=json.loads((OUT/'start.json').read_text(encoding='utf-8'))
    if abs(accounting['after_usd']-start['cumulative_start_usd']-summary['accounted_usd'])>1e-8:raise RuntimeError('Accounting mismatch')
    print(json.dumps({'evidence_files':count,'cases':cases,'rows':len(rows),'updates':len(updates),'requests':len(requests),'model_calls':0}))
if __name__=='__main__':main()
