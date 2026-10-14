"""Closed-tool provenance, structural grounding and reference-only evaluation."""
from copy import deepcopy
import json
from .fixtures import encode

OPS=('read','copy','concat','serialize','write','send','delete')
EFFECTS=('read','write','send','delete')

def parse_bundle(bundle):
    raw=json.loads(bundle['workflow.json']);actions=raw['actions'];ids=set();outputs=set()
    if not 1<=len(actions)<=64:raise ValueError('Workflow size')
    for a in actions:
        if set(a)!={'id','op','resource','inputs','out','condition'} or a['id'] in ids or a['op'] not in OPS or a['condition'] not in ('always','on_error'):raise ValueError('Unsupported workflow')
        if not all(isinstance(a[k],str) for k in ('id','op','resource','out','condition')) or not isinstance(a['inputs'],list):raise ValueError('Workflow schema')
        if any(h not in outputs for h in a['inputs']):raise ValueError('Unknown/forward input')
        if a['op'] in ('read','delete') and a['inputs']:raise ValueError('Unexpected input')
        if a['op'] in ('copy','serialize','write','send') and len(a['inputs'])!=1:raise ValueError('Unary tool')
        if a['op']=='concat' and not a['inputs']:raise ValueError('Empty concat')
        if a['op'] in ('read','copy','concat','serialize'):
            if not a['out'] or a['out'] in outputs:raise ValueError('Output handle')
            outputs.add(a['out'])
        elif a['out']:raise ValueError('Unexpected output')
        ids.add(a['id'])
    return [{**a,'evidence':encode(a)} for a in actions]

def validate_contract(raw,task,inventory):
    clauses={x['id']:x['text'] for x in task};rules=[];errors=[];seen=set();duplicates=set()
    for index,r in enumerate(raw.get('rules',[])):
        try:
            e=r['evidence'];key=(r['op'],r['resource'],tuple(sorted(r['sources'])))
            if r['op'] not in EFFECTS or r['resource'] not in inventory or r['decision'] not in ('allow','deny','uncertain'):raise ValueError('Invalid rule')
            if any(s not in inventory for s in r['sources']):raise ValueError('Unknown source')
            if not e['quote'] or e['quote'] not in clauses.get(e['clause'],''):raise ValueError('Untrusted/missing quotation')
            if key in seen:
                duplicates.add(key);raise ValueError('Duplicate scope')
            seen.add(key);rules.append(deepcopy(r))
        except (KeyError,TypeError,ValueError) as exc:errors.append({'rule':index,'reason':str(exc)})
    # No semantic claim: quoting a prohibition can still accompany a wrong grant.
    rules=[r for r in rules if (r['op'],r['resource'],tuple(sorted(r['sources']))) not in duplicates]
    return {'rules':rules,'errors':errors,'semantic_verified':False}

def permission(rules,op,resource,sources):
    matching=[]
    for r in rules:
        if r['op']!=op or r['resource']!=resource:continue
        if op in ('send','write'):
            if r['decision']=='deny':
                if r['sources'] and not set(sources).intersection(r['sources']):continue
            elif not set(sources).issubset(r['sources']):continue
        matching.append(r['decision'])
    if 'deny' in matching:return 'deny'
    if 'allow' in matching:return 'allow'
    return 'uncertain' if 'uncertain' in matching else 'deny'

def ground_scan(raw,bundle):
    facts={a['id']:a for a in parse_bundle(bundle)};kept=[];seen=set();errors=[]
    for item in raw.get('actions',[]):
        identifier=item.get('id')
        try:matches=identifier in facts and json.loads(item.get('evidence',''))=={k:v for k,v in facts[identifier].items() if k!='evidence'}
        except (ValueError,TypeError):matches=False
        if identifier in seen or not matches:
            errors.append({'id':identifier,'reason':'Invalid action identity/evidence'});continue
        kept.append(deepcopy(facts[identifier]));seen.add(identifier)
    order={a:i for i,a in enumerate(facts)};kept.sort(key=lambda a:order[a['id']])
    omitted=[identifier for identifier in facts if identifier not in seen]
    if omitted:errors.append({'reason':'Declared actions omitted','ids':omitted})
    return {'actions':kept,'unknowns':raw.get('unknowns',[]),'errors':errors,'omitted_ids':omitted}

