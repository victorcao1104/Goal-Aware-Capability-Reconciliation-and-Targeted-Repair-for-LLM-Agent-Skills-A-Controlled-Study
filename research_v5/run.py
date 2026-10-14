"""Prospectively frozen execution, durable accounting and credential-free replay."""
import argparse
from concurrent.futures import ThreadPoolExecutor,as_completed
from copy import deepcopy
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import random
import subprocess
import threading
from research_v3.run import dump,sha
from research_v4.run import freeze as verify_v4
from .fixtures import make_cases,encode
from .core import policy_valid,policy_errors,reference,simulate,scan_records,check_audit,apply_update,allowed,mechanism_controls
from .model import PROMPTS,SCHEMAS,LIMITS,payload_policy,payload_scan,payload_audit,payload_update
from .analysis import summarize
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'research_v5/results'
PRIOR=1.435230375;REPEATS=2
_locks={};_mutex=threading.Lock()

def request_key(role,payload,repeat):
    return hashlib.sha256(encode({'role':role,'payload':payload,'repeat':repeat,'prompt':PROMPTS[role],'schema':SCHEMAS[role],'limit':LIMITS[role]}).encode()).hexdigest()

def request_spec(role,payload):
    from src.api import MODEL
    return {'model':MODEL,'store':False,'reasoning':{'effort':'low'},'max_output_tokens':LIMITS[role],
            'input':[{'role':'system','content':PROMPTS[role]},{'role':'user','content':json.dumps(payload,ensure_ascii=False)}],
            'text':{'format':{'type':'json_schema','name':'v5_'+role,'strict':True,'schema':SCHEMAS[role]}}}

def fingerprint(role,payload,repeat):
    return hashlib.sha256(json.dumps(request_spec(role,payload),ensure_ascii=False).encode()+('v5:'+request_key(role,payload,repeat)).encode()).hexdigest()

def validate_record(p,role,payload,repeat,client=None):
    import jsonschema
    key=request_key(role,payload,repeat);fp=fingerprint(role,payload,repeat)
    if any(p.get(k)!=v for k,v in {'key':key,'role':role,'repeat':repeat,'payload':payload,'fingerprint':fp}.items()):
        raise RuntimeError('Request identity mismatch')
    statuses={'ok':'ok','ModelRefusal':'model_refusal','ModelIncomplete':'model_incomplete'}
    valid=(p.get('provider_status') in ('http_error','transport_error','invalid_response') if p.get('status')=='RuntimeError'
           else p.get('provider_status')==statuses.get(p.get('status'),'INVALID'))
    if not valid:raise RuntimeError('Invalid request status')
    if p['status']=='ok':jsonschema.validate(p['value'],SCHEMAS[role])
    elif p.get('value')!={}:raise RuntimeError('Failed request contains a value')
    attempts=p.get('attempts')
    if not isinstance(attempts,list) or not attempts or len({a['id'] for a in attempts})!=len(attempts):raise RuntimeError('Invalid attempt inventory')
    for a in attempts:
        if a['id'] not in {fp+':'+str(i) for i in range(3)} or a['status'] not in ('pending','settled'):raise RuntimeError('Invalid attempt')
    if client is not None:
        private=json.loads((client.calls/(fp+'.json')).read_text(encoding='utf-8'))
        if private.get('call_id')!='v5:'+key or private.get('fingerprint')!=fp or private.get('request')!=request_spec(role,payload):
            raise RuntimeError('Private request identity mismatch')
        if private.get('status')!=p['provider_status'] or (p['status']=='ok' and private.get('value')!=p['value']):
            raise RuntimeError('Private response mismatch')
        response=private.get('response',{})
        if p.get('usage')!=response.get('usage',{}) or p.get('model')!=response.get('model'):raise RuntimeError('Private usage mismatch')
        with client.budget.transaction():expected=[{'id':k,**v} for k,v in client.budget.records.items() if k.startswith(fp+':')]
        if expected!=attempts:raise RuntimeError('Cumulative ledger mismatch')
    return p

def record_infrastructure_failure(key,fp,exc):
    dump(ROOT/'results/raw_runs/v5_infrastructure'/(key+'.json'),
         {'key':key,'fingerprint':fp,'exception_class':type(exc).__name__,'utc':datetime.now(timezone.utc).isoformat()})

