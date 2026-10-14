import unittest
from copy import deepcopy
from research_v5.fixtures import make_cases
from research_v5.run import evaluate_case,evaluate_update
from research_v5.analysis import summarize
from research_v5.core import reference

class ReplayTests(unittest.TestCase):
    def test_failed_pairs_are_unknown_not_zero_attack_success(self):
        cases=make_cases()[:2]
        def failed(role,payload,repeat):return {'key':role,'status':'ModelRefusal','value':{}}
        rows=[r for c in cases for r in evaluate_case(c,0,failed)]
        result=summarize(rows,[],[])
        pair=result['contamination']['MixedRuntime']['all']
        self.assertEqual(pair['valid_pair'],0)
        self.assertIsNone(pair['difference'])
    def test_oracle_stub_pipeline_keeps_authorized_utility(self):
        c=next(c for c in make_cases() if c['variant']=='authorized')
        def oracle(role,payload,repeat):
            value={'policy':deepcopy(c['oracle']['policy'])} if role=='policy' else (
                {'action_ids':[a['id'] for a in c['actions']],'unknowns':[]} if role=='scan' else
                {'decision':reference(c),'findings':[]})
            return {'key':role,'status':'ok','value':value}
        rows=evaluate_case(c,0,oracle)
        self.assertEqual(len(rows),4)
        self.assertTrue(all(r['execution']['required_complete'] for r in rows))
        self.assertEqual(sum(r.get('audit_correct',False) for r in rows),2)
    def test_invalid_update_preserves_initial_and_records_failure(self):
        c=make_cases()[0]
        r=evaluate_update(c,0,'overbroad',lambda *args:{'key':'failed','status':'ModelRefusal','value':{}})
        self.assertFalse(r['pipeline_ok'])
        self.assertEqual(r['effective_errors']['excess'],['e7','e9'])
        self.assertEqual(r['execution']['unauthorized'],2)
if __name__=='__main__':unittest.main()
