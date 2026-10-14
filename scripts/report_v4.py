"""Post-measurement v4 reporting. Never changes frozen inputs or calls a model."""
import argparse
from collections import Counter
import csv
import hashlib
import io
import json
from pathlib import Path
from statistics import mean
from research_v4.run import ROOT,OUT,collect
from research_v4.reproduce import verify_preparation
from research_v2.reproduce import verify_artifacts
from research_v4.analysis import summarize

DEST=ROOT/'research_v4/report'

def derive():
    verify_preparation();verify_artifacts(OUT)
    rows,requests=collect();summary=summarize(rows,requests)
    assert summary==json.loads((OUT/'summary.json').read_text(encoding='utf-8'))
    lookup={p['key']:p for p in requests};confusion={};logical={};disagreements=[];audit_stages={}
    for method in summary['methods']:
        subset=[r for r in rows if r['method']==method]
        confusion[method]=None if method=='TaskRuntime' else {v:dict(Counter(r['reference_verdict']+' -> '+r['decision'] for r in subset if r['variant']==v)) for v in ('clean','attack','authorized','underspecified')}
        if method!='TaskRuntime':
            audit_stages[method]={'scheduled':len(subset),
                'raw_correct_and_pipeline_ok':sum(r['pipeline_ok'] and lookup[r['components'][-1]]['value'].get('decision')==r['reference_verdict'] for r in subset),
                'validated_correct':sum(r['audit_correct'] for r in subset),
                'evidence_error_trajectories':sum(bool(r['audit']['errors']) for r in subset),
                'evidence_error_reasons':dict(Counter(reason for r in subset for reason in r['audit']['errors']))}
        used=[lookup[k] for r in subset for k in r['components']]
        logical[method]={'logical_role_uses':len(used),'distinct_reused_requests':len({p['key'] for p in used}),
            'input_tokens_per_trajectory':mean(sum(lookup[k].get('usage',{}).get('input_tokens',0) for k in r['components']) for r in subset),
            'output_tokens_per_trajectory':mean(sum(lookup[k].get('usage',{}).get('output_tokens',0) for k in r['components']) for r in subset),
            'logical_use_estimated_usd':sum(sum(a.get('settled',a['reserved']) for a in p['attempts']) for p in used)}
    paired={(r['case_id'],r['repeat'],r['method']):r for r in rows}
    for r in rows:
        if r['method'].endswith('-Flat'):
            b=paired[(r['case_id'],r['repeat'],r['method'].replace('-Flat','-Graph'))]
            if r['decision']!=b['decision'] or r['audit_correct']!=b['audit_correct']:
                disagreements.append({'case_id':r['case_id'],'repeat':r['repeat'],'contract_mode':r['method'].split('-')[0],
                    'reference':r['reference_verdict'],'flat':r['decision'],'graph':b['decision'],
                    'flat_errors':r['audit']['errors'],'graph_errors':b['audit']['errors'],
                    'flat_request':r['components'][-1],'graph_request':b['components'][-1]})
    components={}
    for role in ('contract','scan','audit'):
        ps=[p for p in requests if p['role']==role]
        components[role]={'unique_requests':len(ps),'statuses':dict(Counter(p['status'] for p in ps)),
                         'models':dict(Counter(p.get('model') for p in ps)),
                         'max_input_tokens':max((p.get('usage',{}).get('input_tokens',0) for p in ps),default=0)}
    isolated_errors=[]
    for r in rows:
        if r['method'] not in ('Isolated-Flat','Mixed-Flat'):continue
        if r['raw_excess'] or r['validated_excess'] or r['contract']['errors']:
            isolated_errors.append({'case_id':r['case_id'],'repeat':r['repeat'],'method':r['method'],
                'raw_excess':r['raw_excess'],'validated_excess':r['validated_excess'],'contract_errors':r['contract']['errors'],'request':r['components'][0]})
    runtime_failures=[{'case_id':r['case_id'],'repeat':r['repeat'],'contract_request':r['components'][0],
        'denied':r['execution']['denied'],'contract_errors':r['contract']['errors'],
        'unconditional_send_denies':[x for x in r['contract']['rules'] if x['op']=='send' and x['decision']=='deny' and not x['sources']]}
        for r in rows if r['method']=='TaskRuntime' and r['variant'] in ('clean','authorized') and not r['execution']['required_effects_complete']]
    data={'status':'MEASURED','frozen_summary_sha256':hashlib.sha256((OUT/'summary.json').read_bytes()).hexdigest(),
          'confusion':confusion,'audit_stages':audit_stages,'logical_usage':logical,'unique_components':components,'audit_disagreements':disagreements,
          'contract_error_trajectories':isolated_errors,'runtime_benign_failures':runtime_failures,
          'caveats':['Post-measurement diagnostics; primary outcomes remain in frozen summary.json',
                     'TaskRuntime confusion is null because it has no preflight audit',
                     'Logical-use costs charge reused records on each use and are not additive physical API expenditure',
                     'Distinct request sets overlap between methods; the physical total counts their union',
                     'Related authored cases and repeated cached inputs are not independent observations']}
    return summary,data

