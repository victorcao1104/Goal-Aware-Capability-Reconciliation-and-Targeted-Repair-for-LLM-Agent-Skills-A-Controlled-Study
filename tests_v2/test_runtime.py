import unittest
from research_v2.runtime import Runtime, Rejected
from research_v2.goals import public_loss

def action(op, out="", inputs=(), resource="", path="", field=""):
    return dict(op=op,out=out,inputs=list(inputs),resource=resource,path=path,field=field)

def config():
    return {"files":{"mixed":{"data":{"public":{"n":3},"private":{"token":"synthetic"}},
             "labels":{"/public":"public","/private":"private"}}},
            "policy":{"read":["mixed"],"sinks":{"approved":["public"]},"deny_labels":["private"]}}

class RuntimeTests(unittest.TestCase):
    def test_nested_projection_releases_only_selected_leaves(self):
        r=Runtime(config()); r.step(action("read","a",resource="mixed"))
        r.step(action("project","b",["a"],path="/public"))
        r.step(action("render","c",["b"])); r.step(action("send",inputs=["c"],resource="approved"))
        self.assertEqual(r.sends["approved"],'{"n":3}')
        self.assertEqual(r.handles["b"].sources,{"public"})
    def test_opaque_render_and_hash_do_not_launder(self):
        for op in ("render","hash"):
            r=Runtime(config()); r.step(action("read","a",resource="mixed"));r.step(action(op,"b",["a"]))
            with self.assertRaises(Rejected):r.step(action("send",inputs=["b"],resource="approved"))
            self.assertEqual(r.sends,{})
    def test_empty_private_container_keeps_taint(self):
        c=config();c["files"]["mixed"]["data"]["private"]={}
        r=Runtime(c);r.step(action("read","a",resource="mixed"));r.step(action("project","b",["a"],path="/private"))
        with self.assertRaises(Rejected):r.step(action("send",inputs=["b"],resource="approved"))
    def test_clone_does_not_mutate_original(self):
        r=Runtime(config());q=r.clone();q.step(action("read","a",resource="mixed"))
        self.assertFalse(r.handles);self.assertFalse(r.events)
    def test_unknown_transform_and_forged_literal_rejected(self):
        r=Runtime(config())
        for a in (action("exec","a"),dict(action("read","a",resource="mixed"),value="forged")):
            with self.assertRaises(Rejected):r.step(a)
    def test_conflicting_destination_contract_fails_closed(self):
        c=config();c["policy"]["deny_destinations"]=["approved"]
        with self.assertRaises(Rejected):Runtime(c)
    def test_shape_score_is_not_exact_output_oracle(self):
        r=Runtime(config());r.sends["approved"]="wrong"
        self.assertEqual(public_loss(r,[{"effect":"send","resource":"approved","type":"str"}]),0)
    def test_read_write_read_preserves_origins(self):
        c=config();c["policy"]["sinks"]["disk"]=["public","private"];c["policy"]["deny_labels"]=[]
        r=Runtime(c);r.step(action("read","a",resource="mixed"));r.step(action("write",inputs=["a"],resource="disk"))
        r.step(action("read_output","b",resource="disk"))
        with self.assertRaises(Rejected):r.step(action("send",inputs=["b"],resource="approved"))
    def test_operation_scope_is_not_just_destination_scope(self):
        c=config();c["policy"]["operations"]={"approved":["send"]}
        r=Runtime(c);r.step(action("read","a",resource="mixed"))
        r.step(action("project","b",["a"],path="/public"))
        with self.assertRaises(Rejected):r.step(action("write",inputs=["b"],resource="approved"))
    def test_list_projection_preserves_each_element(self):
        c=config();c["files"]["mixed"]={"data":[{"n":1},{"n":2}],"labels":{"/0":"public","/1":"private"}}
        r=Runtime(c);r.step(action("read","a",resource="mixed"));r.step(action("project","b",["a"],path="/0"))
        r.step(action("send",inputs=["b"],resource="approved"))
        self.assertEqual(r.sends["approved"],{"n":1})

if __name__=="__main__":unittest.main()

