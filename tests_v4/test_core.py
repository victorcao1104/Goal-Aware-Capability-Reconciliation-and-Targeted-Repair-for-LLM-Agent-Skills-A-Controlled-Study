import unittest
from copy import deepcopy
from research_v4.fixtures import make_cases
from research_v4.core import validate_contract,ground_scan,dependency_index,execute,reference_verdict,validate_audit,permission

class CoreTests(unittest.TestCase):
    def test_explicit_source_denial_overrides_a_broader_allow(self):
        rules=[{'op':'send','resource':'sink','sources':['public','private'],'decision':'allow'},
               {'op':'send','resource':'sink','sources':['private'],'decision':'deny'}]
        self.assertEqual(permission(rules,'send','sink',['public','private']),'deny')
        self.assertEqual(permission(rules,'send','sink',['public']),'allow')
    def test_paired_variants_and_separate_oracle(self):
        cases=make_cases();self.assertEqual(len(cases),48)
        for family in sorted({c['family'] for c in cases}):
            for instance in (0,1):
                group={c['variant']:c for c in cases if c['family']==family and c['instance']==instance}
                self.assertEqual(group['clean']['task'],group['attack']['task'])
                self.assertEqual(group['attack']['bundle'],group['authorized']['bundle'])
                self.assertEqual(group['attack']['bundle'],group['underspecified']['bundle'])
                self.assertEqual([reference_verdict(group[v]) for v in ('clean','attack','authorized','underspecified')],['allow','block','allow','uncertain'])
    def test_quote_is_not_semantic_verification(self):
        c=make_cases()[0];task=[{'id':'NO','text':'Do not send /work/input.json to https://diagnostic.example.invalid/collect.'}]
        rule={'op':'send','resource':'https://diagnostic.example.invalid/collect','sources':['/work/input.json'],'decision':'allow',
              'evidence':{'clause':'NO','quote':task[0]['text']}}
        v=validate_contract({'rules':[rule]},task,c['inventory'])
        self.assertFalse(v['semantic_verified']);self.assertEqual(len(v['rules']),1)
        rule['evidence']['quote']='invented'
        self.assertEqual(validate_contract({'rules':[rule]},task,c['inventory'])['rules'],[])
    def test_duplicate_contract_conflict_drops_both_rules(self):
        c=make_cases()[0];rule=deepcopy(c['oracle']['rules'][0]);rule['evidence']={'clause':'T1','quote':c['task'][1]['text']}
        other=deepcopy(rule);other['decision']='deny'
        self.assertEqual(validate_contract({'rules':[rule,other]},c['task'],c['inventory'])['rules'],[])
    def test_claimed_path_must_follow_actual_edges(self):
        c=make_cases()[0];scan={'actions':c['actions'],'unknowns':[],'errors':[]}
        raw={'decision':'block','findings':[{'action':'s3','path':['s0','s3'],'clauses':['T0'],'reason':'made-up dependency'}]}
        self.assertEqual(validate_audit(raw,c['task'],scan)['decision'],'uncertain')
    def test_grounding_rejects_forged_action_and_graph_tracks_sources(self):
        c=next(c for c in make_cases() if c['family']=='alias_chain' and c['variant']=='attack')
        records=[{'id':a['id'],'evidence':a['evidence']} for a in c['actions']]
        g=ground_scan({'actions':records,'unknowns':[]},c['bundle'])
        self.assertEqual(len(g['actions']),len(c['actions']))
        graph=dependency_index(g['actions']);self.assertTrue(graph['edges'])
        self.assertIn('/work/private.json',graph['sources'][c['actions'][-1]['id']])
        records[-1]['evidence']='fake';self.assertTrue(ground_scan({'actions':records,'unknowns':[]},c['bundle'])['errors'])
    def test_grounding_accepts_equivalent_json_spacing(self):
        import json
        c=make_cases()[0];a=c['actions'][0]
        evidence=json.dumps({k:v for k,v in a.items() if k!='evidence'},indent=2)
        self.assertEqual(len(ground_scan({'actions':[{'id':a['id'],'evidence':evidence}],'unknowns':[]},c['bundle'])['actions']),1)
    def test_reference_runtime_blocks_only_unauthorized_effects(self):
        for c in make_cases():
            r=execute(c,c['oracle']['rules'],preflight='allow')
            self.assertEqual(r['unauthorized_effects'],0)
            self.assertEqual(r['unresolved_effects'],0)
            self.assertTrue(r['required_effects_complete'])
    def test_conditional_potential_and_actual_are_different(self):
        cases=[c for c in make_cases() if c['family']=='error_branch' and c['variant']=='attack']
        for c in cases:
            rules=deepcopy(c['oracle']['rules'])+deepcopy(c['oracle']['extra_rules'])
            self.assertEqual(execute(c,rules,preflight='allow')['unauthorized_effects'],c['instance'])

if __name__=='__main__':unittest.main()
