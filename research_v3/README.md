# Multi-site dependency repair study (v3)

This branch tests whether a derived dependency index helps an unrestricted graph-free planner under equal model, output, repair and simulation limits. Both can infer dependencies and rewrite complete programs. All model calls use gpt-6-luna. This is an authored six-topology mechanism study, not an independent benchmark.

## Offline reproduction

From the repository root, with Python 3.12 and the pinned root dependencies installed:

```text
python -m unittest discover -s tests_v3
python -m research_v3.reproduce
```

No API key or Docker is needed. Replay verifies frozen code, older study freezes, all evidence hashes, complexity certificates, adaptive request/history linkage, every trajectory and every aggregate field. Published controls take zero model calls. Simulation uses synthetic files and a mock outbox; nothing is sent externally.

## Artifact map

- `fixtures.py`: six workflow families, trusted goals and separate expected values.
- `engine.py`: multi-edit/reordering/free-plan interface, isolated simulations and public feedback.
- `oracle.py`: independent exact-value and receipt-version evaluation.
- `model.py`: shared prompt/schema and graph-only payload difference.
- `audit.py`: exhaustive single-parameter catalogue and authored-correction subset certificates.
- `run.py`: frozen, committed-input gate; resumable requests; original cumulative budget.
- `analysis.py`: paired case estimates and descriptive topology-cluster bootstrap.
- `results/`: frozen inputs, public synthetic requests, attempts, trajectories and checksums.
- `../docs/protocol/dependency-repair-v3.md`: pre-measurement protocol.

The published experiment is immutable. Do not delete request caches to reroll failures. The live entry point requires the existing ignored `.env.local` and shared cost ledger; it can incur charges and is unnecessary for reproduction. A new scientific experiment needs its own versioned protocol, freeze and output namespace, while retaining cumulative accounting. The original v1 manuscript remains a frozen historical artifact.
