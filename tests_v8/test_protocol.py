import copy
import unittest
from research_v8.fixtures import tasks,variants,oracle
from research_v8.model import payload,schema,spec,request_cost_bound,SETTINGS
from research_v8.run import gate_decision,evaluate_task,preparation
from research_v8.api import validate_record
from research_v8.analysis import cluster_interval, contrasts

class ProtocolTests(unittest.TestCase):
    def test_cluster_interval_keeps_family_as_unit(self):
        z=cluster_interval([0.5]*6)
        self.assertEqual(z,{'mean':0.5,'low':0.5,'high':0.5,'families':6})
        z=cluster_interval([-1,1])
        self.assertEqual((z['low'],z['high']),(-1,1))
    def test_paired_contrast_preserves_repeats_within_family(self):
        rows=[]
        for t in ('a','b'):
            for m in ('Fixed','TaskPreserving'):
                rows.append(dict(task=t,repeat=0,setting='mini',cohort='oracle',method=m,event='neutral',
                    score=dict(safe_feasible=m=='TaskPreserving',valid_narrowing=False)))
        first=contrasts(rows)
        doubled=rows+[dict(r,repeat=1) for r in rows]
        self.assertEqual(first,contrasts(doubled))
    def test_extractor_never_sees_skill_or_truth(self):
        t=tasks('pilot')[0];p=payload('contract',t)
        self.assertEqual(set(p),{'trusted_task','catalogue'})
        self.assertNotIn('gold_',str(p))
        self.assertNotIn('suggested_allowed',str(p))
    def test_updater_sees_source_but_not_event_label(self):
        t=tasks('pilot')[0]
        p=payload('update',t,oracle(t),variants(t)[1])
        self.assertNotIn('kind',p['event'])
        self.assertEqual(p['event']['source'],'skill')
        self.assertNotIn('gold_',str(p))

    def test_scoring_grants_cannot_leak_into_update_events(self):
        t=tasks('pilot')[0];c=oracle(t)
        before=[payload('update',t,c,e) for e in variants(t)]
        t['gold_allowed']=['private_export']
        after=[payload('update',t,c,e) for e in variants(t)]
        self.assertEqual(before,after)
    def test_budgets_preflight_all_cases(self):
        z=preparation()
        self.assertLessEqual(z['pilot_bound'],1)
        self.assertLessEqual(z['formal_bound'],5)
    def test_gate_requires_two_distinct_families_same_model(self):
        rows=[]
        for task in ('a','b'):
            for kind in ('neutral','security_shutdown'):
                rows.append(dict(task=task,setting='mini',cohort='oracle',method='LLM',
                    event=kind,repeat=0,status='ok',
                    score=dict(feasible=kind=='neutral',nonexpanding=True,initial_feasible=True)))
        self.assertTrue(gate_decision(rows)['proceed'])
        rows=[r for r in rows if r['task']=='a']
        self.assertFalse(gate_decision(rows+copy.deepcopy(rows))['proceed'])
    def test_parsing_failure_not_a_success(self):
        t=tasks('pilot')[0]
        def get(stage,setting,role,p,sc,repeat=0):
            return dict(key='test',status='invalid_response',value={})
        rows=evaluate_task('pilot',t,0,'mini',get)
        for r in rows:
            if r['method']=='LLM':
                self.assertFalse(r['score']['safe_feasible'])
    def test_real_source_and_replayed_fake_different_requests(self):
        t=tasks('pilot')[0];c=oracle(t)
        vs={v['kind']:v for v in variants(t)}
        self.assertNotEqual(spec('mini','update',payload('update',t,c,vs['fake_cancel']),schema('update',t)),
                            spec('mini','update',payload('update',t,c,vs['trusted_cancel']),schema('update',t)))
if __name__=='__main__':unittest.main()

