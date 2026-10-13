# Upstream repair development pilot

This branch adds a bounded mechanism study alongside the unchanged v1.0.0 paper and evidence.
Read the [pre-measurement design](../docs/protocol/upstream-repair-v2-design.md) for feasibility decisions, comparison fairness and stop conditions.

## Offline reproduction

Use Python 3.12. No additional dependencies, API key, Docker or network are needed for the v2 replay:

```text
python -m unittest discover -s tests_v2
python -m research_v2.reproduce
```

The second command verifies frozen source and fixture hashes, every published v2 evidence file,
the complete paired trial matrix, proposal-to-trial linkage and exact replay of all states and metrics.
The v1 environment remains pinned separately in requirements.lock.

## Components

| File | Responsibility |
| --- | --- |
| runtime.py | Closed typed tools, leaf origins, destination/operation/source checks |
| goals.py | Public necessary goal predicates used by candidate selection |
| graph.py | Dependency index of the same DSL available to both planners |
| repair.py | Shared bounded search, candidate simulation and validated replay |
| fixtures.py | Six development families and four matched variants |
| oracle.py | Independent exact result and committed-effect evaluation |
| model.py | Shared Luna prompt, tool catalogue and strict candidate schema |
| run.py | Frozen inputs, recorded API proposals, trials and accounting |
| reproduce.py | Offline integrity checks and replay |
| results/ | Frozen inputs, sanitized synthetic-data requests/proposals and trial evidence |

## Fresh paid execution

The archived experiment is frozen; edits to scientific source or prompts must start a separately named experiment,
not silently replace this evidence. `python -m research_v2.run --live` resumes the existing campaign and caches successful
responses. It loads the already configured, ignored study `.env.local` through the original API client, and shares
the original cumulative US$20 ledger in `results/raw_runs/`. Install requirements.lock for paid execution.
Provider errors, refusals and incomplete responses remain failed observations. Do not post credentials in issues.

All model roles use gpt-6-luna. Each blocked case receives one call per planner arm, at most four candidate
plans and twelve actions per plan. GraphNoSim reuses GraphPlanner proposals, so it has no additional model call.
The private response cache is ignored; published records contain only synthetic fixtures, candidate plans,
request/model identifiers, token usage and timing.

## Scope

These are scripted blocked prefixes followed by repair, not native attacks against an autonomous agent.
The interpreter has dictionary effects only. Its guarantees cover explicit tracked data dependencies,
not covert control-flow channels or arbitrary external tools. Opaque transforms and joins keep conservative
union provenance; verified projection is precise. Public shape predicates cannot certify semantic correctness;
the separate exact-output oracle decides success.

There are six authored development families, two data instances each, and no independent human annotation.
The graph is a structural index of the input program, not a hidden correct-repair recipe.
Neither higher joint success over stopping nor superiority over handle selection alone proves that the graph helps.
