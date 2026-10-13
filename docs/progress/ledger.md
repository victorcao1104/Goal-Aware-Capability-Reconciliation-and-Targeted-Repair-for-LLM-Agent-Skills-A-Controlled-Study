# Execution ledger — plan: docs/protocol/implementation-plan.md

2026-10-13: Resource preparation complete: 11 paper PDF hashes reverified by primary agent; four repositories acquired by resource subagent. No third-party code executed. User handbook and screenshots copied without changing originals.

2026-10-13: User approved new OpenAI key, US$20 total ceiling, automatic evaluation without independent human annotation, deadline 2026-11-12, author Victor Cao / University of Auckland / Faculty of Science. User then explicitly selected gpt-6-luna for all roles.

2026-10-13: Secure API key created with widget-selected target and 2,592,000-second lifetime, saved only to confirmed .env.local. Authenticated using read-only /v1/models. Balance remains unverified; no paid inference yet. Docker 29.7.2 Linux engine verified through standard approved access.

Ruling: Follow user's explicit autonomous execution preference instead of repeated skill design/plan approval prompts. The provided handbook is the design starting point, with factual corrections and scope limitations recorded; risk is that practical benchmark adaptations may limit external validity, which must be disclosed.

Ruling: Preserve all process material and use native Windows commands instead of POSIX progress helpers. New repository provides the requested isolation; old study remains untouched.

Task 1: Core implementation and container smoke complete. 15 initial tests plus subsequent suites passed; Docker network=none, read-only root, non-root user, no mounted host paths, all capabilities dropped. Container image sha256:382dd2812aab74a5103c51c7487efad4c137e3ab296f6a19bec0a92e6b3cd03c. Tools operate simulated structured files and outbox, never original attack code.

Task 2: Passive data construction complete: 168 paired static projections (84 injection representatives and 84 clean versions), 118 complete-text and 50 partial-text projections. Full bundles are retained locally. 96 authored controls: 32 development, 16 validation, 48 test. Each family stays in one split; broad mechanisms recur, so this is not unseen-mechanism generalization. No human reference labels.

Ruling: Windows reached the 260-character path boundary while retaining complete upstream bundles. Added tested extended-length filesystem paths; source IDs and portable metadata remain unchanged. Tests and full data generation now succeed. Cost if wrong: incomplete local bundles; hashes and source mapping checks must detect this.

Ruling: Bundled Python cannot initialize ensurepip in a virtual environment here. Installed dependencies into ignored work/pydeps only and run bundled Python 3.12.14 with that scoped import path. No system Python packages changed.

Task 3: API client, analyzers, evaluator, closed script translator and runner implemented; 32 tests passed. First analyzer development pilot succeeded, conservative usage US$0.0009045. End-to-end development pilot active (scripts/pilot.py, work/pilot.log); held-out tests not run. API reservation ledger is results/raw_runs/budget-ledger.json.

Ruling: Add B2P (task-only gateway with provenance) to prevent attributing a stronger runtime gate to graph reasoning. Separate deterministic scripted stress runs from real-model agent runs; never call replay outcomes observed LLM attack success.

Task 3 review: independent AI reviewer found incomplete oracle state/content checks, cross-client budget race, refusal classification and missing-rate plotting. Corrected before formal inference; 56 tests pass. No independent human annotation is implied. Final validation-v4 passed 4/4 baseline legitimate cases. Frozen manifest records 1,920 jobs, 30 scientific input hashes and final container sha256:9850de469127d1bcb737b4be6b8a76b78208999b3c83fe2f17b73531ddc73477. Formal execution and original static analysis now proceed under the same US$20 ledger.

Paper tooling: official Tectonic 0.17.0 acquired with verified archive hash. Windows long-path failure in the deep project-local TeX cache was resolved by using the shorter temporary gcr-texcache directory; source and results remain in the study folder. Thirteen papers now acquired including the prior review's Progent and CaMeL references.


## 2026-10-14: Completed findings and manuscript

All scheduled executions completed with unchanged frozen scientific hashes. Original static analysis resolved 167/168 cases; the incomplete generation is retained as unresolved. All 1,362 API calls requested/returned gpt-6-luna, costing an estimated US$1.013328125 with zero pending reservations. Independent final AI review verified measurements and found no material blockers. The paper has 12 body pages plus one reference page (14 entries), and every rendered page was visually inspected. Sanitized evidence export contains 3,595 measurement/accounting files; full originals remain local. The final package is undergoing offline reaggregation and archive verification.


Final delivery verification: a fresh short-path Windows extraction restored all 3,595 evidence/accounting records, ran the frozen aggregator without an API credential or paid calls, and reproduced every summary field within 1e-10 plus all three manuscript LaTeX tables byte-for-byte. Initial deep-path extraction failed at the Windows path-length boundary; the reproduction guide now recommends a short extraction root. Final archive CRC and SHA256 checks passed with no credential-pattern findings. No scientific inputs were changed after freezing and nothing was published or submitted.
