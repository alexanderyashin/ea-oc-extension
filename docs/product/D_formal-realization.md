# D — Formal Realization Mapping (C → Repo)

**Project:** EA-OC-EXTENSION / ESTRA  
**Parent:** PRODUCT SYSTEM HQ  
**Child:** CHILD-D (Formal Realization Mapping)  
**Status:** ACTIVE (facts-first; maps current repo implementation; no new semantics)  
**Language:** RU only  
**Rule:** Diagnostic-only. No prescriptions. Repo is SPOT.

---

## 0) Binding dependencies (source of truth)

This mapping is **binding** to:

- `docs/product/C_functional-core.md` (defines F1..F6 contract)
- `docs/product/B_user-ontology.md` (roles/forbidden roles; expectation→refusal; User↔STOP↔Ledger↔Θ)
- `docs/product/A_capability-envelope.md` exists but is currently **empty (0 bytes)** → cannot contribute constraints (nominal binding only).

**Norm:** if discrepancies exist, `A` and `B` override `C`, and this document only records **observed realization** + **observed mismatches**.

---

## 1) Repo discovery (facts)

### 1.1 Product docs (this folder)
- `docs/product/00_index.md`
- `docs/product/A_capability-envelope.md` (empty / 0 bytes)
- `docs/product/B_user-ontology.md` (ACTIVE)
- `docs/product/C_functional-core.md` (ACTIVE)
- `docs/product/D_formal-realization.md` (this file)

### 1.2 Implementation strata (cockpit)

**Compute (functional core realization)**
- `apps/cockpit/src/compute/determinism.ts`
- `apps/cockpit/src/compute/shock.ts`
- `apps/cockpit/src/compute/cascade.ts`
- `apps/cockpit/src/compute/thresholds.ts`
- `apps/cockpit/src/compute/simulate.ts`
- `apps/cockpit/src/compute/types.ts`

**State & STOP latch**
- `apps/cockpit/src/store/graph.store.ts`

**UI (observation wrappers)**
- `apps/cockpit/src/ui/Ledger.tsx` (explicitly “Ledger (factual)” + “STOP locked”)
- other UI panels: `TopBar.tsx`, `Inspector.tsx`, `Palette.tsx`, etc.

**Gates (feature locking / demo tier)**
- `apps/cockpit/src/gates/tier.ts` (BUILD_TIER default demo → safe-by-default)

**Entry wiring**
- `apps/cockpit/src/App.tsx` (default app)
- `apps/cockpit/src/main.tsx` (mode switch: `Child16App` vs `App`)

---

## 2) Anchors of Truth vs derived wrappers

### 2.1 Anchors of Truth (truth-bearing)
1) **Compute pipeline**: `compute/simulate.ts` + `thresholds.ts` + `cascade.ts` + `shock.ts` + `determinism.ts`  
2) **STOP latch and refusal guards**: `store/graph.store.ts` (`simLocked` + early-return in setters / runShock)  
3) **Build tier single source of truth**: `gates/tier.ts` (`IS_DEMO` default)

### 2.2 Derived wrappers (must not carry semantics)
- UI rendering: `ui/*`, `App.tsx`
- UI is allowed to:
  - select inputs,
  - trigger run/reset,
  - render observation (states + ledger),
  - show locked feature dialogs.
- UI is forbidden to:
  - compute Θ / STOP reasons,
  - create recommendations,
  - introduce scoring/optimization/prediction semantics.

---

## 3) Invariants and where they are enforced

### 3.1 STOP is terminal (latch)
**Where:** `apps/cockpit/src/store/graph.store.ts`

**Observed enforcement:**
- `simLocked: boolean // STOP lock`
- Guards:
  - `setShockType`, `setShockScope`, `setShockIntensity`: `if (get().simLocked) return;`
  - `runShock`: `if (get().simLocked) return;`
- On run result:
  - `simLocked: res.stop`

**Meaning (binding to C/B):** STOP is not UI-mode; it is a functional terminal boundary.

### 3.2 Θ is computed, not guessed
**Where:** `apps/cockpit/src/compute/thresholds.ts` + used in `simulate.ts`

