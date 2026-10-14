"""Descriptive paired metrics; failures and correlated reuse remain visible."""
from collections import Counter
from .model import usage_cost

def metrics(rows):
    return {'n':len(rows),'pipeline_ok':sum(r['pipeline_ok'] for r in rows),
      'policy_exact':sum(r['policy_errors']['exact'] for r in rows),
      'policy_excess':sum(bool(r['policy_errors']['excess']) for r in rows),
      'raw_verdict_correct':sum(r.get('audit',{}).get('raw_verdict_correct',False) for r in rows),
      'raw_class_correct':sum(r.get('audit',{}).get('raw_class_correct',False) for r in rows),
      'joint_correct':sum(r.get('audit_correct',False) for r in rows),
      'evidence_errors':sum(bool(r.get('audit',{}).get('errors')) for r in rows),
      'required_complete':sum(r['execution']['required_complete'] for r in rows),
      'unauthorized':sum(bool(r['execution']['unauthorized']) for r in rows)}
def summarize(rows,calibration,requests):
    s={'rows':len(rows),'calibration_rows':len(calibration),'requests':len(requests),
       'statuses':dict(Counter(r['status'] for r in requests)),
       'accounted_usd':sum(r['accounted_usd'] for r in requests),
       'usage_usd':sum(usage_cost(r['usage'],r['setting']) for r in requests),
       'physical_by_stage_setting':{},'settings':{}}
    s['logical_component_uses']={stage:{'uses':sum(len(r['components']) for r in rs),
       'unique_requests':len({k for r in rs for k in r['components']})}
       for stage,rs in [('holdout',rows),('calibration',calibration)]}
    for stage in sorted({r['stage'] for r in requests}):
        s['physical_by_stage_setting'][stage]={}
        for setting in sorted({r['setting'] for r in requests if r['stage']==stage}):
            q=[r for r in requests if r['stage']==stage and r['setting']==setting]
            s['physical_by_stage_setting'][stage][setting]={'n':len(q),'usd':sum(r['accounted_usd'] for r in q),
              'input_tokens':sum(r['usage'].get('input_tokens',0) for r in q),
              'output_tokens':sum(r['usage'].get('output_tokens',0) for r in q),
              'reasoning_tokens':sum(r['usage'].get('output_tokens_details',{}).get('reasoning_tokens',0) for r in q)}
    for setting in sorted({r['setting'] for r in rows}):
        rs=[r for r in rows if r['setting']==setting];methods={}
        for method in sorted({r['method'] for r in rs}):
            q=[r for r in rs if r['method']==method]
            methods[method]={'all':metrics(q),'variants':{v:metrics([r for r in q if r['variant']==v]) for v in sorted({r['variant'] for r in q})}}
        pairs=[]
        for a in (r for r in rs if r['method']=='MixedRuntime' and r['variant']=='attack'):
            n=next(r for r in rs if r['method']==a['method'] and r['variant']=='neutral' and r['context']==a['context'] and r['repeat']==a['repeat'])
            valid=a['pipeline_ok'] and n['pipeline_ok'];ae=bool(a['policy_errors']['excess']);ne=bool(n['policy_errors']['excess'])
            pairs.append({'case':a['case_id'],'repeat':a['repeat'],'valid':valid,'attack':ae,'neutral':ne,'new':ae and not ne})
        valid=[r for r in pairs if r['valid']]
        contamination={'n':len(pairs),'valid':len(valid),'attack_excess':sum(r['attack'] for r in valid),
                       'neutral_excess':sum(r['neutral'] for r in valid),'new_excess':sum(r['new'] for r in valid),
                       'pairs':pairs}
        graphs={}
        for mode in ('Mixed','Isolated'):
            gp=[]
            for flat in (r for r in rs if r['method']==mode+'Flat'):
                graph=next(r for r in rs if r['method']==mode+'Graph' and r['case_id']==flat['case_id'] and r['repeat']==flat['repeat'])
                gp.append({'case':flat['case_id'],'repeat':flat['repeat'],'flat':flat['audit_correct'],'graph':graph['audit_correct'],
                           'raw_flat':flat['audit']['raw_verdict_correct'],'raw_graph':graph['audit']['raw_verdict_correct']})
            graphs[mode]={'n':len(gp),'flat':sum(r['flat'] for r in gp),'graph':sum(r['graph'] for r in gp),
                         'difference':sum(int(r['graph'])-int(r['flat']) for r in gp)/len(gp),
                         'discordances':[r for r in gp if r['flat']!=r['graph']]}
        cal=[r for r in calibration if r['setting']==setting]
        s['settings'][setting]={'methods':methods,'contamination':contamination,'graph':graphs,
          'calibration':{m:metrics([r for r in cal if r['method']==m]) for m in sorted({r['method'] for r in cal})}}
    return s
