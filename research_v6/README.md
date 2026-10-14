# V6 adaptive provenance study — aborted before holdout

This version adds GPT-4.1 Mini without a reasoning parameter and GPT-6 Luna with none/low reasoning. It preserves the strong authority prompt and tests explicit graph edges against a fully capable flat action-list baseline. Source and tests were frozen before the first paid call.

## Reproduce without API access

Use Python 3.12 and install the root requirements.lock. On Windows use a short checkout path such as C:/research/gcr.

```text
python -m unittest discover -s tests_v6
python -m research_v6.reproduce --prepared
python -m research_v6b.reproduce
```

Replay validates source and evidence hashes, reconstructs every development feedback record and selection decision, regenerates held-out cases and all method outcomes, checks request inventories, and reconciles model-specific conservative cost estimates. No credentials or model calls are needed.

## Artifact map

- fixtures.py: synthetic sources, workflows, safe/unsafe counterfactuals and deterministic labels.
- model.py: role prompts, strict schemas, model settings and cost envelopes.
- core.py: content flow, evidence checks and simulated permission enforcement.
- api.py: cumulative-budget reservations, request identity and retained failures.
- run.py: calibration, fixed bounded attack development, immutable selection and holdout execution.
- results/: frozen sources, preparation certificates, all sanitized API records, selected and rejected candidates, trajectories and summary.
- report/: generated findings and diagnostic counts.
- ../docs/protocol/adaptive-provenance-v6.md: prospective design and limitations.

The existing live runner belongs to the frozen recorded measurement. Do not delete its evidence or rerun under a modified source revision. A new paid study requires a new version/output directory, explicit prior-cost reconciliation, approved credentials and a prospective freeze. The original cumulative ceiling remains USD20; this version uses an additional ceiling of USD5.

Results are synthetic and descriptive. Neither the isolated authority boundary nor graph edges establish security for arbitrary real Skill code. No independent human labeling is claimed. The original IEEE manuscript is a preserved v1 artifact; later-version findings are separate supplements.

V6 was stopped for a response-phase parsing defect. See results/aborted.json and the v6b amendment. No completed v6 measurement is claimed. Corrected results reside under research_v6b/.
