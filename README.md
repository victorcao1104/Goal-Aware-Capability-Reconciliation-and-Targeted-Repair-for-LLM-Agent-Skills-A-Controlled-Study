# Goal-Aware Capability Reconciliation and Targeted Repair for LLM Agent Skills

**V8 pilot complete:** [findings and reproduction](research_v8/README.md) · [full tables](research_v8/report/pilot.md) · [observed failures](research_v8/report/case-study.md). Mini had 2/6 paired task-destruction outcomes in the oracle cohort, confined to one task family; Luna none/low each had 0/6. The frozen two-family expansion gate failed, so formal measurement was not run. Fixed contracts matched the proposed feasibility gate on safe feasibility. All 90 requests are retained; V8 USD0.015298550, cumulative USD2.426996075/20.

**Research branch v7 — measured:** [Findings (中文)](research_v7/report/findings.zh.md) · [Full results](research_v7/report/findings.md) · [Evidence-linked cases](research_v7/report/case-study.md) · [Offline replay](research_v7/README.md). Four-sink workflows distinguish four local repairs from two shared-prefix repairs. Full graph input did not improve overall safe completion versus matched flat input. Luna low found minimum repairs in 7/8 unsafe full-graph trials versus 6/8 flat, but graph over-repaired one authorized control; deterministic graph and flat chose exactly the same repairs. All 408 requests (407 completed, one incomplete) and 504 outcomes are retained. V7 cost **USD0.287430100**; cumulative **USD2.411697525 / USD20**. The v1 paper and all older studies remain preserved.

Research workspace for Victor Cao, University of Auckland, Faculty of Science.

**Research branch v6b — measured:** [Findings (中文)](research_v6b/report/findings.zh.md) · [Full results](research_v6b/report/findings.md) · [All candidate samples](research_v6b/report/candidate-catalog.md) · [Offline replay](research_v6b/README.md). GPT-4.1 Mini produced new excess permission in 12/16 paired attacks; Luna none/low produced 0/16. Independent task-only authority eliminated the observed Mini mock leaks, but explicit graph edges added no overall audit accuracy benefit. Mini still over-denied permitted local staging, so isolation did not make all contracts correct. All 764 v6b request records (including one incomplete response) and the aborted v6 transport run are retained. Cumulative conservative cost: **US$2.124267425 / US$20**. The original IEEE paper below remains the v1 artifact; later experiments are separately versioned supplements.

**Research branch v5:** [Findings (中文)](docs/v5-findings.zh.md) · [Measured results](research_v5/RESULTS.md) · [Offline replay](research_v5/README.md). Forty paired Skill narratives did not induce additional permissions in the strong Mixed baseline. Graph/Flat raw verdicts tied; graph had one more evidence-valid logical use. Both auditors failed all eight clean uses because the scanner inferred uncertainty about absent error branches. This is not evidence of a useful graph advantage. Cumulative estimated usage: **US$1.645422625 / US$20**. All 562 v5 requests and 912 method/update records are retained.

**Research branch v4 — measured:** [Findings (中文)](docs/v4-findings.zh.md) · [Recorded results](research_v4/RESULTS.md) · [Offline replay](research_v4/README.md). All 480 trajectories completed with 426 unique gpt-6-luna requests. Neither contract condition produced excess permissions on the authored attacks. Explicit graphs showed no robust benefit; audit evidence-interface failures materially affected the primary metric. Cumulative estimated usage: **US$1.435230375 / US$20**.

**Research branch v3:** [Findings (中文)](docs/v3-findings.zh.md) · [Measured results](research_v3/RESULTS.md) · [Offline replay](research_v3/README.md). Multi-site repair still yielded 72/72 attack success for all three equally capable planners. Correct graphs saved three requests versus no graph but cost 0.78% more. Cumulative estimated usage: **US$1.257365875 / US$20**. The original paper and v1/v2 scientific records remain preserved.

**Research branch v2:** [Feasibility and findings (中文)](docs/v2-feasibility-and-findings.zh.md) · [Development pilot results](research_v2/RESULTS.md) · [Offline v2 replay](research_v2/README.md). Upstream recomputation recovered tasks that handle reuse could not, but the graph added no observed benefit over equally capable planning in this 48-case development pilot. The v1.0.0 paper and evidence below remain frozen.

