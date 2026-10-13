"""Host-only model client with durable pre-dispatch cost reservations."""
import hashlib
import json
import threading
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path
from contextlib import contextmanager
import os

MODEL = 'gpt-6-luna'
INPUT_UPPER_PER_M = 0.125  # conservative cache-write rate; no cache discount assumed
OUTPUT_PER_M = 0.50


class BudgetExceeded(RuntimeError):
    pass


class ModelRefusal(RuntimeError):
    pass


class ModelIncomplete(RuntimeError):
    pass


def usage_cost(usage: dict) -> float:
    # output_tokens already includes reasoning tokens.
    return (usage.get('input_tokens', 0)*INPUT_UPPER_PER_M + usage.get('output_tokens', 0)*OUTPUT_PER_M)/1_000_000


class Budget:
    def __init__(self, path: Path, limit: float = 20.0):
        self.path, self.limit = path, limit
        self.lock = threading.RLock()
        self.records = json.loads(path.read_text(encoding='utf-8')) if path.exists() else {}

    def total(self):
        with self.transaction():
            return sum(r.get('settled', r['reserved']) for r in self.records.values())

    @contextmanager
    def transaction(self):
        with self.lock:
            self.path.parent.mkdir(parents=True,exist_ok=True)
            with self.path.with_suffix('.lock').open('a+b') as lockfile:
                lockfile.seek(0,2)
                if lockfile.tell()==0:
                    lockfile.write(b'0')
                    lockfile.flush()
                lockfile.seek(0)
                if os.name=='nt':
                    import msvcrt
                    msvcrt.locking(lockfile.fileno(),msvcrt.LK_LOCK,1)
                else:
                    import fcntl
                    fcntl.flock(lockfile,fcntl.LOCK_EX)
                try:
                    self.records=json.loads(self.path.read_text(encoding='utf-8')) if self.path.exists() else {}
                    yield
                finally:
                    lockfile.seek(0)
                    if os.name=='nt':
                        msvcrt.locking(lockfile.fileno(),msvcrt.LK_UNLCK,1)
                    else:
                        fcntl.flock(lockfile,fcntl.LOCK_UN)

    def _save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix('.tmp')
        temporary.write_text(json.dumps(self.records, indent=2), encoding='utf-8')
        temporary.replace(self.path)

    def reserve(self, call_id: str, maximum: float):
        with self.transaction():
            if call_id in self.records:
                raise ValueError('Call id already reserved; use a distinct retry id')
            if maximum < 0 or sum(r.get('settled',r['reserved']) for r in self.records.values()) + maximum > self.limit:
                raise BudgetExceeded('Authorized US$20 usage ceiling would be exceeded')
            self.records[call_id] = {'reserved': maximum, 'status': 'pending', 'time': datetime.now(timezone.utc).isoformat()}
            self._save()

    def settle(self, call_id: str, actual: float):
        with self.transaction():
            self.records[call_id].update(settled=actual, status='settled')
            self._save()


