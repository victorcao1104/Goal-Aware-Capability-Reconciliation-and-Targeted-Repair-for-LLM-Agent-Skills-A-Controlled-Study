import copy
import unittest
from research_v7.fixtures import cases
from research_v7.engine import analyze,assess,trusted_contract,minimum_repair
from research_v7.model import payload,schema,spec,SETTINGS,ARMS

class Interfaces(unittest.TestCase):
    def test_input_isolation_and_no_gold(self):
        for c in cases():
            for role,arm in [('policy',None)]+[('audit',a) for a in ARMS]:
                p=payload(role,c,arm,trusted_contract(c));s=str(p)
                self.assertNotIn('ROWMARK_',s)
                for forbidden in ('expected','variant','proposal_safe','minimum_repair'):self.assertNotIn(forbidden,p)
                self.assertEqual('untrusted_skill_prose' in p,arm=='FullFlatRaw')
                if role=='policy':self.assertNotIn('actions',s)
                for setting in SETTINGS:spec(setting,role,p,schema(role,c))
    def test_graph_has_exactly_same_facts_plus_derived_edges(self):
        c=cases()[0];p=trusted_contract(c)
        for flat,graph in [('FullFlatClean','FullGraphClean'),('SliceFlatClean','SliceGraphClean')]:
            f=payload('audit',c,flat,p);g=payload('audit',c,graph,p)
            edges=g.pop('dependency_index')['edges']
            self.assertEqual(f,g)
            self.assertEqual(edges,[[i,a['id']] for a in f['workflow']['actions'] for i in a['inputs']])
    def test_bad_authority_is_not_replaced_by_oracle(self):
        c=cases()[0];p=trusted_contract(c)
        for v in p.values():v['allow_rows']=True
        r=minimum_repair(c,p)
        self.assertEqual(r['count'],0)
        z=assess(c,r['edits'],p)
        self.assertTrue(z['unsafe_execution'])
        self.assertFalse(z['joint'])
    def test_malformed_edits_fail_closed(self):
        c=cases()[0]
        for edits in [[{'node':c['sinks'][0],'keep':[]}],[{'node':'madeup','keep':[]}],None]:
            self.assertFalse(assess(c,edits,trusted_contract(c))['valid'])
    def test_origin_and_content_are_distinct(self):
        c=cases()[0];a=analyze(c)
        node=next(n for n in c['actions'] if n['op']=='aggregate')
        field=a['states'][node['id']][node['output']]
        self.assertEqual(field['class'],'aggregate')
        self.assertEqual(field['origins'],['r0'])
    def test_full_graph_cost_includes_build(self):
        c=cases()[0];f=analyze(c);g=analyze(c,'graph')
        self.assertLess(g['query_visits'],f['query_visits'])
        self.assertGreater(g['total_work_units'],f['total_work_units'])
if __name__=='__main__':unittest.main()
