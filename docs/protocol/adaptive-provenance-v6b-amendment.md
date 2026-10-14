# Prospective response-parser amendment: v6b

Original v6 source remains frozen at 7e191b6. After 86 recorded requests (48 calibration and 38 development), two calibration Luna-none policy responses were classified as invalid JSON because the client concatenated intermediate commentary and final_answer messages. Inspection established valid separate final JSON. No candidates had been selected and no held-out request had been sent.

Execution was stopped. One in-flight call without a recoverable response is conservatively charged its entire USD0.0074964 reservation, never treated as free. Recorded v6 requests cost USD0.041082575. Cumulative prior cost for v6b is USD1.6940016. The original v6 absolute ceiling of USD6.645422625 is unchanged, including the aborted run; the overarching user ceiling remains USD20.

V6b preserves all v6 fixtures, prompts, role schemas, budget envelopes, model settings, scoring, dev search schedule, selection rule and held-out contexts. It imports those frozen modules. Only response transport parsing changes: prefer one explicitly final_answer message, otherwise accept one phase-less message; never parse commentary as final; reject missing/ambiguous finals; retain refusal/incomplete/schema errors. Sanitized message texts and phases are now published so parsing can be independently replayed.

Source: [official Responses API reference](https://developers.openai.com/api/reference/resources/responses/methods/create), which distinguishes commentary and final_answer phases. This is an interface repair, not a prompt change or an attack success optimization.

The complete fixed schedule is restarted under a separate output directory and reservation namespace. Aborted observations are retained for audit and excluded from confirmatory metrics. Their costs remain in cumulative accounting. V6b freezes and commits before any new call. No new held-out cases or adaptive budget are introduced. The original source's reproduce --prepared still verifies; the aborted original run has no complete results claim.
