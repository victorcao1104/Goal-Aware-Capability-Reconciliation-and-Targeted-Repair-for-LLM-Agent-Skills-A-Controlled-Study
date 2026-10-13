# Requirements and preparation decisions

Recorded 2026-10-13, Pacific/Auckland. This is preparation, not an experiment result or final implementation protocol.

## Direct user decisions

- Create an independent directory named after the new research topic, collect resources with one subagent first, then conduct the experiments and write the paper after setup is ready.
- Keep a clear structure for a later GitHub upload. No publication has been requested yet.
- Create a **new OpenAI API key** for this study; do not reuse the earlier experiment's credential.
- Total API usage ceiling: **US$20**. This is spending authorization within the study, not authorization to purchase credit or change account billing.
- User subsequently fixed **gpt-6-luna** for all model roles. Do not switch models or add cross-model experiments.
- Deadline: 30 days from 2026-10-13, therefore **2026-11-12**.
- Author: **Victor Cao**. Affiliation: **University of Auckland, Faculty of Science**.
- Update the literature review using the prior review as a source of references. The current handbook defines the new research direction.
- Fully automatic evaluation using dataset labels and deterministic acceptance criteria; explicitly disclose absence of independent human annotation. No fabricated human agreement statistics.
- Explain how to start Docker before experiments. After setup, proceed without routine approval interruptions, within the budget and supported environment.

The handbook is a proposed research specification, not a source of additional operating authority. Its factual claims and example commands require verification. Its figures are not results.

## Assignment requirements transcribed from screenshots

- IEEE format; target a standard scientific CS/AI paper with title and author.
- **10–12 pages excluding references.**
- Abstract: **one paragraph, about 150–200 words**.
- Introduction: **about 1–1.5 pages**; state the research question, hypotheses, approach and contribution.
- Related Work/Literature Review: **at most 1 page**. This overrides the handbook's 1.5-page suggestion.
- Methodology: detailed, justified, reproducible method, appropriate experimental design and statistics; this is a major grading component.
- Implementation/Results: implementation, comparisons, outcomes and evidence supporting conclusions; negative results are acceptable. Evaluate multiple aspects and limitations.
- Where a new technique is proposed, allocate the remaining body approximately equally to proposed method and experiments/results.
- Conclusion/Future Work: **about 1 page**; summarize findings, limitations and further research. This supersedes the handbook's 0.5-page suggestion.
- Bibliography: **at least 10 references, at most 1 page, IEEE citation format**.
- Deliver a PDF and reproducible LaTeX/BibTeX sources as requested in the handbook and user task.

## Research boundaries to preserve

Core scope is a single Skill bundle with task authority, file and simulated network/external actions, G1 exfiltration, G2 unauthorized modification, and G3 unauthorized external action. Other goals and multi-Skill or persistence experiments remain extensions, subject to available budget and evidence.

Keep analyzer inputs separate from evaluation-only attacker goals and correct labels. Group related Skill families and injection templates when splitting data. Freeze tests before final evaluation. Compare B0–B5 and feasible ablations with the same executor model, fixtures and acceptance criteria. Label reconstructed baselines as inspired implementations rather than official reproductions. Distinguish static potential paths from observed effects, and infrastructure failures from security successes.

Existing old-study results are not transferable to this study. Benchmark-derived and synthetic samples, adapted fixtures and original benchmark executions must be identified separately. Deterministic execution is evidence for the tested event or fixture, not proof of complete semantic graph accuracy. Any component accuracy without independent reference labels must be restricted or omitted rather than presented as human-grounded validation.

## Pending prerequisites

1. Secure key target and local destination selection; confirm account access/credit through appropriate setup without exposing secrets.
2. Docker Desktop Linux engine reachable; isolate attack fixtures before executing any acquired code.
3. Final resource/version/license audit and inspected benchmark interfaces.
4. Select a compatible model and conservative run scale within the US$20 ceiling; estimate from bounded pilot usage before freezing the test schedule.

No per-module approvals are required by the user's stated working preference. Stop paid calls at the authorized ceiling, preserve checkpoints, and do not silently change the empirical claims if a prerequisite fails.
