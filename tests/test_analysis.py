import importlib
import unittest


class AnalysisTests(unittest.TestCase):
    def module(self):
        try:
            return importlib.import_module('src.analysis')
        except ModuleNotFoundError:
            self.fail('statistical aggregation not implemented')

    def row(self, family, variant, attack, task, status='valid'):
        return {'family':family,'variant':variant,'evaluation':{'status':status,'attack_success':attack,'task_success':task,
                'joint_success':bool(task and not attack),'false_blocks':0,'authorized_requests':3},'seconds':1}

    def test_asr_excludes_clean_and_failed_runs(self):
        rows=[self.row('a','injected',True,True),self.row('b','unauthorized',False,True),self.row('c','clean',False,True),
              self.row('d','injected',None,None,'infrastructure_failure')]
        metrics=self.module().summarize(rows)
        self.assertEqual(metrics['attack_n'],2)
        self.assertEqual(metrics['asr'],0.5)
        self.assertEqual(metrics['invalid_runs'],1)
        self.assertEqual(metrics['benign_tsr'],1.0)

    def test_all_failures_produce_missing_rate_not_zero(self):
        metrics=self.module().summarize([self.row('a','injected',None,None,'infrastructure_failure')])
        self.assertIsNone(metrics['asr'])
        self.assertIsNone(metrics['tsr'])

    def test_confusion_counts_use_fixed_reference_universe(self):
        metrics=self.module().classification([True,True,False,False],[True,False,True,False])
        self.assertEqual((metrics['tp'],metrics['fp'],metrics['fn'],metrics['tn']),(1,1,1,1))
        self.assertEqual(metrics['f1'],0.5)

    def test_missing_and_duplicate_runs_are_detected(self):
        result=self.module().audit_jobs(['a','b'],['a','a'])
        self.assertEqual(result['missing'],['b'])
        self.assertEqual(result['duplicates'],['a'])
