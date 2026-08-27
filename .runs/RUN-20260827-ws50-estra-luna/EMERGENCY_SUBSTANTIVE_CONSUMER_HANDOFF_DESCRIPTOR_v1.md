# WS-50 Emergency Candidate Consumer Handoff

This is a bounded framework-engineering candidate handoff descriptor derived from the frozen 40-row metadata matrix. It does not copy or mutate ESTRA source content and does not constitute scientific, publication, release, activation or authority evidence.

## Candidate contract

- Candidate rows: 40; every row remains `candidate_only=true` and `promotion_forbidden=true`.
- Inputs: frozen candidate metadata, accepted producer receipts when supplied, and exact read-only consumer refs.
- Outputs: candidate adapter descriptor, fail-closed admission decision, and consumer handoff metadata.
- Applicability: finite deterministic engineering candidate scope only. Universal, stochastic, enterprise-transfer, dominance, publication and activation claims are out of scope.
- Conformance: freeze-manifest identity and guarded 69-test baseline are evidence pointers only; they do not accept the candidate.

## Consumer anchors

| Consumer | Exact anchor | Required handoff predicate | Open receipt slots |
| --- | --- | --- | ---: |
| WS-60 Toolkit | `c79ca249aa202718debacffe3b4a5566948a06ae` @ `a17246b0d1b6a4256e1c73c48170cdfab6fc2e24` | Exact repository/branch/commit/tree digest, `READ_ONLY_REFERENCE`, recommendation-only reviewer | 40 admission + 40 reviewer |
| WS-70 adapter downstream | `b0ba5b95a75cb507e08013aa6fb66df12e2e5b3d` @ `e65a8fcb2edad46bcf0c49d0b73586857ea74d3b` | Exact repository/branch/commit/tree digest, `READ_ONLY_REFERENCE`, recommendation-only reviewer | 40 admission + 40 reviewer |
| WS-75 Publication closeout | `160312105bf3e8448a958328152c123af0505443` @ `5045192778ef6dbe422d8a4b1e81ae72929cfd95` | Exact repository/branch/commit/tree digest, `READ_ONLY_REFERENCE`, recommendation-only reviewer | 40 admission + 40 reviewer |

Independent engineering review: 1 open receipt slot at `independent_engineering_review.receipt`.

Total open slots: 241. No receipt is invented or inferred. Exact slot enumeration is in `EMERGENCY_SUBSTANTIVE_CANDIDATE_GENERATION_PACKET_v1.json`.

## Fail-closed consumer rules

Stale refs require `BLOCKED_RECAPTURE_REQUIRED`; provenance mismatch `BLOCKED_PROVENANCE`; digest mismatch `BLOCKED_DIGEST`; non-read-only rights `BLOCKED_RIGHTS`; private/runtime effects `BLOCKED_PRIVATE_RUNTIME`; widened claim `BLOCKED_CLAIM_CEILING`. Any attempt to grant authority is rejected. The negative holdout boundary remains fixed: `dominance=false`, holdout delta negative, confidence interval includes zero, and `accepted=0`.

## Downstream request

WS-60, WS-70 and WS-75 owners should return typed admission and reviewer receipts against the exact anchors above. The independent engineering reviewer should return one bounded profile-review receipt covering all 40 rows. Until all receipts are present and exact, the packet remains `BLOCKED_DEPENDENCY` / candidate-only.
