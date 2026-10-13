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

