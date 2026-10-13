# Development pilot results (2026-10-14)

This is an induced-repair mechanism pilot, not a native attack benchmark. Six authored development families, two data instances and four variants produce 48 matched cases. Eight methods produce 384 trial records. Only 72 trials requested model proposals; clean/authorized controls and GraphNoSim do not make extra model calls.

| Method | Joint safety + exact task success | Recovery after a block | Trials with unsafe committed effects | Candidates simulated |
| --- | ---: | ---: | ---: | ---: |
| Gate | 24/48 (50%) | 0/24 | 0/48 | 0 |
| HandleSearch | 36/48 (75%) | 12/24 | 0/48 | 12 |
| ProgramSearch | 48/48 (100%) | 24/24 | 0/48 | 38 |
| GraphSearch | 48/48 (100%) | 24/24 | 0/48 | 38 |
| Planner | 48/48 (100%) | 24/24 | 0/48 | 24 |
| GraphPlanner | 48/48 (100%) | 24/24 | 0/48 | 24 |
| GraphShuffled | 48/48 (100%) | 24/24 | 0/48 | 24 |
| GraphNoSim | 48/48 (100%) | 24/24 | 0/48 | 0 |

HandleSearch restores every wrong-destination case (12/12) but none of the source-contamination cases requiring recomputation (0/12). Both syntactic upstream search and model planning restore all 12 recomputation cases. This supports the utility of upstream repair beyond reuse of existing handles in this environment.

**No incremental graph benefit was observed.** GraphPlanner minus Planner is zero percentage points, overall and conditional on blocking, in each of the six families. GraphSearch also evaluates exactly as many candidates as ProgramSearch (38). Model planning executes 55 repair actions without the graph and 56 with it; there is no measured action-count saving. This is a ceiling result, not evidence that the methods are universally equivalent.

## Why the null graph result is not a definitive graph evaluation

- Every blocked case has only one or two syntactic seed alternatives: the four-candidate cap never binds. The repaired programs need only one local edit, despite involving multiple operations.
- All 72 model responses contain exactly one plan. GraphNoSim therefore does not test selection among competing model candidates; it checks replay without the redundant single-candidate simulation.
- Correct and shuffled dependency indices produce the same success. The source program remains available in all arms, so a model may reconstruct dependencies or simply ignore the added index.
- Public goal predicates are necessary shape/type conditions. They are not full semantic contracts. The separate exact-result oracle, rather than the selector, establishes these task-success counts.
- One repair sample per arm/case, six authored development families, structured authored permissions, and no independent human review do not establish external validity. The descriptive family-bootstrap interval [0, 0] reflects zero observed paired differences and must not be presented as an equivalence test.
- Effects exist only in dictionary state. All prefixes are scripted; none of these numbers is a native prompt-injection ASR.

## Cost and model evidence

| Model arm | Logical requests / actual attempts | Input / output tokens | Conservative usage estimate |
| --- | ---: | ---: | ---: |
| Planner | 24 / 24 | 39,918 / 3,513 | US$0.00674625 |
| GraphPlanner | 24 / 24 | 41,802 / 3,622 | US$0.00703625 |
| GraphShuffled | 24 / 24 | 41,658 / 3,571 | US$0.00699275 |

All requests and returned models are gpt-6-luna. No API failures, retries or pending reservations occurred. Added estimated usage is **US$0.02077525**; the study ledger increased from US$1.013328125 to **US$1.034103375**, below US$20. These are token-based conservative usage estimates, not a reconciled provider invoice. Recorded model timing covers final-response durations, not a controlled end-to-end latency study.

## Decision and next research question

The pre-measurement progression target (ten percentage points of incremental graph success, or useful measured search savings) was not reached. Native and multi-Skill expansion is therefore deferred. Preserve this negative result rather than presenting generic repair gains as graph novelty.

A defensible current contribution is **task-constrained upstream repair with independent exact acceptance in a closed runtime**. Before a stronger graph claim, a separate preregistered dataset should require interacting changes, genuine alternative branches and budget-constrained search; graph-free methods must retain identical planning tools and access to the original workflow. It should also include irrelevant or misleading graphs and quantify costs. This proposal is future work, not evidence already collected.

## Evidence

- [Pre-measurement freeze](results/freeze.json)
- [Full trial records](results/trials.json)
- [Paired differences and model usage](results/analysis.json)
- [Complete summary](results/summary.json)
- [Evidence checksums](results/evidence-manifest.json)
- [Chinese feasibility and findings](../docs/v2-feasibility-and-findings.zh.md)

Run `python -m research_v2.reproduce` to verify 79 evidence hashes and replay all 384 trial records offline. The 25 v2 tests and original 61 tests pass; all 30 original frozen inputs and 3,595 original evidence files remain unchanged.

