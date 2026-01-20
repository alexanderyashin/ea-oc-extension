$ErrorActionPreference = "Stop"

@'
# JPHQ-06 — Structural Tension as a Non-Optimizable Quantity

## Scope and Status

This folder contains a **standalone scientific preprint** produced under
**EA-OC-EXTENSION / Journal Preprint HQ (JPHQ)**.

**Frozen question (Q6):**

> *Is structural tension T an intrinsically non-optimizable quantity in
> enterprises modeled as continua (K_EA)?*

**Status:** submission-ready (formal completeness pending final LaTeX build)

---

## Formal Constraints

This preprint is subject to the following hard constraints:

- Ontology of Continua (OC Core): **frozen**
- Executable Theory Specification: **ETS.K_EA.v1.1 (executable-closed)**
- No new primitives
- No reinterpretation of T, Θ, Ω, ∂Ω, k, or phase logic
- No optimization, control, governance, or KPI framing
- No prescriptions or recovery narratives
- ASCII-only source (no Unicode)

The artifact stands alone and does **not** require the main whitepaper
for logical validity.

---

## Structure

preprints/jphq_06_structural_tension_nonoptimizable/
├── main.tex
├── README.md
├── sections/
│ ├── 00_abstract.tex
│ ├── 01_problem_statement.tex
│ ├── 02_formal_setting.tex
│ ├── 03_definition_structural_tension.tex
│ ├── 04_impossibility_theorems.tex
│ ├── 05_proof_sketches.tex
│ ├── 06_literature_positioning.tex
│ └── 07_falsifiability.tex
├── bibliography/
│ └── references.bib
└── build/
└── .gitkeep

Each section corresponds to a closed SUB-RUN under JPHQ-06 and is designed
for referee-grade inspection.

---

## Central Result

The preprint demonstrates that **structural tension T cannot be treated
as an objective, scalar, or optimizable quantity** without violating at
least one of the following:

- admissibility of Ω_EA,
- threshold semantics Θ,
- phase precedence (STOP ≻ COLLAPSE ≻ INERTIA ≻ SUCCESS),
- continuity measure k_EA.

This is an **impossibility result**, not a modeling preference.

---

## Relation to Existing Work

The work is deliberately positioned *against*:
- optimization and control paradigms,
- resilience metrics,
- maturity models,
- KPI-based aggregation,
- soft-constraint interpretations of thresholds.

It makes no claims about empirical performance or managerial utility.

---

## Build (Local)

From repository root (PowerShell, MiKTeX):

```powershell
cd preprints/jphq_06_structural_tension_nonoptimizable
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
A green build produces main.pdf in this directory.

Non-Claims

This preprint does not claim:

optimal enterprise behavior,

improvement strategies,

recovery conditions,

empirical validation,

universality beyond OC/ETS scope.

Any such interpretation is a category error.

License and Use

See repository root LICENSE.

This artifact may be cited as a theoretical impossibility result within
the OC/ETS framework.

End of README.