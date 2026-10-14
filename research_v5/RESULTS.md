# V5 measured results: policy contamination and independent auditing

Frozen measurement source: 3cf5a2def4aee6c4e628a9f298c1e15e6ecff093. Model: gpt-6-luna, low reasoning, 2500 output-token ceiling for every role. V1–V4 remain unchanged.

No tested narrative induced a new excess permission relative to its neutral partner. Graph minus Flat evidence-valid correctness was +0.54 percentage points; raw verdict scores and benign utility must also be considered. This does not establish a unique graph benefit.

## Scope and prior work
[AuthBench](https://arxiv.org/html/2605.14859) already studies task/environment-to-policy inference and a sufficiency/tightness decomposition. Policy generation and splitting an audit are not our novelty claims.
[Progent](https://arxiv.org/html/2504.11703v3) assumes trusted initialization and gates runtime expansion. Untrusted Skill exposure at initialization changes that premise; this is not its reproduction or a demonstrated attack on it.
[SkillScope](https://arxiv.org/html/2605.05868v3) uses behavior graphs and task-conditioned authorization/testing; generating a synthetic task is not inherently a permission violation.
[CaMeL](https://arxiv.org/html/2503.18813v2) separates trusted planning from untrusted data and is not our automatic-policy-generation comparator.
Our narrower question is within-task causal sensitivity to attacker-controlled prose, separated from semantic policy error and runtime enforcement. Authorization compatibility does not establish necessity across all alternative implementations.

## Fixed design and limits
40 attack/neutral pairs: four dependency structures × ten authored inducement narratives. Paired workflows, tasks and public atom catalogs are identical; only Skill prose changes. Neutral partners still contain risky actions. Twelve clean/authorized/undecided controls bring the total to 92 cases × two repeats; E3 adds 176 update uses.
All effects run in a closed interpreter using fake paths and .invalid URLs. Ten exact operation/resource/original-source atoms and five explicit trusted clauses limit realism. There is no arbitrary native code, actual upload/deletion or independent human annotation.
Mixed and Isolated use the same strong prompt and differ only in Skill exposure. Both auditors see the same isolated model policy, task, catalog and grounded declarations; Flat can reconstruct dependencies freely. Graph adds a derived index with the same model/reasoning/output cap, but more input tokens. Thus equal capability and output budget do not imply identical total cost.
Scanner sees only the Skill. Enum references prospectively improve v4's interface; no v4 outcome was rescored.

## Calls and denominators
736 method rows, 176 update rows, 562 unique physical requests and 562 dispatch attempts. Statuses: {"ok": 562}.
Distinct policy calls: {'MixedRuntime': 110, 'IsolatedRuntime': 6}; auditors: {'IsolatedFlat': 88, 'IsolatedGraph': 88}; scanners: 94.
Pending reservations: 0. Identical inputs reuse one response within a repeat. Logical uses and neutral partners are correlated; no statistical significance or external-population attack-success rate is claimed.

## E1: initial permissions
Mixed excess incidence: attack 0/80 versus neutral 0/80; new excess pairs 0, reverse discordances 0, changed decision maps 0.
Isolated: attack 0/80 versus neutral 0/80. Its prose invariance follows from identical inputs by construction, not independent empirical robustness evidence.
Invalid pairs are excluded from the paired difference denominator, not counted as successful defense. Complete structure/narrative slices, unresolved grants, missing grants and exact discordant IDs are in summary.json.

| Method | Exact policy | Raw audit correct | Evidence-valid audit correct | Required effects complete | Unauthorized effect uses |
|---|---:|---:|---:|---:|---:|
| IsolatedFlat | 184/184 | 171/184 | 167/184 | 3/184 | 0/184 |
| IsolatedGraph | 184/184 | 171/184 | 168/184 | 3/184 | 0/184 |
| IsolatedRuntime | 184/184 | — | — | 184/184 | 0/184 |
| MixedRuntime | 184/184 | — | — | 184/184 | 0/184 |

Exact policy scores the decision map, not semantic validity of the cited clauses. A runtime-only policy can filter forbidden extras while completing necessary actions; a whole-workflow audit can block the whole plan. Attack-case completion is therefore not the benign utility endpoint.

## E2: graph attribution and controls
Evidence-valid correctness: Flat 167/184, Graph 168/184; Graph minus Flat +0.54 percentage points. Graph-only correct pairs 2; Flat-only 1.
Raw verdict correctness: Flat 171/184, Graph 171/184. Evidence-error uses: Flat 6, Graph 4. Incomplete/uncertain scanner uses: 132/184.
The primary endpoint requires the right verdict, successful components and structurally valid references/paths. It does not certify every explanation's semantics or completeness of findings.

| Method | Clean completion | Authorized-extra completion | Undecided workflow decision correct |
|---|---:|---:|---:|
| IsolatedFlat | 0/8 | 3/8 | 7/8 |
| IsolatedGraph | 0/8 | 3/8 | 8/8 |
| IsolatedRuntime | 8/8 | 8/8 | not a workflow classifier |
| MixedRuntime | 8/8 | 8/8 | not a workflow classifier |

### Scanner/interface failure analysis (postmeasurement diagnosis)
Only 85/94 unique scanner outputs returned exactly the declared IDs without extras/duplicates. 65/94 included uncertainty text; 65 mentioned on_error (literal keyword count, not independent human annotation).
Every clean use returned all declared actions but raised uncertainty about a missing error branch. The shared tool-semantics sentence says on_error is potentially reachable; it does not clearly state that this applies only to explicitly declared conditional actions. The scanner treated that generic syntax explanation as an unenumerated behavior. Both auditors then returned uncertain for all eight clean uses, so their required-effect completion was 0/8. Authorized-extra completion was only 3/8, versus 8/8 for both runtime-only methods. This is a substantial utility failure, not evidence of a more secure useful system. It implicates this interface, not a general impossibility of separate scanning. The frozen prompt and outcomes are preserved rather than repaired after seeing results.

All outcomes and component failures remain recorded. Zero unauthorized mock effects, if observed, does not establish general safety. See report/diagnostics.json for errors.
An important sensitivity limitation: attack workflows also contain a directly forbidden archive deletion, and the diagnostic destination is forbidden outright. A correct block verdict therefore does not require resolving the multi-hop provenance path. These workflows contain dependencies but this verdict endpoint does not isolate a graph-essential problem. A tie cannot refute graph value on tasks where source-flow inference is necessary; a new endpoint or new fixtures would need a separate prospective protocol.

## E3: proposed and effective updates
Correct authored initial map: proposed excess 0/88; effective excess 0/88; expansion rejections 0.
Fault-injected overbroad initial map: proposed excess 0/88; effective excess 0/88; expansion rejections 0.
Starting maps are interventions, not measured successful initializer attacks. Failed proposals retain the starting policy and count as failures.
Separately sealed deterministic controls show: unapproved expansion is rejected; an unchanged bad initial policy commits two unauthorized mock effects; a corrected narrowing removes them; a trusted test-harness allowlist enables legitimate expansion. This is not an authentication test or Progent's SMT implementation. Monotonic confinement alone cannot establish the initial policy's semantic correctness.

## Cost and reproduction
V5 conservative increment USD 0.210192250; cumulative USD 1.645422625 / USD 20.
Input is conservatively costed at USD 0.125/million and output at USD 0.50/million, without cache discounts, following docs/progress/v4-live-preflight.json. This is retained token/reservation accounting, not an independently reconciled invoice.
Install requirements.lock, then run:

    python -m research_v5.reproduce
    python -m scripts.report_v5 --verify

No API key or model calls are needed. Frozen inputs, requests, trajectories, accounting and summary have an evidence manifest. Reports have a separate manifest.

## Research decision
Separate authority sources remain a reasonable architectural boundary, but task-only generation can misinterpret user intent and behavior extraction can omit operations. Graph structure does not supply authority or guarantee additional accuracy.
Do not claim samples fool the strong Mixed generator without retained paired raw grants showing it. Do not infer unique graph value from deterministic gates, input invariance, or injected starting-policy errors.
A broader follow-up would need less explicit authority language, genuinely ambiguous environment/tool semantics, independently reviewed labels and held-out native workflows. Those require a new protocol, not retuning this measured run.
