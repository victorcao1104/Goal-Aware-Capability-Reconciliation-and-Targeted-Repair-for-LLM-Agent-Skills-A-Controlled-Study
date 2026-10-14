import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import urllib.error
from research_v7 import api
from research_v7.fixtures import cases
from research_v7.model import payload,schema
from research_v7.engine import trusted_contract
class Response:
    def __init__(self,data):self.data=json.dumps(data).encode()
    def __enter__(self):return self
    def __exit__(self,*args):pass
    def read(self,*args):return self.data

class AccountingTests(unittest.TestCase):
    def setup_root(self,d):
        root=Path(d);ledger=root/'results/raw_runs/budget-ledger.json';ledger.parent.mkdir(parents=True)
        ledger.write_text(json.dumps({'prior':{'reserved':api.PRIOR,'settled':api.PRIOR,'status':'settled'}}))
        (root/'.env.local').write_text('OPENAI_API_KEY=not-real-test-credential\n')
        return root
    def test_model_specific_charge_cache_and_no_credential_export(self):
        scratch=api.ROOT.parent/'v7-test-scratch';scratch.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=scratch) as d:
            root=self.setup_root(d);c=cases()[1]
            response={'model':'gpt-4.1-mini','status':'completed','usage':{'input_tokens':100,'output_tokens':50},
                      'output':[{'content':[{'type':'output_text','text':json.dumps({'policy':trusted_contract(c)})}]}]}
            with patch.object(api,'ROOT',root),patch.object(api,'OUT',root/'public'),patch('urllib.request.urlopen',return_value=Response(response)) as net:
                client=api.Client();args=('calibration','mini','policy',payload('policy',c),schema('policy',c),0)
                a=client.get(*args);b=client.get(*args)
                self.assertEqual(a,b);self.assertEqual(net.call_count,1)
                self.assertAlmostEqual(a['accounted_usd'],.00012)
                self.assertAlmostEqual(client.budget.total(),api.PRIOR+.00012)
                self.assertNotIn('not-real-test-credential',json.dumps(a))
                self.assertEqual(api.offline_get(*args),a)
    def test_unknown_network_charge_is_retained_at_upper_bound(self):
        scratch=api.ROOT.parent/'v7-test-scratch';scratch.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=scratch) as d:
            root=self.setup_root(d);c=cases()[1]
            with patch.object(api,'ROOT',root),patch.object(api,'OUT',root/'public'),patch('urllib.request.urlopen',side_effect=urllib.error.URLError('test')):
                client=api.Client();q=client.get('calibration','mini','policy',payload('policy',c),schema('policy',c))
                self.assertEqual(q['status'],'transport_error')
                self.assertEqual(q['accounted_usd'],q['reserved_usd'])
                self.assertEqual(q['accounting_basis'],'reserved_upper_bound_unknown_charge')
                self.assertAlmostEqual(client.budget.total(),api.PRIOR+q['reserved_usd'])
if __name__=='__main__':unittest.main()