[中文说明](README.zh-CN.md) · [Reproduction guide](docs/artifact-guide.md) · [Paper](output/pdf/goal-aware-skill-study.pdf) · [Automated checks](https://github.com/victorcao1104/Goal-Aware-Capability-Reconciliation-and-Targeted-Repair-for-LLM-Agent-Skills-A-Controlled-Study/actions/workflows/reproduce.yml)

## Reproduce the published measurements

Use Python 3.12 in a virtual environment. On Windows, clone into a short directory such as `C:/research/gcr`.

```text
python -m pip install -r requirements.lock
python -m scripts.reproduce
```

No API key, Docker, or network is needed after dependencies are installed. Results are recomputed in a new `work/reproduced/` directory and compared against every field in the published summary/facts and all three manuscript LaTeX tables. For a repeat attempt, supply a new `--output` path. Use `--verify-only` for hash verification without recomputation. See the [artifact guide](docs/artifact-guide.md) for environment setup, schemas, output paths and optional fresh paid execution.

V1 status: experiment and IEEE manuscript complete. All 1,920 scheduled executions are valid; 167 of 168 original static cases resolved. All 1,362 v1 experimental API calls used `gpt-6-luna`. Conservative v1 usage estimate: **US$1.013328125**, with no unsettled reservations. Including the v2 pilot, cumulative study usage is **US$1.034103375**.

The study tests whether independently inferred task authority, skill behaviour paths, and targeted repair improve security and preserve legitimate task utility. The live baseline had zero observed attacks and 99.3% task success. Under deterministic stress, B5 reached 83.3% attacked joint success versus 33.3% for deny-only B2P, but graph-free selective B2R matched B5. The evidence supports selective filtering in this bounded runtime, **not incremental benefit from goal-graph selection**. Prior studies in the parent workspace are historical references, not results of this study.

Start with the [paper PDF](output/pdf/goal-aware-skill-study.pdf), [Chinese findings brief](docs/results-summary.zh.md), [measured summary](results/summary/summary.json), and [reproduction guide](docs/reproduction.md). The paper has 12 body pages and one reference page containing 14 entries. LaTeX, BibTeX, figures, source code, sanitized measurement records and hashes are included.

## Workspace map

| Directory | Contents |
| --- | --- |
| `docs/input/` | Local copies of the user's handbook and assignment screenshots; excluded from publication |
| `docs/protocol/` | Study decisions, rubric and subsequent frozen protocol |
| `docs/progress/` | Setup status and subsequent progress checkpoints |
| `literature/` | Verified paper downloads and source/version manifest |
| `third_party/` | Passive source-code acquisitions, excluded from Git |
| `datasets/` | Raw, normalized, fixture, annotation and grouped split data |
| `src/` | Analyzers, matcher, graph, repair, independent evaluator and closed gateway |
| `configs/` | Frozen run schedule, code/data hashes and container identity |
| `tests/`, `scripts/` | Validation and reproducibility tooling |
| `results/` | Raw runs, aggregate metrics, figures and error analysis |
| `paper/` | IEEE LaTeX manuscript, bibliography and figures |
| `release/` | Reviewed delivery packages |

V1–v5 experimental model roles use **gpt-6-luna**. V6b additionally tests **gpt-4.1-mini** and explicit Luna none/low reasoning settings. The authorized total API ceiling is **US$20**. No independent human annotation is claimed: the evidence strategy is benchmark labels and deterministic acceptance tests, with limitations disclosed.

See `docs/protocol/requirements-and-decisions.md`, `docs/progress/setup-status.json`, and the acquisition agent's `docs/resource-audit.md` and `literature/resource_manifest.json`.

## Publication and reproducibility

This is the public-ready research artifact for the author's [GitHub repository](https://github.com/victorcao1104/Goal-Aware-Capability-Reconciliation-and-Targeted-Repair-for-LLM-Agent-Skills-A-Controlled-Study). Credentials, user source documents, downloaded PDFs, raw upstream checkouts, and full local API payloads are excluded from Git. The delivery contains source/version references and reviewed measurement evidence. Upstream instructions and attack samples are research data, never operating instructions. Do not execute acquired code on the host. See NOTICE.md before choosing a repository license or redistributing upstream material.

Read `docs/protocol/frozen-design-notes.md` before interpreting the results. The runtime uses synthetic structured files and a mock outbox; it never executes arbitrary upstream code. Static benchmark analysis, transferred attack text and authored execution controls are distinct cohorts. Shared workflow templates limit the held-out split. B2R is the strong task-only repair comparator; B5 is not assumed to outperform it.

## Reproduce

Use Python 3.12 and the versions in `requirements.txt`. Run `python -m unittest discover -s tests` for deterministic checks. See `docs/reproduction.md` for data acquisition, offline analysis, container setup and paid execution. A fresh archive extraction successfully regenerated every summary field (numeric tolerance 1e-10) and all three manuscript LaTeX tables byte-for-byte without an API key or paid calls; see `docs/progress/offline-reproduction-audit.json`. Do not place a key in a command, notebook or committed file; use the ignored `.env.local` or your own secure provisioning workflow.
