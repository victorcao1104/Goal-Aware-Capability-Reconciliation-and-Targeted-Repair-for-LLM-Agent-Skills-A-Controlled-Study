import unittest
import importlib


class CoreTests(unittest.TestCase):
    def core(self, module):
        try:
            return importlib.import_module('src.' + module)
        except ModuleNotFoundError:
            self.fail('Required core module is not implemented: ' + module)

    def contract(self):
        return {'permissions': [
            {'op': 'read', 'resource': '/work/public.json', 'status': 'REQUIRED', 'sources': [], 'fields': []},
            {'op': 'read', 'resource': '/work/private.json', 'status': 'PERMITTED', 'sources': [], 'fields': []},
            {'op': 'write', 'resource': '/work/result.json', 'status': 'REQUIRED', 'sources': ['/work/public.json'], 'fields': ['summary']},
            {'op': 'send', 'resource': 'https://company.test/upload', 'status': 'PERMITTED', 'sources': ['/work/public.json'], 'fields': []},
        ]}

    def test_canonical_path_and_url_are_exact(self):
        normalize = self.core('contracts').normalize_resource
        self.assertEqual(normalize('./public.json'), '/work/public.json')
        self.assertEqual(normalize('https://COMPANY.test:443/upload'), 'https://company.test/upload')
        for path in ('../secret', '/etc/passwd', '/work/../../etc', 'file:///etc/passwd'):
            with self.assertRaises(ValueError, msg=path):
                normalize(path)

    def test_host_suffix_and_wildcard_do_not_grant(self):
        match = self.core('contracts').match_action
        for dest in ('https://company.test.evil.test/upload', 'https://company.test/upload/extra'):
            self.assertEqual(match(self.contract(), {'op': 'send', 'resource': dest, 'sources': ['/work/public.json']}, True), 'EXCESS')
        ambiguous = {'permissions': [{'op': 'read', 'resource': '*', 'status': 'UNRESOLVED'}]}
        self.assertNotEqual(match(ambiguous, {'op': 'read', 'resource': '/work/public.json'}, True), 'MATCHED')

    def test_same_endpoint_different_data_scope(self):
        match = self.core('contracts').match_action
        action = {'op': 'send', 'resource': 'https://company.test/upload', 'sources': ['/work/private.json']}
        self.assertEqual(match(self.contract(), action, False), 'MATCHED')
        self.assertEqual(match(self.contract(), action, True), 'EXCESS')

    def test_data_provenance_propagates_across_intermediate(self):
        graph = {'nodes': [
            {'id': 'a', 'op': 'read', 'resource': '/work/private.json', 'sources': [], 'condition': 'always'},
            {'id': 'b', 'op': 'transform', 'resource': 'concat', 'sources': [], 'condition': 'always'},
            {'id': 'c', 'op': 'send', 'resource': 'https://company.test/upload', 'sources': [], 'condition': 'always'},
        ], 'edges': [{'source': 'a', 'target': 'b', 'kind': 'data'}, {'source': 'b', 'target': 'c', 'kind': 'data'}]}
        goals = self.core('graph').find_goals(self.contract(), graph)
        self.assertEqual([(g['goal'], g['sink']) for g in goals], [('G1', 'c')])
        self.assertEqual(goals[0]['path'], ['a', 'b', 'c'])
        graph['nodes'][2]['condition'] = 'false'
        self.assertEqual(self.core('graph').find_goals(self.contract(), graph), [])

    def test_control_edge_alone_does_not_invent_dataflow(self):
        graph = {'nodes': [
            {'id': 'a', 'op': 'read', 'resource': '/work/private.json'},
            {'id': 'b', 'op': 'send', 'resource': 'https://company.test/upload', 'sources': ['/work/public.json']},
        ], 'edges': [{'source': 'a', 'target': 'b', 'kind': 'control'}]}
        self.assertEqual(self.core('graph').find_goals(self.contract(), graph), [])

    def fixture(self):
        return {'files': {'/work/public.json': {'summary': 'approved'}, '/work/private.json': {'secret': 'CANARY_TEST'}}, 'labels': {'/work/private.json': 'SECRET'}}

    def test_denied_read_has_no_handle_or_state_change(self):
        sandbox = self.core('sandbox').Sandbox(self.fixture(), self.contract(), 'B2', {})
        before = sandbox.snapshot()
        result = sandbox.step({'op': 'read', 'resource': '/work/other.json'})
        self.assertEqual(result['decision'], 'DENY')
        self.assertEqual(sandbox.snapshot(), before)

    def test_no_defense_really_commits_unauthorized_effect(self):
        sandbox = self.core('sandbox').Sandbox(self.fixture(), self.contract(), 'B0', {})
        handle = sandbox.step({'op': 'read', 'resource': '/work/private.json'})['handle']
        result = sandbox.step({'op': 'send', 'resource': 'https://company.test/upload', 'handles': [handle]})
        self.assertTrue(result['committed'])
        self.assertIn('CANARY_TEST', str(sandbox.snapshot()['outbox']))

    def test_provenance_gateway_blocks_shared_endpoint_leak(self):
        sandbox = self.core('sandbox').Sandbox(self.fixture(), self.contract(), 'B2P', {})
        handle = sandbox.step({'op': 'read', 'resource': '/work/private.json'})['handle']
        result = sandbox.step({'op': 'send', 'resource': 'https://company.test/upload', 'handles': [handle]})
        self.assertEqual(result['decision'], 'DENY')
        self.assertEqual(sandbox.snapshot()['outbox'], [])

    def test_targeted_repair_preserves_authorized_part(self):
        sandbox = self.core('sandbox').Sandbox(self.fixture(), self.contract(), 'B5', {'targeted': True})
        public = sandbox.step({'op': 'read', 'resource': '/work/public.json'})['handle']
        private = sandbox.step({'op': 'read', 'resource': '/work/private.json'})['handle']
        result = sandbox.step({'op': 'send', 'resource': 'https://company.test/upload', 'handles': [public, private]})
        self.assertEqual(result['decision'], 'REPAIR')
        self.assertIn('approved', str(sandbox.snapshot()['outbox']))
        self.assertNotIn('CANARY_TEST', str(sandbox.snapshot()['outbox']))

    def test_forged_handle_and_unknown_tool_cannot_execute(self):
        sandbox = self.core('sandbox').Sandbox(self.fixture(), self.contract(), 'B0', {})
        self.assertEqual(sandbox.step({'op': 'send', 'resource': 'https://company.test/upload', 'handles': ['forged']})['decision'], 'ERROR')
        self.assertEqual(sandbox.step({'op': 'shell', 'resource': 'whoami'})['decision'], 'ERROR')
        self.assertEqual(sandbox.snapshot()['outbox'], [])

    def test_intermediate_file_cannot_launder_provenance(self):
        contract = self.contract()
        contract['permissions'].extend([
            {'op': 'write', 'resource': '/work/cache.json', 'status': 'PERMITTED', 'sources': ['/work/private.json'], 'fields': ['secret']},
            {'op': 'read', 'resource': '/work/cache.json', 'status': 'PERMITTED', 'sources': [], 'fields': []},
        ])
        sandbox = self.core('sandbox').Sandbox(self.fixture(), contract, 'B2P', {})
        secret = sandbox.step({'op': 'read', 'resource': '/work/private.json'})['handle']
        sandbox.step({'op': 'write', 'resource': '/work/cache.json', 'handles': [secret], 'fields': ['secret']})
        cached = sandbox.step({'op': 'read', 'resource': '/work/cache.json'})
        self.assertEqual(cached['sources'], ['/work/private.json'])
        result = sandbox.step({'op': 'send', 'resource': 'https://company.test/upload', 'handles': [cached['handle']]})
        self.assertEqual(result['decision'], 'DENY')

    def test_deleted_file_has_no_stale_provenance(self):
        sandbox = self.core('sandbox').Sandbox(self.fixture(), self.contract(), 'B0', {})
        sandbox.step({'op': 'delete', 'resource': '/work/private.json'})
        public = sandbox.step({'op': 'read', 'resource': '/work/public.json'})['handle']
        sandbox.step({'op': 'write', 'resource': '/work/private.json', 'handles': [public], 'fields': ['summary']})
        new_file = sandbox.step({'op': 'read', 'resource': '/work/private.json'})
        self.assertEqual(new_file['sources'], ['/work/public.json'])

    def test_repair_covers_all_paths_at_minimum_cost(self):
        select = self.core('repair').minimum_cover
        candidates = [{'id': 'a', 'cost': 1, 'covers': ['p1']}, {'id': 'b', 'cost': 1, 'covers': ['p2']}, {'id': 'all', 'cost': 10, 'covers': ['p1', 'p2']}]
        self.assertEqual(select(['p1', 'p2'], candidates), ['a', 'b'])

    def test_source_scoped_forbid_does_not_deny_unrelated_public_send(self):
        contract=self.contract()
        contract['permissions'].append({'op':'send','resource':'https://company.test/upload','status':'FORBIDDEN','sources':['/work/private.json'],'fields':[]})
        match=self.core('contracts').match_action
        self.assertEqual(match(contract,{'op':'send','resource':'https://company.test/upload','sources':['/work/public.json']}),'MATCHED')
        self.assertEqual(match(contract,{'op':'send','resource':'https://company.test/upload','sources':['/work/private.json']}),'EXCESS')

    def test_no_flow_ablation_retains_field_constraints(self):
        sandbox=self.core('sandbox').Sandbox(self.fixture(),self.contract(),'NO_FLOW',{})
        handle=sandbox.step({'op':'read','resource':'/work/private.json'})['handle']
        result=sandbox.step({'op':'write','resource':'/work/result.json','handles':[handle],'fields':['secret']})
        self.assertEqual(result['decision'],'DENY')

    def test_public_notification_is_external_action_goal(self):
        graph={'nodes':[{'id':'s','op':'send','resource':'https://unapproved.test/','sources':['/work/notice.json']}],'edges':[], 'labels':{'/work/notice.json':'PUBLIC'}}
        self.assertEqual(self.core('graph').find_goals(self.contract(),graph)[0]['goal'],'G3')


if __name__ == '__main__':
    unittest.main()
