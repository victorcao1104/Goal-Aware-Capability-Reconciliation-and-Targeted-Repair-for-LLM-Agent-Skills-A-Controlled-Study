"""Exact small hitting-set selection; no claim of global program minimality."""
from itertools import combinations


def minimum_cover(paths: list[str], candidates: list[dict]) -> list[str]:
    needed = set(paths)
    if not needed:
        return []
    if len(candidates) > 20:
        raise ValueError('Repair optimization budget exceeded')
    best = None
    for size in range(1, len(candidates) + 1):
        for subset in combinations(candidates, size):
            covered = set().union(*(set(c['covers']) for c in subset))
            if needed <= covered:
                score = (sum(c['cost'] for c in subset), len(subset), tuple(c['id'] for c in subset))
                if best is None or score < best:
                    best = score
    if best is None:
        raise ValueError('No feasible repair')
    return list(best[2])


def select_repair(findings: list[dict], graph: dict) -> dict:
    paths = [f'p{i}' for i in range(len(findings))]
    sinks = sorted({f['sink'] for f in findings})
    candidates = [{'id': 'restrict:' + sink, 'cost': 1,
                   'covers': [paths[i] for i, f in enumerate(findings) if f['sink'] == sink]} for sink in sinks]
    candidates.append({'id': 'block_skill', 'cost': 10 + len(sinks), 'covers': paths})
    if len(candidates) > 20:
        return {'targeted': False, 'block_all': True, 'unresolved': 'repair_budget'}
    selected = minimum_cover(paths, candidates)
    return {'targeted': bool(findings), 'selected': selected, 'sink_ids': sinks,
            'resources': sorted({n['resource'] for n in graph['nodes'] if n['id'] in sinks}),
            'cost': sum(c['cost'] for c in candidates if c['id'] in selected),
            'scope': 'minimum among enumerated restrictions; utility requires execution'}
