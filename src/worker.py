"""JSON-lines RPC worker, normally run in a network-disabled Linux container."""
import json
import sys
from .sandbox import Sandbox


def main():
    sandbox = None
    for line in sys.stdin:
        try:
            if len(line) > 2_000_000:
                raise ValueError('Request too large')
            message = json.loads(line)
            command = message.get('command')
            if command == 'init':
                sandbox = Sandbox(message['fixture'], message['contract'], message['method'], message['policy'])
                response = {'ready': True}
            elif command == 'step' and sandbox:
                response = sandbox.step(message['action'])
            elif command == 'snapshot' and sandbox:
                response = sandbox.snapshot()
            elif command == 'events' and sandbox:
                response = sandbox.events
            else:
                raise ValueError('Unknown RPC command')
        except (ValueError, KeyError, TypeError) as exc:
            response = {'error': str(exc)}
        print(json.dumps(response, ensure_ascii=True), flush=True)


if __name__ == '__main__':
    main()
