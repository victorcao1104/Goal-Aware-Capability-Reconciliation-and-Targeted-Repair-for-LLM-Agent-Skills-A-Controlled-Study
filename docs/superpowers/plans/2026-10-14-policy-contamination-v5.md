# Policy-contamination v5 implementation plan
Spec: docs/protocol/policy-contamination-v5.md
Execution: inline, user already authorized. Follow TDD and final fresh-context gpt-6-luna review. Preserve all frozen v1-v4 sources/evidence.
Global constraints: no credential output; original shared USD20 ledger; no API call before committed freeze; no oracle keys in payloads; no attack execution outside synthetic interpreter.

## Task 1: fixtures and semantic checks
- [x] Add tests_v5/test_study.py with failing tests for 92 cases, matched pairs, authority variation, provenance, and update gates.
- [x] Implement research_v5/fixtures.py and core.py.
Interfaces: make_cases()->list[case]; core.policy_errors(map,case)->dict; core.simulate(case,map,verdict)->dict; core.apply_update(initial,proposal)->map.
Acceptance: same task/workflow/catalog in each pair, only prose differs; authorized extras succeed; erroneous policy causes demonstrable mock effects; narrowing gate blocks new excess and retains existing excess; trusted test-harness allowlist expansion succeeds (not an authentication test).
Verification: unittest discover -s tests_v5.

## Task 2: model boundaries and auditable runner
- [x] Failing tests for task-only invariance, scan exclusion of task, graph/flat information equality, enum schemas, replay identity and model failure accounting.
- [x] Implement model.py, run.py, analysis.py and reproduce.py, using original Client/Budget without modifying it.
Interfaces: payload builders contain no oracle; content-addressed request record binds full request identity; collect() recomputes every saved trajectory; summarize(rows,requests) deterministic.
Acceptance: all roles fixed 2500 output tokens; matched auditor capabilities; errors retained; ledger prior/start separated; offline replay independent of .env.
Verification: full 120 prior tests plus new tests, frozen v4 replay.

## Task 3: premeasurement review and frozen execution
- [x] Fresh gpt-6-luna reviewer inspects protocol, implementation and tests; fix important flaws before paid measurement.
- [x] Freeze all measured files and commit; verify byte hashes match HEAD.
- [x] Run fixed jobs under cumulative USD20 ledger, retaining requests, trajectories, attempts, model IDs and usage. Do not retune.
- [x] Replay independently and seal evidence hashes.
Acceptance: exact job inventory or transparently recorded failures; source revision retained; zero unresolved budget reservations at successful completion.

## Task 4: reporting and publication
- [x] Generate English v5 report and Chinese findings, structured summary and self-contained offline instructions.
- [x] Add v5 to Windows/Linux CI, preserve old checks, review secrets before commit.
- [x] Push the authorized new research branch and create/attach stacked draft PR; verify CI (Windows/Linux remote checks tracked in PR #4).
Acceptance: distinguish contamination/semantic error/gating; negative results retained; actual incremental/cumulative cost; no claims to have reproduced named systems.
