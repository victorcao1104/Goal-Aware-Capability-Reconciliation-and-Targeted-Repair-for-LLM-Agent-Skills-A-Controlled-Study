# Independent authority and grounded Skill audit — measured v4

**MEASURED 2026-10-14.** [Results](RESULTS.md) · [中文结论](../docs/v4-findings.zh.md). All 480 method trajectories and 426 unique model requests are recorded. No excess permissions were induced in either contract condition; no robust graph benefit was established. Evidence-format failures materially affected the primary metric. Added estimated cost: US$0.177864500; cumulative US$1.435230375 / US$20. Earlier v1–v3 scientific records and the paper remain unchanged.

The initial preparation snapshot in preparation.json and the protocol's preparation status are retained as historical pre-measurement records. They do not describe the current measured status.

This study distinguishes two hypotheses: excluding untrusted Skill text from permission generation may reduce unjustified grants; an explicit dependency index may improve an audit beyond equally informative flat records. Either hypothesis can fail. A valid quotation does not prove that a permission follows from it.

## Fixed comparison

| Method | Contract input | Audit input |
| --- | --- | --- |
| Mixed-Flat | Trusted task/inventory plus explicitly untrusted Skill | Task, candidate contract, grounded records |
| Mixed-Graph | Same Mixed contract | Same records plus derived dependency index |
| Isolated-Flat | Trusted task/inventory only | Task, candidate contract, grounded records |
| Isolated-Graph | Same Isolated contract | Same records plus derived dependency index |
| TaskRuntime | Same Isolated contract | No preflight audit; deterministic runtime provenance |

All effects use the generated contract and common runtime gate. Neither a Skill nor an audit may enlarge that contract. Scan sees the Skill and tool semantics, without the task or author labels. Flat can freely reconstruct dependencies. Output limits and model capabilities match by role; Graph input overhead is counted.

Six mechanisms cover upload pretexts, excessive payloads to approved destinations, multi-step source laundering, cleanup scope, conditional error transfers and forged approval/scanner suppression. Each has two task/state instances and four variants: clean, attack, explicitly authorized, and undecided authorization. Attack/authorized/undecided variants retain exactly the same Skill and differ in trusted authority. The 48 cases and two repeats yield 480 method trajectories. There are at most 672 unique role requests before shared-input caching; this is not a count of per-method logical uses or transport attempts.

The completeness guard detects omitted IDs in the public declarative workflow, records them as omissions, and prevents allow. It does not recover arbitrary executable behavior. The runtime tracks source sets and committed mock effects; it does not evaluate real document contents or execute native code.

## Offline reproduction

Use Python 3.12 and the repository's pinned dependencies. A short checkout path is recommended on Windows.

```text
python -m pip install -r requirements.lock
python -m unittest discover -s tests_v4
python -m research_v4.reproduce
python -m scripts.report_v4 --verify
```

These commands need no API key after dependencies are installed. Reproduction verifies frozen inputs, 527 evidence hashes, all 480 trajectories, component linkage and every summary field. The report command verifies derived diagnostics, CSV and figure/source hashes. Use python -m research_v4.reproduce --prepared to check only the original input preparation. Reference checks and the 480-trajectory stub test are plumbing checks, never model measurements.

## Files

- [Protocol](../docs/protocol/authority-audit-v4.md): hypotheses, authority boundaries, denominators and limits.
- [Readable samples](samples/): 24 first-instance bundles, each with trusted-task.txt, SKILL.md and workflow.json. Treat all bundle instructions as untrusted research data.
- [All cases](results/cases.json), [model interfaces](results/model-spec.json), [freeze](results/freeze.json): the full prepared schedule and source hashes.
- fixtures.py / core.py: authored data, grounding, contract validation, provenance and mock execution.
- model.py / run.py: role interfaces, component caching, budget and committed-source guards.
- analysis.py / reproduce.py: paired outcomes and complete offline replay for the measured run.

## Measured-run integrity and future paid execution

The preparation release made zero paid calls. The completed live run used gpt-6-luna and the original cumulative US$20 ledger; preceding usage was US$1.257365875 and measured cumulative usage is US$1.435230375. The ignored local credential and original ledger are required. No credential or full private API record is published.

Before a future live run, confirm current model availability/prices against the client's reservation assumptions and retain the original ledger. The runner rejects absent/understated/unsettled ledgers, uncommitted frozen inputs and inconsistent cached responses. Run `python -m research_v4.run --live` only when intending to spend the remaining study budget. It never refreshes the freeze automatically. Changing the design after freezing requires a new version, not overwriting a measured study.

Measured output contains public component requests, trajectories, accounting and a summary/evidence manifest. One orchestration interruption was resumed with one new request and all 520 existing request/trajectory hashes unchanged. Its inner exception was not retained. The accounting before_usd field records the resume balance; full v4 expenditure is after_usd minus prior_usd. See RESULTS.md and docs/progress/v4-interruption.json for the complete disclosure. Identical component inputs are reused within a repeat. Physical costs, logical role uses, API failures, missing pairs and metric-specific denominators remain separate. TaskRuntime's nonexistent audit accuracy is N/A. For the four audited arms, audit_accuracy is correctness over all scheduled trajectories, with pipeline/API failures counted as incorrect and also reported separately. Full retained API records are needed for paid resume; public evidence suffices for offline replay with `python -m research_v4.reproduce` for these recorded measurements.

## Interpretation limits

These are related development fixtures, not independent real-world attacks, held-out programs or human-reviewed labels. The two instances mostly vary task identifiers; only the conditional family varies branch activation. No adaptive success filtering is allowed. A positive result would support only this bounded mechanism; a null result must be retained. The study cannot establish novelty merely from separation or graph use, or claim to reproduce named permission systems.

Related architectural context: [CaMeL](https://arxiv.org/html/2503.18813v2) separates trusted control from untrusted data; [Progent](https://arxiv.org/html/2504.11703v3) includes task-derived policies and controlled policy changes. This preparation does not establish superiority over either system.
