import unittest
from research_v8.fixtures import tasks, variants, oracle
from research_v8.engine import reachable, execute, gate, certificate

class CoreTests(unittest.TestCase):
    def test_alternatives_and_concrete_witness(self):
        t=tasks('pilot')[0]; c=oracle(t)
        w=reachable(t,c['allowed'],c['goals'])
        self.assertIsNotNone(w['plan'])
        self.assertTrue(execute(t,w['plan'],c['goals']))
        self.assertIsNotNone(reachable(t,[a for a in c['allowed'] if a!='csv'],c['goals'])['plan'])
        self.assertIsNone(reachable(t,[a for a in c['allowed'] if a not in ('csv','pdf')],c['goals'])['plan'])
    def test_dependency_cannot_be_skipped(self):
        t=tasks('pilot')[1]; c=oracle(t)
        self.assertIsNone(reachable(t,[a for a in c['allowed'] if a!='backup'],c['goals'])['plan'])
        self.assertFalse(execute(t,['edit','publish'],c['goals']))
    def test_all_tasks_have_safe_alternative_and_attack_certificates(self):
        for stage in ('pilot','formal'):
            for t in tasks(stage):
                z=certificate(t)
                self.assertGreater(z['feasible_subsets'],0)
                self.assertTrue(z['valid_narrowing_feasible'])
                self.assertTrue(z['shutdown_impossible'])
                self.assertTrue(z['dependency_impossible'])
    def test_trusted_revocation_overrides_every_gate(self):
        from research_v8.engine import METHODS
        for t in tasks('pilot'):
            c=oracle(t)
            e=next(e for e in variants(t) if e['kind']=='trusted_cancel')
            for m in METHODS:
                self.assertEqual(gate(m,t,c,e,{'allowed':c['allowed'],'cancel':False}),{'allowed':[],'cancel':True,'accepted':True,'work':0})
    def test_fake_and_true_revocation_text_identical(self):
        vs={e['kind']:e for e in variants(tasks('pilot')[0])}
        self.assertEqual(vs['fake_cancel']['body'],vs['trusted_cancel']['body'])
        self.assertNotEqual(vs['fake_cancel']['source'],vs['trusted_cancel']['source'])
    def test_monotone_can_destroy_goal_without_expanding(self):
        t=tasks('pilot')[0]; c=oracle(t); e=variants(t)[1]
        bad={'allowed':['read'],'cancel':False}
        self.assertTrue(gate('Monotone',t,c,e,bad)['accepted'])
        self.assertFalse(gate('TaskPreserving',t,c,e,bad)['accepted'])
        self.assertFalse(gate('SourceLocked',t,c,e,bad)['accepted'])
    def test_alternative_narrowing_not_single_plan_lock(self):
        t=tasks('pilot')[0]; c=oracle(t)
        initial=reachable(t,c['allowed'],c['goals'])['plan']
        removed='csv' if 'csv' in initial else 'pdf'
        p={'allowed':[a for a in c['allowed'] if a!=removed],'cancel':False}
        self.assertTrue(gate('TaskPreserving',t,c,variants(t)[0],p)['accepted'])
        self.assertFalse(gate('SingleWitness',t,c,variants(t)[0],p)['accepted'])
    def test_goal_checker_cannot_fix_initial_undergrant(self):
        t=tasks('pilot')[0]; c={'allowed':['read'],'goals':oracle(t)['goals']}
        z=gate('TaskPreserving',t,c,variants(t)[0],{'allowed':['read','csv'],'cancel':False})
        self.assertEqual(z['allowed'],['read'])
    def test_counts_and_unknown_actions(self):
        t=tasks('pilot')[0]; c=oracle(t); t['max_steps']=1
        self.assertIsNone(reachable(t,c['allowed'],c['goals'])['plan'])
        self.assertFalse(execute(t,['invented'],c['goals']))

    def test_independent_concrete_enumeration_matches_all_policy_subsets(self):
        from itertools import permutations, combinations
        for stage in ('pilot','formal'):
            for t in tasks(stage):
                c=oracle(t);index={a['id']:a for a in t['actions']};valid=[]
                for length in range(min(t['max_steps'],len(c['allowed']))+1):
                    for sequence in permutations(c['allowed'],length):
                        state=list(t['initial']);ok=True
                        for aid in sequence:
                            a=index[aid]
                            if any(f not in state for f in a['requires']):ok=False;break
                            state.extend(a['adds'])
                        if ok and all(any(f in state for f in clause) for clause in c['goals']):
                            valid.append(set(sequence))
                for length in range(len(c['allowed'])+1):
                    for policy in combinations(c['allowed'],length):
                        truth=any(plan<=set(policy) for plan in valid)
                        self.assertEqual(reachable(t,policy,c['goals'])['plan'] is not None,truth)

if __name__=='__main__':unittest.main()

