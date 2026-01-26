# ESTRA Monolith — Product System HQ

Status: ACTIVE  
SPOT: repo is source of truth.

This folder defines the Product System layer for the ESTRA monolith (diagnostic demonstrator; not a BI tool).

Files:
- A_capability-envelope.md (DRAFT, CHILD-A) — what the tool can/cannot do; STOP boundaries; non-claims; repo mapping.
- C_functional-core.md (pending)
- D_formal-realization.md (pending)
- E_ui-system-derivation.md (pending)
- F_technical-architecture.md (pending)
- G_implementation-plan.md (pending)

Summary (current):
- The cockpit is deterministic and reproducible; operations are bounded by explicit inputs and hard STOP semantics.
- Explanations are factual (ledger/events); recommendations/optimization/prediction/reporting are forbidden within the demonstrator.
