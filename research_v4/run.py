"""Preparation and explicit live execution with immutable inputs and shared ledger."""
import argparse
from concurrent.futures import ThreadPoolExecutor,as_completed
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import random
import subprocess
import threading
from research_v3.run import dump,sha,freeze as verify_v3
from .fixtures import make_cases,encode
from .core import validate_contract,ground_scan,validate_audit,execute,reference_verdict
from .model import PROMPTS,SCHEMAS,LIMITS,contract_payload,scan_payload,audit_payload
from .analysis import grant_errors,summarize

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'research_v4/results';REPEATS=2
PRIOR=1.257365875
_locks={};_mutex=threading.Lock()

def request_key(role,payload,repeat):
    return hashlib.sha256(encode({'role':role,'payload':payload,'repeat':repeat,'prompt':PROMPTS[role],'schema':SCHEMAS[role],'limit':LIMITS[role]}).encode()).hexdigest()

def request_spec(role,payload):
    from src.api import MODEL
    return {'model':MODEL,'store':False,'reasoning':{'effort':'low'},'max_output_tokens':LIMITS[role],
            'input':[{'role':'system','content':PROMPTS[role]},{'role':'user','content':json.dumps(payload,ensure_ascii=False)}],
            'text':{'format':{'type':'json_schema','name':'v4_'+role,'strict':True,'schema':SCHEMAS[role]}}}

def fingerprint(role,payload,repeat):
    return hashlib.sha256(json.dumps(request_spec(role,payload),ensure_ascii=False).encode('utf-8')+
                          ('v4:'+request_key(role,payload,repeat)).encode()).hexdigest()

def validate_request(p,role,payload,repeat,client=None):
    import jsonschema
    key=request_key(role,payload,repeat);fp=fingerprint(role,payload,repeat)
    if any(p.get(k)!=v for k,v in {'key':key,'role':role,'repeat':repeat,'payload':payload,'fingerprint':fp}.items()):
        raise RuntimeError('Request identity mismatch')
    statuses={'ok':'ok','ModelRefusal':'model_refusal','ModelIncomplete':'model_incomplete'}
    if p.get('status')=='RuntimeError':
        valid=p.get('provider_status') in ('http_error','transport_error','invalid_response')
    else:valid=p.get('provider_status')==statuses.get(p.get('status'),'INVALID')
    if not valid:raise RuntimeError('Invalid recorded request status')
    if p['status']=='ok':jsonschema.validate(p['value'],SCHEMAS[role])
    elif p.get('value')!={}:raise RuntimeError('Failed request has a model value')
    attempts=p.get('attempts')
    if not isinstance(attempts,list) or len({a['id'] for a in attempts})!=len(attempts):raise RuntimeError('Invalid attempt inventory')
    for a in attempts:
        if a['id'] not in {fp+':'+str(i) for i in range(3)} or a['status'] not in ('pending','settled'):
            raise RuntimeError('Invalid dispatch attempt')
    if client is not None:
        path=client.calls/(fp+'.json')
        if not path.exists():raise RuntimeError('Retained private API record required for resume')
        private=json.loads(path.read_text(encoding='utf-8'))
        if private.get('fingerprint')!=fp or private.get('call_id')!='v4:'+key or private.get('request')!=request_spec(role,payload):
            raise RuntimeError('Private request identity mismatch')
        if private.get('status')!=p['provider_status'] or (p['status']=='ok' and private.get('value')!=p['value']):
            raise RuntimeError('Public/private response mismatch')
        response=private.get('response',{})
        if p.get('usage')!=response.get('usage',{}) or p.get('model')!=response.get('model'):
            raise RuntimeError('Public/private accounting mismatch')
        with client.budget.transaction():
            expected=[{'id':k,**v} for k,v in client.budget.records.items() if k.startswith(fp+':')]
        if not expected or attempts!=expected:raise RuntimeError('Public/cumulative ledger mismatch')
    return p

