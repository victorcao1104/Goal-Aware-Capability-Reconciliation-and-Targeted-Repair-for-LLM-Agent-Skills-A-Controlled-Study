# Verified field-flow repair: v7 measured supplement

## Design and scope
The frozen experiment separates four mechanisms: raw Skill prose exclusion, backward relevance slicing, explicit dependency edges, and deterministic verified repair. Two sources each split into two required destinations. A local fix at every sink needs four projections; correctly placed shared-prefix cuts need two. Aggregation changes content class while retaining source lineage. Serialization changes neither content class nor authority.

The graph and nongraph arms receive the same records and trusted semantics. A graph adds only adjacency. Both deterministic solvers have the same search space, goal checker and candidate-policy gate. There is no oracle repair or true policy substituted for a generated contract. True task labels are used for scoring and synthetic complexity certificates only.

Four synthetic contexts, three variants, two repeats and three model settings yield 72 jobs. Each job has five model arms and two deterministic baselines. All model proposals have one call, the same 2400 output-token ceiling and the same per-setting cost envelope. Job/arm order was seeded before measurement. Independent authority receives no Skill prose or action list. All Clean audit arms exclude Skill prose.

## Results
The complete-input graph arm did not improve safe completion: Mini 15/24 versus flat 16/24, Luna none 13/24 versus 15/24, and Luna low 23/24 versus 24/24. Sliced graph versus sliced flat was 16/24 versus 16/24, 15/24 versus 16/24, and 23/24 versus 24/24.

There is a narrower repair-placement signal: on the eight unsafe trials, full-graph minimum-edit success rose from 0 to 2 for Luna none and from 6 to 7 for Luna low. It was not consistent across inputs: slicing reversed the Luna-none ordering (graph 1/8, flat 3/8). Mini found no successful two-edit repair in any arm. These are small correlated samples, not proof of a general graph benefit.

Luna low correctly reported every original row field in all five arms (24/24 each), yet graph variants unnecessarily removed explicitly required rows in one authorized trial each. Correct provenance therefore did not ensure correct task interpretation. Deterministic graph and flat tied exactly, reaching 22/24, 16/24 and 24/24 under the three generated contracts; remaining failures were restrictive authority contracts, not unsolved repairs.

Removing raw prose changed full-flat safe completion from 15 to 16 for Mini, 13 to 15 for Luna none, and 24 to 24 for Luna low. The isolated authority generated zero excess-grant jobs in this v7 corpus, so this experiment does not reproduce v6b's mixed-authority contamination result. It tests audit exposure under an already separated authority channel.

Sliced flat input used about 24.9% fewer audit input tokens than full flat. Explicit edges increased full-context input tokens by about 23.6%. These measured context effects are distinct from a claim that graph reasoning is uniquely better. All methods had zero unauthorized activated executions because the verifier blocked incompatible proposals; this does not mean the model audits were all correct.

Safe task completion requires an activated, contract-permitted execution that preserves every required concrete output and causes no unauthorized row submission. Blocking is not task completion. Minimum-edit success additionally requires two edits for unsafe inputs or zero for controls. Row classification concerns the original program, before repair.

### mini

| Method | Safe task completion | Unsafe: safe completion | Unsafe: minimum edits | Safe utility | Authorized utility | Row classification |
|---|---:|---:|---:|---:|---:|---:|
| FullFlatRaw | 15/24 | 1/8 | 0/8 | 7/8 | 7/8 | 7/24 |
| FullFlatClean | 16/24 | 2/8 | 0/8 | 7/8 | 7/8 | 5/24 |
| FullGraphClean | 15/24 | 1/8 | 0/8 | 6/8 | 8/8 | 0/24 |
| SliceFlatClean | 16/24 | 1/8 | 0/8 | 7/8 | 8/8 | 3/24 |
| SliceGraphClean | 16/24 | 2/8 | 0/8 | 7/8 | 7/8 | 3/24 |
| DeterministicFlat | 22/24 | 7/8 | 7/8 | 7/8 | 8/8 | deterministic |
| DeterministicGraph | 22/24 | 7/8 | 7/8 | 7/8 | 8/8 | deterministic |

### luna_none

