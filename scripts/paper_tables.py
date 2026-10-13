"""Presentation-only derivations from the frozen analysis outputs."""
import csv
import json
from pathlib import Path
from collections import Counter

ROOT=Path(__file__).resolve().parent.parent


def pct(value):
    return '--' if value is None else f'{100*value:.1f}'


def main():
    root=ROOT
    summary=json.loads((root/'results/summary/summary.json').read_text())
    rows={(r['campaign'],r['mode'],r['method']):r for r in summary['metrics']}
    out=root/'paper/tables'
    out.mkdir(parents=True,exist_ok=True)
    methods=['B0','B1','B2','B2P','B2R','B3','B4','B5']
    table=[r'\begin{table*}[t]',r'\caption{Main-test outcomes (percent). Each live condition has 144 runs, including 72 attacked and 72 clean/authorized runs; each stress condition has 48 runs, including 24 attacked and 24 clean/authorized runs. Joint success is measured on attacked runs.}',r'\label{tab:mainresults}',r'\centering\small',r'\begin{tabular}{lrrrrrrrr}',r'\toprule',r'& \multicolumn{4}{c}{Live model plans} & \multicolumn{4}{c}{Deterministic stress replay} \\',r'\cmidrule(lr){2-5}\cmidrule(lr){6-9}',r'Method & ASR $\downarrow$ & TSR $\uparrow$ & Benign TSR & Joint $\uparrow$ & ASR $\downarrow$ & TSR $\uparrow$ & Benign TSR & Joint $\uparrow$ \\',r'\midrule']
    for method in methods:
        cells=[method]
        for mode in ('agent','scripted'):
            cells += [pct(rows[('formal-v1',mode,method)][k]) for k in ('asr','tsr','benign_tsr','joint_repair_success')]
        table.append(' & '.join(cells)+r' \\')
    table += [r'\bottomrule',r'\end{tabular}',r'\end{table*}']
    # Preserve the original Windows artifact bytes on every operating system.
    (out/'main-results.tex').write_text('\n'.join(table),encoding='utf8',newline='\r\n')
    table=[r'\begin{table}[t]',r'\caption{Original-bundle label agreement (percent), conditional on resolved analysis. This is not semantic permission ground truth.}',r'\label{tab:static}',r'\centering\small',r'\begin{tabular}{llrrrr}',r'\toprule',r'Coverage & Judge & $n$ & Prec. & Rec. & F1 \\',r'\midrule']
    for r in summary['static']:
        coverage={'all':'All','complete_text':'Complete','partial_text':'Partial'}[r['coverage']]
        role='Skill only' if r['role']=='scanner' else 'Task aware'
        table.append(' & '.join([coverage,role,str(r['n']),pct(r['precision']),pct(r['recall']),pct(r['f1'])])+r' \\')
    table += [r'\bottomrule',r'\end{tabular}',r'\end{table}']
    (out/'static-results.tex').write_text('\n'.join(table),encoding='utf8',newline='\r\n')
    components=list(csv.DictReader((root/'results/summary/components.csv').open(encoding='utf8')))
    micro={}
    for extractor in ('llm','ast','hybrid'):
        members=[r for r in components if r['extractor']==extractor]
        for kind in ('nodes','data_edges','contract'):
            counts={k:sum(int(r[kind+'_'+k]) for r in members) for k in ('tp','fp','fn')}
            tp,fp,fn=[counts[k] for k in ('tp','fp','fn')]
            counts.update(precision=tp/(tp+fp) if tp+fp else None,recall=tp/(tp+fn) if tp+fn else None,f1=2*tp/(2*tp+fp+fn) if 2*tp+fp+fn else None)
            micro[extractor+'_'+kind]=counts
    unique=[r for r in components if r['extractor']=='llm']
    exact=sum(r['contract_exact_authorization_set']=='True' for r in unique)
    micro['contract_exact']={'correct':exact,'n':len(unique),'rate':exact/len(unique)}
    table=[r'\begin{table}[t]',r'\caption{Controlled graph reconstruction against observed closed-tool traces (micro-averaged percent). This vocabulary was designed for the parser.}',r'\label{tab:components}',r'\centering\small',r'\begin{tabular}{llrrr}',r'\toprule',r'Extractor & Target & Prec. & Rec. & F1 \\',r'\midrule']
    for extractor in ('llm','ast','hybrid'):
        for kind in ('nodes','data_edges'):
            r=micro[extractor+'_'+kind]
            table.append(' & '.join([extractor.upper(),{'nodes':'Actions','data_edges':'Data edges'}[kind],pct(r['precision']),pct(r['recall']),pct(r['f1'])])+r' \\')
    table += [r'\bottomrule',r'\end{tabular}',r'\end{table}']
    (out/'components.tex').write_text('\n'.join(table),encoding='utf8',newline='\r\n')
    runs=[json.loads(p.read_text(encoding='utf8')) for p in (root/'results/raw_runs/runs').glob('*.json')]
    runs=[r for r in runs if r['campaign'] in ('formal-v1','transfer-v1')]
    extras={'benign_attack_events':Counter(r['method']+'-'+r['mode'] for r in runs if r['variant'] in ('clean','authorized') and r['evaluation']['attack_success']),
            'model_outcomes':Counter(r.get('model_outcome','completed') for r in runs),
            'validity':Counter(r['evaluation']['status'] for r in runs)}
    facts={'components':micro,'extra_outcomes':extras,'cost':summary['cost'],'returned_models':summary['returned_models']}
    (root/'results/summary/paper-facts.json').write_text(json.dumps(facts,indent=2),encoding='utf8')
    print(json.dumps(facts,indent=2))


if __name__=='__main__':
    main()
