"""Strict offline replay; never reads credentials or sends API requests."""
import json
from .api import OUT,PRIOR
from .run import freeze,preparation,collect,inventory
def main():
    freeze()
    if preparation()!=json.loads((OUT/'preparation.json').read_text(encoding='utf8')):raise RuntimeError('Preparation differs')
    allrecords={};total=0
    for stage in ('pilot','formal'):
        if not (OUT/stage/'summary.json').exists():
            if stage=='pilot':raise RuntimeError('Missing pilot')
            continue
        summary,rows,records=collect(stage);allrecords.update(records);total+=summary['cost_usd']
        for name,value in [('summary',summary),('rows',rows)]:
            if value!=json.loads((OUT/stage/(name+'.json')).read_text(encoding='utf8')):raise RuntimeError(name+' differs')
        if stage=='pilot':
            expected=dict(**summary['gate'],formal_status='authorized_by_gate' if summary['gate']['proceed'] else 'not_run_gate_failed')
            if expected!=json.loads((OUT/'decision.json').read_text(encoding='utf8')):raise RuntimeError('Decision differs')
            if not summary['gate']['proceed'] and (OUT/'formal').exists():raise RuntimeError('Formal run violates gate')
    if set(allrecords)!={p.stem for p in (OUT/'requests').glob('*.json')}:raise RuntimeError('Request inventory differs')
    if inventory()!=json.loads((OUT/'evidence-manifest.json').read_text(encoding='utf8')):raise RuntimeError('Evidence hashes differ')
    print(json.dumps(dict(replay='passed',requests=len(allrecords),v8_usd=total,cumulative_usd=PRIOR+total)))
if __name__=='__main__':main()

