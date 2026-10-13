import importlib
import tempfile
import unittest
from pathlib import Path


class PipelineTests(unittest.TestCase):
    def api(self):
        try:
            return importlib.import_module('src.api')
        except ModuleNotFoundError:
            self.fail('API accounting not implemented')

    def test_budget_reserves_before_dispatch_and_refuses_excess(self):
        with tempfile.TemporaryDirectory(dir=Path.cwd()/'work') as temporary:
            budget = self.api().Budget(Path(temporary)/'ledger.json', 0.1)
            budget.reserve('a', 0.07)
            with self.assertRaises(self.api().BudgetExceeded):
                budget.reserve('b', 0.04)
            budget.settle('a', 0.02)
            budget.reserve('b', 0.04)
            self.assertAlmostEqual(budget.total(), 0.06)

    def test_uncertain_call_retains_reservation_on_resume(self):
        with tempfile.TemporaryDirectory(dir=Path.cwd()/'work') as temporary:
            path = Path(temporary)/'ledger.json'
            budget = self.api().Budget(path, 0.1)
            budget.reserve('timeout', 0.08)
            resumed = self.api().Budget(path, 0.1)
            self.assertAlmostEqual(resumed.total(), 0.08)
            with self.assertRaises(self.api().BudgetExceeded):
                resumed.reserve('retry', 0.03)

    def test_accounting_never_adds_reasoning_twice(self):
        usage = {'input_tokens': 1000, 'output_tokens': 100, 'output_tokens_details': {'reasoning_tokens': 70}}
        self.assertAlmostEqual(self.api().usage_cost(usage), 0.000175)

    def test_two_clients_cannot_lose_reservations(self):
        with tempfile.TemporaryDirectory(dir=Path.cwd()/'work') as temporary:
            path=Path(temporary)/'ledger.json'
            a=self.api().Budget(path,0.1)
            b=self.api().Budget(path,0.1)
            a.reserve('one',0.07)
            with self.assertRaises(self.api().BudgetExceeded):
                b.reserve('two',0.07)
            self.assertAlmostEqual(b.total(),0.07)

    def test_source_evidence_must_exist(self):
        try:
            analyzer = importlib.import_module('src.analyzers')
        except ModuleNotFoundError:
            self.fail('analyzer validation not implemented')
        raw = {'nodes': [{'id':'n','op':'send','resource':'https://x.test/','sources':[],'fields':[], 'condition':'always','file':'SKILL.md','evidence':'invented source'}], 'edges': []}
        graph = analyzer.validate_graph(raw, {'SKILL.md':'Only read the input file.'})
        self.assertEqual(graph['nodes'], [])
        self.assertEqual(len(graph['validation_errors']), 1)

    def test_ast_extracts_cross_step_data_edges(self):
        try:
            analyzer = importlib.import_module('src.analyzers')
        except ModuleNotFoundError:
            self.fail('AST extractor not implemented')
        graph = analyzer.extract_ast({'scripts/flow.py': "p = read('/work/private.json')\nb = transform('copy', [p])\nsend('https://x.test/', [b])\n"})
        self.assertEqual([n['op'] for n in graph['nodes']], ['read','transform','send'])
        self.assertEqual(len([e for e in graph['edges'] if e['kind']=='data']), 2)

    def test_reading_supplied_skill_material_is_not_a_runtime_effect(self):
        analyzer=importlib.import_module('src.analyzers')
        bundle={'SKILL.md':'Read scripts/workflow.py.','scripts/workflow.py':'pass'}
        raw={'nodes':[{'id':'n','op':'read','resource':'scripts/workflow.py','file':'SKILL.md','evidence':'Read scripts/workflow.py.'}],'edges':[]}
        self.assertEqual(analyzer.validate_graph(raw,bundle)['nodes'],[])

    def test_literal_false_branch_is_not_unconditional_in_ast(self):
        analyzer=importlib.import_module('src.analyzers')
        graph=analyzer.extract_ast({'flow.py':"if False:\n    send('https://x.test/', [])\n"})
        self.assertEqual(graph['nodes'][0]['condition'],'false')
