"""Recompute published measurements in an isolated copy; never call a model."""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent.parent
EXTERNAL_INPUTS = {'datasets/normalized/skillinject.jsonl', 'datasets/normalized/transfer.jsonl'}


def safe_child(root, name):
    path = PurePosixPath(name)
    if not name or path.is_absolute() or '..' in path.parts or '\\' in name or ':' in name:
        raise ValueError('Unsafe relative artifact path')
    target = (root / name).resolve()
    if not target.is_relative_to(root.resolve()):
        raise ValueError('Artifact path escapes its root')
    return target


def verify_evidence(directory):
    manifest = json.loads((directory / 'manifest.json').read_text(encoding='utf8'))
    seen = set()
    for record in manifest['files']:
        name = record['path']
        path = safe_child(directory, name)
        if name in seen or hashlib.sha256(path.read_bytes()).hexdigest() != record['sha256']:
            raise ValueError('Evidence hash or duplicate mismatch: ' + name)
        seen.add(name)
    return len(seen)


def verify_frozen(root):
    manifest = json.loads((root / 'configs/frozen-study.json').read_text(encoding='utf8'))
    omitted = []
    for name, expected in manifest['hashes'].items():
        path = safe_child(root, name)
        if not path.exists() and name in EXTERNAL_INPUTS:
            omitted.append(name)
            continue
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError('Frozen scientific input differs: ' + name)
    return {'verified': len(manifest['hashes'])-len(omitted), 'external_inputs_not_distributed': omitted}


def assert_equivalent(expected, actual, location='$'):
    if isinstance(expected, dict):
        if not isinstance(actual, dict) or expected.keys() != actual.keys():
            raise ValueError('Different object fields at ' + location)
        for key, value in expected.items():
            assert_equivalent(value, actual[key], location+'.'+key)
    elif isinstance(expected, list):
        if not isinstance(actual, list) or len(expected) != len(actual):
            raise ValueError('Different array at ' + location)
        for i, (a, b) in enumerate(zip(expected, actual)):
            assert_equivalent(a, b, location+'['+str(i)+']')
    elif isinstance(expected, (int, float)) and not isinstance(expected, bool):
        if isinstance(actual, bool) or not isinstance(actual, (int, float)) or not math.isfinite(actual) or not math.isclose(expected, actual, rel_tol=0, abs_tol=1e-10):
            raise ValueError('Different numeric value at ' + location)
    elif type(expected) is not type(actual) or expected != actual:
        raise ValueError('Different value at ' + location)


def prepare_workspace(root, destination):
    # Collapse '..' before Windows realpath; missing deep paths can otherwise
    # retain the long lexical spelling and hit the legacy path-length limit.
    root = Path(os.path.abspath(root)).resolve()
    destination = Path(os.path.abspath(destination)).resolve()
    if destination.exists():
        raise FileExistsError('Output already exists; choose a new directory: '+str(destination))
    # Only reviewed inputs are copied, even when invoked from the full local study.
    files = []
    for directory in ('src', 'scripts'):
        files.extend((root / directory).glob('*.py'))
    files.extend([root/'configs/frozen-study.json', root/'datasets/normalized/controls.jsonl',
                  root/'datasets/normalized/transfer-public-metadata.jsonl'])
    files.append(root/'results/evidence/manifest.json')
    records = json.loads(files[-1].read_text(encoding='utf8'))['files']
    files.extend(safe_child(root/'results/evidence', r['path']) for r in records)
    destination.mkdir(parents=True)
    for source in files:
        relative = source.relative_to(root)
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    return destination


def reproduce(root, destination):
    frozen = verify_frozen(root)
    count = verify_evidence(root/'results/evidence')
    destination = prepare_workspace(root, destination)
    env = os.environ.copy()
    for key in tuple(env):
        if key.startswith('OPENAI_'):
            del env[key]
    commands = [('scripts.restore_evidence',), ('src.cli', 'aggregate'),
                ('scripts.paper_tables',), ('scripts.paper_figures',)]
    with (destination/'reproduction.log').open('w', encoding='utf8') as log:
        for command in commands:
            print('Running '+ ' '.join(command), flush=True)
            subprocess.run([sys.executable, '-m', *command], cwd=destination,
                           env=env, stdout=log, stderr=subprocess.STDOUT, check=True)
    for name in ('summary.json', 'paper-facts.json'):
        expected = json.loads((root/'results/summary'/name).read_text(encoding='utf8'))
        actual = json.loads((destination/'results/summary'/name).read_text(encoding='utf8'))
        assert_equivalent(expected, actual)
    tables = ('main-results.tex', 'static-results.tex', 'components.tex')
    for name in tables:
        if (root/'paper/tables'/name).read_bytes() != (destination/'paper/tables'/name).read_bytes():
            raise ValueError('Manuscript table differs: '+name)
    report = {'status':'passed', 'created_utc':datetime.now(timezone.utc).isoformat(),
              'python':sys.version.split()[0], 'evidence_files_verified':count, 'frozen':frozen,
              'summary_comparison':'all fields; absolute numeric tolerance 1e-10',
              'tables_byte_identical':list(tables), 'paid_api_calls':0,
              'note':'Offline reanalysis reproduces recorded measurements, not new model samples.'}
    (destination/'reproduction-check.json').write_text(json.dumps(report, indent=2), encoding='utf8')
    print(json.dumps(report, indent=2))
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT/'work/reproduced',
                        help='New directory; use a short path on Windows. Existing directories are never overwritten.')
    parser.add_argument('--verify-only', action='store_true', help='Check hashes without recomputing statistics.')
    args = parser.parse_args()
    if args.verify_only:
        print(json.dumps({'frozen':verify_frozen(ROOT), 'evidence_files':verify_evidence(ROOT/'results/evidence')}, indent=2))
    else:
        reproduce(ROOT, args.output)


if __name__ == '__main__':
    main()
