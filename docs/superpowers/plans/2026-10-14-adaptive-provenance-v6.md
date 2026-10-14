# Adaptive provenance v6 implementation plan

> Execution: superpowers:executing-plans inline; user has already authorized continuation. Final fresh-context reviewer uses gpt-6-luna.

Goal: improve Skill attack samples and compare GPT-4.1 Mini with Luna none/low without weakening the baseline.
Architecture: separate versioned fixtures, role interfaces, model-aware client, bounded development controller, held-out replay and reports. Reuse immutable Budget and file helpers; never change v1-v5 frozen code.
Tech stack: Python3.12, existing pinned jsonschema/matplotlib dependencies, Responses API.
Spec: docs/protocol/adaptive-provenance-v6.md.

## Global constraints
Original cumulative USD20 cap; v6 incremental USD5 ceiling; current priorUSD1.645422625. Same approved ignored credential. No real upload/delete or attacker-controlled tool execution.
Mini omits reasoning; Luna none/low explicit. Every role max2500 output. Per-call conservative total ceiling MiniUSD.016/LunaUSD.005.
All data authored; no human labels claim. Preserve all development attempts. Freeze selection before holdout.

## Task 1 — fixtures and evaluation
- [x] RED tests: safe/unsafe differ only one edge, all sinks approved, only unsafe carries rows, aggregate removes row content but retains lineage, forged declassification fails, legitimate authorized row upload succeeds.
- [x] Implement research_v6/fixtures.py and core.py with dynamic resources, closed semantics, role-independent labels.
- [x] GREEN unit checks and deterministic replay certificates.
Interfaces: make_case(context,variant,prose)->case; flow(actions,inventory)->facts; evaluate(policy,audit,case)->metrics.
## Task 2 — model-aware I/O and accounting
- [x] RED tests: Mini has no reasoning parameter, Luna configs differ in fingerprints/cost rates, per-case enum scope, no phantom branch, graph only adds edges, byte/output budget and USD5/20 limits.
- [x] Implement model.py and api.py; shared original Budget ledger, durable private/public records, all failures retained.
- [x] GREEN tests; exact request matching for offline replay.
## Task 3 — bounded adaptive search and holdout
- [x] RED tests: only dev feedback reaches attacker, 12-candidate schedule, deterministic top-two tie rule, immutable selection, exact holdout inventory, fail-closed metrics do not erase failed pairs.
- [x] Implement run.py/analysis.py/reproduce.py with separate preparation, calibration, development, selection and evaluation stages.
- [x] Fresh gpt-6-luna preflight review; repair important defects, run all tests, freeze and commit.
- [x] Execute calibration, dev search, then frozen holdout; stop rather than substitute if a requested model is unavailable.
## Task 4 — evidence and publication
- [x] Independent replay all requests, feedback, selection and held-out outcomes; reconcile exact per-model cost.
- [x] Report model and reasoning distinctions, contamination, full 2x2 attribution, legitimate utility, limits and failures; no retuning.
- [ ] Add CI, scan public records for secrets, push new branch and attach draft PR, verify Windows/Linux CI.

Transport amendment: original v6 was aborted before selection/holdout and retained. V6b completes the same scientific schedule with phase-aware parsing; see docs/protocol/adaptive-provenance-v6b-amendment.md.
