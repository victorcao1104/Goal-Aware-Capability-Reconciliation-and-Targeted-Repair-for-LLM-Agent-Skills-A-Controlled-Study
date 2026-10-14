# V5 policy contamination study

This supplement tests whether attacker-controlled Skill prose changes initial permissions, whether a graph helps a separately scoped auditor, and what a monotonic update gate does with correct or overbroad initial policies. It does not reproduce or claim attacks on SkillScope, Progent or CaMeL. See the [prospective protocol](../docs/protocol/policy-contamination-v5.md).

## Offline replay

Use Python 3.12; on Windows clone into a short directory (for example C:/research/gcr). Install the root requirements.lock, then run:

```text
python -m unittest discover -s tests_v5
python -m research_v5.reproduce --prepared
python -m research_v5.reproduce
```

The first preparation check only verifies fixtures and deterministic mechanism controls. Full replay verifies evidence hashes, every request identity, every trajectory, every summary field and recorded cost accounting. It needs no API key, Docker or model calls. Prior studies have their own replay commands.

## Data layout

- fixtures.py: 40 matched prose pairs plus 12 authority/utility controls; authored labels, no human annotation.
- core.py: ten exact permission atoms, grounding, provenance and in-memory effects.
- model.py: prompts and enum schemas; every role uses gpt-6-luna, low reasoning, 2500 output tokens.
- run.py: fixed jobs, precommitted freeze, deduplication, cumulative budget and auditable API records.
- results/cases.json and model-spec.json: frozen stimuli and model interfaces.
- results/mechanism-controls.json: deterministic intervention checks, not model performance.
- results/requests/: sanitized model outputs, payloads, accounting and source request fingerprints.
- results/trajectories/: derivable method outcomes and update outcomes.
- results/summary.json and evidence-manifest.json: deterministic statistics and hashes.

Identical inputs reuse one response within a repeat. Report physical calls separately from logical uses; repeats are not a substitute for new task families. Neutral partners have the same risky workflow with no inducement, so they are not harmless-workflow controls. Clean and explicitly authorized controls are separate.

## Live execution and provenance

Recorded measurements are frozen. Do not edit their inputs or overwrite results for a new run. A fresh paid replication must use a new run namespace and preserve these artifacts. The original authorized experiment used `python -m research_v5.run --live` after `--freeze` and committing all frozen sources. That runner deliberately requires the original private cumulative budget ledger and credential; it is not a one-command fresh experiment launcher for new users. Private API/provider records remain ignored; sanitized public evidence supports offline replay.

No actual upload, deletion, native Skill execution, or real authentication occurs. The trusted expansion control is a harness-supplied allowlist, never an approval extracted from Skill text. E3's correct/overbroad starting maps are authored interventions, not measured model errors. Exact clause IDs establish structural references only, not semantic correctness or independent human annotation.
