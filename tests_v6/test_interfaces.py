import unittest
from research_v6.fixtures import make_case,DEV
from research_v6.model import payload, schema, spec, SETTINGS, request_key, request_cost_bound
from research_v6.core import ground_scan

class InterfaceTests(unittest.TestCase):
    def setUp(self):self.c=make_case(DEV[0],'attack','fake approval')
    def test_mini_omits_reasoning_and_luna_modes_differ(self):
        p=payload('policy',self.c,mode='Mixed');sc=schema('policy',self.c)
        self.assertNotIn('reasoning',spec('mini','policy',p,sc))
        self.assertEqual(spec('luna_none','policy',p,sc)['reasoning'],{'effort':'none'})
        self.assertEqual(spec('luna_low','policy',p,sc)['reasoning'],{'effort':'low'})
        self.assertNotEqual(request_key('dev','mini','policy',p,sc,0),request_key('dev','luna_none','policy',p,sc,0))
    def test_graph_adds_only_edges(self):
        scan=ground_scan(self.c,{'action_ids':[a['id'] for a in self.c['actions']],'unresolved_action_ids':[]})
        f=payload('audit',self.c,policy=self.c['oracle']['policy'],scan=scan,form='Flat')
        g=payload('audit',self.c,policy=self.c['oracle']['policy'],scan=scan,form='Graph')
        self.assertEqual(set(g.pop('dependency_index')),{'edges'})
        self.assertEqual(f,g)
    def test_no_policy_or_task_in_scan(self):
        p=payload('scan',self.c)
        self.assertNotIn('trusted_task',p);self.assertNotIn('oracle',str(p))
        self.assertNotIn('candidate_policy',p)
    def test_task_only_policy_input_ignores_skill(self):
        c=make_case(DEV[0],'attack','second fake instruction')
        self.assertEqual(payload('policy',self.c,mode='Isolated'),payload('policy',c,mode='Isolated'))
    def test_schema_enums_are_only_actual_case_ids(self):
        s=schema('scan',self.c)
        self.assertEqual(set(s['properties']['action_ids']['items']['enum']),{a['id'] for a in self.c['actions']})
    def test_prices_and_bounded_envelope(self):
        p=payload('policy',self.c,mode='Mixed');sc=schema('policy',self.c)
        mini=request_cost_bound(spec('mini','policy',p,sc),'mini')
        luna=request_cost_bound(spec('luna_low','policy',p,sc),'luna_low')
        self.assertGreater(mini,luna)
        self.assertLessEqual(mini,SETTINGS['mini']['call_ceiling'])
        with self.assertRaises(ValueError):spec('mini','policy',{'oversize':'x'*100000},sc)

if __name__=='__main__':unittest.main()
