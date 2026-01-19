# JPHQ-03 — Threshold-Induced Phase Logic in Socio-Technical Systems

**Status:** Preprint (journal-grade, diagnostic-only)  
**Tag:** `jphq-03-preprint-v1`  
**Commit:** `82cfa8a`  
**Repository:** `ea-oc-extension`  
**Path:** `preprints/jphq_03_threshold_phase_logic/`

---

## Purpose

This preprint provides a **strictly formal, non-prescriptive** treatment of
**threshold-induced phase logic** in socio-technical systems, using the
**Ontology of Continua (OC Core)** and the executable specification
**ETS.K_EA.v1.1** as *immutable inputs*.

The paper introduces **no new primitives**, **no interventions**, and
**no governance prescriptions**.  
All results are **diagnostic classifications** derived from ETS predicates.

---

## Scope & Non-Claims (Firewall)

This work **does NOT**:
- prescribe actions, controls, optimizations, or governance measures;
- claim continuity of enterprise evolution;
- treat KPIs, metrics, or scores as primitives;
- assert physical identity with thermodynamic or critical systems;
- propose recovery strategies or steering mechanisms.

This work **ONLY**:
- defines phase predicates as ETS-faithful Boolean conditions;
- studies their logical interaction and precedence;
- analyzes admissible and forbidden phase transitions;
- positions the logic structurally (not physically) relative to phase theory.

---

## Formal Basis

All symbols and semantics are taken **verbatim** from:
- **OC Core** (internal, hash-anchored);
- **ETS.K_EA.v1.1** (status: `executable_closed`).

No reinterpretation, extension, or relaxation is permitted.

Key elements:
- Enterprise continuum: `K_EA`
- Admissible region: `Ω(K_EA)`
- Structural tension components: `f_k`
- Thresholds: `Θ_k`
- Cycles: governance, value, reproduction, finance, learning
- Continuity measure: `k_EA ∈ [0,1]`
- Phase logic: `SUCCESS ≺ INERTIA ≺ COLLAPSE ≺ STOP`

---

## Structure

preprints/jphq_03_threshold_phase_logic/
├─ main.tex
├─ references.bib
├─ sections/
│ ├─ 00_abstract.tex
│ ├─ 01_problem_statement.tex
│ ├─ 02_formal_setting.tex
│ ├─ 03_phase_definitions.tex
│ ├─ 04_phase_propositions.tex
│ ├─ 05_proof_sketches.tex
│ ├─ 06_scope_limits_nonclaims.tex
│ ├─ 07_falsifiability.tex
│ └─ 08_literature_positioning.tex
├─ critique/
│ └─ critique_log.md
└─ .gitignore


---

## Build Instructions (pdfLaTeX)

Tested with **MiKTeX 25.x** and `pdflatex`.

From repository root:

```powershell
Set-Location preprints/jphq_03_threshold_phase_logic

pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
The resulting file:

main.pdf


Warnings about undefined citations disappear once references.bib
is completed with external entries.

Falsifiability

The paper is falsifiable at the formal level:

violation of phase precedence;

existence of cycles-free admissible SUCCESS states;

empirical cases classified as SUCCESS with k_EA = 0;

admissible COLLAPSE → SUCCESS transitions without external Ψ.

See Section 7 for explicit criteria.

Relation to Other JPHQ Preprints

JPHQ-02 — STOP as Diagnostic
Focuses on STOP as an absorbing diagnostic condition.

JPHQ-03 (this work)
Generalizes to the full ETS phase lattice and transition logic.

License & Use

This preprint is intended for:

peer review,

formal-methods critique,

methodological comparison.

It is not a management framework, playbook, or advisory tool.

Author: Alexander Yashin
Date: 2026