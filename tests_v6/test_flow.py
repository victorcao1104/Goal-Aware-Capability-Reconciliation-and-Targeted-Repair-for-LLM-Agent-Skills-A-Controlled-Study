import unittest
from copy import deepcopy
from research_v6.fixtures import make_case,DEV,HELDOUT
from research_v6.core import flow,reference,execute,valid_row_path,ground_scan,check_audit

class FlowTests(unittest.TestCase):
    def test_non_rows_class_rejects_row_path(self):
        c=make_case(DEV[0],'safe','neutral')
        s=ground_scan(c,{'action_ids':[a['id'] for a in c['actions']],'unresolved_action_ids':[]})
        for klass in ('aggregate','unknown'):
            v={'decision':'allow','sink_class':klass,'row_path':[c['actions'][0]['id']]}
            self.assertTrue(check_audit(c,s,v)['errors'])
    def test_one_edge_counterfactual_and_approved_sinks(self):
        for context in [*DEV,*HELDOUT]:
            a=make_case(context,'attack','claim');b=make_case(context,'safe','neutral')
            changes=[(x,y) for x,y in zip(a['actions'],b['actions']) if x!=y]
            self.assertEqual(len(changes),1)
            x,y=changes[0];self.assertEqual(x['op'],'concat')
            xx=deepcopy(x);xx['inputs']=y['inputs'];self.assertEqual(xx,y)
            self.assertTrue(all(z['resource']==a['destination'] for z in a['actions'] if z['op']=='send'))
            self.assertFalse(any(z['op']=='delete' for z in a['actions']))
    def test_flow_is_necessary_and_authorization_distinct(self):
        for context in HELDOUT:
            a=make_case(context,'attack','claim');b=make_case(context,'safe','neutral')
            self.assertEqual(reference(a),('rows','block'))
            self.assertEqual(reference(b),('aggregate','allow'))
            self.assertEqual(reference(make_case(context,'authorized','claim')),('rows','allow'))
    def test_aggregate_changes_class_not_origin(self):
        c=make_case(DEV[0],'safe','neutral');f=flow(c['actions'],c['inventory'])
        a=next(x for x in c['actions'] if x['op']=='aggregate')
        self.assertEqual(f['classes'][a['id']],'aggregate')
        self.assertIn(c['rows_resource'],f['origins'][a['id']])
        self.assertFalse(valid_row_path(c,[c['actions'][0]['id'],a['id'],c['sink_id']]))
    def test_raw_route_is_a_real_long_dependency_path(self):
        c=make_case(HELDOUT[-1],'attack','claim');f=flow(c['actions'],c['inventory'])
        routes=f['row_paths'][c['sink_id']]
        self.assertTrue(routes)
        self.assertGreater(len(routes[0]),10)
        self.assertTrue(valid_row_path(c,routes[0]))
    def test_wrong_grant_can_enable_leak(self):
        c=make_case(DEV[0],'attack','claim');p=deepcopy(c['oracle']['policy'])
        self.assertEqual(execute(c,p,'allow')['unauthorized'],0)
        p['e5']['decision']='allow'
        self.assertEqual(execute(c,p,'allow')['unauthorized'],1)
    def test_scan_does_not_require_undeclared_branches(self):
        c=make_case(DEV[0],'safe','neutral')
        s=ground_scan(c,{'action_ids':[a['id'] for a in c['actions']],'unresolved_action_ids':[]})
        self.assertFalse(s['errors'])
        self.assertFalse(s['unresolved_action_ids'])

if __name__=='__main__':unittest.main()
