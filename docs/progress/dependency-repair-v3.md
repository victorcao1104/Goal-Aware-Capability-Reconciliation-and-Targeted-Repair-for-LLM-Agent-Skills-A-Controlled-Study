# V3 execution ledger

Branch created from v2 commit 43aea34. Protocol drafted before implementation and measurement. The baseline may freely reconstruct dependency information. Pre-flight: fixture public views feed engine/model; only the independent evaluator reads reference data. New orchestration imports but never changes frozen v2 modules.

Pre-measurement review by a separate gpt-6-luna reviewer found a receipt-witness roundtrip discrepancy and a missing committed-input gate. Regression tests reproduced both and fixes passed. The live runner now rejects combined freeze/live invocation, requires the exact frozen source and manifest in HEAD, records every attempt in the original shared US$20 ledger, and writes public records atomically. The API client itself is explicitly hashed.

The reviewer also caught that the reused v2 shuffled index rotated only edges. V3 now consistently permutes edges, effect nodes and distance keys, with a dedicated test. The preliminary uncommitted v3 freeze was regenerated after this correction; no v3 API request had been made. V1/v2 frozen sources remain unchanged. Clean and authorized controls consume zero model requests.
