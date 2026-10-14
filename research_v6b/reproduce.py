"""Replay development, frozen selection and every held-out outcome offline."""
import argparse
import json
from research_v2.reproduce import verify_artifacts
from .run import ROOT,OUT,freeze,preparation,collect
from research_v6.analysis import summarize

def main():
    p=argparse.ArgumentParser();p.add_argument('--prepared',action='store_true');args=p.parse_args()
    freeze()
    verify_artifacts(ROOT/'research_v6/results')
    if preparation()!=json.loads((OUT/'preparation.json').read_text(encoding='utf-8')):raise RuntimeError('Preparation differs')
    if args.prepared:print('V6 counterfactual certificates and interfaces verified; zero model calls');return
    n=verify_artifacts(OUT);rows,calibration,requests=collect()
    s=summarize(rows,calibration,requests)
    if s!=json.loads((OUT/'summary.json').read_text(encoding='utf-8')):raise RuntimeError('Summary differs')
    a=json.loads((OUT/'accounting.json').read_text(encoding='utf-8'));start=json.loads((OUT/'start.json').read_text(encoding='utf-8'))
    if abs(a['after_usd']-start['cumulative_start_usd']-s['accounted_usd'])>1e-8:raise RuntimeError('Ledger delta differs')
    print(json.dumps({'evidence_files':n,'holdout_rows':len(rows),'calibration_rows':len(calibration),'requests':len(requests),'model_calls':0}))
if __name__=='__main__':main()
