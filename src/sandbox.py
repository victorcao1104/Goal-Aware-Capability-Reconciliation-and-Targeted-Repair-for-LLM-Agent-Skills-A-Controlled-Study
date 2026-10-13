"""Closed simulated tools. No OS command, external network or dynamic code evaluation."""
from copy import deepcopy
from .contracts import normalize_resource, match_action, permission_for

METHODS = {'B0', 'B1', 'B2', 'B2P', 'B3', 'B4', 'B5', 'NO_TASK', 'NO_FLOW', 'NO_REPAIR', 'SCOPE_INSPIRED'}


class Sandbox:
    def __init__(self, fixture: dict, contract: dict, method: str, policy: dict):
        if method not in METHODS:
            raise ValueError('Unknown method')
        self.files = {normalize_resource(k): deepcopy(v) for k, v in fixture['files'].items()}
        self.labels = fixture.get('labels', {})
        self.field_sources = {path: {key: {path} for key in value} if isinstance(value, dict) else {'*': {path}}
                              for path, value in self.files.items()}
        self.contract, self.method, self.policy = contract, method, policy
        self.handles, self.outbox, self.events = {}, [], []
        self.counter = 0

    def snapshot(self):
        return deepcopy({'files': self.files, 'outbox': self.outbox})

    def handle(self, value, sources):
        self.counter += 1
        key = f'h{self.counter}'
        self.handles[key] = {'value': deepcopy(value), 'sources': sorted(set(sources))}
        return key

    def step(self, request: dict) -> dict:
        event = {'requested': deepcopy(request), 'decision': 'ERROR', 'committed': False}
        try:
            result = self._step(request, event)
        except (ValueError, KeyError, TypeError) as exc:
            result = {'error': str(exc)}
        event.update(result)
        self.events.append(deepcopy(event))
        return event

    def _step(self, request, event):
        op = request.get('op')
        if op not in ('read', 'write', 'delete', 'send', 'transform', 'create', 'finish'):
            raise ValueError('Unsupported tool')
        if op == 'finish':
            event['decision'] = 'ALLOW'
            return {'finished': True}
        if self.policy.get('block_all') and self.method != 'B0':
            event['decision'] = 'DENY'
            return {'reason': 'SKILL_BLOCKED'}
        if op == 'read':
            resource = normalize_resource(request['resource'])
            action = {'op': op, 'resource': resource}
            if self.method not in ('B0', 'B1', 'NO_TASK') and match_action(self.contract, action) != 'MATCHED':
                event['decision'] = 'DENY'
                return {'reason': 'OUTSIDE_TASK_AUTHORITY'}
            if resource not in self.files:
                raise ValueError('Resource does not exist')
            origins = set().union(*self.field_sources[resource].values()) if self.field_sources[resource] else {resource}
            key = self.handle(self.files[resource], origins)
            event['decision'] = 'ALLOW'
            return {'handle': key, 'value': deepcopy(self.files[resource]), 'sources': sorted(origins)}
        handles = request.get('handles', [])
        if not isinstance(handles, list) or any(h not in self.handles for h in handles):
            raise ValueError('Unknown data handle')
        sources = set().union(*(set(self.handles[h]['sources']) for h in handles)) if handles else set()
        if op in ('create', 'transform'):
            if op == 'create':
                # Free text can copy any previously seen data; conservative taint.
                value = request.get('value', {})
                sources = set().union(*(set(h['sources']) for h in self.handles.values())) if self.handles else set()
            else:
                transform = request.get('resource', 'concat')
                values = [deepcopy(self.handles[h]['value']) for h in handles]
                if transform == 'copy' and len(values) == 1:
                    value = values[0]
                elif transform == 'concat':
                    value = values
                elif transform == 'select_fields' and len(values) == 1 and isinstance(values[0], dict):
                    value = {k: values[0][k] for k in request.get('fields', []) if k in values[0]}
                else:
                    raise ValueError('Unsupported transform')
            event['decision'] = 'ALLOW'
            return {'handle': self.handle(value, sources), 'value': value, 'sources': sorted(sources)}
        resource = normalize_resource(request['resource'])
        fields = request.get('fields', [])
        action = {'op': op, 'resource': resource, 'sources': sorted(sources), 'fields': fields}
        event['action'] = deepcopy(action)
        provenance = self.method in ('B2P', 'B5', 'NO_REPAIR', 'SCOPE_INSPIRED')
        decision = 'MATCHED' if self.method in ('B0', 'B1', 'NO_TASK') else match_action(self.contract, action, provenance, field_scope=True if self.method=='NO_FLOW' else None)
        repaired = False
        if decision != 'MATCHED' and self.method in ('B5','NO_FLOW') and self.policy.get('targeted') and ('resources' not in self.policy or resource in self.policy['resources']):
            permission = permission_for(self.contract, op, resource)
            if permission and op in ('write', 'send'):
                allowed = set(permission.get('sources', []))
                kept = [h for h in handles if self.method=='NO_FLOW' or set(self.handles[h]['sources']) <= allowed]
                kept_fields = [f for f in fields if f in permission.get('fields', [])] if op == 'write' else fields
                if kept and (op != 'write' or kept_fields):
                    handles, fields = kept, kept_fields
                    sources = set().union(*(set(self.handles[h]['sources']) for h in handles))
                    action.update(sources=sorted(sources), fields=fields)
                    decision = match_action(self.contract, action, self.method!='NO_FLOW', field_scope=True)
                    repaired = decision == 'MATCHED'
        if decision != 'MATCHED':
            event['decision'] = 'DENY'
            return {'reason': 'OUTSIDE_TASK_AUTHORITY_OR_DATA_SCOPE'}
        values = [deepcopy(self.handles[h]['value']) for h in handles]
        if op == 'send':
            if not handles:
                raise ValueError('send requires data handles')
            self.outbox.append({'destination': resource, 'values': values, 'sources': sorted(sources)})
        elif op == 'write':
            if len(values) != 1 or not isinstance(values[0], dict) or not fields:
                raise ValueError('write requires one object handle and explicit fields')
            if any(f not in values[0] for f in fields):
                raise ValueError('Missing field in input value')
            current = deepcopy(self.files.get(resource, {}))
            if not isinstance(current, dict):
                raise ValueError('Only structured fixture files are supported')
            current.update({f: values[0][f] for f in fields})
            event['written_values']={f:deepcopy(values[0][f]) for f in fields}
            self.files[resource] = current
            origins = self.field_sources.setdefault(resource, {})
            for field in fields:
                origins[field] = set(sources)
        elif op == 'delete':
            if resource not in self.files:
                raise ValueError('Resource does not exist')
            del self.files[resource]
            del self.field_sources[resource]
        event.update(decision='REPAIR' if repaired else 'ALLOW', committed=True, effective_action=action)
        return {'ok': True}
