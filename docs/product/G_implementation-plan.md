# ESTRA Monolith — Implementation & Verification Plan (G)

## 0. Binding (source of truth)
This document is **binding** only as a *merge* of requirements already defined in:
- **B** `docs/product/B_user-ontology.md`
- **C** `docs/product/C_functional-core.md`
- **D** `docs/product/D_formal-realization.md`
- **E** `docs/product/E_ui-system-derivation.md`
- **F** `docs/product/F_technical-architecture.md`

**G** does not introduce new product claims.  
**G** defines “DONE” as executable gates + verifiable behavior consistent with B–F.

---

## 1. Product identity: what “READY” means (DoD)
**ESTRA Monolith is READY** when *all* conditions below are satisfied:

### 1.1 Build / Type safety gates (mandatory)
- [ ] `npm --prefix apps/cockpit run typecheck` is **GREEN**
- [ ] `npm --prefix apps/cockpit run build` is **GREEN**
- [ ] `git status -sb` shows only intentional changes (or clean after push)

### 1.2 Behavioral invariants (mandatory)
- [ ] **STOP terminality (simLocked)** is observable:
  - once STOP is reached, the simulation becomes **locked**
  - re-running shock or cascade does not mutate state
- [ ] **Ledger is facts-only**:
  - ledger entries are descriptive events
  - no recommendations, no “should”, no optimization language
  - all key state transitions are recorded
- [ ] **UI tiering / locks** match document E:
  - Demo tier exposes only minimal safe interactions
  - Extended tier is hidden or explicitly locked
  - no “fake-working” or misleading controls
- [ ] **Determinism** holds in core compute:
  - identical input → identical output
  - node states, STOP state, ledger order and content are stable

### 1.3 Non-claims (mandatory)
The product explicitly **does not claim**:
- consulting conclusions
- prescriptions or recommendations
- optimization advice
- exportable client reports
- “truth” or evaluation of a company

ESTRA Monolith is a **technology demonstrator**, not a BI tool and not a decision engine.

---

## 2. Required gates: how to run and record
All commands are executed from repo root (PowerShell).

### 2.1 Typecheck
```powershell
npm --prefix apps/cockpit run typecheck
2.2 Build
npm --prefix apps/cockpit run build

2.3 Gate results log (manual)

Raw console output must be pasted here verbatim.

Gate Results — Typecheck

Date:

Commit:

Output:

<PASTE OUTPUT HERE>

Gate Results — Build

Date:

Commit:

Output:

<PASTE OUTPUT HERE>

3. Verification protocol (behavioral)

This section defines what must be verifiable, not how to improve the system.

3.1 STOP terminality (simLocked)

Definition: STOP is a terminal boundary.

Acceptance evidence:

re-triggering shock does not change node states

ledger may record an ignored attempt, or remain unchanged

state mutation after STOP is forbidden

reset (if present) is the only allowed exit

Binding references: C, D, F.

3.2 Ledger completeness (facts-only)

Definition: Ledger is a factual event stream.

Acceptance evidence:

events exist for:

shock applied

cascade steps

threshold crossings

STOP (if reached)

reset (if executed)

language is descriptive and neutral

Binding references: C, D, E.

3.3 UI locks & tiering

Definition: Demo UI must communicate structure and limits, not product usability.

Acceptance evidence:

Demo tier shows minimal controls only

Extended functions are clearly locked or segregated

no export / report / save / recommendation features exist in demo

Binding references: B, E.

3.4 Determinism (no randomness in core)

Definition: Core computation is deterministic.

Acceptance evidence:

two runs with identical parameters produce identical:

node states

STOP / lock state

ledger content and ordering

no randomness, time-based values, or unstable iteration in core compute

Binding references: F, C, D.

4. Known Issues registry (facts-only)

This registry records observed facts, not tasks or solutions.

KI-01 Dropdowns appear visually “empty/white”; users perceive “nothing happens”.

KI-02 RunShock is perceived as a one-time action; repeated execution appears ineffective.

KI-03 Intensity values are discrete (10/30/50); 100% is not available.

KI-04 Extended panel is visible but empty or unclear.

KI-05 Inspector and lower metrics panel are perceived as unexplained or unnecessary.

KI-06 Visible locked elements in demo create frustration due to low interaction density.

5. Regression requirements

Any change affecting compute, store, or UI tiering must re-satisfy:

 typecheck GREEN

 build GREEN

 STOP terminality unchanged

 Ledger remains facts-only and complete

 Determinism preserved

 Demo tier does not gain product features

6. Implementation checklist

 G_implementation-plan.md exists and is non-empty

 linked from docs/product/00_index.md

 gates executed and logged

 behavioral verification completed

 known issues registry updated

 changes committed and pushed

7. Status

Current status: ACTIVE

Becomes DONE when all DoD criteria are satisfied and gates are GREEN