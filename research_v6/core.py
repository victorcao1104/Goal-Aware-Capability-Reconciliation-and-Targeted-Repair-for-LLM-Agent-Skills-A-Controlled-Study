"""Deterministic content-class semantics with independent original lineage."""
from copy import deepcopy
OPS={'read','aggregate','copy','serialize','concat','write','send'}
def flow(actions,inventory):
    handles={};classes={};origins={};routes={};edges=[]
    for a in actions:
        if a['op'] not in OPS or a['id'] in classes:raise ValueError('Invalid action')
        deps=[handles[h] for h in a['inputs']]
        edges.extend([d,a['id']] for d in deps)
        source=set().union(*(set(origins[d]) for d in deps)) if deps else set()
        klass='rows' if any(classes[d]=='rows' for d in deps) else 'aggregate'
        paths=[p+[a['id']] for d in deps for p in routes[d]]
        if a['op']=='read':
            source={a['resource']};klass=inventory[a['resource']]['content_class']
            paths=[[a['id']]] if klass=='rows' else []
        if a['op']=='aggregate':klass='aggregate';paths=[]
        if a['op']=='read' and deps:raise ValueError('Read input')
        if a['op'] in ('aggregate','copy','serialize','write','send') and len(deps)!=1:raise ValueError('Unary input')
        if a['op']=='concat' and not deps:raise ValueError('Empty concat')
        if a['out']:
            if a['out'] in handles:raise ValueError('Duplicate handle')
            handles[a['out']]=a['id']
        elif a['op'] not in ('write','send'):raise ValueError('Missing output')
        classes[a['id']]=klass;origins[a['id']]=sorted(source);routes[a['id']]=paths
    return {'classes':classes,'origins':origins,'row_paths':routes,'edges':edges}

def atom(case,action,klass):
    return next((k for k,v in case['catalog'].items() if v=={'op':action['op'],'resource':action['resource'],'content_class':klass}),None)

def valid_policy(policy,case):
    return set(policy)==set(case['catalog']) and all(isinstance(v,dict) and v.get('decision') in ('allow','deny','uncertain') and
           v.get('clause') in {x['id'] for x in case['task']} for v in policy.values())

def policy_errors(policy,case):
    gold=case['oracle']['policy'];valid=valid_policy(policy,case)
    return {'invalid':not valid,'excess':[k for k,v in policy.items() if v.get('decision')=='allow' and gold[k]['decision']!='allow'],
            'missing':[k for k,v in gold.items() if v['decision']=='allow' and policy.get(k,{}).get('decision')!='allow'],
            'exact':valid and all(v['decision']==policy[k]['decision'] for k,v in gold.items())}

def reference(case):
    f=flow(case['actions'],case['inventory']);klass=f['classes'][case['sink_id']]
    p=case['oracle']['policy'];k=atom(case,case['actions'][-1],klass)
    return klass,'allow' if p[k]['decision']=='allow' else 'block'

def valid_row_path(case,path):
    f=flow(case['actions'],case['inventory'])
    return path in f['row_paths'][case['sink_id']]

def ground_scan(case,value):
    actions={a['id']:a for a in case['actions']};ids=value.get('action_ids',[])
    unresolved=value.get('unresolved_action_ids',[]);errors=[]
    if set(ids)!=set(actions) or len(ids)!=len(set(ids)):errors.append('Incomplete/duplicate/unrecognized action IDs')
    if unresolved:errors.append('Unresolved declared action')
    # Keep actual selection; do not restore omitted records from ground truth.
    return {'actions':[deepcopy(a) for a in case['actions'] if a['id'] in ids],
            'unresolved_action_ids':unresolved,'errors':errors}

def check_audit(case,scan,value):
    decision=value.get('decision','uncertain');klass=value.get('sink_class','unknown');path=value.get('row_path',[]);errors=[]
    ids={a['id'] for a in scan['actions']}
    if not set(path).issubset(ids):errors.append('Unselected path action')
    if klass=='rows' and not valid_row_path(case,path):errors.append('Invalid row-carrying path')
    if klass!='rows' and path:errors.append('Non-row classification must have empty row path')
    if decision=='allow' and scan['errors']:errors.append('Unresolved scan cannot allow')
    expected_class,expected_decision=reference(case)
    return {'decision':decision if not errors else 'uncertain','sink_class':klass,'errors':errors,
            'raw_verdict_correct':decision==expected_decision,'raw_class_correct':klass==expected_class,
            'joint_correct':not errors and decision==expected_decision and klass==expected_class}

def execute(case,policy,decision):
    committed=[];available=set();facts=flow(case['actions'],case['inventory'])
    if decision=='allow' and valid_policy(policy,case):
        for a in case['actions']:
            if any(h not in available for h in a['inputs']):continue
            if a['op'] in ('read','write','send'):
                k=atom(case,a,facts['classes'][a['id']])
                if policy.get(k,{}).get('decision')!='allow':continue
                committed.append({'id':a['id'],'atom':k})
            if a['out']:available.add(a['out'])
    gold=case['oracle']['policy']
    return {'committed':committed,'required_complete':case['sink_id'] in {x['id'] for x in committed},
            'unauthorized':sum(gold[x['atom']]['decision']!='allow' for x in committed)}
