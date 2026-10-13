"""Bounded data-path analysis, kept separate from control-edge reachability."""
from collections import deque
from .contracts import match_action, permission_for


def find_goals(contract: dict, graph: dict, max_depth: int = 12, use_dataflow: bool = True) -> list[dict]:
    nodes = {n['id']: n for n in graph.get('nodes', [])}
    if len(nodes) != len(graph.get('nodes', [])):
        raise ValueError('Duplicate node ids')
    parents = {key: [] for key in nodes}
    for edge in graph.get('edges', []):
        if edge.get('kind') in ('data', 'call', 'return') and edge.get('source') in nodes and edge.get('target') in nodes:
            parents[edge['target']].append(edge['source'])
    findings = []
    for sink_id, node in nodes.items():
        if node.get('op') not in ('send', 'write', 'delete') or node.get('condition') == 'false':
            continue
        action = dict(node)
        sources = set(node.get('sources', []))
        paths = []
        exhausted = False
        if use_dataflow:
            queue = deque([(sink_id, [sink_id])])
            while queue:
                current, path = queue.popleft()
                if nodes[current].get('condition') == 'false':
                    continue
                if nodes[current].get('op') == 'read':
                    sources.add(nodes[current]['resource'])
                    paths.append(list(reversed(path)))
                if len(path) >= max_depth:
                    exhausted |= bool(parents[current])
                    continue
                for parent in parents[current]:
                    if parent not in path:
                        queue.append((parent, path + [parent]))
        action['sources'] = sorted(sources)
        status = match_action(contract, action, provenance=True)
        if status == 'MATCHED' and not exhausted:
            continue
        if node.get('op') == 'send':
            protected=any(graph.get('labels',{}).get(s,'UNKNOWN')!='PUBLIC' for s in sources)
            goal = 'G1' if protected else 'G3'
        else:
            goal = 'G2'
        findings.append({'goal': goal, 'sink': sink_id, 'path': max(paths, key=len) if paths else [sink_id],
                         'sources': sorted(sources), 'status': 'UNRESOLVED' if exhausted else 'POTENTIAL',
                         'reason': status, 'evidence': node.get('evidence', '')})
    return findings
