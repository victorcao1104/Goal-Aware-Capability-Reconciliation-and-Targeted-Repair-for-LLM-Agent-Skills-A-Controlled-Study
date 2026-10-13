# Independent AI code review before formal inference

Reviewer: a fresh subagent with no inherited conversation history, instructed to inspect source/tests and avoid API calls or credentials. This is not independent human annotation. The reviewer made no source edits.

## Findings and disposition

1. **Incomplete modification oracle (P1).** The original oracle checked only summary and owner. A deleted private file and extra output field were missed. The revised oracle compares the complete file map and checks committed effects, including writes later restored. Regression tests cover delete/extra fields and forbidden-source restoration.
2. **Incomplete required-delivery oracle (P1).** A summary-only record and an empty record carrying private taint could pass. The revised oracle requires structural equality with the complete required record, recursively through list concatenation. Source taint does not prove delivery.
3. **Shared budget race (P1).** Two separate Budget instances could overwrite reservations. The revised implementation locks a ledger lockfile at the operating-system level, reloads the ledger for each transaction, and persists reservations atomically. The stale-instance double-reservation reproduction now raises BudgetExceeded.
4. **Refusal misclassification (P2).** Provider refusals could become invalid JSON/infrastructure failure. Explicit ModelRefusal and ModelIncomplete categories preserve observable state and behavioral denominators. A mock refusing client test verifies task failure with no observed attack and a valid outcome status.
5. **Missing-rate charting (P1).** `rate or 0` could show unavailable rates as secure zero. Figure construction now uses NaN/omitted bars and an N/A annotation.

The reviewer rechecked the initial fixes and identified remaining committed-write source checks and chart handling. Those were corrected before freezing, and 56 tests passed. Formal source hashes include these corrections. The final local runtime test suite includes worker exit, bounded RPC timeout, canonical resource identity, scoped prohibitions, true baseline distinctions, label-exclusion checks, and independent acceptance.

## Supported conclusions of review

- B2R does not require a graph in its configuration.
- Comparable methods share the initial executor proposal without selecting outcomes.
- Repeat-specific IDs preserve repeated model sampling.
- The fixes improve measurement correctness; they do not establish unrestricted sandbox security or general semantic correctness.

The review did not tune model prompts from held-out outcomes. Formal input freeze occurred after the review and final validation. Original development and validation records are retained separately.
