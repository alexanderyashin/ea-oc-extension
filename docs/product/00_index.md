# ESTRA Monolith — Product System HQ

Status: ACTIVE
SPOT: repo is source of truth.

This folder defines the Product System layer for the ESTRA monolith (diagnostic demonstrator; not a BI tool).

Files:
- A_capability-envelope.md (DRAFT, CHILD-A) — what the tool can/cannot do; STOP boundaries; non-claims; repo mapping. (**NOTE:** currently empty / 0 bytes)
- B_user-ontology.md (ACTIVE, CHILD-B) — user-as-observer; allowed roles; forbidden roles; expectation→refusal; User↔STOP↔Ledger↔Θ.
- C_functional-core.md (ACTIVE, CHILD-C) — functional contract F1..F6 fixed against current code (compute+store); terminal STOP semantics; ledger-bound factual explanation; UI-independent; diagnostic-only.
- D_formal-realization.md (ACTIVE, CHILD-D) — formal mapping C→repo: F1..F6 → files/functions; invariants (STOP/Θ/Ledger); anchors-of-truth vs wrappers; structural prohibitions; non-claims; observed mismatches.
- E_ui-system-derivation.md (ACTIVE, CHILD-E) — strict derivation of UI system as observable projection of functional core: required visible elements (STOP/ledger/state map), forbidden UI elements (recommendations/exports/healing), conditionality (STOP/Θ/tier), and non-UI claims.
- F_technical-architecture.md (ACTIVE, CHILD-F) — technical layering (compute/store/ui/gates), responsibility boundaries, invariants, do-not-touch anchors, permitted refactorings, determinism & reproducibility gates.
- G_implementation-plan.md (pending)

Summary:
- The cockpit is deterministic and reproducible at the compute/core level; operations are bounded.
- The system exposes a functional core with terminal states (STOP) and explicit composition boundaries.
- Explanations are factual (ledger/events); recommendations, optimization, prediction, scoring, and reporting are forbidden within the demonstrator.
