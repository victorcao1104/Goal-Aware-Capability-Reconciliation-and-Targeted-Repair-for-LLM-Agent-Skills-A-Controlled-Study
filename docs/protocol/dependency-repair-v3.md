# V3: multi-site, dependency-sensitive repair protocol

Date: 2026-10-14. Branch: research/dependency-repair-v3, based on frozen v2.
The user explicitly requests continued autonomous implementation, strong graph-free baselines, gpt-6-luna only and the existing cumulative US$20 ceiling.

## Hypothesis and scope
Does a precomputed dependency index improve repair under identical tool, feedback, candidate and model-output budgets? Raw source programs already contain all dependency information. The baseline may reconstruct or reason about dependencies without restriction. Any effect is an indexing/representation benefit under bounded resources, not proof that only graphs can solve the task.

Six topologies: fan-in aggregation, chained joins, shared-base diamonds, staged receipts, cross-branch rewiring, stale-cache/version dependencies. Each has two data instances and widths two/four, giving 24 attacked workflows. Twelve correct controls (one clean and one explicitly authorized per topology) give 36 fixtures. Three repeats and three model arms produce 324 trajectories, with at most 432 logical model requests. This remains an authored mechanism study, not a native benchmark or independent held-out generalization study.

Attacks introduce multiple incorrect source projections plus a destination, wiring, ordering or version error. Every required branch contributes unique data to the independent expected result. Before API measurement, verify valid reference execution, failed attacked prefixes, failure of all single edits in the public edit catalogue, successful multi-site restoration and receipt freshness. Report exact catalogue sizes, action counts and dependency depths. Single-edit failure is scoped to that catalogue, not a proof over arbitrary programs.

## Equal-capability methods
Planner receives the entire untrusted program, trusted task/policy, full current typed state, tool semantics, public edit catalogue and simulation feedback. It may infer dependencies, change multiple nodes, move nodes, or propose a completely new plan.
GraphPlanner receives the same information plus a dependency index parsed only from that program. GraphShuffled receives an index with deterministically permuted node identities. No reference repairs, hidden expected values, fault annotations or oracle verdicts enter any payload.
All three use gpt-6-luna, low reasoning, max 8000 output tokens/request, two logical requests/trajectory, four candidates/request, sixteen edits/moves or 96 actions/candidate, and at most eight candidate simulations. All receive identical feedback fields. Stop early only when a validated candidate satisfies all PUBLIC goal predicates, never on hidden oracle success. Baseline reasoning strategies are unrestricted. Extra graph input tokens and indexing work are reported as overhead.
The original API client may make up to three transient transport/HTTP attempts per logical request; all are separately accounted. Incomplete/refused/invalid model outputs are failed observations, not resampled.

## Execution and evaluator
Use the frozen v2 closed tool interpreter; no external effects or arbitrary execution. Candidate changes are untrusted. Simulate on copies of the same blocked-prefix state; replay a selected candidate through the same gate. The public edit catalogue supplies syntactically plausible values, not repairs filtered by correctness.
Public goals include shape/type conditions and explicit receipt dependencies (hashes must observe the latest committed named outputs). They contain no expected content. The independent evaluator computes exact values from fixture data outside the runtime and checks all final outputs and unsafe effects. Safe but semantically wrong candidates remain failures.

## Outcomes
Primary: paired GraphPlanner minus Planner joint safety/exact-task success on the 24 attacked workflows, averaging repeats within case and cases within topology. Report all per-case differences, descriptive six-topology bootstrap intervals and discordant pairs; do not treat repeats as independent families.
Secondary: recovery by width/topology, simulated actions, candidates, rounds, model input/output tokens, costs, first-candidate success, failures after exhausting budget, and source/action counts in successful repairs. Compare correct versus shuffled graphs. Preserve ceiling and negative findings. A >=10 pp practical gain is a progression signal only; do not weaken the baseline or tune fixtures after seeing results to reach it.
Separate mechanistic complexity evidence from observed model difficulty. If all methods still solve the tasks, report that the graph was unnecessary here; do not claim universality.

## Preservation and publication
New code/tests/evidence stay under research_v3/ and tests_v3/. Verify v1 and v2 freezes. Commit hashes of inputs, prompts, code and schedule before paid measurement. Reuse the approved ignored key and original shared ledger (current estimate US$1.034103375). No new credentials or budget. Store synthetic public proposals, attempt-level accounting, feedback, states and offline replay checksums. Push only the research branch, open a draft PR, never merge main automatically.
