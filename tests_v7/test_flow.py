import unittest
from research_v7.fixtures import cases
from research_v7.engine import concrete,analyze,slice_ids,minimum_repair,assess,trusted_contract
class FlowTests(unittest.TestCase):
    def test_symbolic_engines_match_actual_marker_content(self):
        for c in cases():
            value=concrete(c)
            for mode in ('flat','graph'):
                a=analyze(c,mode)
                for sink in c['sinks']:
                    actual=sorted(k for k,v in value[sink].items() if 'ROWMARK_' in str(v))
                    self.assertEqual(actual,sorted(k for k,v in a['states'][sink].items() if v['class']=='rows'))
    def test_slices_equal_and_decoys_removed(self):
        for c in cases():
            self.assertEqual(slice_ids(c,'flat')[0],slice_ids(c,'graph')[0])
            self.assertLess(len(slice_ids(c,'graph')[0]),len(c['actions']))
    def test_minimum_two_site_repair_and_controls(self):
        for c in cases():
            r=minimum_repair(c,trusted_contract(c),'flat')
            self.assertEqual(r['count'],2 if c['variant']=='unsafe' else 0)
            self.assertTrue(assess(c,r['edits'],trusted_contract(c))['joint'])
    def test_graph_solver_same_capability_as_flat(self):
        for c in cases():
            p=trusted_contract(c)
            f=minimum_repair(c,p,'flat');g=minimum_repair(c,p,'graph')
            self.assertEqual(f['count'],g['count'])
            self.assertEqual(f['edits'],g['edits'])
    def test_deleting_required_aggregate_is_not_success(self):
        c=cases()[0];node=next(a for a in c['actions'] if a['op']=='aggregate')
        z=assess(c,[{'node':node['id'],'keep':[]}],trusted_contract(c))
        self.assertFalse(z['joint'])
    def test_serialize_is_not_declassification(self):
        c=cases()[0];a=analyze(c,'flat')
        self.assertTrue(any(any(v['class']=='rows' for v in a['states'][n['id']].values()) for n in c['actions'] if n['op']=='serialize'))
    def test_local_repairs_need_four_but_shared_cuts_need_two(self):
        for c in cases():
            if c['variant']!='unsafe':continue
            states=analyze(c)['states']
            index={a['id']:a for a in c['actions']}
            edits=[]
            for s in c['sinks']:
                parent=index[s]['inputs'][0]
                edits.append({'node':parent,'keep':sorted(f for f,m in states[parent].items() if m['class']!='rows')})
            self.assertEqual(len(edits),4)
            self.assertTrue(assess(c,edits,trusted_contract(c))['joint'])
            self.assertEqual(minimum_repair(c,trusted_contract(c))['count'],2)
if __name__=='__main__':unittest.main()
