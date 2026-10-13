$ErrorActionPreference = 'Stop'
$researchRoot = Split-Path -Parent $PSScriptRoot
$buildRoot = Join-Path $researchRoot 'work/container-build'
New-Item -ItemType Directory -Force -Path (Join-Path $buildRoot 'src') | Out-Null
foreach ($moduleName in @('__init__.py','contracts.py','sandbox.py','worker.py')) {
    Copy-Item -LiteralPath (Join-Path $researchRoot "src/$moduleName") -Destination (Join-Path $buildRoot "src/$moduleName")
}
@'
FROM python:3.12-slim
WORKDIR /app
COPY src /app/src
USER 65534:65534
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
ENTRYPOINT ["python","-m","src.worker"]
'@ | Set-Content -LiteralPath (Join-Path $buildRoot 'Dockerfile') -Encoding utf8
docker build --tag goal-skill-sandbox:research $buildRoot
if ($LASTEXITCODE -ne 0) { throw 'Container build failed' }
docker image inspect goal-skill-sandbox:research --format '{{.Id}}'
