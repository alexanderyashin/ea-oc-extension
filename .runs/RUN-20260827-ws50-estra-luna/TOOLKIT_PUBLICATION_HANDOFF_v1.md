# Toolkit/publication handoff — WS-50-ESTRA initial tranche

## Handoff state

`DISCOVERY_CHECKPOINT__GUARDED_BASELINE_PASS__SEMANTIC_ACCEPTANCE_OPEN`

Worker branch: `workstream/oc14-estra-luna-20260827`
Source candidate checkout: `main` at `5398bfed0efbc56ad969382df48af568ee2df24b`
Freeze manifest: `CANDIDATE_FREEZE_MANIFEST_v1.json`

## Delivered evidence

- 40 modified/untracked candidate files are individually hash-bound and
  classified `PRESERVE_INHERITED`.
- 2.0 and 3.0 are reviewed as separate additive lineages.
- Historical candidate receipts and their claim ceilings are recorded without
  being promoted to fresh baseline evidence; the fresh guarded 69-test suite
  passed with `PYTHONPATH=src`.
- The negative Phase C holdout boundary is retained; dominance is not claimed.
- Exact worker evidence diff is limited to the `.runs/RUN-20260827-ws50-estra-luna/`
  packet.

## Open obligations

1. Perform independent semantic review of source, schema, paper, fixture and
   release-manifest parity for each lineage.
2. Decide a separately authorized canonical transport set; do not infer it
   from this preservation manifest.
3. Keep Toolkit and publication consumers pointed at this handoff as
   `HOLD_SEMANTIC_ACCEPTANCE` until fresh evidence exists.

## Claim ceiling

This handoff proves only preservation, file identity and bounded semantic
review preparation. It does not prove current conformance, dominance,
publication readiness, release readiness, certification, deployment or
activation.
