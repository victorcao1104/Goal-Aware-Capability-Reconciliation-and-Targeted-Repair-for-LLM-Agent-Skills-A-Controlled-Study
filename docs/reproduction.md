# Reproduction guide

## Scope and entry points

This repository implements a bounded mechanism study, not native SkillInject execution. All external effects occur in a simulated outbox and structured in-memory files. The corpus contains AI-authored parametric controls; broad templates recur across named-family partitions. No independent human ground truth is available.

The CLI offers `prepare`, `annotate-check`, `validate`, `freeze`, `evaluate`, `analyze`, `aggregate` and `report`, for example `python -m src.cli aggregate`. Commands must run from the repository root, using Python 3.12 and requirements.txt. `analyze` invokes paid models on the original static cohort; it is not offline aggregation.

## Deterministic verification

1. Create a local Python environment and install requirements.txt.
2. Ensure the ignored `work/` directory exists (some tests create temporary fixture directories there).
3. Run `python -m unittest discover -s tests`.
4. Regenerate controlled fixtures with `src.dataset.make_controls()` if auditing their specification. The committed JSONL preserves the exact frozen case bytes.

These tests use only closed local tools and mock model clients. They do not require an API key or execute any upstream attack script.

## Acquire original material

Clone `https://github.com/aisa-group/skill-inject` into `third_party/skill-inject` and check out `182f3d9d9836e81cdae213e9b9cec1d9be96eea3`. Inspect its license and nested bundle rights before redistribution. The acquisition audit lists other research repositories, which are references rather than runtime dependencies. Run `python -m src.cli prepare` to rebuild the complete original bundles, text projections, controls and transferred-text fixtures. Do not run upstream installation hooks or Skills.

`datasets/annotations/case_selection.csv` records the selected first constructible association and exclusions. The original benchmark has several possible task associations per injection; this study does not count those associations as distinct executed trials. Full local bundles may need Windows extended-length paths; the normalizer handles this without shortening stored source identities.

## Offline result analysis

Recommended automated entry point: `python -m scripts.reproduce` creates a fresh analysis copy, verifies hashes, reaggregates records and compares the output to the published measurements. Install `requirements.lock` for the full pinned dependency set. See `docs/artifact-guide.md` for a complete quick start. The lower-level commands below remain available for inspection.

The reviewed delivery provides sanitized evidence sufficient for the published tables, plus source hashes and transformation notes. On Windows, extract under a short path such as `C:/research/` to avoid legacy path-length limits. In a new extracted copy, run `python -m scripts.restore_evidence`, then `python -m src.cli aggregate`. Run `python -m scripts.paper_tables` and `python -m scripts.paper_figures` to regenerate manuscript tables and presentation figures. No API key or Docker is needed for these commands. The helper refuses to overwrite existing local raw records and restores only sanitized accounting records, not API response caches suitable for resuming paid calls. A scientific rerun needs a fresh output directory and fresh ledger, with explicit budget authorization; do not use restored accounting summaries as live client caches.

The raw local workspace retains original complete API responses and run state for audit. In the public-ready export, original injection text and full original bundle projections are omitted; static risk flags and coverage are sufficient for the reported classification agreement. The export does not confer new rights to upstream material.

## Fresh paid execution

Use a separate checkout/output copy so original scientific records cannot be overwritten. Provision a new key securely into the ignored `.env.local` as OPENAI_API_KEY. The supplied client only calls the OpenAI Responses endpoint and never passes the credential into a container. The model must be gpt-6-luna; verify current access and pricing before authorizing a new campaign.

Start Docker Desktop in Linux-container mode. Build the isolated runtime with `scripts/build_container.ps1` on Windows, or construct the equivalent Dockerfile using only src/__init__.py, contracts.py, sandbox.py and worker.py. Do not build from the repository root or include the credential file in a Docker context. The builder creates its own minimal context under work/container-build.

Run validation, then create a NEW frozen manifest for the new campaign, then evaluate and analyze. The archived configs/frozen-study.json is the original experiment record; preserve it and use a separate experiment copy for any new freeze. Its image hash intentionally prevents silently substituting a rebuilt container. A rebuild can change the image identity even when the tool semantics remain the same. Record the new identity rather than editing the original provenance record.

The original schedule has 1,920 execution jobs: 1,152 live principal comparisons, 624 deterministic stress runs, and 144 transferred-text live comparisons. There are only 48 main-test cases from six families. Three repeats are stochastic repeated observations, not independent new tasks. The initial model plan is reused across comparable methods; feedback plans depend on each method.

The budget ledger reserves estimated charges before every request and retains unknown charges. Keep all paid stages within one authorized campaign. The transactional lock protects against separate clients losing ledger updates. The configured US$20 ceiling is a safety bound; a new run still requires its own human spending authorization.

## Paper build

Use an IEEEtran-capable TeX distribution and compile `paper/main.tex`, with BibTeX as needed. The original build uses official Tectonic 0.17.0, with the Windows MSVC archive verified against SHA256 `f61ce51f0b0ade1015b7de7ef368541c5424e9756ecbd0d7af97d6d48030845f`. Its official source is https://github.com/tectonic-typesetting/tectonic/releases/tag/tectonic%400.17.0. IEEEtran is available from https://ctan.org/pkg/ieeetran.

The frozen scripts/report.py generates initial figures; scripts/paper_figures.py redraws the same measured values with legends outside the plots for manuscript typesetting. scripts/paper_tables.py converts summaries to LaTeX without changing the frozen statistics. Architecture and worked-example material are native LaTeX. The paper's final page audit and figure/table checks are recorded under docs/progress/.

## Interpretation guardrails

- Live model ASR and scripted stress ASR have different meanings; never pool them.
- Benchmark label agreement is not independent semantic ground truth.
- Missing runs and infrastructure failures have missing rates, not secure zeros.
- A completed model refusal is a behavioral outcome, not an infrastructure failure.
- The graph identifies potential effects; runtime state establishes observed effects.
- Repair minimality is restricted to enumerated choices; field/source filtering is not native script rewriting.
- Warm-cache runner times are not cold-start end-to-end method overhead.
- Publication of the reviewed artifact was authorized on 2026-10-14; source documents, credentials and full local API payloads remain excluded.
