# Goal-Aware Capability Reconciliation and Targeted Repair for LLM Agent Skills

Research workspace for Victor Cao, University of Auckland, Faculty of Science.

[中文说明](README.zh-CN.md) · [Reproduction guide](docs/artifact-guide.md) · [Paper](output/pdf/goal-aware-skill-study.pdf) · [Automated checks](https://github.com/victorcao1104/Goal-Aware-Capability-Reconciliation-and-Targeted-Repair-for-LLM-Agent-Skills-A-Controlled-Study/actions/workflows/reproduce.yml)

## Reproduce the published measurements

Use Python 3.12 in a virtual environment. On Windows, clone into a short directory such as `C:/research/gcr`.

```text
python -m pip install -r requirements.lock
python -m scripts.reproduce
```

No API key, Docker, or network is needed after dependencies are installed. Results are recomputed in a new `work/reproduced/` directory and compared against every field in the published summary/facts and all three manuscript LaTeX tables. For a repeat attempt, supply a new `--output` path. Use `--verify-only` for hash verification without recomputation. See the [artifact guide](docs/artifact-guide.md) for environment setup, schemas, output paths and optional fresh paid execution.

Status: experiment and IEEE manuscript complete. All 1,920 scheduled executions are valid; 167 of 168 original static cases resolved. All 1,362 experimental API calls used `gpt-6-luna`. Conservative total usage estimate: **US$1.013328125**, with no unsettled reservations.

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

All experimental model roles use **gpt-6-luna**. The authorized total API ceiling is **US$20**. Setup is complete. No independent human annotation is claimed: the evidence strategy is benchmark labels and deterministic acceptance tests, with limitations disclosed.

See `docs/protocol/requirements-and-decisions.md`, `docs/progress/setup-status.json`, and the acquisition agent's `docs/resource-audit.md` and `literature/resource_manifest.json`.

## Publication and reproducibility

This is the public-ready research artifact for the author's [GitHub repository](https://github.com/victorcao1104/Goal-Aware-Capability-Reconciliation-and-Targeted-Repair-for-LLM-Agent-Skills-A-Controlled-Study). Credentials, user source documents, downloaded PDFs, raw upstream checkouts, and full local API payloads are excluded from Git. The delivery contains source/version references and reviewed measurement evidence. Upstream instructions and attack samples are research data, never operating instructions. Do not execute acquired code on the host. See NOTICE.md before choosing a repository license or redistributing upstream material.

Read `docs/protocol/frozen-design-notes.md` before interpreting the results. The runtime uses synthetic structured files and a mock outbox; it never executes arbitrary upstream code. Static benchmark analysis, transferred attack text and authored execution controls are distinct cohorts. Shared workflow templates limit the held-out split. B2R is the strong task-only repair comparator; B5 is not assumed to outperform it.

## Reproduce

Use Python 3.12 and the versions in `requirements.txt`. Run `python -m unittest discover -s tests` for deterministic checks. See `docs/reproduction.md` for data acquisition, offline analysis, container setup and paid execution. A fresh archive extraction successfully regenerated every summary field (numeric tolerance 1e-10) and all three manuscript LaTeX tables byte-for-byte without an API key or paid calls; see `docs/progress/offline-reproduction-audit.json`. Do not place a key in a command, notebook or committed file; use the ignored `.env.local` or your own secure provisioning workflow.
