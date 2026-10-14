# V3 execution ledger

Branch created from v2 commit 43aea34. Protocol drafted before implementation and measurement. The baseline may freely reconstruct dependency information. Pre-flight: fixture public views feed engine/model; only the independent evaluator reads reference data. New orchestration imports but never changes frozen v2 modules.

Pre-measurement review by a separate gpt-6-luna reviewer found a receipt-witness roundtrip discrepancy and a missing committed-input gate. Regression tests reproduced both and fixes passed. The live runner now rejects combined freeze/live invocation, requires the exact frozen source and manifest in HEAD, records every attempt in the original shared US$20 ledger, and writes public records atomically. The API client itself is explicitly hashed.

The reviewer also caught that the reused v2 shuffled index rotated only edges. V3 now consistently permutes edges, effect nodes and distance keys, with a dedicated test. The preliminary uncommitted v3 freeze was regenerated after this correction; no v3 API request had been made. V1/v2 frozen sources remain unchanged. Clean and authorized controls consume zero model requests.

Measurement began only after source/freeze commit `476c7255219ae06b77f200d991e57c9dc0244237`. All 324 trajectories completed with 220 successful gpt-6-luna requests and no transient retries or pending reservations. Attacked final joint success was 72/72 in every arm. GraphPlanner used 72 requests, Planner 75, GraphShuffled 73. Incremental conservative cost was US$0.223262500; cumulative original-ledger total US$1.257365875. No cases or failures were excluded and no frozen scientific code changed after measurement.

Local verification: 14 v3, 25 v2 and 61 v1 tests passed; v2 replay reproduced 384 trajectories and 79 evidence hashes; v3 replay verified 550 evidence files, all 324 trajectories and all 220 adaptive requests, including recomputed complexity certificates. The presentation helper initially resolved its base one directory too high; corrected before generating the report, without touching frozen experiment code. Figure inspected visually. Public v3 artifacts were checked against the configured credential and token patterns with zero matches. Cost entries reconcile exactly to the original cumulative ledger.

Windows full v1 reanalysis first hit the documented deep-path limit in a nested output directory. Re-run uses the shorter parent-workspace `v3-v1-replay` destination. This affects scratch output only. CI extracts the committed source into a short runner path on both Windows and Linux.

Independent gpt-6-luna publication review checked all 324 trajectories, 220 requests, raw-call inventory, token totals, attempts, costs, complexity denominators and both-language claims. One wording correction clarified that feedback fields/mechanism, rather than literal error messages, are shared. No numerical or publication-claim blocker remained.

Published research branch `research/dependency-repair-v3` and draft PR #2, stacked on v2 PR #1: https://github.com/victorcao1104/Goal-Aware-Capability-Reconciliation-and-Targeted-Repair-for-LLM-Agent-Skills-A-Controlled-Study/pull/2 . Main remains unchanged. Windows/Linux CI is configured to replay all three studies; see the PR checks for final status.
