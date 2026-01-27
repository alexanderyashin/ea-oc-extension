# B — User Ontology (ESTRA Demonstrator)

Status: ACTIVE (CHILD-B)  
SPOT: repo is source of truth.  
Scope: **diagnostic demonstrator** (not a BI tool; not an optimizer; not a decision system).

## 0) Binding constraint note (A_capability-envelope.md)
`docs/product/A_capability-envelope.md` exists but is currently **empty (0 bytes)**.  
Therefore, this document **must not invent** an envelope. The user ontology below is derived **only** from observable repository facts (compute + UI + gating).

---

## 1) Formal definition: User-as-Observer

A **User** in ESTRA is a system role defined by the following invariant:

> The user may **select inputs** and **observe deterministic outputs** (states + ledger) inside a bounded demonstrator.
> The user must not receive advice, prescriptions, optimization results, exports, or decision automation.

Formally, the user operates on **declared inputs** only:
- `SimConfig = { shockType, scope, intensity }`
- selection scope: `selected | all_systems`
- explicit run trigger: `runShock()`
- explicit reset: `resetShock()`

The user never changes the underlying world by “applying decisions”; the user only triggers a **simulation episode** and observes a **factual trace** (Ledger).

---

## 2) Capability envelope for the user (derived from repo facts)

### 2.1 Allowed actions (what user can do)
Derived from `apps/cockpit/src/store/graph.store.ts` + compute layer:
- **Configure a shock** via `SimConfig`:
  - `ShockType`: `infra_capacity_drop | node_failure_rate`
  - `ShockScope`: `selected | all_systems`
  - `ShockIntensity`: `0.1 | 0.3 | 0.5`
- **Select target context**:
  - `selected` requires a selected node; otherwise the run yields an `info` ledger event.
  - `all_systems` targets nodes that are `system` kind; fallback is “all nodes” (compute rule).
- **Run** a deterministic episode: `simulateShock(...)`
- **Observe**:
  - node states `{OK, WARN, RED, STOP}`
  - `stop` boolean → STOP lock
  - ledger events (factual event stream)
- **Reset** state: clears ledger, states, stop lock.

### 2.2 Hard constraints (STOP lock)
After a run, if `stop === true`, UI/store enforces **hard lock**:
- `simLocked: true` blocks `setShockType`, `setShockScope`, `setShockIntensity`, `runShock` (guards: `if (get().simLocked) return;`).
- Ledger UI shows `"STOP locked"`.

This makes the user’s position **non-operator**: they cannot continue “tuning” the system after STOP.

---

## 3) User roles within the demonstrator (U1..Un)

Roles are **capability roles**, not personas.

### U1 — Public Demo Observer
- Observes: graph, node states, ledger.
- Uses: minimal inputs (SimConfig) + run/reset.
- Has no access to full/audit-gated features.

### U2 — Scenario Selector (bounded)
- Same as U1, with emphasis on selecting:
  - `shockType`, `scope`, `intensity`
  - `selected node` vs `all_systems`
- Still cannot generate recommendations or actions.

### U3 — Model Viewer / Graph Arranger (bounded)
- Interacts with graph structure in the UI (add/connect/arrange) to create a scenario surface for observation.
- This is not “system editing”; it is **demonstrator scenario setup**.

### U4 — Full-build Auditor (gated)
Derived from `LockedFeatureDialog.tsx` + tier gating:
- Full build requires `VITE_BUILD_TIER=full` **and** “full audit / evidence context”.
- The user role here is not “operator”; it is an **audit-context carrier** enabling gated functions under controlled conditions.

---

## 4) Forbidden roles (Z1..Zm) with reasons

### Z1 — Operator
Forbidden because:
- STOP lock prevents iterative operational control.
- No “apply” mechanics exist; only simulation episodes.

### Z2 — Decision-maker (in-tool)
Forbidden because:
- Demonstrator produces **no prescriptions** and no decision automation.
- Ledger is explicitly factual (“Ledger (factual)”), not a decision output.

### Z3 — Optimizer
Forbidden because:
- No optimization loop, no objective, no solver, no “improve” actions.
- STOP terminates exploration structurally.

### Z4 — BI Analyst / Reporting system user
Forbidden because:
- Demo explicitly disallows reporting/export/prediction.
- “No hidden exports exist in the demo.” (LockedFeatureDialog)

### Z5 — Forecaster / Predictor
Forbidden because:
- The system is deterministic demonstrator logic for states and thresholds; it does not claim predictive validity.
- The output is an observation trace of the simulated episode, not a forecast.

---

## 5) Expectation → Refusal map (user-facing ontology guard)

| What user might expect | Refusal / why it must not be provided |
|---|---|
| “Tell me what to do” | No advice or prescriptions; demonstrator is diagnostic-only. |
| “Optimize my architecture / costs / resilience” | No optimization loops; no objectives; STOP ends control. |
| “Generate a report / export PDF/CSV” | Reporting/export is forbidden; demo has no hidden exports. |
| “Predict future outcomes” | No prediction claim; outputs are episode-trace (ledger) only. |
| “Run unlimited what-if tuning” | STOP lock prevents iterative control after terminal conditions. |
| “Make decisions inside the tool” | The tool does not act on reality; it only shows deterministic trace. |

---

## 6) User ↔ Θ ↔ Ledger ↔ STOP

### Θ (thresholds)
Thresholds are encoded as deterministic mapping `score → state`:
- `score ≥ 0.9 → STOP`
- `score ≥ 0.6 → RED`
- `score ≥ 0.3 → WARN`
- else `OK`

The user does not set Θ; the user only observes threshold crossings.

### Ledger (factual trace)
Ledger is the only explanatory channel and is constrained to factual statements:
- events are emitted on **worsening only** (`isWorse(next, prev)`),
- each event carries **prev/next state** and **scorePrev/scoreNext**,
- `info` events exist for “no target nodes”.

This positions the user as a **trace reader**, not an interpreter receiving conclusions.

### STOP (terminal boundary)
STOP is produced by:
- Any node reaching STOP, OR
- A global criterion (ratio of RED+STOP).

When STOP is reached:
- a `global_stop` ledger event is emitted,
- `stop: true` locks the simulation controls (`simLocked`).

Thus STOP is a **structural boundary** that defines the user position:
> the user can observe how the boundary was reached (ledger), but cannot continue as an operator.

---

## 7) Non-Claims (explicit)
The user is **not**:
- an operator of a real system,
- a decision-maker receiving prescriptions,
- an optimizer running objective functions,
- a forecaster,
- a reporting/export consumer,
- a BI user.

The demonstrator claims only:
- bounded inputs,
- deterministic episode,
- factual ledger trace,
- explicit STOP semantics.

---

## 8) Repository fact anchors (non-exhaustive)
- `apps/cockpit/src/compute/types.ts` — SimConfig, states, ledger event schema.
- `apps/cockpit/src/compute/thresholds.ts` — score→state thresholds; global STOP criterion.
- `apps/cockpit/src/compute/simulate.ts` — deterministic simulation + ledger emission rules.
- `apps/cockpit/src/store/graph.store.ts` — simLocked gating; allowed input setters; run/reset.
- `apps/cockpit/src/ui/Ledger.tsx` — “Ledger (factual)”; “STOP locked”.
- `apps/cockpit/src/ui/LockedFeatureDialog.tsx` — demo is partial/diagnostic-only; gated full build; no hidden exports.
- `apps/cockpit/src/gates/tier.ts` — demo/full tier single source of truth.

