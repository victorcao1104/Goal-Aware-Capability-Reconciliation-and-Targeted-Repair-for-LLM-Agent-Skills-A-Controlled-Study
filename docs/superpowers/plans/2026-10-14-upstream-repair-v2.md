# Upstream Repair v2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox syntax for tracking.

**Goal:** Test goal-constrained upstream repair against equally capable graph-free planning.
**Architecture:** Independent closed interpreter and fixtures, bounded repair search, optional Luna candidate proposals, separate exact-output evaluator. Preserve all v1 frozen artifacts.
**Tech Stack:** Python 3.12 standard library, existing jsonschema/API client and budget ledger.
**Spec:** docs/protocol/upstream-repair-v2-design.md

## Global Constraints
- gpt-6-luna only; cumulative US$20 ceiling.
- Six development families, two instances, four variants; no human-label claim.
- Four candidates, twelve actions, one model call per blocked case/method.
- Never expose oracle answers to candidate generation or selection.
- No modifications to v1 frozen source, datasets, tests or paper.

## Review Focus
- Nested/empty containers and opaque transforms must not erase private provenance.
- Conflicting grants and malformed resources must fail closed.
- Simulation or failed candidates must not mutate the original runtime.
- Correct-looking but incorrect values must pass only public ranking, then fail the independent oracle.
- Resume/failure accounting and graph ablations must retain matched budgets and denominators.

## Task 1: Shared enforcement and deterministic goals
Files: research_v2/runtime.py, research_v2/goals.py, tests_v2/test_runtime.py.
Interfaces: Runtime(config).step(action), clone(), snapshot(); public_loss(runtime, goals).
- [ ] Write failing tests for projection, opaque taint, policy conflict, clone isolation and unknown operations.
- [ ] Run unittest discovery; observe failures.
- [ ] Implement immutable Value(data, origins), bounded typed operations and dictionary-only effects.
- [ ] Run tests; require all assertions pass.
- [ ] Commit this independently testable component.

## Task 2: Fixtures, graph indexing and fair repair
Files: research_v2/fixtures.py, graph.py, repair.py, oracle.py; tests_v2/test_repair.py.
Interfaces: make_cases()->list[dict]; public_case(case)->dict; evaluate(case,runtime)->dict; repair(runtime,plans,goals,simulate=True)->dict.
- [ ] Write failing tests for six-family variant balance, oracle separation, legal recomputation, equal candidate limits and graph cycles.
- [ ] Implement independent fixture expectations and public-only goal selection.
- [ ] Implement shared edit enumeration, graph/source ordering and strong free-plan interface.
- [ ] Run tests and v1 frozen integrity checks.
- [ ] Commit implementation and preregistration before paid measurements.

## Task 3: Execute and package the mechanism pilot
Files: research_v2/run.py, reproduce.py, README.md, results/*; tests_v2/test_reproduction.py.
Interfaces: python -m research_v2.run --live; python -m research_v2.reproduce.
- [ ] Test offline evaluator and replay against retained proposals, including failed model calls.
- [ ] Review security and methodological fairness with a fresh reviewer, resolve important findings.
- [ ] Freeze inputs and run deterministic and live repair comparisons with the existing ledger.
- [ ] Recompute all metrics offline, preserve full denominators and v1 regression.
- [ ] Write actual findings and limitations; push only the research branch and open a draft PR.

## Execution ruling
The user already requested autonomous implementation of feasible suggestions and prior GitHub publication. Proceed inline without another design approval prompt; use a fresh reviewer before completion. Work on the explicitly requested branch in the dedicated existing repository. Existing project API authorization persists. This does not authorize merging main.

