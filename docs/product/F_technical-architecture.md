# F — Technical Architecture (ESTRA Monolith)

Status: ACTIVE (CHILD-F)
SPOT: repo is source of truth.

This document фиксирует **техническую архитектуру** монолита ESTRA как взаимодействие слоёв
`compute / store / ui / gates` и их инварианты.

Binding (must remain consistent):
- `docs/product/C_functional-core.md`
- `docs/product/D_formal-realization.md`
- `docs/product/E_ui-system-derivation.md`

Non-goal: не вводит новых функций/смыслов, не меняет контракт C, не даёт продуктовых обещаний.

---

## 0) Repo facts (observed)

Code (observed):
- Compute: `apps/cockpit/src/compute/{determinism,shock,cascade,thresholds,simulate,types}.ts`
- Store:  `apps/cockpit/src/store/graph.store.ts`
- UI:     `apps/cockpit/src/ui/*` (TopBar, Inspector, Palette, nodes/Emap0Node, dialogs, child16/*)
- Gates:  `apps/cockpit/src/gates/tier.ts` + `apps/cockpit/src/ui/LockedFeatureDialog.tsx`

Gates (observed green):
- `npm --prefix apps/cockpit run typecheck` ✅
- `npm --prefix apps/cockpit run build` ✅

Functional observables (binding excerpt from C/E, confirmed in store state):
- O1 `store.simLocked: boolean` (STOP latch)
- O2 `store.nodeStates: Record<string, NodeState>` (status map)
- O3 `store.ledger: LedgerEvent[]` (factual trace)
- O4 last stop reason appears as `LedgerEvent { type:"global_stop", reason }` (compute) and is projected by UI.

---

## 1) Layer diagram (technical flows)

Text-only diagram (technical, not UX):

(UI) ── emits intents ──▶ (STORE actions)
▲ │
│ │ calls
│ ▼
│ (COMPUTE)
│ │ returns { nodeStates, ledger, stop, ... }
│ ▼
└── projects STORE state ◀─(STORE commit boundary)


Gates / feature locks (policy, not meaning):

(UI surface) ── uses ──▶ (gates/tier.ts, LockedFeatureDialog)
│
└─ must NOT alter compute semantics; only hide/disable/label.


Key principle (binding-consistent):
- **Meaning lives in compute + store invariants.**
- UI is strictly a **projection** of store, not “second system”.

---

## 2) Responsibility boundaries & invariants

### 2.1 Compute layer (`apps/cockpit/src/compute/*`)
Role:
- Pure deterministic pipeline: `Shock → Cascade → Θ (thresholds) → STOP`
- Produces **mandatory factual trace** (`ledger`) + terminal flag (`stop`).

Observed contract:
- Entry: `simulateShock(cfg, nodes, edges, selectedNodeId) : SimResult`
  - Implemented in `compute/simulate.ts`
- Shock:
  - `applyShockBaseScore(cfg)` in `compute/shock.ts` (uses intensity 0.1/0.3/0.5, clamped).
- Cascade:
  - `propagateCascades(...)` in `compute/cascade.ts`
  - Uses deterministic edge sorting: `byStableEdge` from `compute/determinism.ts`
- Thresholds / STOP:
  - `stateFromScore`, `isWorse`, `globalStopFromStates` in `compute/thresholds.ts`
  - STOP conditions:
    - any node reaches `STOP` (score >= 0.9) OR
    - global ratio `RED+STOP >= 0.30`

Determinism invariants (observed in compute):
- Stable ordering: `sortIds`, `byStableEdge`
- No time/random usage in compute modules shown.
- Numeric stability: `clamp01`.

Forbidden in compute (architectural):
- Any side effects (DOM/storage/network/time/random).
- Hidden nondeterminism (unordered iteration without explicit sort).

Allowed refactorings (meaning-preserving):
- Split/merge files, rename identifiers, tighten types
- Extract constants
- Replace internal structure if **(inputs → outputs)** are identical for all inputs (requires golden tests if/when added)

Do-not-touch anchors (meaning-bearing):
- `compute/simulate.ts` pipeline structure + ledger emission rules
- `compute/thresholds.ts` (Θ boundaries + STOP criteria)
- `compute/determinism.ts` (sorting / stable edge key rules)
- Ledger event shapes (see §2.4)

---

### 2.2 Store layer (`apps/cockpit/src/store/graph.store.ts`)
Role:
- Single Source of Truth (SSOT)
- **Commit boundary** between compute and UI
- **STOP latch** enforcement

Observed store invariants:
- State fields:
  - `simConfig: SimConfig`
  - `simLocked: boolean` (STOP lock)
  - `nodeStates: Record<string, NodeState>`
  - `ledger: LedgerEvent[]`
- STOP latch behavior:
  - `runShock()` early-return if `simLocked` true.
  - `setShockType/scope/intensity` also blocked when `simLocked` true.
  - `resetShock()` explicitly clears:
    - `simLocked: false`
    - `nodeStates: {}`
    - `ledger: []`
    - node styles reset

Commit boundary (observed atomic patch):
- `runShock()` calls `simulateShock(...)` then applies **one** `set((st)=>({ ... }))` patch that updates:
  - `simLocked`
  - `nodeStates`
  - `ledger`
  - `nodes` (style projection from nodeStates via `stateStyle`)

Forbidden in store (architectural):
- Duplicating compute semantics (no “second thresholds” in store).
- Partial updates that can leave state inconsistent (must keep atomic patch for coupled fields).

Allowed refactorings:
- Extract action helpers; reorganize Zustand slice
- Strengthen typing for actions/state
- Keep atomic commit semantics intact

Do-not-touch anchors:
- STOP latch enforcement in setters and `runShock`
- Atomic patch structure of `runShock()` applying compute result
- `resetShock()` semantics (seed return: stop+ledger+states cleared)

Determinism note (observed risk, not a meaning change):
- `addNodeFromPalette` uses `Math.random()` for node position.
  - Это не compute-смысл, но это **недетерминирует UI-layout**.
  - Архитектурно: допустимо как UI/authoring convenience, но нельзя “протечь” в compute semantics.

---

### 2.3 UI layer (`apps/cockpit/src/ui/*`)
Role:
- Render-only projection of store state; emits intents.

Required (binding-consistent):
- Make observable: STOP latch, ledger, node state map, discrete ShockSpec.
- No semantic recomputation in UI.

Forbidden:
- Computing Θ/STOP/cascade logic in UI.
- “recommend/mitigate/fix/optimize” surfaces.
- Exports/reports/KPI dashboards.

Do-not-touch anchors (meaning-bearing by contract, even if UI changes):
- UI must not bypass store guards (STOP)
- Ledger must remain factual trace (UI formatting only)

---

### 2.4 Gates layer (`apps/cockpit/src/gates/tier.ts` + locked UI)
Role:
- Tier/feature locks affect **access/visibility**, never truth.

Invariant:
- Gates must not introduce semantic fork between DEMO and FULL.
- “Locked features” are allowed only as explicit lock UI (no hidden operations).

Do-not-touch anchors:
- Tier decision logic in `gates/tier.ts` (policy boundary)
- `LockedFeatureDialog.tsx` as explicit disclosure mechanism

---

## 3) Technical anchors (critical do-not-touch list)

These changes are meaning-changing unless C/D/E updated accordingly:

1) Compute pipeline contract:
   - `simulateShock` inputs/outputs (`SimResult` shape)
   - ledger emission rules (threshold crossings, stop reason)
   - deterministic ordering (`sortIds`, `byStableEdge`)

2) Θ boundaries & STOP criteria:
   - score→state mapping (`stateFromScore`)
   - STOP conditions (`globalStopFromStates`)

3) Store STOP latch:
   - monotonic stop during run; hard block mutations; reset is the only unlock

4) Store commit boundary:
   - atomic patch that sets `{ simLocked, nodeStates, ledger, nodes styles }` together

5) “UI is projection” rule:
   - UI may not re-derive new truths (only display store truths)

---

## 4) Permitted refactorings (meaning-preserving)

Compute:
- Rename/split/merge modules
- Extract constants; improve types; add canonicalization
- Internal algorithm refactor if outputs identical for same inputs (golden tests recommended when introduced)

Store:
- Reorganize Zustand structure; extract helpers
- Refactor selection/modal handling
- Maintain STOP guards + atomic patch

UI:
- Layout/styling/accessibility; component composition
- Better disclosure of “demo is partial” and “no optimization/no export”
- Must not add semantic computation

Gates:
- Refactor tier flags; move locks to store as defense-in-depth (while keeping behavior equivalent)
- Improve locked placeholders (explicit, not misleading)

---

## 5) Forbidden changes (meaning-changing)

- Any change that alters `simulateShock` results for identical inputs
- Any softening/undo of STOP (auto-unlock, “continue anyway”, partial runs post-STOP)
- Any UI interpretation of ledger into advice/verdict
- Any exports/reports/doc generation, KPI dashboards
- Introducing nondeterminism into compute (time/random/unordered iteration)
- Semantic divergence between demo/full (hidden ops)

---

## 6) Determinism & reproducibility requirements

Hard rules:
- Compute must be side-effect free; no time/random; stable ordering enforced
- Inputs to compute must be explicit and fully provided by store (nodes/edges snapshots)
- Store must apply compute results atomically

Repo gates (observed):
- Typecheck: `npm --prefix apps/cockpit run typecheck`
- Build:     `npm --prefix apps/cockpit run build`

Operational note:
- PowerShell `Select-String -Pattern` must use a single quoted string (or an array of strings).
  Example:
  `Select-String -Path apps/cockpit/src -Pattern 'simLocked|STOP|ledger|determin|threshold|shock|cascade|feature|extended' -List`

---

## 7) Non-Claims (explicit)

This architecture does NOT claim:
- correctness as an “enterprise assessment”
- applicability to any конкретной организации
- optimization, recommendation, benchmarking
- reporting/exporting/audit artifacts
- security/auth/multi-tenant/persistence guarantees

It only fixes: technical layer boundaries + invariants for a diagnostic demonstrator.

---
