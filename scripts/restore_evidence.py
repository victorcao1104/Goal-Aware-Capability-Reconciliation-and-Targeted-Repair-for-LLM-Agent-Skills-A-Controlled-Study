"""Materialize sanitized records in a NEW analysis copy; no model calls."""
import hashlib
import json
import shutil
from pathlib import Path


def main():
    root=Path(__file__).resolve().parent.parent
    source=root/'results/evidence'
    target=root/'results/raw_runs'
    if target.exists() and any(target.iterdir()):
        raise RuntimeError('Refusing to overwrite local raw research records; use a new extracted analysis copy')
    manifest=json.loads((source/'manifest.json').read_text(encoding='utf-8'))
    for record in manifest['files']:
        path=source/record['path']
        if hashlib.sha256(path.read_bytes()).hexdigest()!=record['sha256']:
            raise RuntimeError('Evidence hash mismatch: '+record['path'])
    for record in manifest['files']:
        destination=target/record['path']
        destination.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(source/record['path'],destination)
    # Aggregate reads transfer metadata, but does not need original attack text.
    transfer=root/'datasets/normalized/transfer.jsonl'
    metadata=root/'datasets/normalized/transfer-public-metadata.jsonl'
    if not transfer.exists():
        shutil.copyfile(metadata,transfer)
    print('Sanitized evidence restored for offline aggregation only. Do not run paid evaluation from this copy.')


if __name__=='__main__':
    main()