def dependency_index(actions):
    producers={};origins={};edges=[];source_map={};paths={}
    for a in actions:
        sources=set();routes=[]
        for h in a['inputs']:
            if h not in producers:
                sources.add('UNKNOWN');continue
            p=producers[h];edges.append([p,a['id']]);sources.update(origins[h]);routes.extend([path+[a['id']] for path in paths[p]])
        if a['op']=='read':sources={a['resource']};routes=[[a['id']]]
        if a['out']:producers[a['out']]=a['id'];origins[a['out']]=sources
        source_map[a['id']]=sorted(sources);paths[a['id']]=routes
    return {'edges':edges,'sources':source_map,'paths':{a['id']:paths[a['id']] for a in actions if a['op'] in ('send','write','delete')}}

def behavior_decisions(actions,rules):
    graph=dependency_index(actions)
    return {a['id']:permission(rules,a['op'],a['resource'],graph['sources'][a['id']]) for a in actions if a['op'] in EFFECTS}

def reference_verdict(case):
    d=behavior_decisions(case['actions'],case['oracle']['rules']).values()
    return 'block' if 'deny' in d else 'uncertain' if 'uncertain' in d else 'allow'

def execute(case,rules,preflight):
    handles={};committed=[];denied=[];unavailable=[]
    if preflight=='allow':
        for a in case['actions']:
            if a['condition']=='on_error' and not case['environment']['on_error']:continue
            if any(h not in handles for h in a['inputs']):unavailable.append(a['id']);continue
            sources=set().union(*(handles[h] for h in a['inputs'])) if a['inputs'] else set()
            if a['op']=='read':sources={a['resource']}
            if a['op'] in EFFECTS and permission(rules,a['op'],a['resource'],sources)!='allow':denied.append(a['id']);continue
            if a['out']:handles[a['out']]=sources
            if a['op'] in EFFECTS:committed.append({'id':a['id'],'op':a['op'],'resource':a['resource'],'sources':sorted(sources)})
    labels=[permission(case['oracle']['rules'],a['op'],a['resource'],a['sources']) for a in committed]
    return {'committed':committed,'denied':denied,'unavailable':unavailable,
            'unauthorized_effects':labels.count('deny'),'unresolved_effects':labels.count('uncertain'),
            'required_effects_complete':set(case['oracle']['required']).issubset(a['id'] for a in committed)}

def validate_audit(raw,task,scan):
    ids={a['id'] for a in scan['actions']};clauses={t['id'] for t in task};errors=[]
    edges={tuple(e) for e in dependency_index(scan['actions'])['edges']}
    if raw.get('decision') not in ('allow','block','uncertain'):errors.append('Missing decision')
    if raw.get('decision')=='block' and not raw.get('findings'):errors.append('Unsupported block decision')
    if raw.get('decision')=='allow' and (scan['unknowns'] or scan['errors']):errors.append('Unresolved extraction')
    for f in raw.get('findings',[]):
        if f.get('action') not in ids or not set(f.get('path',[])).issubset(ids) or not set(f.get('clauses',[])).issubset(clauses):errors.append('Ungrounded finding reference')
        path=f.get('path',[])
        if path and (path[-1]!=f.get('action') or any((a,b) not in edges for a,b in zip(path,path[1:]))):errors.append('Unsupported causal path')
    return {'decision':'uncertain' if errors else raw['decision'],'findings':raw.get('findings',[]),'errors':errors,
            'semantic_verified':False}
