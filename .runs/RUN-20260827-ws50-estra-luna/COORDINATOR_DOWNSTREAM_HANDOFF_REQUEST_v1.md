# WS-50 ESTRA — Coordinator-facing downstream handoff request v1

Request target: OC14 coordinator and downstream WS-60 Toolkit, WS-70 adapter/execution contour, and WS-75 Publication.

Review `.runs/RUN-20260827-ws50-estra-luna/COORDINATOR_ESTRA_CONTRACT_TRACEABILITY_ADMISSION_ENVELOPE_v1.json` as a metadata-only 40-row contract traceability packet. Resolve the exact ESTRA concept, OC producer ceiling, frozen semantic digest, source provenance, rights, recorded replay evidence and consumer route for every row. Return only a read-only admission receipt or deterministic fail-closed rejection. Do not accept, promote, execute, publish, mutate candidates, or alter OC/shared state.

Required response: WS-60 and WS-75 must return current commit/tree/digest and read-only rights receipts. WS-70 must provide the missing current commit/tree/digest and rights receipt; until then admission returns `BLOCKED_RECAPTURE_REQUIRED` / `CURRENT_WS60_WS70_WS75_REFS_REQUIRED`. All consumers must reject stale/provenance/digest/rights/private-runtime/widened-claim negatives using the envelope codes.

Replay is pure metadata-only: `.runs/RUN-20260827-ws50-estra-luna/NINTH_TRANCHE_COORDINATOR_REPLAY_FIXTURE_v1.json` and `validate_ninth_coordinator_traceability_v1.py`. No live ESTRA execution, DB/raw/cold storage, HOST_IO or shared Logion edit occurred. Preserve `candidate_only=true`, `dominance=false`, negative holdout, CI-includes-zero and promotion/acceptance forbidden.
