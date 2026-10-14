"""Check preparation or replay measured outcomes. Neither mode invokes a model."""
import argparse
import json
from research_v2.reproduce import verify_artifacts
from .run import OUT,freeze,collect
from .fixtures import make_cases
from .model import PROMPTS,SCHEMAS,LIMITS
from .analysis import summarize
from .core import parse_bundle,reference_verdict,execute

def verify_preparation():
    freeze()
    if json.loads((OUT/'cases.json').read_text(encoding='utf-8'))!=make_cases():raise AssertionError('Fixture mismatch')
    if json.loads((OUT/'model-spec.json').read_text(encoding='utf-8'))!={'prompts':PROMPTS,'schemas':SCHEMAS,'limits':LIMITS}:raise AssertionError('Model interface mismatch')
    counts={}
    sample_root=OUT.parent/'samples'
    for c in make_cases():
        if parse_bundle(c['bundle'])!=c['actions']:raise AssertionError('Source/action mismatch')
        expected={'clean':'allow','attack':'block','authorized':'allow','underspecified':'uncertain'}[c['variant']]
        if reference_verdict(c)!=expected:raise AssertionError('Reference label mismatch')
        result=execute(c,c['oracle']['rules'],'allow')
        if result['unauthorized_effects'] or result['unresolved_effects'] or not result['required_effects_complete']:raise AssertionError('Reference runtime mismatch')
        counts[expected]=counts.get(expected,0)+1
        if c['instance']==0:
            expected_files={**{name:text.rstrip()+'\n' for name,text in c['bundle'].items()},
                            'trusted-task.txt':'\n'.join(x['id']+': '+x['text'] for x in c['task'])+'\n'}
            for name,text in expected_files.items():
                if (sample_root/c['id']/name).read_bytes()!=text.encode('utf-8'):raise AssertionError('Readable sample differs')
    return {'cases':len(make_cases()),'reference_verdicts':counts,'model_calls':0}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--prepared',action='store_true');args=parser.parse_args()
    prepared=verify_preparation()
    if args.prepared:
        print(json.dumps({'preparation_verified':prepared,'note':'Reference checks are not measured model outcomes.'}));return
    count=verify_artifacts(OUT);rows,requests=collect()
    if summarize(rows,requests)!=json.loads((OUT/'summary.json').read_text(encoding='utf-8')):raise AssertionError('Summary mismatch')
    print(json.dumps({'evidence_files':count,'trajectories':len(rows),'unique_role_requests':len(requests),'model_calls':0}))

if __name__=='__main__':main()
