import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from contextlib import nullcontext
from copy import deepcopy
from unittest.mock import patch
from research_v4.fixtures import make_cases
from research_v4.model import contract_payload,scan_payload,audit_payload
from research_v4.core import ground_scan,validate_contract
from research_v4.run import request_key,request,ensure_ledger,parse_args,fingerprint,request_spec,validate_request,committed

class PipelineTests(unittest.TestCase):
    def test_isolation_and_information_parity(self):
        c=make_cases()[1]
        self.assertEqual(set(contract_payload(c,'Isolated')),{'trusted_task','trusted_inventory','tool_semantics'})
        self.assertIn('untrusted_bundle',contract_payload(c,'Mixed'))
        scan=scan_payload(c);self.assertEqual(set(scan),{'untrusted_bundle','tool_semantics'})
        for payload in (scan,contract_payload(c,'Mixed')):
            self.assertNotIn('oracle',payload);self.assertNotIn('variant',payload)
        flat=audit_payload(c,{'rules':[]},{'actions':c['actions'],'unknowns':[],'errors':[]},'Flat')
        graph=audit_payload(c,{'rules':[]},{'actions':c['actions'],'unknowns':[],'errors':[]},'Graph');graph.pop('dependency_index')
        self.assertEqual(flat,graph)
    def test_component_identity_and_resume(self):
        cases=make_cases();clean,attack=cases[:2]
        self.assertEqual(request_key('contract',contract_payload(clean,'Isolated'),0),request_key('contract',contract_payload(attack,'Isolated'),0))
        self.assertNotEqual(request_key('contract',contract_payload(clean,'Mixed'),0),request_key('contract',contract_payload(attack,'Mixed'),0))
        root=Path(__file__).resolve().parents[1];(root/'work').mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=root/'work') as folder:
            payload={'task':'test'};key=request_key('contract',payload,0)
            path=Path(folder)/'requests';path.mkdir()
            fp=fingerprint('contract',payload,0)
            attempt={'id':fp+':0','status':'settled','reserved':0.01,'settled':0.001}
            record={'key':key,'role':'contract','repeat':0,'payload':payload,'fingerprint':fp,
                    'status':'ok','provider_status':'ok','value':{'rules':[]},'attempts':[attempt],'usage':{},'model':None}
            calls=Path(folder)/'private';calls.mkdir()
            private={'fingerprint':fp,'call_id':'v4:'+key,'request':request_spec('contract',payload),'status':'ok','value':{'rules':[]}}
            private_path=calls/(fp+'.json');private_path.write_text(json.dumps(private),encoding='utf-8')
            budget=SimpleNamespace(transaction=nullcontext,records={attempt['id']:{k:v for k,v in attempt.items() if k!='id'}})
            client=SimpleNamespace(calls=calls,budget=budget)
            public_path=path/(key+'.json');public_path.write_text(json.dumps(record),encoding='utf-8')
            with patch('research_v4.run.OUT',Path(folder)):
                self.assertEqual(request(client,'contract',payload,0),record)
                for field,value in [('key','bad'),('fingerprint','bad'),('status','test'),('value',{'invalid':True})]:
                    altered=deepcopy(record);altered[field]=value
                    with self.assertRaises(Exception):validate_request(altered,'contract',payload,0,client)
                private['value']={'rules':[{}]};private_path.write_text(json.dumps(private),encoding='utf-8')
                with self.assertRaises(RuntimeError):request(client,'contract',payload,0)
                # A refused call remains a failure through validated resume.
                private.update(status='model_refusal');private.pop('value')
                private_path.write_text(json.dumps(private),encoding='utf-8')
                failed={**record,'status':'ModelRefusal','provider_status':'model_refusal','value':{}}
                public_path.write_text(json.dumps(failed),encoding='utf-8')
                self.assertEqual(request(client,'contract',payload,0)['status'],'ModelRefusal')
                corrupted={**failed,'value':{'rules':[]}}
                with self.assertRaises(RuntimeError):validate_request(corrupted,'contract',payload,0,client)
                private['call_id']='wrong';private_path.write_text(json.dumps(private),encoding='utf-8')
                with self.assertRaises(RuntimeError):request(client,'contract',payload,0)
    def test_commit_guard_rejects_changed_frozen_bytes(self):
        root=Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory(dir=root/'work') as folder:
            out=Path(folder);(out/'freeze.json').write_bytes(b'{}')
            with patch('research_v4.run.OUT',out),patch('research_v4.run.subprocess.check_output',return_value=b'changed'):
                with self.assertRaises(RuntimeError):committed({'files':{}})
    def test_unsettled_or_understated_ledger_rejected(self):
        root=Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory(dir=root/'work') as folder:
            path=Path(folder)/'ledger.json'
            for data in ({'x':{'status':'pending','reserved':2}}, {'x':{'status':'settled','reserved':0,'settled':0}}):
                path.write_text(json.dumps(data),encoding='utf-8')
                with self.assertRaises(RuntimeError):ensure_ledger(path)
    def test_existing_cumulative_ledger_required(self):
        with self.assertRaises(RuntimeError):ensure_ledger(Path('does-not-exist-v4-ledger.json'))
    def test_freeze_and_live_are_exclusive(self):
        import io
        from contextlib import redirect_stderr
        with redirect_stderr(io.StringIO()),self.assertRaises(SystemExit):parse_args(['--freeze','--live'])

if __name__=='__main__':unittest.main()
