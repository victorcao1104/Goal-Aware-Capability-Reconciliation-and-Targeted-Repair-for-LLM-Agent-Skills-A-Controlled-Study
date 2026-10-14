import unittest
from copy import deepcopy
import jsonschema
from research_v5.fixtures import make_cases
from research_v5.core import scan_records, check_audit
from research_v5.model import payload_policy,payload_scan,payload_audit,SCHEMAS,LIMITS
from research_v5.run import request_key,validate_record,request_spec,fingerprint,evaluate_case
class BoundaryTests(unittest.TestCase):
    def setUp(self):self.case=make_cases()[0]
    def test_isolation_and_only_prose_changes_mixed(self):
        c=self.case;n=make_cases()[1]
        self.assertEqual(payload_policy(c,'Isolated'),payload_policy(n,'Isolated'))
        self.assertNotEqual(payload_policy(c,'Mixed'),payload_policy(n,'Mixed'))
        self.assertNotIn('task',payload_scan(c))
        for p in (payload_scan(c),payload_policy(c,'Mixed')):
            self.assertNotIn('oracle',str(p))
    def test_graph_is_only_a_derived_index(self):
        c=self.case;s=scan_records(c,{'action_ids':[a['id'] for a in c['actions']],'unknowns':[]})
        f=payload_audit(c,c['oracle']['policy'],s,'Flat')
        g=payload_audit(c,c['oracle']['policy'],s,'Graph')
        del g['dependency_index'];self.assertEqual(f,g)
        self.assertEqual(set(LIMITS.values()),{2500})
    def test_schema_prevents_free_text_ids(self):
        q={'decision':'block','findings':[{'action':'upload the report','path':[],'clauses':['T0'],'reason':'bad'}]}
        with self.assertRaises(jsonschema.ValidationError):jsonschema.validate(q,SCHEMAS['audit'])
    def test_omitted_scanner_action_is_not_reinserted(self):
        c=self.case;s=scan_records(c,{'action_ids':['input'],'unknowns':[]})
        self.assertEqual(len(s['actions']),1);self.assertIn('leak',s['omitted_ids'])
        self.assertEqual(check_audit({'decision':'allow','findings':[]},c,s)['decision'],'uncertain')
    def test_request_keys_include_repeat_and_role(self):
        p=payload_policy(self.case,'Mixed')
        self.assertNotEqual(request_key('policy',p,0),request_key('policy',p,1))
        self.assertNotEqual(request_key('policy',p,0),request_key('update',p,0))
    def test_record_tampering_detected(self):
        p=payload_policy(self.case,'Mixed');fp=fingerprint('policy',p,0)
        r={'key':request_key('policy',p,0),'role':'policy','repeat':0,'payload':p,'fingerprint':fp,
           'status':'ok','provider_status':'ok','value':{'policy':self.case['oracle']['policy']},
           'attempts':[{'id':fp+':0','status':'settled','reserved':0.01,'settled':0.001}],
           'usage':{'input_tokens':100,'output_tokens':10},'model':'gpt-6-luna'}
        validate_record(r,'policy',p,0)
        r['payload']=dict(p,extra='tamper')
        with self.assertRaises(RuntimeError):validate_record(r,'policy',p,0)
    def test_failed_policy_never_counts_as_correct(self):
        def get(role,payload,repeat):
            return {'key':role,'status':'ModelRefusal','value':{}}
        rows=evaluate_case(self.case,0,get)
        self.assertTrue(all(not r['pipeline_ok'] for r in rows))
        self.assertTrue(all(not r.get('audit_correct',False) for r in rows))
        self.assertTrue(all(not r['execution']['required_complete'] for r in rows))
if __name__=='__main__':unittest.main()