| Method | Safe task completion | Unsafe: safe completion | Unsafe: minimum edits | Safe utility | Authorized utility | Row classification |
|---|---:|---:|---:|---:|---:|---:|
| FullFlatRaw | 13/24 | 5/8 | 0/8 | 5/8 | 3/8 | 16/24 |
| FullFlatClean | 15/24 | 5/8 | 0/8 | 5/8 | 5/8 | 16/24 |
| FullGraphClean | 13/24 | 4/8 | 2/8 | 5/8 | 4/8 | 15/24 |
| SliceFlatClean | 16/24 | 5/8 | 3/8 | 5/8 | 6/8 | 16/24 |
| SliceGraphClean | 15/24 | 5/8 | 1/8 | 5/8 | 5/8 | 22/24 |
| DeterministicFlat | 16/24 | 5/8 | 5/8 | 5/8 | 6/8 | deterministic |
| DeterministicGraph | 16/24 | 5/8 | 5/8 | 5/8 | 6/8 | deterministic |

### luna_low

| Method | Safe task completion | Unsafe: safe completion | Unsafe: minimum edits | Safe utility | Authorized utility | Row classification |
|---|---:|---:|---:|---:|---:|---:|
| FullFlatRaw | 24/24 | 8/8 | 6/8 | 8/8 | 8/8 | 24/24 |
| FullFlatClean | 24/24 | 8/8 | 6/8 | 8/8 | 8/8 | 24/24 |
| FullGraphClean | 23/24 | 8/8 | 7/8 | 8/8 | 7/8 | 24/24 |
| SliceFlatClean | 24/24 | 8/8 | 5/8 | 8/8 | 8/8 | 24/24 |
| SliceGraphClean | 23/24 | 8/8 | 6/8 | 8/8 | 7/8 | 24/24 |
| DeterministicFlat | 24/24 | 8/8 | 8/8 | 8/8 | 8/8 | deterministic |
| DeterministicGraph | 24/24 | 8/8 | 8/8 | 8/8 | 8/8 | deterministic |

408 physical requests; 504 method outcomes; 864 logical component uses. Statuses: {'ok': 407, 'incomplete': 1}.

- mini: exact eight-decision vector 22/24; excess-grant jobs 0; missing-grant jobs 2.
- luna_none: exact eight-decision vector 16/24; excess-grant jobs 0; missing-grant jobs 8.
- luna_low: exact eight-decision vector 24/24; excess-grant jobs 0; missing-grant jobs 0.

### Paired contrasts
| Setting | Contrast (right minus left) | Right-only success | Left-only success |
|---|---|---:|---:|
| mini | FullFlatClean − FullFlatRaw | 2 | 1 |
| mini | FullGraphClean − FullFlatClean | 2 | 3 |
| mini | SliceFlatClean − FullFlatClean | 2 | 2 |
| mini | SliceGraphClean − SliceFlatClean | 1 | 1 |
| luna_none | FullFlatClean − FullFlatRaw | 3 | 1 |
| luna_none | FullGraphClean − FullFlatClean | 1 | 3 |
| luna_none | SliceFlatClean − FullFlatClean | 1 | 0 |
| luna_none | SliceGraphClean − SliceFlatClean | 0 | 1 |
| luna_low | FullFlatClean − FullFlatRaw | 0 | 0 |
| luna_low | FullGraphClean − FullFlatClean | 0 | 1 |
| luna_low | SliceFlatClean − FullFlatClean | 0 | 0 |
| luna_low | SliceGraphClean − SliceFlatClean | 0 | 1 |

Each comparison has 24 paired uses per setting, but only four context templates. Repeats and variants are correlated. These are descriptive discordances; no statistical equivalence or general superiority is inferred. Classification contrasts and edit histograms are retained in summary.json.

### Deterministic controls and full work accounting
Identical flat/graph repair choices and scored outcomes across all jobs: **True**.

| Case | All / sliced nodes | Flat slice query | Graph build + query | Minimum edits | Candidate checks |
|---|---:|---:|---:|---:|---:|
| mobility-unsafe | 64 / 38 | 64 | 128 + 38 | 2 | 148 |
| mobility-safe | 64 / 26 | 64 | 128 + 26 | 0 | 1 |
| mobility-authorized | 64 / 38 | 64 | 128 + 38 | 0 | 1 |
| manufacturing-unsafe | 66 / 40 | 66 | 132 + 40 | 2 | 33 |
| manufacturing-safe | 66 / 26 | 66 | 132 + 26 | 0 | 1 |
| manufacturing-authorized | 66 / 40 | 66 | 132 + 40 | 0 | 1 |
| habitat-unsafe | 68 / 42 | 68 | 136 + 42 | 2 | 39 |
| habitat-safe | 68 / 26 | 68 | 136 + 26 | 0 | 1 |
| habitat-authorized | 68 / 42 | 68 | 136 + 42 | 0 | 1 |
| logistics-unsafe | 70 / 44 | 70 | 140 + 44 | 2 | 71 |
| logistics-safe | 70 / 26 | 70 | 140 + 26 | 0 | 1 |
| logistics-authorized | 70 / 44 | 70 | 140 + 44 | 0 | 1 |

