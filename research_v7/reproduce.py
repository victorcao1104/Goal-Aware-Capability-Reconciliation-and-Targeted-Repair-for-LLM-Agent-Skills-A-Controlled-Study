"""No credentials, network, or model calls are needed for replay."""
import json
from .run import freeze,preparation,collect,evidence
from .api import OUT
def main():
    freeze()
    if preparation()!=json.loads((OUT/'preparation.json').read_text(encoding='utf-8')):raise RuntimeError('Preparation differs')
    summary,rows,_=collect()
    for name,value in [('rows',rows),('summary',summary)]:
        if value!=json.loads((OUT/(name+'.json')).read_text(encoding='utf-8')):raise RuntimeError(name+' differs')
    if evidence()!=json.loads((OUT/'evidence-manifest.json').read_text(encoding='utf-8')):raise RuntimeError('Evidence differs')
    print(json.dumps({k:summary[k] for k in ('rows','physical_requests','statuses','incremental_usd','cumulative_usd')}))
if __name__=='__main__':main()
