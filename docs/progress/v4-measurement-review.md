# V4 measurement and publication review

Measured under the unchanged frozen source commit 1011556dbee7e04d5a6c7422b6d522df27dd48d3. User explicitly authorized live execution after preparation.

- All 480 method trajectories completed; 426 retained requests/dispatches, all gpt-6-luna. No outcome-driven scientific edits or resampling.
- One orchestration interruption is disclosed in v4-interruption.json. Original inner error is unavailable; resume completed the sole missing call and preserved all 520 prior request/trajectory hashes.
- Full incremental token-based estimate US$0.177864500; cumulative US$1.435230375. Zero pending reservations. before_usd in the run accounting is a resume balance; use after_usd minus prior_usd for the full v4 increment.
- Offline replay verified 527 evidence hashes, every scheduled trajectory and every summary field. Twenty v4 unit tests passed. Derived report verification and visual inspection passed.
- Independent read-only gpt-6-luna review reproduced the measurements, checked costs and denominators, and found no data or English-report blocker. Its final Chinese-report findings were addressed by explicitly defining evidence-valid correctness, explaining uncertain fallback scoring, and reporting both negative Mixed and positive Isolated raw-verdict differences as secondary diagnostics.
- Frozen protocol, model interfaces, case generation, gate, analysis and original v1–v3 scientific artifacts remain unchanged. Additions are measured evidence, a post-measurement diagnostic exporter and candid English/Chinese results reports.

The result does not demonstrate excess-permission attacks succeeding against Mixed or a robust graph advantage. Output-interface compliance and semantic over-restriction are substantive limitations, not silently corrected outcomes.