def csv_text(summary):
    fields=['method','n','audit_n','audit_correct','audit_accuracy','pipeline_failures','unauthorized_trials','unresolved_effect_trials','benign_n','benign_blocked','benign_required_complete','mean_scan_coverage']
    f=io.StringIO(newline='');w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');w.writeheader()
    for method,m in summary['methods'].items():w.writerow({'method':method,**{k:m[k] for k in fields[1:]}})
    return f.getvalue()

def plot(summary):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    methods=list(summary['methods']);audited=[m for m in methods if m!='TaskRuntime']
    colors=['#355c7d','#e67e22','#355c7d','#e67e22','#4c956c']
    fig,axes=plt.subplots(1,2,figsize=(10.5,4.6),layout='constrained')
    for ax,names,key,title,denominator in [(axes[0],audited,'audit_correct','Evidence-valid audit correctness','audit_n'),(axes[1],methods,'benign_required_complete','Required benign effects completed','benign_n')]:
        vals=[100*summary['methods'][m][key]/summary['methods'][m][denominator] for m in names]
        ax.bar(range(len(names)),vals,color=colors[:len(names)],width=.65)
        ax.set_xticks(range(len(names)),[m.replace('-','\n') for m in names],fontsize=9)
        ax.set_ylim(0,114);ax.set_ylabel('Percent');ax.set_title(title,fontsize=11)
        ax.spines[['top','right']].set_visible(False)
        for i,m in enumerate(names):
            d=summary['methods'][m];ax.text(i,vals[i]+2,f"{d[key]}/{d[denominator]}",ha='center',fontsize=9)
    fig.suptitle('V4: authored declarative workflows; repeated uses are not independent',fontsize=11)
    fig.savefig(DEST/'comparison.png',dpi=170)
    fig.savefig(DEST/'comparison.pdf',metadata={'CreationDate':None,'ModDate':None})
    plt.close(fig)

def main():
    p=argparse.ArgumentParser();p.add_argument('--verify',action='store_true');args=p.parse_args()
    summary,data=derive();csv_data=csv_text(summary)
    if args.verify:
        assert json.loads((DEST/'diagnostics.json').read_text(encoding='utf-8'))==data
        assert (DEST/'method-summary.csv').read_text(encoding='utf-8')==csv_data
        manifest=json.loads((DEST/'manifest.json').read_text(encoding='utf-8'))
        for name,digest in manifest.items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest
        print('V4 reporting diagnostics, CSV and figure/source hashes verified; no model calls.')
        return
    DEST.mkdir(parents=True,exist_ok=True)
    (DEST/'diagnostics.json').write_bytes((json.dumps(data,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
    (DEST/'method-summary.csv').write_bytes(csv_data.encode('utf-8'));plot(summary)
    files=[DEST/'diagnostics.json',DEST/'method-summary.csv',DEST/'comparison.png',DEST/'comparison.pdf',Path(__file__).resolve()]
    manifest={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    (DEST/'manifest.json').write_bytes((json.dumps(manifest,indent=2)+'\n').encode('utf-8'))
    print('Generated post-measurement tables, diagnostic records and figure; no model calls.')

if __name__=='__main__':main()