def request(client,role,payload,repeat):
    key=request_key(role,payload,repeat);fp=fingerprint(role,payload,repeat)
    with _mutex:lock=_locks.setdefault(key,threading.Lock())
    with lock:
        path=OUT/'requests'/(key+'.json')
        if path.exists():return validate_record(json.loads(path.read_text(encoding='utf-8')),role,payload,repeat,client)
        from src.api import BudgetExceeded
        private_path=client.calls/(fp+'.json')
        with client.budget.transaction():
            if any(k.startswith(fp+':') and v['status']=='pending' for k,v in client.budget.records.items()):
                raise RuntimeError('Unresolved reservation: inspect before any redispatch')
        record={'role':role,'repeat':repeat,'payload':payload,'key':key}
        try:
            private=client.generate('v5_'+role,PROMPTS[role],payload,SCHEMAS[role],'v5:'+key,max_output=LIMITS[role])
            record.update(status='ok',value=private['value'])
        except BudgetExceeded:raise
        except Exception as exc:
            if not private_path.exists():
                # No exception message or secret goes into public records; chained traceback retained locally.
                record_infrastructure_failure(key,fp,exc)
                raise RuntimeError('Unauditable API failure; original exception class: '+type(exc).__name__) from exc
            private=json.loads(private_path.read_text(encoding='utf-8'))
            record.update(status=type(exc).__name__,value={})
        with client.budget.transaction():attempts=[{'id':k,**v} for k,v in client.budget.records.items() if k.startswith(fp+':')]
        record.update(fingerprint=fp,attempts=attempts,usage=private.get('response',{}).get('usage',{}),
                      model=private.get('response',{}).get('model'),provider_status=private['status'])
        validate_record(record,role,payload,repeat,client);dump(path,record);return record

def evaluate_case(case,repeat,get):
    scan_request=get('scan',payload_scan(case),repeat)
    scan=scan_records(case,scan_request['value'])
    if scan_request['status']!='ok':scan['unknowns'].append('Scanner request failed')
    rows=[]
    for mode in ('Mixed','Isolated'):
        p=get('policy',payload_policy(case,mode),repeat);policy=p['value'].get('policy',{})
        ok=p['status']=='ok' and policy_valid(policy,case)
        base={'case_id':case['id'],'structure':case['structure'],'narrative':case['narrative'],'variant':case['variant'],
              'repeat':repeat,'policy_errors':policy_errors(policy,case),'policy_decisions':{k:v['decision'] for k,v in policy.items()},
              'reference':reference(case)}
        rows.append({**base,'method':mode+'Runtime','pipeline_ok':ok,'components':[p['key']],
                     'execution':simulate(case,policy,'allow')})
        if mode=='Isolated':
            for form in ('Flat','Graph'):
                q=get('audit',payload_audit(case,policy,scan,form),repeat)
                audit=check_audit(q['value'],case,scan)
                pipeline=ok and scan_request['status']=='ok' and q['status']=='ok'
                rows.append({**base,'method':'Isolated'+form,'pipeline_ok':pipeline,'audit':audit,
                     'raw_decision':q['value'].get('decision'),'raw_audit_correct':q['status']=='ok' and q['value'].get('decision')==base['reference'],
                     'audit_correct':pipeline and not audit['errors'] and audit['decision']==base['reference'],
                     'scan':scan,'components':[p['key'],scan_request['key'],q['key']],
                     'execution':simulate(case,policy,audit['decision'] if pipeline else 'uncertain')})
    return rows

def update_cases():
    return [c for c in make_cases() if c['variant']=='attack' or (c['variant']=='neutral' and c['narrative']=='necessity')]

def evaluate_update(case,repeat,initial_kind,get):
    initial=deepcopy(case['oracle']['policy'])
    if initial_kind=='overbroad':
        for k in ('e7','e9'):initial[k]['decision']='allow'
    p=get('update',payload_update(case,initial),repeat);proposal=p['value'].get('policy',{})
    ok=p['status']=='ok' and policy_valid(proposal,case)
    effective=apply_update(initial,proposal) if ok else deepcopy(initial)
    return {'case_id':case['id'],'structure':case['structure'],'narrative':case['narrative'],'variant':case['variant'],
      'repeat':repeat,'initial_kind':initial_kind,'intervention':True,'pipeline_ok':ok,'components':[p['key']],
      'proposed_errors':policy_errors(proposal,case),'effective_errors':policy_errors(effective,case),
      'expansion_rejected':ok and not allowed(proposal).issubset(allowed(initial)),
      'execution':simulate(case,effective,'allow')}

def jobs():
    return [('case',c,r,None) for c in make_cases() for r in range(REPEATS)]+[
      ('update',c,r,k) for c in update_cases() for r in range(REPEATS) for k in ('correct','overbroad')]

def job_id(job):
    kind,c,r,k=job
    return f"{kind}-{c['id']}-r{r}"+('-'+k if k else '')

def evaluate(job,get):
    kind,c,r,k=job
    return evaluate_case(c,r,get) if kind=='case' else evaluate_update(c,r,k,get)

