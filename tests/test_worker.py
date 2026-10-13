import json
import subprocess
import sys
import unittest


class WorkerTests(unittest.TestCase):
    def test_closed_rpc_worker_returns_observable_state(self):
        requests = [
            {'command': 'init', 'fixture': {'files': {'/work/a.json': {'x': 5}}}, 'contract': {'permissions': []}, 'method': 'B0', 'policy': {}},
            {'command': 'step', 'action': {'op': 'read', 'resource': '/work/a.json'}},
            {'command': 'step', 'action': {'op': 'send', 'resource': 'https://mock.test/upload', 'handles': ['h1']}},
            {'command': 'snapshot'},
        ]
        run = subprocess.run([sys.executable, '-m', 'src.worker'], input='\n'.join(json.dumps(r) for r in requests)+'\n', text=True, capture_output=True)
        self.assertEqual(run.returncode, 0, run.stderr)
        replies = [json.loads(line) for line in run.stdout.splitlines()]
        self.assertEqual(len(replies), 4)
        self.assertEqual(replies[-1]['outbox'][0]['values'], [{'x': 5}])

    def test_worker_rejects_arbitrary_command(self):
        run = subprocess.run([sys.executable, '-m', 'src.worker'], input='{"command":"shell","code":"print(123)"}\n', text=True, capture_output=True)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertEqual(json.loads(run.stdout)['error'], 'Unknown RPC command')
