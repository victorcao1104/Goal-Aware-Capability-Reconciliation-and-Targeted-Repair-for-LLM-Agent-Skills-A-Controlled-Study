# Authority Audit V4 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans inline; request one fresh-context review before measurement.

**Goal:** Prepare a reproducible study that separates permission contamination, behavior omissions and graph representation effects.

**Architecture:** Trusted clauses and inventory feed Contract; untrusted bundles feed Scan; common grounded records feed Flat/Graph Audit. All mock effects use generated contracts, never oracle-clamped policies. A deterministic task-only runtime baseline has the same authority source.

**Tech Stack:** Python 3.12, existing pinned dependencies and immutable gpt-6-luna client.

**Spec:** docs/protocol/authority-audit-v4.md

## Global constraints

Original cumulative US$20 cap; no preparation API calls; existing approved ignored credential only. Preserve v1–v3 frozen code. New work under research_v4/ and tests_v4/. User approved the direction and modifications; implement inline without redundant approval handoffs. This turn's deliverable is design, working preparation artifacts and pre-run verification; do not silently treat generated examples as observed attack successes.

## Review focus

- Negative quotations can be valid evidence strings but must not become claimed semantic proofs.
- Scanner outputs and audit findings cannot grant authority or acquire oracle fields.
- Missing extraction, unknown authorization and unreachable-in-this-instance branches have distinct denominators.
- Shared components must not confuse physical API cost with per-arm logical capacity.
- A live run must reject absent/incomplete prior ledger, uncommitted inputs and inconsistent cache payloads.

## Task 1: fixtures and deterministic mechanisms

- [x] tests_v4/test_core.py: observe failing tests for paired variants, role isolation, negative evidence boundary, source propagation and conditional execution.
- [x] research_v4/fixtures.py: six mechanisms, source-backed synthetic bundles and independent author labels.
- [x] research_v4/core.py: bounded workflow interpretation, contract validation, grounding, derived index, audit evaluation and strong runtime baseline.

## Task 2: equal model interfaces and reproducible runner

- [x] tests_v4/test_pipeline.py: role payload parity, no oracle leakage, cache identity, committed source and ledger guards.
- [x] research_v4/model.py: strict shared role schemas/prompts and matched limits.
- [x] research_v4/run.py: component schedule, explicit freeze/live modes, original client/ledger, auditable resumable requests.
- [x] research_v4/reproduce.py and analysis.py: complete no-API replay and paired descriptive outcomes.

## Task 3: preparation and review

- [x] Generate readable sample bundles and machine-readable fixture/schema manifests.
- [x] Verify synthetic reference and adversarial regression tests, old freezes, deterministic offline fake-client exercise (clearly not model results).
- [x] Independent gpt-6-luna review, resolve important findings, freeze and commit before any paid measurement.
- [ ] Publish prepared branch/draft PR and clearly mark model experiment as not yet run.

Review disposition: independent gpt-6-luna review found omission completeness, request-resume integrity and missingness reporting issues; all were addressed with regressions. Final read-only review found no remaining preparation blocker. No paid v4 run is authorized by this preparation checklist itself.
