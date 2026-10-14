"""Model-aware requests using the original cumulative budget, never global monkeypatching."""
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import threading
import urllib.error
import urllib.request
import jsonschema
from src.api import Budget,BudgetExceeded
from research_v3.run import dump
from .model import spec,request_key,request_cost_bound,usage_cost
from research_v6b.response import parse,messages
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'research_v8/results'
PRIOR=2.411697525;INCREMENTAL_CAP=6.0
_locks={};_guard=threading.Lock()
def validate_record(record,stage,setting,role,p,sc,repeat):
    key=request_key(stage,setting,role,p,sc,repeat);request=spec(setting,role,p,sc)
    for k,v in {'key':key,'stage':stage,'setting':setting,'role':role,'repeat':repeat,'request':request}.items():
        if record.get(k)!=v:raise RuntimeError('Request identity mismatch: '+k)
    if record['status'] not in ('ok','refusal','incomplete','invalid_response','http_error','transport_error'):raise RuntimeError('Invalid status')
    if record['status']=='ok':jsonschema.validate(record['value'],sc)
    elif record['value']!={}:raise RuntimeError('Failure has a value')
    if record['reservation_id']!='v8:'+key or record['reserved_usd']!=request_cost_bound(request,setting):raise RuntimeError('Reservation identity mismatch')
    expected=usage_cost(record['usage'],setting) if record['usage'] else record['reserved_usd']
    if abs(record['accounted_usd']-expected)>1e-10:raise RuntimeError('Per-model cost mismatch')
    if 'provider_status' in record:
        try:parsed=parse({'status':record['provider_status'],'output':record['response_messages']},sc)
        except (ValueError,jsonschema.ValidationError):parsed={'status':'invalid_response','value':{}}
        if parsed!={'status':record['status'],'value':record['value']}:raise RuntimeError('Response parse differs')
    return record
class Client:
    def __init__(self, stage):
        self.stage=stage
        ledger=ROOT/'results/raw_runs/budget-ledger.json'
        if not ledger.exists():raise RuntimeError('Original ledger required')
        pilot_cost=json.loads((OUT/'pilot/summary.json').read_text(encoding='utf8'))['cost_usd'] if stage=='formal' else 0
        self.budget=Budget(ledger,min(20,PRIOR+(1 if stage=='pilot' else pilot_cost+5)))
        with self.budget.transaction():
            if any(r['status']!='settled' for r in self.budget.records.values()):raise RuntimeError('Unresolved prior reservation')
        if self.budget.total()<PRIOR-1e-10:raise RuntimeError('Missing prior spend')
        lines=(ROOT/'.env.local').read_text(encoding='utf-8').splitlines()
        self._key=next(l.split('=',1)[1].strip().strip('"').strip("'") for l in lines if l.startswith('OPENAI_API_KEY='))
        self.private=ROOT/'results/raw_runs/v8_calls';self.private.mkdir(parents=True,exist_ok=True)
    def get(self,stage,setting,role,p,sc,repeat=0):
        if stage!=self.stage:raise RuntimeError('Wrong stage client')
        key=request_key(stage,setting,role,p,sc,repeat)
        with _guard:lock=_locks.setdefault(key,threading.Lock())
        with lock:
            public=OUT/'requests'/(key+'.json');private_path=self.private/(key+'.json')
            if public.exists():
                r=validate_record(json.loads(public.read_text(encoding='utf-8')),stage,setting,role,p,sc,repeat)
                private=json.loads(private_path.read_text(encoding='utf-8'))
                if private['public']!=r:raise RuntimeError('Private/public record mismatch')
                with self.budget.transaction():entry=self.budget.records.get(r['reservation_id'])
                if entry is None or entry.get('settled')!=r['accounted_usd']:raise RuntimeError('Ledger record mismatch')
                return r
            request=spec(setting,role,p,sc);reserve=request_cost_bound(request,setting);rid='v8:'+key
            with self.budget.transaction():
                if rid in self.budget.records:raise RuntimeError('Interrupted call reservation exists; inspect without redispatch')
            self.budget.reserve(rid,reserve)
            record={'key':key,'stage':stage,'setting':setting,'role':role,'repeat':repeat,'request':request,
                    'reservation_id':rid,'reserved_usd':reserve,'usage':{},'value':{},
                    'status':'transport_error','model':None,'utc':datetime.now(timezone.utc).isoformat()}
            raw={};http_status=None
            try:
                req=urllib.request.Request('https://api.openai.com/v1/responses',data=json.dumps(request,ensure_ascii=False).encode(),
                    headers={'Authorization':'Bearer '+self._key,'Content-Type':'application/json'},method='POST')
                with urllib.request.urlopen(req,timeout=120) as response:raw=json.load(response)
                record.update(usage=raw.get('usage',{}),model=raw.get('model'),provider_status=raw.get('status'))
                record['response_messages']=messages(raw)
                record.update(parse(raw,sc))
            except urllib.error.HTTPError as exc:record.update(status='http_error',http_status=exc.code)
            except (urllib.error.URLError,TimeoutError,OSError) as exc:record.update(status='transport_error',exception_class=type(exc).__name__)
            except (ValueError,jsonschema.ValidationError) as exc:record.update(status='invalid_response',exception_class=type(exc).__name__)
            record['accounted_usd']=usage_cost(record['usage'],setting) if record['usage'] else reserve
            record['accounting_basis']='token_usage' if record['usage'] else 'reserved_upper_bound_unknown_charge'
            # Full reservation charged conservatively for unknown errors, never assumed free.
            self.budget.settle(rid,record['accounted_usd'])
            validate_record(record,stage,setting,role,p,sc,repeat)
            dump(private_path,{'public':record,'provider_response':raw});dump(public,record);return record
def offline_get(stage,setting,role,p,sc,repeat=0):
    key=request_key(stage,setting,role,p,sc,repeat)
    return validate_record(json.loads((OUT/'requests'/(key+'.json')).read_text(encoding='utf-8')),stage,setting,role,p,sc,repeat)
