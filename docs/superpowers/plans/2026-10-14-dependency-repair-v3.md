# Multi-site Dependency Repair v3 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans inline. Track completion in docs/progress/dependency-repair-v3.md.

**Goal:** Test graph indexing on real multi-site repair without weakening graph-free planning.
**Architecture:** New fixtures and orchestration reuse frozen v2 tools. Both planners share patch/free-plan interfaces, simulation and public feedback. Exact oracle stays separate.
**Tech Stack:** Python 3.12, existing API client and dependencies.
**Spec:** docs/protocol/dependency-repair-v3.md

## Global constraints
gpt-6-luna; cumulative US$20; no oracle feedback; 2 requests, 4 candidates/request, 16 edits/moves or 96 actions/candidate; 3 repeats; no changes to v1/v2 scientific files.
## Review focus
- Multi-site complexity cannot be only a longer single-fix task.
- Reordering must preserve actual resource versions, not just names.
- Candidate feedback and graph cannot leak the reference repair.
- Adaptive budgets and failed API attempts must remain paired and auditable.
- Offline replay must verify the full schedule and request-to-trial linkage.

## Task 1: Workflows and authority (research_v3/fixtures.py, oracle.py, engine.py; tests_v3/test_core.py)
- [ ] Write and observe failing tests for six topologies, correct references, blocked attacks, single-edit failure, multiple-edit restoration and stale receipt rejection.
- [ ] Implement fixtures, independent expected outputs and bounded candidate execution.
- [ ] Verify and record complexity certificates, including every catalogued single edit.

## Task 2: Equal model interfaces and study (research_v3/model.py, run.py, analysis.py; tests_v3/test_study.py)
- [ ] Test oracle exclusion, payload parity except index, budget limits, retry accounting and resume.
- [ ] Implement identical prompts, two-round feedback, three-repeat schedule, paired metrics and manifest.
- [ ] Obtain fresh review, fix important findings, freeze before paid calls.

## Task 3: Evidence and delivery (research_v3/reproduce.py, README.md, RESULTS.md; CI)
- [ ] Run Luna trajectories without exceeding the shared cap; preserve failures.
- [ ] Replay full evidence offline and verify old freezes/tests.
- [ ] Document positive or null findings with limitations, review claims, push branch and draft PR.

## Ruling
The user's explicit autonomous continuation and existing key/publication authorization supersede redundant approval handoffs. Implement inline with a fresh reviewer; do not ask the user to reconfirm choices already specified.
