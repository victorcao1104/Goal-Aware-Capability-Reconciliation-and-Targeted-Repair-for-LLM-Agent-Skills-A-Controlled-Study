"""Create a secret-free local delivery from Git's non-ignored file inventory."""
import hashlib
import json
import re
import subprocess
import zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent


def main():
    root=ROOT
    files=subprocess.check_output(['git','ls-files','--cached','--others','--exclude-standard','-z'],cwd=root).decode().split('\0')
    files=sorted(set(name for name in files if name))
    forbidden=('.env.local','docs/input/','third_party/','results/raw_runs/','results/preformal/','work/','release/','.git/')
    selected=[]
    for name in files:
        path=root/name
        if not path.is_file():
            continue
        if any(name==p or name.startswith(p) for p in forbidden) or name.endswith(('.pem','.key')):
            raise RuntimeError('Forbidden file in release inventory: '+name)
        if name.startswith('literature/') and path.suffix.lower()=='.pdf':
            raise RuntimeError('Original paper must not enter public release')
        raw=path.read_bytes()
        if re.search(rb'\bsk-(?:proj-)?[A-Za-z0-9_-]{20,}|-----BEGIN [A-Z ]*PRIVATE KEY-----',raw):
            raise RuntimeError('Potential credential detected; packaging stopped without printing contents')
        selected.append((name,raw))
    manifest={'file_count':len(selected),'files':[{'path':name,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()} for name,raw in selected],
              'excluded':'credentials, private coursework, original papers/bundles, raw local payloads, development records, caches, Git metadata'}
    destination=root/'release'
    destination.mkdir(exist_ok=True)
    archive=destination/'goal-aware-skill-study.zip'
    prefix='goal-aware-skill-study/'
    with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as output:
        for name,raw in selected:
            output.writestr(prefix+name,raw)
        output.writestr(prefix+'release-manifest.json',json.dumps(manifest,indent=2))
    with zipfile.ZipFile(archive) as check:
        if check.testzip() is not None:
            raise RuntimeError('Archive integrity check failed')
        for item in manifest['files']:
            if hashlib.sha256(check.read(prefix+item['path'])).hexdigest()!=item['sha256']:
                raise RuntimeError('Archive content hash mismatch')
    result={'archive':str(archive),'bytes':archive.stat().st_size,'sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),
            'included_files':len(selected),'secret_pattern_findings':0,'archive_integrity':'passed'}
    (destination/'package-audit.json').write_text(json.dumps(result,indent=2),encoding='utf8')
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    main()
