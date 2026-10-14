"""Frozen finite experiment; all outcomes can be rebuilt from public responses."""
import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor,as_completed
from datetime import datetime,timezone
import hashlib
import json
import random
from pathlib import Path
import subprocess
from research_v3.run import dump,sha
from research_v6b.run import freeze as verify_prior
from .fixtures import cases
from .engine import analyze,concrete,slice_ids,trusted_contract,minimum_repair,assess
from .model import SETTINGS,ARMS,payload,schema,spec,request_cost_bound,encode
from .api import ROOT,OUT,PRIOR,INCREMENTAL_CAP,Client,offline_get

def jobs():
    return [(c,r,s) for c in cases() for r in (0,1) for s in SETTINGS]
def job_name(c,r,s):return c['id']+'-r'+str(r)+'-'+s
def policy_errors(c,p):
    truth=trusted_contract(c);missing=[];excess=[]
    for s in c['sinks']:
        for k,v in truth[s].items():
            observed=p.get(s,{}).get(k)
            if v and observed is not True:missing.append(s+':'+k)
            if not v and observed is True:excess.append(s+':'+k)
    return dict(exact=p==truth,missing=missing,excess=excess)
def evaluate_proposal(c,value,p,ok):
    decision=value.get('decision','deny');edits=value.get('edits',[])
    z=assess(c,edits,p)
    shape=ok and decision in ('allow','repair','deny') and (decision!='allow' or not edits) and (decision!='repair' or bool(edits))
    if not shape or decision=='deny':
        z.update(activated=False,unsafe_execution=False,joint=False)
    z['proposal_shape_valid']=shape
    actual={s:sorted(f for f,v in fields.items() if 'ROWMARK_' in str(v)) for s,fields in concrete(c).items()}
    prediction=value.get('rows_at_sinks',{})
    normalized={s:sorted(v) for s,v in prediction.items()}
    z['raw_class_correct']=ok and normalized==actual
    z['initial_decision_correct']=ok and decision==('repair' if c['variant']=='unsafe' else 'allow')
    z['edit_count']=len(edits) if isinstance(edits,list) else None
    z['optimal_joint']=z['joint'] and z['edit_count']==(2 if c['variant']=='unsafe' else 0)
    return z
def evaluate_case(c,repeat,setting,get):
    q=get('evaluation',setting,'policy',payload('policy',c),schema('policy',c),repeat)
    p=q['value'].get('policy',{})
    base=dict(case_id=c['id'],context=c['context'],variant=c['variant'],repeat=repeat,setting=setting,
              policy=p,policy_status=q['status'],policy_errors=policy_errors(c,p))
    rows=[]
    arm_order=list(ARMS)
    seed=hashlib.sha256(encode([c['id'],repeat,setting,7647]).encode()).hexdigest()
    random.Random(seed).shuffle(arm_order)
    for arm in arm_order:
        a=get('evaluation',setting,'audit',payload('audit',c,arm,p),schema('audit',c),repeat)
        score=evaluate_proposal(c,a['value'],p,q['status']==a['status']=='ok')
        rows.append(dict(**base,method=arm,components=[q['key'],a['key']],audit_status=a['status'],
                         proposal=a['value'],score=score))
    for mode in ('flat','graph'):
        if q['status']=='ok':repair=minimum_repair(c,p,mode)
        else:repair=dict(count=None,edits=[],checks=0,work={})
        z=assess(c,repair['edits'],p)
        if repair['count'] is None:z.update(activated=False,unsafe_execution=False,joint=False)
        z.update(edit_count=repair['count'],optimal_joint=z['joint'] and repair['count']==(2 if c['variant']=='unsafe' else 0))
        rows.append(dict(**base,method='Deterministic'+mode.title(),components=[q['key']],repair=repair,score=z))
    return rows

def preparation():
    certs=[];max_cost={s:0 for s in SETTINGS}
    for c in cases():
        p=trusted_contract(c);f=minimum_repair(c,p,'flat');g=minimum_repair(c,p,'graph')
        assert (f['count'],f['edits'])==(g['count'],g['edits'])
        assert f['count']==(2 if c['variant']=='unsafe' else 0)
        assert assess(c,f['edits'],p)['joint']
        sf,wf=slice_ids(c,'flat');sg,wg=slice_ids(c,'graph');assert sf==sg
        certs.append(dict(case_id=c['id'],nodes=len(c['actions']),slice_nodes=len(sf),minimum=f,
                          flat_slice_work=wf,graph_slice_work=wg))
        # False is the longest boolean spelling; covers every possible policy value.
        maxp={s:dict(allow_aggregate=False,allow_rows=False) for s in c['sinks']}
        for setting in SETTINGS:
            for role,arm in [('policy',None)]+[('audit',a) for a in ARMS]:
                req=spec(setting,role,payload(role,c,arm,maxp),schema(role,c))
                max_cost[setting]=max(max_cost[setting],request_cost_bound(req,setting))
    worst=sum(v['call_ceiling']*144 for v in SETTINGS.values())
    assert worst<=INCREMENTAL_CAP
    return dict(certificates=certs,settings=SETTINGS,cases=cases(),max_request_bound_usd=max_cost,
                maximum_physical_calls=432,worst_case_usd=worst,repeats=2,model_jobs=72,audit_calls=360)
