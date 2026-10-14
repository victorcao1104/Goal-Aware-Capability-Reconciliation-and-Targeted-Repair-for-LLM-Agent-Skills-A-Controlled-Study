import unittest
from research_v7.fixtures import cases
from research_v7.engine import trusted_contract,minimum_repair
from research_v7.run import evaluate_proposal,evaluate_case,preparation
from research_v7.model import request_key
class Measurement(unittest.TestCase):
    def test_deny_is_not_repair_success(self):
        c=cases()[0];p=trusted_contract(c)
        q=dict(decision='deny',edits=[],rows_at_sinks={s:['f'+str(i//2)+'1'] for i,s in enumerate(c['sinks'])})
        z=evaluate_proposal(c,q,p,True)
        self.assertFalse(z['joint']);self.assertTrue(z['raw_class_correct'])
    def test_repair_success_and_failed_call_denominator(self):
        c=cases()[0];p=trusted_contract(c);r=minimum_repair(c,p)
        q=dict(decision='repair',edits=r['edits'],rows_at_sinks={s:['f'+str(i//2)+'1'] for i,s in enumerate(c['sinks'])})
        self.assertTrue(evaluate_proposal(c,q,p,True)['optimal_joint'])
        self.assertFalse(evaluate_proposal(c,q,p,False)['joint'])
    def test_authority_failure_retained_for_all_methods(self):
        def get(stage,setting,role,p,sc,repeat):
            return dict(key=request_key(stage,setting,role,p,sc,repeat),status='incomplete',value={})
        rows=evaluate_case(cases()[0],0,'mini',get)
        self.assertEqual(len(rows),7)
        self.assertTrue(all(not r['score']['joint'] for r in rows))
    def test_conservative_budget_and_minimum_certificates(self):
        p=preparation()
        self.assertLessEqual(p['worst_case_usd'],6)
        self.assertEqual(len(p['certificates']),12)
if __name__=='__main__':unittest.main()
