"""Gold-driven stubs verify plumbing only; they are never experimental results."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from research_v4.fixtures import make_cases
from research_v4.core import behavior_decisions,reference_verdict,dependency_index
from research_v4.run import evaluate_case,request_key,collect,dump,fingerprint
from research_v4.analysis import summarize

def fake_get(case,records):
    def get(role,payload,repeat):
        key=request_key(role,payload,repeat)
        if role=='contract':value={'rules':[{**r,'evidence':{'clause':'T0','quote':case['task'][0]['text']}} for r in case['oracle']['rules']]}
        elif role=='scan':value={'actions':[{'id':a['id'],'evidence':a['evidence']} for a in case['actions']],'unknowns':[]}
        else:
            decision=reference_verdict(case);findings=[]
            if decision!='allow':
                decisions=behavior_decisions(case['actions'],case['oracle']['rules']);node=next(k for k,v in decisions.items() if v==('deny' if decision=='block' else 'uncertain'))
                paths=dependency_index(case['actions'])['paths'].get(node,[])
                findings=[{'action':node,'path':paths[0] if paths else [node],'clauses':['T0'],'reason':'TEST STUB, not a model judgment'}]
            value={'decision':decision,'findings':findings}
        record={'key':key,'role':role,'payload':payload,'repeat':repeat,'value':value,'status':'ok','model':'TEST-STUB','attempts':[],'provider_status':'ok','fingerprint':fingerprint(role,payload,repeat)}
        if key in records:assert records[key]==record
        records[key]=record;return record
    return get

class ReplayTests(unittest.TestCase):
    def test_full_schedule_without_any_api(self):
        records={};rows=[]
        for c in make_cases():
            for repeat in (0,1):rows.extend(evaluate_case(c,repeat,fake_get(c,records)))
        self.assertEqual(len(rows),480)
        audited=[r for r in rows if r['method']!='TaskRuntime']
        self.assertTrue(all(r['audit_correct'] for r in audited))
        self.assertTrue(all(r['execution']['unauthorized_effects']==0 for r in rows))
        summary=summarize(rows,list(records.values()))
        self.assertEqual(summary['graph_effect']['Isolated']['difference_pp'],0)
        self.assertTrue(all(r['execution']['required_effects_complete'] for r in rows if r['method']=='TaskRuntime'))
    def test_replay_checks_request_and_trajectory_inventory(self):
        root=Path(__file__).resolve().parents[1];(root/'work').mkdir(exist_ok=True)
        c=make_cases()[1];records={};rows=evaluate_case(c,0,fake_get(c,records))
        with tempfile.TemporaryDirectory(dir=root/'work') as directory:
            out=Path(directory)
            for key,p in records.items():dump(out/'requests'/(key+'.json'),p)
            dump(out/'trajectories'/f"{c['id']}-r0.json",rows)
            with patch('research_v4.run.OUT',out),patch('research_v4.run.jobs',return_value=[(c,0)]):
                self.assertEqual(collect()[0],rows)
                dump(out/'requests'/'extra.json',{})
                with self.assertRaises(RuntimeError):collect()

if __name__=='__main__':unittest.main()
