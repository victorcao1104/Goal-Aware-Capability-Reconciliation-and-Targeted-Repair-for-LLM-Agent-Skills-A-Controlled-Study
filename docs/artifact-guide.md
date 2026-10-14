# Research artifact guide

This repository separates the original scientific record from later reproduction conveniences. The `src/` implementation and original tests/report scripts are frozen by SHA256 in `configs/frozen-study.json`. The new offline helper, dependency lock and CI were added after the experiment. They do not change prompts, acceptance rules, samples, or published results.

## Choose a reproduction level

| Purpose | Requirements | Entry point | What it establishes |
|---|---|---|---|
| Read findings | PDF viewer | `output/pdf/goal-aware-skill-study.pdf` | 12 body pages, one reference page |
| Verify artifact integrity | Python 3.12, standard library | `python -m scripts.reproduce --verify-only` | Frozen distributed files and 3,595 evidence records match their hashes |
| Recompute results | Python 3.12 and `requirements.lock` | `python -m scripts.reproduce` | Summary/facts match within 1e-10; three LaTeX tables match byte-for-byte |
| Replay v2 repair pilot | Python 3.12 | `python -m research_v2.reproduce` | 384 trajectories and request evidence |
| Replay v3 complex repair | Python 3.12 | `python -m research_v3.reproduce` | 324 trajectories, adaptive histories, paired summaries and exhaustive complexity certificates |
| Regenerate v3 presentation | Python 3.12 and `requirements.lock` | `python -m research_v3.tools.report` | Derived tables, counts and plots from v3 recorded evidence |
| Test implementation | Same Python environment | `python -m unittest discover -s tests` | Deterministic regression checks, including reproduction-integrity tests |
| Rebuild manuscript | IEEEtran TeX distribution or Tectonic | `tectonic paper/main.tex` | Editable source builds the paper; no model calls |
| Collect new model samples | OpenAI access, authorized budget, Docker Linux engine, original pinned dataset | `docs/reproduction.md` | New experiment, not guaranteed identical stochastic outcomes |

Only installing dependencies needs internet for the standard offline path. Once installed, result reanalysis needs no credentials, model API, Docker, original paper downloads, or original attack bundles. The helper invokes a fixed list of reporting commands; it never invokes `evaluate` or `analyze`.

## Quick start

Clone into a short path on Windows, such as `C:/research/gcr`, to avoid legacy path-length limits.

```text
git clone https://github.com/victorcao1104/Goal-Aware-Capability-Reconciliation-and-Targeted-Repair-for-LLM-Agent-Skills-A-Controlled-Study.git gcr
cd gcr
python -m venv .venv
```

Activate with `.venv\Scripts\Activate.ps1` on PowerShell or `source .venv/bin/activate` on Linux/macOS. Alternatively invoke the virtual environment's Python directly.

```text
python -m pip install -r requirements.lock
python -m scripts.reproduce
```

The default new output directory is `work/reproduced/`. The helper does not overwrite existing directories. For another attempt, choose another path with `--output`, for example `python -m scripts.reproduce --output work/reproduced-2`.

Read `reproduction-check.json` for pass/fail evidence and `reproduction.log` for details. Recomputed CSV/JSON files are under the output's `results/summary/`; regenerated charts/tables are under its `paper/`. A failure exits nonzero and retains its directory for diagnosis.

## Storage and provenance

| Path | Role | Editing policy |
|---|---|---|
| `src/`, original `tests/`, `scripts/report.py` | Experimental implementation and acceptance | Preserve hashes for original-study claims |
| `configs/frozen-study.json` | 1,920-job schedule, scientific hashes and container identity | Preserve; use a separate copy for a new campaign |
| `datasets/normalized/controls.jsonl` | Complete authored controls with reference acceptance | Public, frozen |
| `datasets/normalized/transfer-public-metadata.jsonl` | Transfer identities and scoring metadata without original attack text | Enough for recorded-result reanalysis |
| `results/evidence/` | Sanitized executions, analyses, static flags and API accounting | SHA256 manifest; 3,595 files |
| `results/summary/` | Expected results for automatic comparison | Recompute elsewhere; do not replace to make a failing check pass |
| `paper/`, `output/pdf/` | LaTeX/BibTeX, figures/tables, final PDF | Reporting artifacts |
| `literature/resource_manifest.json` | Source links, versions, licenses and hashes | Acquisition provenance; downloaded files not vendored |
| `docs/protocol/`, `docs/progress/` | Scope decisions, deviations, audits and historical checkpoints | Preserve chronology; old status entries are historical |
| `scripts/reproduce.py`, `requirements.lock`, `.github/` | Post-study reproduction conveniences | May evolve with review without altering scientific inputs |

The full local study additionally retains credentials, user coursework, downloaded papers, upstream checkouts, complete API payloads and development records. Those are **not** published. Original bundles can be reacquired from pinned sources; sanitized data suffice for offline numerical reproduction. No data file or upstream instruction is a command to execute.

## Evidence schemas

- `runs/*.json`: run identity, cohort/method/repeat, trace, final state, deterministic evaluation and runtime. Transfer configurations quoting original text are omitted.
- `analyses/*.json`: controlled-case task contracts, extracted graphs and scanner findings used by formal runs.
- `static/*.json`: original case identity, coverage, status and two Boolean risk judgments; one incomplete case remains unresolved.
- `api_calls/*.json`: role, returned model, tokens, duration and estimated cost; no key or full message content. These records cannot resume paid requests.
- `budget-ledger.json`: settled/reserved accounting for the whole study, including development. Estimates are not an invoice.
- `manifest.json`: exported-file hash plus local-source hash, documenting the sanitization transformation.

## Dependencies and limits

`requirements.txt` names direct dependencies; `requirements.lock` pins all 19 observed Python package versions. It is a version lock, not a universal wheel/hash lock. The original execution used Python 3.12.14 and Docker 29.7.2 in Linux mode. No virtual environment, platform binary, Docker image, or downloaded TeX distribution is committed. Python and optional system tools are installed separately. Scientific arrays/CSV/JSON and LaTeX tables are checked, not byte-identical PDF metadata or platform-specific font rendering.

The workflow runs offline reproduction on Linux and Windows with no repository API secrets. GitHub status is execution evidence; the workflow definition by itself is not a claim that a run passed. MacOS uses the same Python command but is not part of that CI matrix.

See `NOTICE.md` for authorship, AI assistance and rights. No broad software or third-party redistribution license has been selected on the author's behalf. The artifact does not claim native Skill-Inject reproduction, independent human annotations, or an incremental goal-graph benefit.

## V7 field-flow supplement

The [v7 guide](../research_v7/README.md) covers the frozen four-sink fixtures, 408 response records, 504 model/baseline outcomes, exact offline reconstruction and report verification. It uses the same pinned Python dependencies; no Docker or API key is needed for replay. All previous studies remain independently reproducible. The original IEEE paper is v1; v7 findings are a separately versioned supplement.
