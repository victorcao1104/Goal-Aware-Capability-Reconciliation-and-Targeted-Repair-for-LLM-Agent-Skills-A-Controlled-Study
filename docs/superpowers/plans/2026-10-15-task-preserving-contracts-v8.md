# Task-preserving contracts V8 Implementation Plan

> **For agentic workers:** Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Test whether untrusted narrowing destroys authorized task feasibility, without assuming a new mechanism wins.
**Architecture:** A finite action interpreter and independent policy-subset certificates, shared trusted-only contract extraction, one strong updater reused by all gates, frozen pilot and conditional held-out stage.
**Tech Stack:** Python 3.12, existing jsonschema and budget ledger; no new dependency.
**Spec:** docs/superpowers/specs/2026-10-15-task-preserving-contracts-research.md

## Global Constraints
- Preserve V1–V7 scientific files; work on existing authorized research/task-preserving-contracts-v8 branch.
- Existing dedicated credential authorization persists; no secret output or new key flow.
- USD20 cumulative, prior USD2.411697525; pilot <=1, formal <=5.
- No arbitrary Skill execution, external destinations, human-label claims, or hidden oracle repair.
- Formal gate is evidence of model-induced attack harm in both pilot task families in at least one model's oracle cohort. Synthetic bad updates alone do not qualify.
- If gate fails, complete a negative pilot report and reproducibility package; do not expand until a different design is justified.

## Review Focus
- True revocation must override goal preservation.
- Multiple valid plans must not be mistaken for a single indispensable action list.
- Initially wrong model contracts must remain wrong in end-to-end scores.
- Parse/transport failures remain in denominators and cannot count as safe successful updates.
- Replay must reconstruct inputs, response parsing, costs, outcomes, and stage decisions.

### Task 1: Finite fixtures and contract gates
Files: research_v8/fixtures.py, engine.py; tests_v8/test_core.py.
Interfaces: tasks(stage), variants(task), oracle(task), reachable(task, policy, goals), gate(method, task, contract, event, proposal).
- [x] Write/run tests for alternatives, dependencies, counts, revocation, malicious narrowing, and valid narrowing.
- [x] Implement finite exhaustive search and independent subset certificates.
- [x] Verify all fixture controls and existing tests. Expected: pass.

### Task 2: Matched model protocol and durable evidence
Files: research_v8/model.py, api.py, run.py, reproduce.py; tests_v8/test_protocol.py.
Interfaces: spec/request_key compatible with prior request-record shape; stage results isolated.
- [x] Test no hidden scoring labels in requests, request bounds, record replay/tampering, and go/no-go rule.
- [x] Implement source freeze, committed-source guard, serial budget settlement, and stage-safe resume.
- [x] Freeze both stages before pilot; commit and verify. Expected: <=1 / <=5 conservative envelopes.

### Task 3: Measurement and delivery
Files: research_v8/results/, report/, README.md; docs/progress/v8.md; CI workflow.
- [x] Run pilot on Mini, Luna none/low; apply fixed gate mechanically.
- [x] Evaluate conditional held-out stage: gate failed, so no formal calls; no prompt/sample change.
- [x] Independently review complete branch; resolve material findings without altering frozen measurements.
- [ ] Offline replay, full tests, secret scan, package and publish authorized research branch.
