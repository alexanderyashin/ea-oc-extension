# ESTRA Monolith — Product System HQ

Status: ACTIVE  
SPOT: repo is source of truth.

This folder defines the Product System layer for the ESTRA monolith (diagnostic demonstrator; not a BI tool).

Files:
- A_capability-envelope.md (DRAFT, CHILD-A) — what the tool can/cannot do; STOP boundaries; non-claims; repo mapping. (**NOTE:** currently empty / 0 bytes)
- B_user-ontology.md (ACTIVE, CHILD-B) — user-as-observer; allowed roles; forbidden roles; expectation→refusal; User↔STOP↔Ledger↔Θ.
 Cascade → Θ → STOP), terminal STOP semantics, ledger-bound factual explanation; UI-independent; diagnostic-only.   
- C_functional-core.md (ACTIVE, CHILD-C) — functional contract F1..F6 fixed against current code (compute+store); diagnostic-only.
- D_formal-realization.md (ACTIVE, CHILD-D) — formal mapping C→repo: F1..F6 → files/functions; invariants (STOP/Θ/Ledger); anchors-of-truth vs wrappers; structural prohibitions; non-claims; observed mismatches.
- E_ui-system-derivation.md (pending)
- F_technical-architecture.md (pending)
- G_implementation-plan.md (pending)

Summary (current):
- The cockpit is deterministic and reproducible at the compute/core level; operations are bounded by explicit inputs and hard STOP semantics.
- The system exposes a functional core with terminal states (STOP) and explicit composition boundaries.
- Explanations are factual (ledger/events); recommendations, optimization, prediction, scoring, and reporting are forbidden within the demonstrator.
