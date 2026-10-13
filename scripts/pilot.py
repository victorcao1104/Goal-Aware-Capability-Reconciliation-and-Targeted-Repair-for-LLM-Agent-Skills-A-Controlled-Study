"""Development-only pilot; no held-out cases are consulted."""
import json
from pathlib import Path
from src.api import Client
from src.runner import get_analysis, run_case, load_cases

root=Path.cwd()
client=Client(root)
cases=[c for c in load_cases(root,'development') if c['instance']==1 and c['variant'] in ('clean','injected')]
results=[]
for case in cases:
    analysis=get_analysis(client,root,case,0)
    for method in ('B0','B5'):
        result=run_case(client,root,case,analysis,method,0,'agent',True)
        results.append({'case':case['case_id'],'method':method,**result['evaluation']})
        print(json.dumps(results[-1]),flush=True)
(root/'work/pilot-summary.json').write_text(json.dumps({'runs':results,'budget_upper_usd':client.budget.total()},indent=2),encoding='utf-8')
print(json.dumps({'pilot_done':True,'runs':len(results),'budget_upper_usd':client.budget.total()}),flush=True)
