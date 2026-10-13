# v2 execution ledger

Plan: docs/superpowers/plans/2026-10-14-upstream-repair-v2.md

- Branch created from v1.0.0. A+C+D selected; B/E conditional.
- Interfaces preflight: runtime feeds repair; public fixture payload excludes oracle; evaluator reads committed state only. New files do not change v1 interfaces.
- Ruling: use six development families and one live repair repeat, rather than claiming a powered formal study. Preserve all failures and negative findings.
- Task 1 complete: closed runtime, projection and opaque provenance, operation/source checks; red-to-green tests observed.
- Task 2 complete: 48 development fixtures, shared alternatives, graph index and independent evaluator; v1 61 tests, 30 frozen hashes and 3595 published evidence hashes pass.
- Fresh review found retry-accounting, paired-analysis and authorized-control wording issues. All resolved before measurement; reviewer cleared the run.
- Ruling: preserve the frozen v1 API client and record up to three transient dispatch attempts per logical request. This changes no model-output retry policy and preserves the cumulative US$20 cap.
- Added failed-response cost attribution and JSON pointer export regressions. Strengthened HandleSearch to scan all handles and skip satisfied goals; its old first-four truncation failed a control test before the fix.
- Pre-measurement focused suite: 25 tests pass. No model calls spent on fixture tuning. Timing records describe final-response duration, not total retry latency.
- Measurement complete: 72 logical requests / 72 dispatches, all returned gpt-6-luna; no failures, retries or unsettled reservations. Added estimate US$0.02077525; cumulative US$1.034103375.
- Offline replay verified 79 evidence hashes and all 384 trial states/metrics. GraphPlanner and Planner both 48/48 joint; HandleSearch 36/48. GraphNoSim and shuffled graph also 48/48.
- Ruling after measurement: progression target not reached. Preserve the null graph result and defer native/multi-Skill expansion. All model outputs supplied one candidate and syntactic pools contained at most two; disclose ceiling effects and lack of a meaningful selection test.
- Final publication review independently cross-checked 384 trials, 72 proposal records, paired zero differences, single-candidate responses and cost delta; no publication-claim blocker found.
- Publication audit: 106 changed/new files (2,947,387 bytes at audit time), no credential/private-path findings. Final local checks: 25 v2 tests, 61 v1 tests, 79 evidence checksums and 384 exact replays pass.
- Published only research/upstream-repair-v2; draft PR: https://github.com/victorcao1104/Goal-Aware-Capability-Reconciliation-and-Targeted-Repair-for-LLM-Agent-Skills-A-Controlled-Study/pull/1 . Main and v1.0.0 remain unchanged.

