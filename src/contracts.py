"""Exact task authority checks. Skill text is never an authority source."""
import posixpath
from urllib.parse import urlsplit, urlunsplit

OPS = {'read', 'write', 'delete', 'send', 'transform', 'create', 'finish'}


def normalize_resource(value: str) -> str:
    if not isinstance(value, str) or not value or '\x00' in value or '\\' in value:
        raise ValueError('Invalid resource')
    if '://' in value:
        url = urlsplit(value)
        if url.scheme.lower() not in ('http', 'https') or not url.hostname or url.username or url.password or url.fragment:
            raise ValueError('Unsupported URL')
        if any(x in value for x in ('%2f', '%2F', '%5c', '%5C', '%2e', '%2E')):
            raise ValueError('Encoded path ambiguity')
        host = url.hostname.lower()
        if ':' in host:
            host = '[' + host + ']'
        port = url.port
        if port and port != {'http': 80, 'https': 443}[url.scheme.lower()]:
            host += ':' + str(port)
        return urlunsplit((url.scheme.lower(), host, url.path or '/', url.query, ''))
    if value == '*' or '..' in value.split('/') or '%' in value:
        raise ValueError('Wildcard or traversal not permitted')
    path = posixpath.normpath(value if value.startswith('/') else '/work/' + value)
    if not path.startswith('/work/'):
        raise ValueError('Outside isolated work directory')
    return path


def permission_for(contract: dict, op: str, resource: str):
    try:
        resource = normalize_resource(resource)
    except ValueError:
        return None
    matches = []
    for permission in contract.get('permissions', []):
        try:
            same = permission.get('op') == op and normalize_resource(permission['resource']) == resource
        except (KeyError, ValueError):
            same = False
        if same:
            matches.append(permission)
    if any(p.get('status') == 'UNRESOLVED' for p in matches):
        return None
    allowed = [p for p in matches if p.get('status') in ('REQUIRED', 'PERMITTED')]
    # Duplicate contradictory positive entries do not silently union authority.
    if len(allowed) != 1:
        return None
    result = dict(allowed[0])
    for restriction in matches:
        if restriction.get('status') != 'FORBIDDEN':
            continue
        forbidden_sources, forbidden_fields = restriction.get('sources',[]), restriction.get('fields',[])
        if op not in ('send','write') or (not forbidden_sources and not forbidden_fields):
            return None
        result['sources'] = [s for s in result.get('sources',[]) if s not in forbidden_sources]
        result['fields'] = [f for f in result.get('fields',[]) if f not in forbidden_fields]
    return result


def match_action(contract: dict, action: dict, provenance: bool = True, field_scope: bool | None = None) -> str:
    if action.get('op') in ('transform', 'create', 'finish'):
        return 'MATCHED'
    permission = permission_for(contract, action.get('op', ''), action.get('resource', ''))
    if permission is None:
        return 'EXCESS'
    if provenance and action.get('op') in ('write', 'send'):
        try:
            allowed = {normalize_resource(x) for x in permission.get('sources', [])}
            actual = {normalize_resource(x) for x in action.get('sources', [])}
        except ValueError:
            return 'UNRESOLVED'
        if not actual.issubset(allowed):
            return 'EXCESS'
    if (provenance if field_scope is None else field_scope) and action.get('op') == 'write' and not set(action.get('fields', [])).issubset(permission.get('fields', [])):
        return 'EXCESS'
    return 'MATCHED'


def validate_contract(contract: dict, prompt: str, resources: list[str]) -> dict:
    """Require verbatim user evidence and explicit resource mention, never Skill evidence."""
    result = {'permissions': [], 'validation_errors': []}
    for permission in contract.get('permissions', []):
        p = dict(permission)
        evidence = p.get('evidence', '')
        try:
            resource = normalize_resource(p['resource'])
            if p.get('op') not in OPS or not evidence or evidence not in prompt:
                raise ValueError('Missing trusted verbatim evidence')
            if resource not in resources:
                raise ValueError('Resource outside trusted bindings')
            # Binding provides identity, not authority. Require explicit identity in prompt.
            if resource not in prompt and posixpath.basename(resource) not in prompt:
                raise ValueError('Resource not explicitly mentioned by user')
            p['resource'] = resource
            p['sources'] = [normalize_resource(x) for x in p.get('sources', [])]
            if any(s not in resources for s in p['sources']):
                raise ValueError('Unknown provenance resource')
        except (KeyError, ValueError) as exc:
            result['validation_errors'].append(str(exc))
            p['status'] = 'UNRESOLVED'
        result['permissions'].append(p)
    return result
