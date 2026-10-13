# Goal-aware Skill research implementation plan

> **For agentic workers:** Use superpowers:executing-plans to implement this plan task-by-task. The user explicitly requested autonomous inline execution after the acquisition subagent and setup; do not add intermediate approval gates.

**Goal:** Implement, measure and honestly report task-authority reconciliation and selective repair in a bounded Skill-agent environment.

**Architecture:** A host-only gpt-6-luna client emits validated JSON. Independent task and skill analyzers feed deterministic graph/path and repair logic. An isolated, network-disabled container executes only our controlled tools on synthetic resources; public SkillInject bundles are static inputs, never host-executed code. Evaluation-only labels and acceptance criteria do not enter analyzers.

**Tech stack:** Python standard library for runtime and HTTP, JSON schemas, unittest, Docker Linux isolation, bundled numpy/scipy/matplotlib for statistics, actual IEEE LaTeX manuscript and PDF.

**Spec:** User handbook in `docs/input/experiment-handbook.zh.txt`, with overriding user decisions and rubric in `docs/protocol/requirements-and-decisions.md`.

## Global constraints

- gpt-6-luna only; all billable calls within US$20, conservative reservation before dispatch, persisted usage ledger, bounded retries.
- Deadline 2026-11-12; no publication, no actual external messages, no real private data or credentials in agent inputs.
- Keep original Skill bundles complete on disk; record omitted/unsupported content in any analyzer projection.
- Separate original static-benchmark results, adapted execution fixtures, and independently authored synthetic controls. No official benchmark reproduction claim for adapted tasks.
- Independent human annotations unavailable by user choice. Benchmark labels and executable specifications are reference evidence, not human labels.
- Freeze test manifest, prompts and code/config hashes before test inference. No tuning based on test outcomes.
- Use same model, maximum steps, resources and deterministic evaluators across B0–B5. Model refusals and environment errors remain distinct.

## Review focus

1. Prefix host/path tricks must not widen authority; tests pin canonical identities and traversal rejection.
2. Shared authorized endpoint with unrelated sensitive data must remain distinguishable from legitimate upload; provenance-preserving tools and paired tests.
3. B0 must log effects without accidentally applying the full gateway; baseline distinction tests.
4. Duplicate/missing runs or budget uncertainty must not be counted as a secure success; ledger/completeness tests.
5. Evaluation labels must not appear in model payloads; allowlisted payload construction and leakage tests.

## Tasks and completion evidence

### Task 1: Core contracts, graph and gateway

Files: `src/schema.py`, `src/contracts.py`, `src/graph.py`, `src/repair.py`, `src/sandbox.py`, `tests/test_core.py`.

Interfaces: `normalize_resource(str)->str`; `match_action(contract, action, provenance:bool)->str`; `find_goals(contract, graph)->list[dict]`; `select_repair(findings, graph)->dict`; `Sandbox(fixture, contract, method, policy).step(action)->dict`.

- [x] Write failing tests for traversal, hostname suffix, exact task scope, dataflow through intermediate output, conditional infeasibility, minimal repair preserving clean path, and deny without side effects.
- [x] Implement the smallest validated core satisfying those tests; run the complete unittest suite.
- [x] Add container worker with no network, mounts, credentials or arbitrary shell; verify identical event results in local unit fixtures and isolated container.

### Task 2: Traceable datasets and evaluation

Files: `src/dataset.py`, `src/evaluation.py`, `scripts/prepare_data.py`, `tests/test_data.py`; outputs under `datasets/`.

Interfaces: `prepare_skillinject(root, output)->list[dict]`; `prepare_controls(output)->list[dict]`; `model_input(case, role)->dict`; `evaluate_run(case, trace, state)->dict`.

- [x] Test source mapping, clean/injected pairing, deterministic fixture acceptance independent of defense, split grouping and evaluation-label exclusion.
- [x] Inspect original JSON structures and official builder; implement audited passive bundle construction with exact insertion parity and record excluded resources.
- [x] Build controlled G1–G3 cases with benign, malicious, authorized and unauthorized dual-use variants, known executable ground truth, and held-out named families; broad workflow templates recur, as disclosed in deviations-from-handbook.md.
- [x] Save selection/exclusion CSV, source commit/hash, split IDs and reference-label provenance. Do not describe generated labels as independent human ground truth.

### Task 3: Model pipeline and bounded runner

Files: `src/api.py`, `src/analyzers.py`, `src/runner.py`, `src/cli.py`, `configs/eval.json`, `tests/test_pipeline.py`, `prompts/`.

Interfaces: `Client.generate(role, payload, schema, call_id)->dict`; `analyze_task(prompt, bindings)->dict`; `analyze_skill(bundle)->dict`; `run_case(case, method, repeat)->dict`.

- [x] Test budget reservation/settlement and interrupted resume, schema/evidence rejection and baseline configurations.
- [x] Implement credential-free logging, public/synthetic-only payloads, structured outputs, prompt hashes and source-span verification.
- [x] Implement B0 no defense, B1 skill-only scanner, B2 task-only gateway, B3 action reconciliation, B4 goal-aware coarse block, B5 targeted repair; retain explicit B1 and SkillScope-inspired approximation labels.
- [x] Pilot on development cases only. Verify normal-task capability and costs, freeze run manifest, then run paired repeated experiments and feasible ablations.

### Task 4: Analysis and reproducibility

Files: `src/analysis.py`, `scripts/validate_results.py`, `scripts/report.py`, `tests/test_analysis.py`.

- [x] Test metric denominators, paired differences, bootstrap grouping, missing-run detection and accounting with hand-calculated fixtures.
- [x] Generate component accuracy only where reference evidence supports it; report static label agreement separately from semantic graph/path truth.
- [x] Compute ASR, TSR, FBR, joint repair success, clustered intervals and overhead from preserved records; preserve negative findings.
- [x] Produce architecture, worked-example, security/utility and ablation figures plus trace-backed failure cases.

### Task 5: IEEE paper and audited delivery

Files: `paper/main.tex`, `paper/references.bib`, figures, reproducibility README and release manifest.

- [x] Read relevant full papers and prior review, map every claim/citation to a verified source.
- [x] Write from measured results: 10–12 body pages, 150–200-word abstract, related work <=1 page, references >=10 and <=1 page, conclusion about 1 page.
- [x] Compile actual IEEE LaTeX, render and inspect every page, fix layout and verify figures/tables against metrics.
- [x] Obtain one fresh code/research-integrity review (required by inline execution skill), fix important findings with regression tests, rerun only affected experiments if necessary with version disclosure.
- [x] Build secret-free GitHub-ready package with original code, permitted data, acquisition instructions, sanitized evidence, PDF and LaTeX; verify archive and report true cost/limitations.

## Process adaptation

The workspace is an explicitly requested new independent repository (`research` branch), not a modification of the old experiment. A separate Git worktree would not isolate anything further. On Windows, progress is kept in `docs/progress/ledger.md` rather than POSIX skill helper scripts. These adaptations do not weaken tests or evidence requirements. Preserve progress files as requested process materials.


## Final completion record

The bounded study is implemented and measured; checked items refer to the implemented scope, not every capability proposed in the original handbook. Strict unseen-template transfer, human path labels, general script analysis and native benchmark execution were not implemented and are explicitly recorded as deviations. B2P and B2R were added as stronger comparators before freezing. Figure/table formatting helpers were added after freeze without modifying scientific analysis. Evidence: 56 passing pre-freeze tests; 1,920 valid scheduled runs; 167/168 resolved static cases; final research review and paper audit. Offline package verification is recorded separately.
