# WS-50 ESTRA — dynamic downstream recapture request v1

Coordinator and downstream consumers WS-60, WS-70 and WS-75 must revalidate the 40-row traceability envelope from:

`.runs/RUN-20260827-ws50-estra-luna/DYNAMIC_CONSUMER_RECAPTURE_ENVELOPE_v1.json`

Return a read-only receipt containing exact repository, branch, commit, tree, commit-tree digest, rights, independent-reviewer predicate and runtime predicate. WS-70 current ref is now resolved as `622990823741fa0954c6b8d4b00d295b46c02411@a87e1755980bffb58b04009eac79af968e6e43d6`; do not substitute another ref.

The prior snapshot remains immutable history. Any stale or missing current ref returns `BLOCKED_RECAPTURE_REQUIRED`; provenance, digest, rights, private/runtime and widened-claim mutations return the envelope's fail-closed codes. Do not execute ESTRA live, mutate features/catalogues, touch DB/raw/cold/HOST_IO/shared/public state, promote or accept any candidate. Preserve `candidate_only=true`, `dominance=false`, negative holdout, CI-includes-zero and `semantic-review-candidate-only`.

Terminal readback found post-capture drift in WS-70 and WS-75; the captured dynamic snapshot is marked stale and requires a new recapture. Captured refs remain immutable and no history was rewritten.

Pure replay evidence:

- `.runs/RUN-20260827-ws50-estra-luna/TENTH_TRANCHE_DYNAMIC_RECAPTURE_FIXTURE_v1.json`
- `.runs/RUN-20260827-ws50-estra-luna/validate_tenth_dynamic_recapture_v1.py`
- `.runs/RUN-20260827-ws50-estra-luna/TENTH_TRANCHE_DYNAMIC_RECAPTURE_RECEIPT_v1.json`
