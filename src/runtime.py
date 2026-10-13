"""Host-to-container transport; the container never receives an API credential."""
import json
import subprocess
import queue
import threading
import uuid


class ResponseReader:
    def __init__(self, stream):
        self.responses = queue.Queue()
        def pump():
            while True:
                line = stream.readline()
                self.responses.put(line)
                if not line:
                    break
        threading.Thread(target=pump, daemon=True).start()

    def next(self, timeout=30):
        try:
            line = self.responses.get(timeout=timeout)
        except queue.Empty:
            raise TimeoutError('Sandbox RPC timeout; no security result can be inferred') from None
        if not line:
            raise RuntimeError('Sandbox worker stopped; no security result can be inferred')
        return json.loads(line)


class ContainerRuntime:
    def __init__(self, fixture, contract, method, policy):
        self.name = 'skill-research-'+uuid.uuid4().hex
        command = ['docker','run','--name',self.name,'--rm','-i','--network','none','--read-only','--cap-drop','ALL',
                   '--security-opt','no-new-privileges','--pids-limit','32','--memory','128m','--cpus','1',
                   'goal-skill-sandbox:research']
        self.process = subprocess.Popen(command,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                                        text=True,encoding='utf-8',bufsize=1)
        self.reader = ResponseReader(self.process.stdout)
        try:
            self.ask({'command':'init','fixture':fixture,'contract':contract,'method':method,'policy':policy})
        except Exception:
            self.close()
            raise

    def ask(self, message):
        self.process.stdin.write(json.dumps(message,ensure_ascii=True)+'\n')
        self.process.stdin.flush()
        result = self.reader.next()
        if isinstance(result,dict) and 'error' in result and 'decision' not in result:
            raise RuntimeError('Sandbox RPC error: '+result['error'])
        return result

    def step(self, action):
        return self.ask({'command':'step','action':action})

    def snapshot(self):
        return self.ask({'command':'snapshot'})

    def close(self):
        if self.process.stdin and not self.process.stdin.closed:
            self.process.stdin.close()
        try:
            self.process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            subprocess.run(['docker','rm','-f',self.name],capture_output=True,timeout=15)
            self.process.kill()
            self.process.wait(timeout=10)


class LocalRuntime:
    """For tests only; formal runs select the container transport."""
    def __init__(self, fixture, contract, method, policy):
        from .sandbox import Sandbox
        self.sandbox = Sandbox(fixture,contract,method,policy)

    def step(self, action):
        return self.sandbox.step(action)

    def snapshot(self):
        return self.sandbox.snapshot()

    def close(self):
        pass
