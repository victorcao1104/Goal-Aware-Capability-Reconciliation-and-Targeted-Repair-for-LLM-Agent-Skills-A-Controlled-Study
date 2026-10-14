import copy
import unittest
from research_v4.fixtures import make_cases
from research_v4.core import ground_scan,validate_audit
from research_v4.analysis import paired,summarize


class IntegrityTests(unittest.TestCase):
    def test_omitted_forbidden_action_cannot_be_allowed(self):
        case=make_cases()[1]
        raw={'actions':[{'id':a['id'],'evidence':a['evidence']} for a in case['actions'][:-1]],'unknowns':[]}
        scan=ground_scan(raw,case['bundle'])
        self.assertEqual(scan['omitted_ids'],[case['actions'][-1]['id']])
        self.assertEqual(len(scan['actions']),len(case['actions'])-1)
        audit=validate_audit({'decision':'allow','findings':[]},case['task'],scan)
        self.assertEqual(audit['decision'],'uncertain')

    def test_paired_denominators_retain_missing_values(self):
        base={'case_id':'c','repeat':0,'family':'f','variant':'attack'}
        rows=[{**base,'method':'a','score':True},{**base,'method':'b','score':None}]
        result=paired(rows,'score','a','b')
        self.assertEqual(result['eligible_pairs'],1)
        self.assertEqual(result['missing_value_pairs'],1)
        self.assertEqual(result['n'],0)
        self.assertEqual(result['family_counts']['f']['missing_values'],1)
        self.assertEqual(result['observed_families'],0)

    def test_runtime_audit_metric_is_not_applicable(self):
        row={'case_id':'c','repeat':0,'family':'f','variant':'clean','method':'TaskRuntime',
             'pipeline_ok':True,'audit_correct':None,'decision':'allow','components':['x'],
             'execution':{'unauthorized_effects':0,'unresolved_effects':0,'required_effects_complete':True}}
        result=summarize([row],[])['methods']['TaskRuntime']
        self.assertEqual(result['audit_n'],0)
        self.assertIsNone(result['audit_accuracy'])
        self.assertEqual(result['audit_not_applicable'],1)
