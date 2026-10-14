"""Deterministic descriptive analysis; authored templates are not population samples."""
from collections import Counter
from src.api import usage_cost
from .core import allowed
def rates(rows):
    return {'n':len(rows),'pipeline_ok':sum(r['pipeline_ok'] for r in rows),
            'raw_excess':sum(bool(r['policy_errors']['excess']) for r in rows),
            'unresolved_grants':sum(bool(r['policy_errors']['unresolved_grants']) for r in rows),
            'missing_grants':sum(bool(r['policy_errors']['missing']) for r in rows),
            'exact_policy':sum(r['policy_errors']['exact'] for r in rows),
            'raw_audit_correct':sum(r.get('raw_audit_correct',False) for r in rows),
            'audit_correct':sum(r.get('audit_correct',False) for r in rows),
            'evidence_errors':sum(bool(r.get('audit',{}).get('errors')) for r in rows),
            'required_complete':sum(r['execution']['required_complete'] for r in rows),
            'unauthorized':sum(r['execution']['unauthorized']>0 for r in rows),
            'unresolved':sum(r['execution']['unresolved']>0 for r in rows)}
def summarize(rows,updates,requests):
    methods=sorted({r['method'] for r in rows})
    summary={'logical_rows':len(rows),'update_rows':len(updates),'unique_requests':len(requests),
      'status_counts':dict(Counter(r['status'] for r in requests)),
      'models':dict(Counter(str(r['model']) for r in requests)),
      'usage_usd':sum(usage_cost(r['usage']) for r in requests),
      'accounted_usd':sum(a.get('settled',a['reserved']) for r in requests for a in r['attempts']),
      'roles':{},'methods':{},'contamination':{},'graph_comparison':{},'updates':{}}
    for role in sorted({r['role'] for r in requests}):
        q=[r for r in requests if r['role']==role]
        summary['roles'][role]={'requests':len(q),'usage_usd':sum(usage_cost(r['usage']) for r in q),
          'input_tokens':sum(r['usage'].get('input_tokens',0) for r in q),
          'output_tokens':sum(r['usage'].get('output_tokens',0) for r in q)}
    for m in methods:
        r=[x for x in rows if x['method']==m]
        summary['methods'][m]={'all':rates(r),'variants':{v:rates([x for x in r if x['variant']==v]) for v in sorted({x['variant'] for x in r})}}
    for method in ('MixedRuntime','IsolatedRuntime'):
        r=[x for x in rows if x['method']==method]
        pairs=[]
        for attack in (x for x in r if x['variant']=='attack'):
            neutral=next(x for x in r if x['case_id']==attack['case_id'].replace('-attack','-neutral') and x['repeat']==attack['repeat'])
            a=bool(attack['policy_errors']['excess']);n=bool(neutral['policy_errors']['excess'])
            pairs.append({'case_id':attack['case_id'],'repeat':attack['repeat'],'structure':attack['structure'],'narrative':attack['narrative'],'attack':a,'neutral':n,
                          'new':a and not n,'resolved':n and not a,
                          'valid_pair':attack['pipeline_ok'] and neutral['pipeline_ok'],
                          'changed_map':attack['policy_decisions']!=neutral['policy_decisions']})
        def paired(p):
            valid=[x for x in p if x['valid_pair']]
            return {'n':len(p),'valid_pair':len(valid),
                    **{k:sum(x[k] for x in valid) for k in ('attack','neutral','new','resolved','changed_map')},
                    'difference':sum(int(x['attack'])-int(x['neutral']) for x in valid)/len(valid) if valid else None}
        summary['contamination'][method]={'all':paired(pairs),
          'discordant_pairs':[x for x in pairs if x['valid_pair'] and x['attack']!=x['neutral']],
          'by_structure':{s:paired([x for x in pairs if x['structure']==s]) for s in sorted({x['structure'] for x in pairs})},
          'by_narrative':{n:paired([x for x in pairs if x['narrative']==n]) for n in sorted({x['narrative'] for x in pairs})}}
    pairs=[]
    for f in (x for x in rows if x['method']=='IsolatedFlat'):
        g=next(x for x in rows if x['method']=='IsolatedGraph' and x['case_id']==f['case_id'] and x['repeat']==f['repeat'])
        pairs.append({'case_id':f['case_id'],'repeat':f['repeat'],'structure':f['structure'],'variant':f['variant'],'flat':f['audit_correct'],'graph':g['audit_correct'],
                      'graph_only':g['audit_correct'] and not f['audit_correct'],'flat_only':f['audit_correct'] and not g['audit_correct']})
    def graph(p):return {'n':len(p),**{k:sum(x[k] for x in p) for k in ('flat','graph','graph_only','flat_only')},
                        'difference':sum(int(x['graph'])-int(x['flat']) for x in p)/len(p)}
    summary['graph_comparison']={'all':graph(pairs),
      'discordant_pairs':[x for x in pairs if x['flat']!=x['graph']],
      'by_structure':{s:graph([x for x in pairs if x['structure']==s]) for s in sorted({x['structure'] for x in pairs})},
      'by_variant':{v:graph([x for x in pairs if x['variant']==v]) for v in sorted({x['variant'] for x in pairs})}}
    for initial in ('correct','overbroad'):
        u=[r for r in updates if r['initial_kind']==initial]
        summary['updates'][initial]={'n':len(u),'pipeline_ok':sum(r['pipeline_ok'] for r in u),
            'proposed_excess':sum(bool(r['proposed_errors']['excess']) for r in u),
            'effective_excess':sum(bool(r['effective_errors']['excess']) for r in u),
            'expansion_rejected':sum(r['expansion_rejected'] for r in u),
            'required_complete':sum(r['execution']['required_complete'] for r in u),
            'unauthorized':sum(r['execution']['unauthorized']>0 for r in u)}
    return summary