def request(client,role,payload,repeat):
    key=request_key(role,payload,repeat)
    with _mutex:lock=_locks.setdefault(key,threading.Lock())
    with lock:
        path=OUT/'requests'/(key+'.json')
        if path.exists():
            p=json.loads(path.read_text(encoding='utf-8'))
            return validate_request(p,role,payload,repeat,client)
        from src.api import BudgetExceeded
        cached=None;p={'role':role,'repeat':repeat,'payload':payload,'key':key}
        try:
            cached=client.generate('v4_'+role,PROMPTS[role],payload,SCHEMAS[role],'v4:'+key,max_output=LIMITS[role])
            p.update(status='ok',value=cached['value'])
        except BudgetExceeded:raise
        except Exception as exc:
            p.update(status=type(exc).__name__,value={})
            for f in client.calls.glob('*.json'):
                record=json.loads(f.read_text(encoding='utf-8'))
                if record.get('call_id')=='v4:'+key:cached=record;break
        if cached is None:raise RuntimeError('Missing auditable API record')
        with client.budget.transaction():attempts=[{'id':k,**v} for k,v in client.budget.records.items() if k.startswith(cached['fingerprint']+':')]
        p.update(fingerprint=cached['fingerprint'],attempts=attempts,usage=cached.get('response',{}).get('usage',{}),
                 model=cached.get('response',{}).get('model'),provider_status=cached['status'])
        validate_request(p,role,payload,repeat,client)
        dump(path,p);return p

def evaluate_case(case,repeat,get):
    s=get('scan',scan_payload(case),repeat);scan=ground_scan(s['value'],case['bundle'])
    if s['status']!='ok':scan['unknowns'].append('Scanner model request failed')
    rows=[]
    for mode in ('Mixed','Isolated'):
        p=get('contract',contract_payload(case,mode),repeat)
        contract=validate_contract(p['value'],case['task'],case['inventory'])
        errors=grant_errors(contract['rules'],case['oracle']['rules'])
        raw=grant_errors(p['value'].get('rules',[]),case['oracle']['rules'])
        base={'case_id':case['id'],'family':case['family'],'variant':case['variant'],'repeat':repeat,
              'contract':contract,'raw_grants':raw,'validated_grants':errors,
              'raw_excess':bool(raw['excess']) if p['status']=='ok' else None,
              'validated_excess':bool(errors['excess']) if p['status']=='ok' else None,
              'scan':scan,'scan_coverage':len(scan['actions'])/len(case['actions']),
              'reference_verdict':reference_verdict(case)}
        for form in ('Flat','Graph'):
            q=get('audit',audit_payload(case,contract,scan,form),repeat);audit=validate_audit(q['value'],case['task'],scan)
            ok=all(x['status']=='ok' for x in (p,s,q))
            rows.append({**base,'method':mode+'-'+form,'decision':audit['decision'],'audit':audit,'pipeline_ok':ok,
              'audit_correct':audit['decision']==base['reference_verdict'] and ok and not audit['errors'],
              'components':[p['key'],s['key'],q['key']], 'execution':execute(case,contract['rules'],audit['decision'])})
        if mode=='Isolated':
            rows.append({**base,'method':'TaskRuntime','decision':'allow','audit_correct':None,'pipeline_ok':p['status']=='ok',
              'components':[p['key']],'execution':execute(case,contract['rules'],'allow')})
    return rows

def jobs():return [(c,r) for c in make_cases() for r in range(REPEATS)]

def ensure_ledger(path):
    if not path.exists():raise RuntimeError('Original cumulative ledger is required')
    records=json.loads(path.read_text(encoding='utf-8'))
    if any(r['status']!='settled' for r in records.values()):raise RuntimeError('Unresolved prior reservations require inspection')
    total=sum(r.get('settled',r['reserved']) for r in records.values())
    if total+1e-10<PRIOR or total>20:raise RuntimeError('Prior cumulative budget is missing or exhausted')
    return total

