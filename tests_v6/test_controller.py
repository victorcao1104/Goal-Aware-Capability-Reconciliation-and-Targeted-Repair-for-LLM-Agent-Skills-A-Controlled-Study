import unittest
from research_v6.run import select_candidates,holdout_jobs,attacker_payload
from research_v6.fixtures import holdout_cases
from research_v6.analysis import summarize
class ControllerTests(unittest.TestCase):
    def test_selection_uses_score_then_predeclared_id(self):
        c=[{'id':'c02','score':0,'valid':True,'prose':'two'}, {'id':'c01','score':0,'valid':True,'prose':'one'},
           {'id':'c00','score':99,'valid':False,'prose':''}]
        self.assertEqual([x['id'] for x in select_candidates(c)],['c01','c02'])
        c[0]['score']=1;self.assertEqual(select_candidates(c)[0]['id'],'c02')
    def test_holdout_inventory_is_fixed_and_disjoint_from_dev(self):
        selected=[{'id':'c00','prose':'a'},{'id':'c01','prose':'b'}]
        cases=holdout_cases(selected)
        self.assertEqual(len(cases),20);self.assertEqual(len(holdout_jobs(selected)),120)
        self.assertFalse(any(c['context'] in ('retail','clinic') for c in cases))
    def test_attacker_has_only_development_contexts(self):
        p=attacker_payload('family',{'prose':'a','id':'c00','feedback':[]})
        self.assertEqual({c['context'] for c in p['development_contexts']},{'retail','clinic'})
        self.assertNotIn('energy',str(p));self.assertNotIn('survey',str(p))
    def test_empty_success_subset_not_reported_as_no_attack(self):
        s=summarize([],[],[])
        self.assertEqual(s['rows'],0)
        self.assertEqual(s['requests'],0)
if __name__=='__main__':unittest.main()
