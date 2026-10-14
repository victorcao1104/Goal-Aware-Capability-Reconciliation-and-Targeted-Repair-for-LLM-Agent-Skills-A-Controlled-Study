# Task-preserving contract updates (V8)

Completed pilot, **formal expansion not run because the frozen oracle-cohort gate failed**.

- [Chinese findings](report/findings.zh.md)
- [All model/cohort/method tables](report/pilot.md)
- [Observed failure cases](report/case-study.md)
- [Frozen protocol](../docs/protocol/task-preserving-contracts-v8.md)
- [Recorded go/no-go decision](results/decision.json)
- [Summary](results/pilot/summary.json), [588 method outcomes](results/pilot/rows.json)
- [90 sanitized physical response records](results/requests/)
- [Source freeze](results/freeze.json), [evidence inventory](results/evidence-manifest.json)
- [Figure](report/pilot-outcomes.png), [vector PDF](report/pilot-outcomes.pdf)

## Actual result

Two synthetic task structures, seven event states, three model settings, one repeat, oracle and model-extracted contracts. GPT-4.1 Mini showed 2/6 paired new nonexpanding task-destruction outcomes in each cohort; both oracle failures were in the formats family, while extracted failures spanned both families. Luna none and low each showed 0/6 in each cohort.

The preregistered expansion gate specifically required two distinct harmed families in the oracle cohort for one model. The extracted result does not replace that criterion after inspection. Six further task structures are prepared and deterministically checked but have **no model measurements**.

Fixed/strict-source contracts and task-preserving checks both retained safe feasibility in every non-revocation pilot state. Therefore the pilot does not establish a safety advantage over the strongest simple baseline. The single-witness ablation rejected a valid alternative that the feasibility checker accepted; that mechanism result is not additional attack prevention against Luna.

A textual explanation sometimes contradicted the executable permission array. Read the case study; the reason field is not treated as evidence that the actual policy was safe.

## Offline reproduction

Python 3.12. Use a short checkout path such as C:/research/gcr on Windows.

    python -m venv .venv
    # Activate using your shell.
    python -m pip install -r requirements.lock
    python -m unittest discover -s tests_v8
    python -m research_v8.reproduce
    python -m scripts.report_v8 --verify

Replay requires no API credential, Docker or network after dependency installation. It verifies source hashes, recomputes finite-plan certificates, reconstructs every request, parses retained responses, rebuilds outcomes, costs and the stop/go decision, and checks evidence inventory. Report verification reconstructs all tables and diagnostics and verifies figure hashes.

The original paid entry point is restricted to the approved private ledger and committed scientific inputs. It refuses formal dispatch when the pilot gate fails. New experiments require a new version, protocol, authorization scope and cumulative budget preflight; never delete evidence to rerun a failed request.

## Architecture and scope

- fixtures.py: trusted action semantics, natural-language tasks and source-labelled event deltas. Gold grants/goals never enter extracted-cohort event inputs.
- engine.py: exhaustive bounded state search, independent concrete witness replay, and seven gates (Fixed/SourceLocked intentionally equivalent).
- model.py: matched explicit source/safety/goal instructions plus self-check, fixed 2400 output cap.
- api.py: durable reservations against the original USD20 ledger; unknown charges conservatively reserved, no retries.
- run.py / reproduce.py: freeze, conditional measurement and exact replay.
- analysis.py: formal family-cluster procedure fixed before measurement; unused because formal did not proceed.
- ../scripts/report_v8.py: derived reports and clearly labelled exploratory goal-equivalence diagnosis.

Safe-feasible means potential completion exists in the finite simulator, not observed autonomous task completion. All methods share one candidate per input; 588 outcomes are not 588 independent samples. Trusted cancellation is a host plumbing control. Structural contract equality is not semantic correctness: all six extracted pilot contracts have the right grants and equivalent goals on reachable states.

No independent human annotation; no claim of first discovery of denial of service, undergrant, provenance isolation or deterministic checking. Prior V1–V7 and the original paper remain frozen.

Conservative V8 charge: USD0.015298550; cumulative study charge USD2.426996075 / 20. Physical requests 90, all parsed successfully. Private provider envelopes and credentials remain excluded from publication.
