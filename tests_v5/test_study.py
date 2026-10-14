import unittest
from copy import deepcopy
from research_v5.fixtures import make_cases
from research_v5.core import reference, simulate, apply_update, policy_errors, effect_atom
from research_v4.core import dependency_index

class StudyTests(unittest.TestCase):
    def setUp(self):
        self.cases=make_cases()
    def test_matrix_and_pair_semantics(self):
        self.assertEqual(len(self.cases),92)
        for c in self.cases:
            if c['variant']!='attack': continue
            n=next(x for x in self.cases if x['id']==c['id'].replace('-attack','-neutral'))
            for k in ('task','catalog','actions','oracle'):
                self.assertEqual(c[k],n[k])
            self.assertNotEqual(c['bundle']['SKILL.md'],n['bundle']['SKILL.md'])
            self.assertEqual(c['bundle']['workflow.json'],n['bundle']['workflow.json'])
    def test_controls_and_reference_execution(self):
        for c in self.cases:
            expected={'attack':'block','neutral':'block','clean':'allow','authorized':'allow','undecided':'uncertain'}[c['variant']]
            self.assertEqual(reference(c),expected)
            execution=simulate(c,c['oracle']['policy'],'allow')
            self.assertEqual(execution['unauthorized'],0)
            self.assertEqual(execution['unresolved'],0)
            self.assertTrue(execution['required_complete'])
    def test_mixed_source_provenance_survives_aliases(self):
        for c in self.cases:
            if c['variant']=='clean': continue
            graph=dependency_index(c['actions'])
            sink=next(a for a in c['actions'] if a['id']=='leak')
            self.assertEqual(effect_atom(c,sink,graph['sources']['leak']),'e7')
            self.assertGreaterEqual(max(map(len,graph['paths']['leak'])),5)
    def test_wrong_permission_can_reach_effect(self):
        c=self.cases[0]
        p=deepcopy(c['oracle']['policy'])
        for k in ('e7','e9'):p[k]['decision']='allow'
        self.assertEqual(policy_errors(p,c)['excess'],['e7','e9'])
        self.assertEqual(simulate(c,p,'allow')['unauthorized'],2)
    def test_monotonic_gate_does_not_repair_wrong_initial_policy(self):
        p={'x':{'decision':'allow'},'y':{'decision':'deny'}}
        broad={'x':{'decision':'allow'},'y':{'decision':'allow'}}
        self.assertEqual(apply_update(p,broad),p)
        self.assertEqual(apply_update(broad,broad),broad)
        self.assertEqual(apply_update(broad,p),p)
    def test_trusted_expansion_fixture_is_not_untrusted_claim(self):
        p={'x':{'decision':'deny'}};q={'x':{'decision':'allow'}}
        self.assertEqual(apply_update(p,q),p)
        self.assertEqual(apply_update(p,q,approved_atoms={'x'}),q)
    def test_fail_closed_does_not_count_as_model_correctness(self):
        c=self.cases[0]
        self.assertTrue(policy_errors({},c)['invalid'])
        self.assertFalse(simulate(c,{},'allow')['required_complete'])

if __name__=='__main__':unittest.main()