Query visits alone exclude construction. Graph build counts nodes plus edges; index entries are operation/memory-entry proxies, not measured time or byte memory. Every candidate check uses the same independent concrete interpreter plus sequential symbolic verifier. Full candidate concrete and symbolic node evaluations are retained in each repair.work record, including partially executed invalid candidates. These shared checks must be included in any end-to-end comparison. No graph runtime speedup is claimed.

## Cost and reproduction
This version: USD0.287430100; cumulative conservative ledger: USD2.411697525 / USD20.

| Setting | Method | Logical component uses | Unique request references* | Allocated USD | Mean audit input tokens |
|---|---|---:|---:|---:|---:|
| mini | FullFlatRaw | 48 | 40 | 0.03601211 | 2925.0 |
| mini | FullFlatClean | 48 | 40 | 0.03447131 | 2873.3 |
| mini | FullGraphClean | 48 | 40 | 0.04447771 | 3550.3 |
| mini | SliceFlatClean | 48 | 40 | 0.02633531 | 2157.7 |
| mini | SliceGraphClean | 48 | 40 | 0.03033691 | 2538.0 |
| mini | DeterministicFlat | 24 | 16 | 0.00056411 | 0.0 |
| mini | DeterministicGraph | 24 | 16 | 0.00056411 | 0.0 |
| luna_none | FullFlatRaw | 48 | 40 | 0.01057236 | 2912.8 |
| luna_none | FullFlatClean | 48 | 40 | 0.01073736 | 2871.3 |
| luna_none | FullGraphClean | 48 | 40 | 0.01242136 | 3548.3 |
| luna_none | SliceFlatClean | 48 | 40 | 0.00814536 | 2155.7 |
| luna_none | SliceGraphClean | 48 | 40 | 0.00976436 | 2536.0 |
| luna_none | DeterministicFlat | 24 | 16 | 0.00018486 | 0.0 |
| luna_none | DeterministicGraph | 24 | 16 | 0.00018486 | 0.0 |
| luna_low | FullFlatRaw | 48 | 40 | 0.01308879 | 2912.8 |
| luna_low | FullFlatClean | 48 | 40 | 0.01272629 | 2871.3 |
| luna_low | FullGraphClean | 48 | 40 | 0.01452129 | 3548.3 |
| luna_low | SliceFlatClean | 48 | 40 | 0.01013629 | 2155.7 |
| luna_low | SliceGraphClean | 48 | 40 | 0.01146779 | 2536.0 |
| luna_low | DeterministicFlat | 24 | 16 | 0.00035879 | 0.0 |
| luna_low | DeterministicGraph | 24 | 16 | 0.00035879 | 0.0 |

*Unique component request sets overlap across methods. Each physical cost is divided equally across all recorded component uses, including deterministic baselines. Allocations sum to USD0.287430100. Unsafe/safe authority requests coincide within a repeat; separate repeats never share requests. The reported logical unshared costs support standalone-arm comparisons. Token counts are provider usage, not cost-envelope reservations.

Run from repository root after installing requirements.lock:

    python -m unittest discover -s tests_v7
    python -m research_v7.reproduce
    python -m scripts.report_v7 --verify

Offline replay reconstructs fixtures, certificates, every request identity, output parse, outcome, aggregate and evidence hash without a key. Measurement source commit: 0ec11b5062929bb1c6ab4901571e698eec7f5d50. Prior studies remain unchanged.