def freeze(create=False):
    verify_v3()
    paths=sorted((ROOT/'research_v4').glob('*.py'))+sorted((ROOT/'tests_v4').glob('*.py'))
    paths += [ROOT/'src/api.py',ROOT/'docs/protocol/authority-audit-v4.md',ROOT/'research_v3/results/freeze.json']
    manifest={'files':{p.relative_to(ROOT).as_posix():sha(p) for p in paths},'cases_sha256':hashlib.sha256(encode(make_cases()).encode()).hexdigest(),
              'repeats':REPEATS,'model':'gpt-6-luna','prior_usd':PRIOR,'limits':LIMITS}
    path=OUT/'freeze.json'
    if path.exists():
        if json.loads(path.read_text(encoding='utf-8'))!=manifest:raise RuntimeError('Frozen v4 inputs changed')
    elif create:
        if (OUT/'requests').exists():raise RuntimeError('Cannot freeze over measured requests')
        dump(path,manifest);dump(OUT/'cases.json',make_cases());dump(OUT/'model-spec.json',{'prompts':PROMPTS,'schemas':SCHEMAS,'limits':LIMITS})
    else:raise RuntimeError('Freeze before running')
    return manifest

def committed(manifest):
    names={'research_v4/results/freeze.json':sha(OUT/'freeze.json'),**manifest['files']}
    for name,digest in names.items():
        data=subprocess.check_output(['git','show','HEAD:'+name],cwd=ROOT,stderr=subprocess.DEVNULL)
        if hashlib.sha256(data).hexdigest()!=digest:raise RuntimeError('Commit all frozen inputs before paid execution')
    return subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()

def collect():
    used={};rows=[]
    def get(role,payload,repeat):
        key=request_key(role,payload,repeat);p=json.loads((OUT/'requests'/(key+'.json')).read_text(encoding='utf-8'))
        validate_request(p,role,payload,repeat)
        used[key]=p;return p
    for c,r in jobs():
        derived=evaluate_case(c,r,get);saved=json.loads((OUT/'trajectories'/f"{c['id']}-r{r}.json").read_text(encoding='utf-8'))
        if derived!=saved:raise RuntimeError('Trajectory differs')
        rows.extend(derived)
    if set(used)!={p.stem for p in (OUT/'requests').glob('*.json')}:raise RuntimeError('Request inventory differs')
    if {f"{c['id']}-r{r}" for c,r in jobs()}!={p.stem for p in (OUT/'trajectories').glob('*.json')}:raise RuntimeError('Trial inventory differs')
    return rows,[used[k] for k in sorted(used)]

def parse_args(argv=None):
    p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group();g.add_argument('--freeze',action='store_true');g.add_argument('--live',action='store_true');return p.parse_args(argv)

def main():
    args=parse_args();manifest=freeze(args.freeze)
    if args.freeze:print('Prepared frozen v4 inputs; zero model calls.');return
    if args.live:
        revision=committed(manifest);before=ensure_ledger(ROOT/'results/raw_runs/budget-ledger.json')
        from src.api import Client
        client=Client(ROOT);client.calls=ROOT/'results/raw_runs/v4_calls';client.calls.mkdir(parents=True,exist_ok=True)
        todo=jobs();random.Random(7644).shuffle(todo)
        def run(job):
            c,r=job;rows=evaluate_case(c,r,lambda role,payload,repeat:request(client,role,payload,repeat))
            dump(OUT/'trajectories'/f"{c['id']}-r{r}.json",rows)
        with ThreadPoolExecutor(max_workers=4) as pool:
            futures=[pool.submit(run,j) for j in todo]
            for i,f in enumerate(as_completed(futures),1):
                f.result()
                if i%8==0:print(f'{i}/{len(todo)} paired case repeats complete',flush=True)
        dump(OUT/'accounting.json',{'before_usd':before,'after_usd':client.budget.total(),'prior_usd':PRIOR,'source_commit':revision,'utc':datetime.now(timezone.utc).isoformat()})
    rows,requests=collect();dump(OUT/'summary.json',summarize(rows,requests))
    dump(OUT/'evidence-manifest.json',{'files':{p.relative_to(OUT).as_posix():sha(p) for p in sorted(OUT.rglob('*.json')) if p.name!='evidence-manifest.json'}})
    print(f'Sealed {len(rows)} method trajectories and {len(requests)} unique role requests.')

if __name__=='__main__':main()
