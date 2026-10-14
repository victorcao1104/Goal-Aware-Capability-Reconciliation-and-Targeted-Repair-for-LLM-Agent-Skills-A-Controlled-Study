# V5 measurement and publication audit

All measurements used frozen source 3cf5a2def4aee6c4e628a9f298c1e15e6ecff093. No post-outcome changes were made to source, prompts, schema, evaluator or labels.

- 360 scheduled jobs completed: 736 method rows and 176 intervention-update rows.
- 562 requests and 562 dispatch attempts, all gpt-6-luna and status ok. No interruption or silent resampling.
- Independent credential-free replay verified 929 evidence files and recomputed every trajectory/summary. Independent gpt-6-luna review also reconciled the original ledger: 2642 cumulative entries, zero unsettled, USD1.645422625 total; V5 increment USD0.210192250.
- All 139 unit tests passed (61 v1, 25 v2, 14 v3, 20 v4, 19 v5). Report verification passed; the three-panel figure was visually inspected. New public artifacts were scanned for credential patterns with zero matches; private provider records and .env.local remain ignored.
- Review identified clean utility failure as a scanner false-uncertainty/semantics interaction: all eight clean uses cite an absent on_error branch. Both reports now explicitly explain the cause and 0/8 clean completion. This is not represented as graph failure or semantic policy error. One Flat finding also references an undeclared branch and is rejected by the grounding check.
- The report separates raw versus evidence-valid verdicts, intervention maps versus model-generated mistakes, and unique physical requests versus repeated logical uses. The graph difference is one logical correct use; raw accuracy ties and both auditors have the same poor benign utility.
- The dependency structures contain direct forbidden effects, so this verdict comparison does not require graph-essential reasoning. The limitation is disclosed; no redesign or rescoring occurred after outcomes.

The primary contamination hypothesis was not supported by these fixed, explicit-authority synthetic samples. This is an evidence-preserving supplement, not a positive-superiority rewrite of the original IEEE paper.
