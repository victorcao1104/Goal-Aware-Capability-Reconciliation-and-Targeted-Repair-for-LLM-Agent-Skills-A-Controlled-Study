"""Read explicit final-answer messages without mixing intermediate commentary."""
import json
import jsonschema

def messages(raw):
    return [{'type':'message','role':m.get('role','assistant'),'phase':m.get('phase'),
             'content':[{k:c[k] for k in ('type','text','refusal') if k in c} for c in m.get('content',[])]}
            for m in raw.get('output',[]) if m.get('type','message')=='message']

def parse(raw,schema):
    ms=messages(raw)
    if any(c.get('type')=='refusal' for m in ms for c in m['content']):return {'status':'refusal','value':{}}
    if raw.get('status')!='completed':return {'status':'incomplete','value':{}}
    finals=[m for m in ms if m['phase']=='final_answer']
    selected=finals if finals else [m for m in ms if m['phase'] is None]
    if len(selected)!=1:raise ValueError('Missing or ambiguous final answer')
    value=json.loads(''.join(c.get('text','') for c in selected[0]['content'] if c.get('type')=='output_text'))
    jsonschema.validate(value,schema)
    return {'status':'ok','value':value}
