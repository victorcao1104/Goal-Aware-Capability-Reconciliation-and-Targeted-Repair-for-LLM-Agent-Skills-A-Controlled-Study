import unittest
from src.dataset import make_controls
from src.analyzers import extract_ast
from scripts.report import contract_components, graph_components


class ReportTests(unittest.TestCase):
    def test_declared_contract_matches_fixed_atoms(self):
        case=make_controls()[0]
        result=contract_components(case,case['reference_contract'])
        self.assertTrue(result['exact_authorization_set'])
        self.assertEqual(result['f1'],1)

    def test_graph_data_edges_compared_to_actual_closed_tool_trace(self):
        case=next(c for c in make_controls() if c['mechanism']=='intermediate' and c['variant']=='injected')
        graph=extract_ast(case['bundle'])
        result=graph_components(case,graph)
        self.assertEqual(result['data_edges']['f1'],1)
        graph['edges']=[]
        self.assertEqual(graph_components(case,graph)['data_edges']['recall'],0)