**Observed Θ model:**
- `stateFromScore(score): NodeState`
  - `>=0.9 → STOP`, `>=0.6 → RED`, `>=0.3 → WARN`, else `OK`
- `globalStopFromStates(states)`:
  - STOP if any node is STOP
  - else STOP if ratio (RED+STOP)/N ≥ 0.30, with explicit reason string

### 3.3 Ledger is the only factual explanation channel
**Where:**
- produced in `compute/simulate.ts` as `LedgerEvent[]`
- stored in `store/graph.store.ts` as `ledger: LedgerEvent[]`
- rendered in `ui/Ledger.tsx` (factual fields only)

**Observed emission rules:**
- emits `threshold_crossed` only on worsening (`isWorse(next, prev)`)
- emits `info` when no target nodes exist for selected scope
- emits `global_stop` when global stop criterion triggers

### 3.4 Determinism is explicit
**Where:** `compute/determinism.ts` + used by `simulate.ts` / `cascade.ts`

**Observed mechanisms:**
- deterministic sort (`sortIds`)
- deterministic edge order (`byStableEdge`)
- clamping (`clamp01`)
- fixed cascade constants (no tuning loop)

---

## 4) Hard prohibitions (structural fences against semantic expansion)

### 4.1 No free-form optimization / tuning
**Where (facts):**
- intensity is **discrete enum**: `ShockIntensity = 0.1 | 0.3 | 0.5` (`compute/types.ts`)
- cascade stress increment is a **fixed constant** `0.12` (`compute/cascade.ts`) with explicit comment:
  “Fixed constants (demo-safe, deterministic, no tuning loop).”

### 4.2 Demo-by-default tier
**Where:** `gates/tier.ts`

**Observed:**
- `BUILD_TIER` defaults to `"demo"`
- `IS_DEMO` true unless tier is full

This is an architectural bias towards “safe demonstrator”.

### 4.3 STOP prevents iterative control post-terminal
**Where:** `store/graph.store.ts` (guards + latch)

The user cannot “keep tweaking” after STOP (aligns with forbidden roles Z1..Z3 in `B_user-ontology.md`).

---

## 5) Functional Core mapping: F1..F6 → repo realization

This section binds **exactly** to `docs/product/C_functional-core.md` (F1..F6).

> Important: the declared types in C use “Intensity = 10|30|50” and “Scope = ALL_SYSTEMS/SELECTED_NODE”.  
> Implementation uses `intensity = 0.1|0.3|0.5` and `scope = "all_systems" | "selected"`.  
> This is recorded as an **observed mismatch** (see §6).

### 5.1 Table: F1..F6 → concrete files/functions

| Function (C) | Declared intent (C) | Realization locus | Concrete symbols | Notes (facts only) |
|---|---|---|---|---|
| **F1 — NormalizeShockInput** | validate/normalize shock input | **PARTIAL / IMPLICIT** in store+compute | `pickTargetNodeIds(...)` (simulate.ts), `ShockIntensity` type (types.ts), `simLocked` guards (store) | No explicit “normalize function” exists; normalization happens via typed enums + fallback logic (“all_systems” → systems → all nodes). |
| **F2 — ApplyShock** | deterministic base shock → affected nodes + ledger | `compute/shock.ts` + `compute/simulate.ts` | `applyShockBaseScore(cfg)` + “Step 0 apply base shock to targetIds” + ledger `threshold_crossed` | Implementation applies base score bump to targets and records threshold crossings (not a dedicated “shock_applied” event). |
| **F3 — Cascade** | propagate through connectivity + ledger | `compute/cascade.ts` + `compute/simulate.ts` | `propagateCascades({ ... })` | Propagates stress from RED/STOP sources to targets; updates `scores` in-place; ledger records subsequent threshold crossings per step (no dedicated “cascade_step” event). |
| **F4 — EvaluateThresholds** | apply Θ and compute STOP + ledger | `compute/thresholds.ts` + `compute/simulate.ts` | `stateFromScore`, `isWorse`, `globalStopFromStates` | Θ model is score→state thresholds + global stop rule. Ledger contains `threshold_crossed` and `global_stop`. |
| **F5 — ReduceToStorePatch** | build atomic store patch (simLocked/nodeStates/ledgerAppend) | **inlined** in store `runShock()` | `runShock(): simulateShock(...) → set({ simLocked, nodeStates, ledger, nodes styled })` | Patch is applied via zustand `set(...)`. There is no separate “patch object” type. |
| **F6 — CommitPatch** | apply patch into store (only side-effect) | `store/graph.store.ts` | zustand `set((st)=>({...}))` | Side-effect boundary is the store action `runShock()` calling compute and committing result. |

