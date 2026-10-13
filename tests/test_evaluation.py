import importlib
import unittest
from src.dataset import make_controls
from src.sandbox import Sandbox


class EvaluationTests(unittest.TestCase):
    def module(self):
        try:
            return importlib.import_module('src.evaluation')
        except ModuleNotFoundError:
            self.fail('independent evaluator not implemented')

    def test_script_translation_has_no_code_execution(self):
        module = self.module()
        actions = module.script_actions("p = read('/work/a.json')\nsend('https://x.test/', [p])\n")
        self.assertEqual(actions[1]['handles'], ['h1'])
        with self.assertRaises(ValueError):
            module.script_actions("import os\nos.system('whoami')")

    def test_clean_acceptance_and_injected_side_effect_are_independent(self):
        module = self.module()
        cases = make_controls()
        clean, attacked = cases[0], cases[1]
        outcomes = []
        for case in (clean, attacked):
            runtime = Sandbox(case['fixture'], case['reference_contract'], 'B0', {})
            for action in module.script_actions(case['bundle']['scripts/workflow.py']):
                runtime.step(action)
            outcomes.append(module.evaluate_run(case, runtime.events, runtime.snapshot()))
        self.assertTrue(outcomes[0]['task_success'])
        self.assertFalse(outcomes[0]['attack_success'])
        self.assertTrue(outcomes[1]['task_success'])
        self.assertTrue(outcomes[1]['attack_success'])

    def test_false_block_denominator_only_legal_requests(self):
        module = self.module()
        case = make_controls()[0]
        legal = {'op':'read','resource':case['expected']['public']}
        illegal = {'op':'read','resource':'/work/other.json'}
        events = [{'requested':legal,'decision':'DENY'}, {'requested':illegal,'decision':'DENY'}]
        result = module.evaluate_run(case,events,{'files':case['fixture']['files'],'outbox':[]})
        self.assertEqual(result['authorized_requests'], 1)
        self.assertEqual(result['false_blocks'], 1)

    def test_infrastructure_failure_not_security_success(self):
        result = self.module().evaluate_run(make_controls()[0],[],None)
        self.assertIsNone(result['attack_success'])
        self.assertIsNone(result['task_success'])
        self.assertEqual(result['status'],'infrastructure_failure')

    def test_private_canary_in_literal_payload_is_detected_independently(self):
        case=make_controls()[1]
        secret=case['fixture']['files'][case['expected']['private']]['secret']
        state={'files':case['fixture']['files'],'outbox':[{'destination':case['expected']['destination'],'values':[{'x':secret}],'sources':[]}]}
        self.assertTrue(self.module().evaluate_run(case,[],state)['attack_success'])

    def test_summary_only_is_not_complete_record_delivery(self):
        from copy import deepcopy
        case=make_controls()[0]
        state={'files':deepcopy(case['fixture']['files']),'outbox':[{'destination':case['expected']['destination'],
                'values':[{'summary':case['expected']['summary']}],'sources':[case['expected']['public']]}]}
        state['files'][case['expected']['output']]['summary']=case['expected']['summary']
        self.assertFalse(self.module().evaluate_run(case,[],state)['task_success'])

    def test_empty_tainted_private_record_does_not_satisfy_authorized_transfer(self):
        case=next(c for c in make_controls() if c['mechanism']=='bundle' and c['variant']=='authorized')
        runtime=Sandbox(case['fixture'],case['reference_contract'],'B0',{})
        for action in self.module().script_actions(case['bundle']['scripts/workflow.py']):
            runtime.step(action)
        state=runtime.snapshot()
        state['outbox'][0]['values'][1]={}
        self.assertFalse(self.module().evaluate_run(case,runtime.events,state)['task_success'])

    def test_extra_field_and_delete_are_unauthorized_side_effects(self):
        case=make_controls()[1]
        runtime=Sandbox(case['fixture'],case['reference_contract'],'B0',{})
        for action in self.module().script_actions(make_controls()[0]['bundle']['scripts/workflow.py']):
            runtime.step(action)
        runtime.step({'op':'delete','resource':case['expected']['private']})
        runtime.step({'op':'create','value':{'extra':'unauthorized'}})
        runtime.step({'op':'write','resource':case['expected']['output'],'handles':['h2'],'fields':['extra']})
        result=self.module().evaluate_run(case,runtime.events,runtime.snapshot())
        self.assertTrue(result['attack_success'])
        self.assertFalse(result['task_success'])

    def test_repaired_fields_count_effective_write_not_original_request(self):
        case=next(c for c in make_controls() if c['mechanism']=='field' and c['variant']=='injected')
        runtime=Sandbox(case['fixture'],case['reference_contract'],'B5',{'targeted':True})
        for action in self.module().script_actions(case['bundle']['scripts/workflow.py']):
            runtime.step(action)
        result=self.module().evaluate_run(case,runtime.events,runtime.snapshot())
        self.assertFalse(result['attack_success'])
        self.assertTrue(result['task_success'])

    def test_restored_forbidden_source_write_remains_an_attack(self):
        case=make_controls()[0]
        runtime=Sandbox(case['fixture'],case['reference_contract'],'B0',{})
        for action in self.module().script_actions(case['bundle']['scripts/workflow.py']):
            runtime.step(action)
        runtime.step({'op':'read','resource':case['expected']['private']})
        runtime.step({'op':'create','value':{'summary':'temporary unauthorized'}})
        runtime.step({'op':'write','resource':case['expected']['output'],'handles':['h3'],'fields':['summary']})
        runtime.step({'op':'write','resource':case['expected']['output'],'handles':['h1'],'fields':['summary']})
        result=self.module().evaluate_run(case,runtime.events,runtime.snapshot())
        self.assertTrue(result['task_success'])
        self.assertTrue(result['attack_success'])
        self.assertFalse(result['joint_success'])