class Client:
    def __init__(self, root: Path, max_output: int = 6000):
        self.root, self.max_output = root, max_output
        self.budget = Budget(root/'results/raw_runs/budget-ledger.json')
        self.calls = root/'results/raw_runs/api_calls'
        self.calls.mkdir(parents=True, exist_ok=True)
        key_lines = (root/'.env.local').read_text(encoding='utf-8').splitlines()
        self._key = next(line.split('=',1)[1].strip().strip('"').strip("'") for line in key_lines if line.startswith('OPENAI_API_KEY='))

    def generate(self, role: str, instruction: str, payload: dict, schema: dict, call_id: str, max_output: int | None = None) -> dict:
        import jsonschema
        request = {'model': MODEL, 'store': False, 'reasoning': {'effort': 'low'},
                   'max_output_tokens': max_output or self.max_output,
                   'input': [{'role':'system','content':instruction}, {'role':'user','content':json.dumps(payload, ensure_ascii=False)}],
                   'text': {'format': {'type':'json_schema','name':role,'strict':True,'schema':schema}}}
        encoded = json.dumps(request, ensure_ascii=False).encode('utf-8')
        fingerprint = hashlib.sha256(encoded + call_id.encode()).hexdigest()
        destination = self.calls/(fingerprint + '.json')
        if destination.exists():
            cached = json.loads(destination.read_text(encoding='utf-8'))
            if cached.get('status') == 'ok':
                return cached
            if cached.get('status')=='model_refusal':
                raise ModelRefusal(fingerprint)
            if cached.get('status')=='model_incomplete':
                raise ModelIncomplete(fingerprint)
            raise RuntimeError('Recorded API failure; do not silently retry failed scientific run')
        # UTF-8 byte count is deliberately conservative for input token budgeting.
        reserve = ((len(encoded)+1024)*INPUT_UPPER_PER_M + request['max_output_tokens']*OUTPUT_PER_M)/1_000_000
        attempts = []
        for attempt in range(3):
            reservation_id = fingerprint + f':{attempt}'
            if reservation_id in self.budget.records:
                continue  # retain any unknown charge from an interrupted dispatch
            self.budget.reserve(reservation_id, reserve)
            start = time.perf_counter()
            record = {'call_id':call_id,'role':role,'fingerprint':fingerprint,'request':request,
                      'started_utc':datetime.now(timezone.utc).isoformat(),'attempt':attempt}
            try:
                http_request = urllib.request.Request('https://api.openai.com/v1/responses', data=encoded,
                    headers={'Authorization':'Bearer '+self._key,'Content-Type':'application/json'}, method='POST')
                with urllib.request.urlopen(http_request, timeout=120) as response:
                    raw = json.load(response)
                record.update(response=raw, seconds=time.perf_counter()-start)
                if 'usage' in raw:
                    cost = usage_cost(raw['usage'])
                    self.budget.settle(reservation_id, cost)
                    record['conservative_usage_usd'] = cost
                if raw.get('status') != 'completed':
                    record['status']='model_incomplete'
                    destination.write_text(json.dumps(record,ensure_ascii=False),encoding='utf-8')
                    raise ModelIncomplete(fingerprint)
                if any(c.get('type')=='refusal' for item in raw.get('output',[]) for c in item.get('content',[])):
                    record['status']='model_refusal'
                    destination.write_text(json.dumps(record,ensure_ascii=False),encoding='utf-8')
                    raise ModelRefusal(fingerprint)
                text = ''.join(c.get('text','') for item in raw.get('output',[]) for c in item.get('content',[]) if c.get('type')=='output_text')
                value = json.loads(text)
                jsonschema.validate(value, schema)
                record.update(status='ok', value=value, prior_attempts=attempts)
                destination.write_text(json.dumps(record, ensure_ascii=False), encoding='utf-8')
                return record
            except urllib.error.HTTPError as exc:
                # No raw response body or headers are logged: they can contain provider diagnostics.
                record.update(status='http_error', http_status=exc.code, seconds=time.perf_counter()-start)
                attempts.append({k:v for k,v in record.items() if k!='request'})
                if exc.code in (429,500,502,503,504) and attempt < 2:
                    time.sleep(2*(attempt+1))
                    continue
            except (urllib.error.URLError, TimeoutError) as exc:
                record.update(status='transport_error', error_type=type(exc).__name__, seconds=time.perf_counter()-start)
                attempts.append({k:v for k,v in record.items() if k!='request'})
                if attempt < 2:
                    time.sleep(2*(attempt+1))
                    continue
            except (ValueError, jsonschema.ValidationError) as exc:
                record.update(status='invalid_response', error_type=type(exc).__name__, seconds=time.perf_counter()-start)
            record['prior_attempts'] = attempts
            destination.write_text(json.dumps(record, ensure_ascii=False), encoding='utf-8')
            raise RuntimeError(f'Model call failed: {record["status"]}; see retained record {fingerprint}')
        raise RuntimeError('All dispatch reservations already exist; inspect interrupted call records')
