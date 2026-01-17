# RUN-20260117-whitepaper-structure-v1

## Goal
Produce a publication-grade outline for the K_EA whitepaper, ETS-first, diagnostic-only.

## Inputs (immutable / referenced)
- configs/ETS.K_EA.v1.1.yaml (sha256: c2385be94c79f52c9cbe6ee4437994c8833224cdce50ed8665241c0fdb7ecce6)
- paper/manifest.yml (current HEAD pinned)
- Existing repo computational artifacts (synthetic demos only; clearly marked)

## Non-negotiable constraints
- No new primitives
- No modification of ETS
- No empirical claims
- No prescriptions / roadmaps / optimization advice
- STOP conditions and No-Go results are first-class

## Deliverables
- paper/outline.md (canonical structure)
- Updated paper/whitepaper.md to match the outline (headings + placeholders only)

## Exit criteria
- Outline covers all ETS fields and adds required publication sections (scope, non-claims, limits, reproducibility).
- Clear separation: formal spec vs synthetic demos vs limits.
