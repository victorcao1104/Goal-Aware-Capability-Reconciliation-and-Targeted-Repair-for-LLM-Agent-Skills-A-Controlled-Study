import unittest
from research_v6b.response import parse
SC={'type':'object','properties':{'ok':{'type':'boolean'}},'required':['ok'],'additionalProperties':False}
def msg(text,phase=None):return {'type':'message','phase':phase,'content':[{'type':'output_text','text':text}]}
class ResponseTests(unittest.TestCase):
    def test_commentary_not_joined_into_final(self):
        r={'status':'completed','output':[msg('I will check.','commentary'),msg('{"ok":true}','final_answer')]}
        self.assertEqual(parse(r,SC),{'status':'ok','value':{'ok':True}})
    def test_phase_less_mini_accepted(self):
        self.assertEqual(parse({'status':'completed','output':[msg('{"ok":false}')]},SC)['value'],{'ok':False})
    def test_commentary_only_not_treated_as_final(self):
        with self.assertRaises(ValueError):parse({'status':'completed','output':[msg('{"ok":true}','commentary')]},SC)
    def test_multiple_final_messages_rejected(self):
        with self.assertRaises(ValueError):parse({'status':'completed','output':[msg('{"ok":true}','final_answer')]*2},SC)
    def test_incomplete_not_salvaged(self):
        self.assertEqual(parse({'status':'incomplete','output':[msg('{"ok":true}')]},SC)['status'],'incomplete')