def freeze(create=False):
    verify_prior()
    paths=sorted((ROOT/'research_v7').glob('*.py'))+sorted((ROOT/'tests_v7').glob('*.py'))+[
        ROOT/'docs/protocol/verified-flow-repair-v7.md',ROOT/'research_v6b/results/freeze.json',
        ROOT/'research_v6b/results/evidence-manifest.json',ROOT/'research_v6b/response.py',
        ROOT/'src/api.py',ROOT/'research_v3/run.py',ROOT/'requirements.lock']
    value=dict(files={p.relative_to(ROOT).as_posix():sha(p) for p in paths},
               preparation_sha256=hashlib.sha256(encode(preparation()).encode()).hexdigest(),
               prior_usd=PRIOR,incremental_cap=INCREMENTAL_CAP)
    path=OUT/'freeze.json'
    if path.exists():
        if json.loads(path.read_text(encoding='utf-8'))!=value:raise RuntimeError('Frozen v7 source changed')
    elif create:
        if (OUT/'requests').exists():raise RuntimeError('Cannot freeze after calls')
        dump(path,value);dump(OUT/'preparation.json',preparation())
    else:raise RuntimeError('Freeze first')
    return value
def committed(f):
    for name,digest in {**f['files'],'research_v7/results/freeze.json':sha(OUT/'freeze.json')}.items():
        if hashlib.sha256(subprocess.check_output(['git','show','HEAD:'+name],cwd=ROOT)).hexdigest()!=digest:
            raise RuntimeError('Uncommitted frozen source '+name)
    return subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
def summarize(rows,records):
    groups=[]
    metrics=('joint','optimal_joint','activated','unsafe_execution','raw_class_correct','initial_decision_correct','goal','proposal_safe')
    for setting in SETTINGS:
        for method in (*ARMS,'DeterministicFlat','DeterministicGraph'):
            for variant in ('all','unsafe','safe','authorized'):
                rs=[r for r in rows if r['setting']==setting and r['method']==method and (variant=='all' or r['variant']==variant)]
                groups.append(dict(setting=setting,method=method,variant=variant,n=len(rs),
                    **{k:sum(bool(r['score'].get(k,False)) for r in rs) for k in metrics}))
    pairs=[]
    for setting in SETTINGS:
        for left,right in [('FullFlatRaw','FullFlatClean'),('FullFlatClean','FullGraphClean'),
                           ('FullFlatClean','SliceFlatClean'),('SliceFlatClean','SliceGraphClean')]:
            l={(r['case_id'],r['repeat']):r for r in rows if r['setting']==setting and r['method']==left}
            rr={(r['case_id'],r['repeat']):r for r in rows if r['setting']==setting and r['method']==right}
            for metric in ('joint','raw_class_correct','optimal_joint'):
                better=sum(rr[k]['score'][metric] and not v['score'][metric] for k,v in l.items())
                worse=sum(v['score'][metric] and not rr[k]['score'][metric] for k,v in l.items())
                pairs.append(dict(setting=setting,left=left,right=right,metric=metric,n=len(l),right_only=better,left_only=worse))
    unique_policy={(r['setting'],r['case_id'],r['repeat']):r for r in rows}
    authority={s:dict(n=24,exact=sum(r['policy_errors']['exact'] for k,r in unique_policy.items() if k[0]==s),
                       excess_jobs=sum(bool(r['policy_errors']['excess']) for k,r in unique_policy.items() if k[0]==s),
                       missing_jobs=sum(bool(r['policy_errors']['missing']) for k,r in unique_policy.items() if k[0]==s))
               for s in SETTINGS}
    cost=sum(q['accounted_usd'] for q in records.values())
    uses=Counter(k for r in rows for k in r['components'])
    per_arm=[]
    for setting in SETTINGS:
        for method in (*ARMS,'DeterministicFlat','DeterministicGraph'):
            rs=[r for r in rows if r['setting']==setting and r['method']==method]
            keys=[k for r in rs for k in r['components']]
            audit_keys={k for k in keys if records[k]['role']=='audit'}
            per_arm.append(dict(setting=setting,method=method,rows=len(rs),
                logical_component_calls=len(keys),unique_component_requests=len(set(keys)),
                unique_audit_requests=len(audit_keys),
                logical_unshared_usd=sum(records[k]['accounted_usd'] for k in keys),
                allocated_physical_usd=sum(records[k]['accounted_usd']/uses[k] for k in keys),
                audit_input_tokens=sum(records[k]['usage'].get('input_tokens',0) for k in audit_keys),
                audit_output_tokens=sum(records[k]['usage'].get('output_tokens',0) for k in audit_keys),
                edit_histogram=dict(Counter(str(r['score']['edit_count']) for r in rs))))
    return dict(groups=groups,paired=pairs,authority=authority,rows=len(rows),physical_requests=len(records),
                statuses=dict(Counter(q['status'] for q in records.values())),
                incremental_usd=cost,cumulative_usd=PRIOR+cost,
                costs_by_setting={s:sum(q['accounted_usd'] for q in records.values() if q['setting']==s) for s in SETTINGS},
                logical_component_uses=sum(len(r['components']) for r in rows),per_arm=per_arm,
                cost_allocation='Each physical request cost divided equally across all recorded component uses, including deterministic baselines. Per-arm unique request sets overlap.')
