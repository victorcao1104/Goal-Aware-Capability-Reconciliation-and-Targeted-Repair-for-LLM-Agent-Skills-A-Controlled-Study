import importlib
import unittest
from src.dataset import make_controls
from src.analyzers import extract_ast


class RunnerTests(unittest.TestCase):
    def runner(self):
        try:
            return importlib.import_module('src.runner')
        except ModuleNotFoundError:
            self.fail('experiment runner not implemented')

    def analysis(self, case):
        return {'contract':case['reference_contract'], 'graph':extract_ast(case['bundle']), 'scanner':{'risk':True}}

    def test_baseline_b0_is_not_accidentally_enforced(self):
        case=make_controls()[1]
        config=self.runner().method_config('B0',self.analysis(case))
        self.assertEqual(config['policy'],{})
        self.assertEqual(config['runtime_method'],'B0')

    def test_b4_blocks_skill_b5_selects_specific_restrictions(self):
        case=next(c for c in make_controls() if c['mechanism']=='bundle' and c['variant']=='injected')
        b4=self.runner().method_config('B4',self.analysis(case))
        b5=self.runner().method_config('B5',self.analysis(case))
        self.assertTrue(b4['policy']['block_all'])
        self.assertTrue(b5['policy']['targeted'])
        self.assertFalse(b5['policy'].get('block_all',False))

    def test_no_goal_does_not_enable_unsolicited_repair(self):
        case=make_controls()[0]
        config=self.runner().method_config('B5',self.analysis(case))
        self.assertFalse(config['policy']['targeted'])

    def test_task_only_repair_requires_no_graph(self):
        case=make_controls()[0]
        analysis={'contract':case['reference_contract']}
        config=self.runner().method_config('B2R',analysis)
        self.assertTrue(config['policy']['targeted'])
        self.assertEqual(config['runtime_method'],'B5')

    def test_refusal_remains_a_valid_failed_task_with_observable_state(self):
        import tempfile
        from pathlib import Path
        from src.api import ModelRefusal
        class RefusingClient:
            def generate(self,*args,**kwargs):
                raise ModelRefusal('retained-api-fingerprint')
        case=make_controls()[0]
        analysis=self.analysis(case)
        analysis.update(input_fingerprint='test',seconds=0)
        with tempfile.TemporaryDirectory(dir=Path.cwd()/'work') as directory:
            result=self.runner().run_case(RefusingClient(),Path(directory),case,analysis,'B0',0,container=False)
        self.assertEqual(result['model_outcome'],'refusal')
        self.assertEqual(result['evaluation']['status'],'valid')
        self.assertFalse(result['evaluation']['task_success'])
        self.assertFalse(result['evaluation']['attack_success'])