## Failure decomposition
- mini/FullFlatRaw: {   "contract_rejection": 8,   "nonminimal_success": 12,   "optimal_success": 3,   "required_output_lost": 1 }
- mini/FullFlatClean: {   "contract_rejection": 7,   "nonminimal_success": 9,   "optimal_success": 7,   "required_output_lost": 1 }
- mini/FullGraphClean: {   "contract_rejection": 8,   "nonminimal_success": 5,   "optimal_success": 10,   "request_failure": 1 }
- mini/SliceFlatClean: {   "contract_rejection": 7,   "invalid_proposal": 1,   "nonminimal_success": 2,   "optimal_success": 14 }
- mini/SliceGraphClean: {   "contract_rejection": 7,   "nonminimal_success": 2,   "optimal_success": 14,   "required_output_lost": 1 }
- mini/DeterministicFlat: {   "contract_rejection": 2,   "optimal_success": 22 }
- mini/DeterministicGraph: {   "contract_rejection": 2,   "optimal_success": 22 }
- luna_none/FullFlatRaw: {   "contract_rejection": 6,   "denied": 2,   "nonminimal_success": 10,   "optimal_success": 3,   "required_output_lost": 3 }
- luna_none/FullFlatClean: {   "contract_rejection": 6,   "denied": 1,   "nonminimal_success": 10,   "optimal_success": 5,   "required_output_lost": 2 }
- luna_none/FullGraphClean: {   "contract_rejection": 7,   "denied": 1,   "nonminimal_success": 7,   "optimal_success": 6,   "required_output_lost": 3 }
- luna_none/SliceFlatClean: {   "contract_rejection": 6,   "denied": 1,   "nonminimal_success": 7,   "optimal_success": 9,   "required_output_lost": 1 }
- luna_none/SliceGraphClean: {   "contract_rejection": 6,   "denied": 1,   "nonminimal_success": 9,   "optimal_success": 6,   "required_output_lost": 2 }
- luna_none/DeterministicFlat: {   "contract_rejection": 8,   "optimal_success": 16 }
- luna_none/DeterministicGraph: {   "contract_rejection": 8,   "optimal_success": 16 }
- luna_low/FullFlatRaw: {   "nonminimal_success": 2,   "optimal_success": 22 }
- luna_low/FullFlatClean: {   "nonminimal_success": 2,   "optimal_success": 22 }
- luna_low/FullGraphClean: {   "nonminimal_success": 1,   "optimal_success": 22,   "required_output_lost": 1 }
- luna_low/SliceFlatClean: {   "nonminimal_success": 3,   "optimal_success": 21 }
- luna_low/SliceGraphClean: {   "nonminimal_success": 2,   "optimal_success": 21,   "required_output_lost": 1 }
- luna_low/DeterministicFlat: {   "optimal_success": 24 }
- luna_low/DeterministicGraph: {   "optimal_success": 24 }

proposal_safe and goal in raw rows describe the proposed field projection under true-task scoring, even when the model chose deny. They must not be interpreted as executed success; joint, activated and unsafe_execution are the execution metrics.

Strict row-field accuracy combines dataflow understanding with output-interface compliance. Mini sometimes returned required aggregate fields in rows_at_sinks while describing them as aggregates in its prose; this is a reporting mismatch, not evidence that every such case involved wrong flow reasoning. The diagnostics separately count aggregate fields reported as rows, omitted actual row fields and lists matching the required-output schema. None of these post-hoc diagnostics changes the frozen primary score. See the evidence-linked case study.

## Interpretation and limitations
Report graph-edge effects only from FullFlatClean versus FullGraphClean and SliceFlatClean versus SliceGraphClean. Report prose exclusion from FullFlatRaw versus FullFlatClean. FullFlatClean versus SliceFlatClean isolates removal of irrelevant records; this is not uniquely graph-based because a reverse sequential scan computes exactly the same slice.

The deterministic baseline establishes what a trusted closed interpreter and repair search can do. Its success is not evidence of graph-specific intelligence. Differences in model completion and minimum-edit selection are separate findings. A four-edit safe repair is useful but fails the minimum-edit endpoint. A zero-leak gate that blocks everything also fails utility.

These inputs are already complete declared IR, not arbitrary Skill code. Hidden actions, dynamic control flow, external tool semantics, races, extraction mistakes and production enforcement are outside scope. The four contexts share one topology family; there are no independent human labels or real deployments. All variants are disclosed, including controls and failures. No outcome-dependent sample selection occurred.

The authority interface supplies opaque sink IDs and a task referring to their corresponding destinations, without a source-to-destination binding table. Permissions are uniform across all four sinks in this corpus, but the interface does not test precise resource binding and may contribute to conservative interpretation. Observed under-grant counts are mismatches to the authored task contract, not a demonstrated causal diagnosis of the model.

## Relation to prior systems
Task-only authority overlaps with [Progent](https://arxiv.org/html/2504.11703v3), and executable provenance/enforcement overlaps with [CaMeL](https://arxiv.org/html/2503.18813v2). [ActionGuard](https://arxiv.org/html/2609.39450) motivates exclusion of raw Skill prose from a reviewer, while [ActGov](https://arxiv.org/html/2609.24446) already separates bounded semantic extraction from deterministic governance. [SkillScope](https://arxiv.org/html/2605.05868v3) already studies skill graphs and localized repair. These are related mechanisms, not full systems reimplemented by this benchmark.

The defensible contribution is a controlled decomposition with an equally capable nongraph baseline, concrete utility verification and multi-site minimum-edit certificates. Do not claim invention of task isolation, information-flow tracking, graph repair or deterministic enforcement. A larger independent workflow corpus and arbitrary-code extraction study are needed before a deployment claim.