### 5.2 “Derived functions” from C: D1, D2 — where realized

- **D1 — RunSimulationOnce**: realized by `store.runShock()` calling `compute/simulateShock(...)` and committing.
- **D2 — ResetSimulation**: **declared in C**, but in current code:
  - `GraphState` declares `resetShock: () => void;`
  - **Implementation currently missing** (no `resetShock` provided in the store initializer).  
  This is an **observed gap** vs the declared contract.

---

## 6) Observed implementation mismatches / defects (facts)

This section does **not** propose new semantics; it records observable discrepancies relevant for formal realization.

### 6.1 Intensity and Scope encoding differs vs C
- C declares `Intensity = 10|30|50` and scope tags `ALL_SYSTEMS` / `SELECTED_NODE`.
- Implementation uses:
  - `ShockIntensity = 0.1 | 0.3 | 0.5`
  - `ShockScope = "selected" | "all_systems"`

This is a representational mismatch (scale/encoding), not a semantic expansion.

### 6.2 `SimResult` type has structural errors (compute/types.ts)
Observed in `apps/cockpit/src/compute/types.ts`:
- `LedgerEvent` union has a variant missing `type: "global_stop"` field (object only `{ reason: string }`)
- `SimResult` includes `stop: boolean` duplicated twice

These are type-level defects that can affect correctness of the “ledger-bound” contract.

### 6.3 STOP latch commit is immediately overwritten (store bug)
Observed in `store/graph.store.ts` inside `runShock()`:
1) First `set(...)` commits:
   - `simLocked: res.stop`
   - `nodeStates: res.nodeStates`
   - `ledger: res.ledger`
   - styles nodes accordingly
2) Immediately after, a second `set(...)` resets:
   - `nodeStates: {}`
   - `ledger: []`
   - `nodes: style undefined`

Thus, even when compute produces ledger and states, the store clears them right away.  
This contradicts the declared intent in C and B that ledger is the explanatory channel and STOP is observable.  
(We record this as fact; fixing is outside this doc’s scope.)

### 6.4 Determinism violation in UI node placement
Observed in `addNodeFromPalette`:
- `position: { x: 120 + Math.random() * 420, y: 120 + Math.random() * 280 }`

This introduces randomness in UI layout. It does not necessarily violate compute determinism, but it violates “fully reproducible scene setup” if reproducibility includes node placement.

---

## 7) Structural elements (not UI) — what is semantic-bearing

Even if surfaced in UI, these are core-structural:
- `SimConfig` domain (`shockType`, `scope`, `intensity`) — `compute/types.ts` and store
- `NodeState` lattice (OK/WARN/RED/STOP) — `compute/types.ts`
- Θ thresholds and stop criterion — `compute/thresholds.ts`
- cascade rule and constants — `compute/cascade.ts`
- STOP latch semantics — `store/graph.store.ts`
- ledger event schema (what may be said) — `compute/types.ts`

---

## 8) Non-Claims (what the realization does NOT do)

Aligned with `B_user-ontology.md` and C’s “No healing / No prescriptions”.

This demonstrator does **not**:
- output recommendations (“do X”), mitigations, recovery plans
- run optimization loops or objective solving
- claim forecasting/predictive validity
- generate BI dashboards, KPIs, maturity scores, benchmarking
- export reports (PDF/CSV) or persist projects
- provide post-STOP continuation (“healing” / undo / auto-fix)

---

## 9) Verification gates (doc-only change)

For documentation updates only:
- `npm --prefix apps/cockpit run typecheck` must be GREEN
- `npm --prefix apps/cockpit run build` must be GREEN

---

## 10) What this document enables (and what it forbids)

**Enables:** traceable audit of where C is realized; locating invariants; identifying prohibited extension points.  
**Forbids:** any introduction of new functions, new meanings, or “productization” semantics.
