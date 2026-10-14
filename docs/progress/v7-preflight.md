# V7 preflight review and freeze
Date: 2026-10-14 (Pacific/Auckland).
User authorized autonomous redesign and measurement; no additional credential setup is required.

- New closed IR fixtures: four contexts, three variants, four sinks. Unsafe programs permit four local edits or two shared-prefix edits; all required aggregates survive the latter.
- 19 v7 tests pass, including independent concrete/symbolic cross-checks, minimum repair, graph/flat parity, malicious authority grants not oracle-corrected, input isolation, failed-call denominators and accounting. Prior 165 tests also passed.
- Fresh read-only reviewer: review_v7_preflight, GPT-6 Luna. No API measurements were made by reviewer.
- Review finding fixed: search candidate verification work was absent from initial counters. Every candidate now records concrete and symbolic node evaluations; reporting is operation proxies, not runtime speedup.
- Review finding fixed: per-arm cost and call accounting added, including explicit shared authority allocation and edit histograms.
- Reviewer request-count objection resolved by exhaustive request hashes: 72 logical policy uses yield 48 unique requests because unsafe/safe inputs coincide within a repeat. No cross-repeat sharing. Together with 360 audits, plan has 408 physical requests; conservative no-sharing bound remains 432.
- Final reviewer acknowledgement: all 19 tests pass; no remaining blocker from accounting review.
- Prior ledger reconciled at USD2.124267425, zero pending reservations. Incremental budget USD6; conservative per-call-envelope worst case USD4.68; original total limit USD20.
- Scope: declared IR and trusted tool semantics, not arbitrary code extraction or production sandbox enforcement. Four synthetic contexts share a topology family. No independent human labels.

Scientific source, tests, protocol and preparation are frozen in research_v7/results/freeze.json and committed before measurement. Later reports are derived from retained responses; frozen source is never silently changed.