def freeze(create=False):
    verify_v4()
    paths=sorted((ROOT/'research_v5').glob('*.py'))+sorted((ROOT/'tests_v5').glob('*.py'))
    paths += [ROOT/'docs/protocol/policy-contamination-v5.md',ROOT/'src/api.py',ROOT/'research_v4/results/freeze.json',ROOT/'requirements.lock']
    manifest={'files':{p.relative_to(ROOT).as_posix():sha(p) for p in paths},'cases_sha256':hashlib.sha256(encode(make_cases()).encode()).hexdigest(),
              'repeats':REPEATS,'model':'gpt-6-luna','prior_usd':PRIOR,'limits':LIMITS}
    path=OUT/'freeze.json'
    if path.exists():
        if json.loads(path.read_text(encoding='utf-8'))!=manifest:raise RuntimeError('Frozen v5 input changed')
    elif create:
        if (OUT/'requests').exists():raise RuntimeError('Cannot freeze over measurements')
        dump(path,manifest);dump(OUT/'cases.json',make_cases());dump(OUT/'model-spec.json',{'prompts':PROMPTS,'schemas':SCHEMAS,'limits':LIMITS})
        dump(OUT/'mechanism-controls.json',mechanism_controls())
    else:raise RuntimeError('Freeze before measurement')
    return manifest

def committed(manifest):
    for name,digest in {'research_v5/results/freeze.json':sha(OUT/'freeze.json'),**manifest['files']}.items():
        if hashlib.sha256(subprocess.check_output(['git','show','HEAD:'+name],cwd=ROOT)).hexdigest()!=digest:
            raise RuntimeError('Frozen source must be committed before live calls')
    return subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()

def collect():
    used={};rows=[];updates=[]
    def get(role,payload,repeat):
        key=request_key(role,payload,repeat)
        p=json.loads((OUT/'requests'/(key+'.json')).read_text(encoding='utf-8'))
        validate_record(p,role,payload,repeat);used[key]=p;return p
    for job in jobs():
        derived=evaluate(job,get)
        if derived!=json.loads((OUT/'trajectories'/(job_id(job)+'.json')).read_text(encoding='utf-8')):raise RuntimeError('Trajectory differs')
        if job[0]=='case':rows.extend(derived)
        else:updates.append(derived)
    if set(used)!={p.stem for p in (OUT/'requests').glob('*.json')}:raise RuntimeError('Request inventory mismatch')
    if {job_id(j) for j in jobs()}!={p.stem for p in (OUT/'trajectories').glob('*.json')}:raise RuntimeError('Job inventory mismatch')
    return rows,updates,[used[k] for k in sorted(used)]

def ledger_total(path):
    if not path.exists():raise RuntimeError('Original cumulative ledger missing')
    records=json.loads(path.read_text(encoding='utf-8'))
    if any(v['status']!='settled' for v in records.values()):raise RuntimeError('Unresolved ledger reservation')
    total=sum(v.get('settled',v['reserved']) for v in records.values())
    if not PRIOR-1e-10<=total<20:raise RuntimeError('Prior budget missing or exhausted')
    return total

def main():
    p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group()
    g.add_argument('--freeze',action='store_true');g.add_argument('--live',action='store_true');args=p.parse_args()
    manifest=freeze(args.freeze)
    if args.freeze:print('V5 prepared; zero model calls');return
    if args.live:
        revision=committed(manifest);before=ledger_total(ROOT/'results/raw_runs/budget-ledger.json')
        from src.api import Client
        client=Client(ROOT);client.calls=ROOT/'results/raw_runs/v5_calls';client.calls.mkdir(parents=True,exist_ok=True)
        start_path=OUT/'start.json'
        if not start_path.exists():dump(start_path,{'cumulative_start_usd':before,'source_commit':revision,'utc':datetime.now(timezone.utc).isoformat()})
        elif json.loads(start_path.read_text(encoding='utf-8'))['source_commit']!=revision:raise RuntimeError('Resume source commit changed')
        todo=jobs();random.Random(7645).shuffle(todo)
        def run(job):
            result=evaluate(job,lambda role,payload,repeat:request(client,role,payload,repeat))
            dump(OUT/'trajectories'/(job_id(job)+'.json'),result)
        with ThreadPoolExecutor(max_workers=4) as pool:
            futures=[pool.submit(run,j) for j in todo]
            for i,f in enumerate(as_completed(futures),1):
                f.result()
                if i%8==0:print(f'{i}/{len(todo)} fixed jobs complete',flush=True)
        after=ledger_total(ROOT/'results/raw_runs/budget-ledger.json')
        dump(OUT/'accounting.json',{'resume_before_usd':before,'after_usd':after,'prior_usd':PRIOR,'source_commit':revision,
                                  'utc':datetime.now(timezone.utc).isoformat()})
    rows,updates,requests=collect();dump(OUT/'summary.json',summarize(rows,updates,requests))
    dump(OUT/'evidence-manifest.json',{'files':{p.relative_to(OUT).as_posix():sha(p) for p in sorted(OUT.rglob('*.json')) if p.name!='evidence-manifest.json'}})
    print(f'Sealed {len(rows)} method rows, {len(updates)} updates, {len(requests)} physical requests.')
if __name__=='__main__':main()