def collect():
    rows=[];records={}
    def get(*args):
        q=offline_get(*args);records[q['key']]=q;return q
    for c,r,s in jobs():
        value=evaluate_case(c,r,s,get)
        if value!=json.loads((OUT/'jobs'/(job_name(c,r,s)+'.json')).read_text(encoding='utf-8')):raise RuntimeError('Outcome replay mismatch')
        rows.extend(value)
    files={p.stem for p in (OUT/'requests').glob('*.json')}
    if files!=set(records):raise RuntimeError('Missing or unused request evidence')
    if {p.stem for p in (OUT/'jobs').glob('*.json')}!={job_name(c,r,s) for c,r,s in jobs()}:
        raise RuntimeError('Unexpected or missing job evidence')
    return summarize(rows,records),rows,records
def evidence():
    return {p.relative_to(ROOT).as_posix():sha(p) for p in sorted(OUT.rglob('*.json')) if p.name!='evidence-manifest.json'}
def complete(client):
    summary,rows,records=collect()
    with client.budget.transaction():
        actual={k:v for k,v in client.budget.records.items() if k.startswith('v7:')}
    if set(actual)!={'v7:'+k for k in records}:raise RuntimeError('Ledger request set mismatch')
    for k,q in records.items():
        if actual['v7:'+k]['status']!='settled' or actual['v7:'+k]['settled']!=q['accounted_usd']:raise RuntimeError('Ledger differs')
    if abs(client.budget.total()-summary['cumulative_usd'])>1e-9:raise RuntimeError('Cumulative ledger differs')
    dump(OUT/'rows.json',rows);dump(OUT/'summary.json',summary)
    dump(OUT/'evidence-manifest.json',evidence())
    return summary
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--prepare',action='store_true');ap.add_argument('--live',action='store_true')
    args=ap.parse_args()
    if args.prepare:
        freeze(True);print('Prepared and frozen; no API calls.');return
    if not args.live:raise SystemExit('Choose --prepare or --live')
    f=freeze();commit=committed(f);client=Client()
    execution=OUT/'execution.json'
    if not execution.exists():dump(execution,dict(source_commit=commit,utc=datetime.now(timezone.utc).isoformat()))
    elif json.loads(execution.read_text(encoding='utf-8'))['source_commit']!=commit:
        raise RuntimeError('Resume source commit changed')
    done=0
    with ThreadPoolExecutor(max_workers=4) as pool:
        todo=jobs();random.Random(7647).shuffle(todo)
        futures={pool.submit(evaluate_case,c,r,s,client.get):(c,r,s) for c,r,s in todo}
        for fut in as_completed(futures):
            c,r,s=futures[fut];dump(OUT/'jobs'/(job_name(c,r,s)+'.json'),fut.result());done+=1
            print(f'Finished {done}/72 {job_name(c,r,s)}',flush=True)
    summary=complete(client)
    print(json.dumps({k:summary[k] for k in ('rows','physical_requests','statuses','incremental_usd','cumulative_usd')}))
if __name__=='__main__':main()
