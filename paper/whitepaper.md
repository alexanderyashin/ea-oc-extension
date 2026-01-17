# The Enterprise Continuum (K_EA): Executable-Closed Diagnostic Whitepaper

**Status:** Draft (Executable-Closed Projection)  
**Source of truth:** `configs/ETS.K_EA.v1.1.yaml` (immutable)  
**ETS id:** `ETS.K_EA.v1.1`  
**ETS sha256:** `c2385be94c79f52c9cbe6ee4437994c8833224cdce50ed8665241c0fdb7ecce6`

---

## Abstract

This whitepaper provides a formal, diagnostic-only specification of the Enterprise Continuum **K_EA** as an Ontology-of-Continua (OC) continuum with executable-closed scope. It projects the immutable Executable Theory Specification **ETS.K_EA.v1.1** into a coherent scientific document. The work does not introduce new primitives, does not provide prescriptions, and does not make empirical claims. Synthetic demonstrations (if referenced) are explicitly non-empirical and non-predictive.

---

## 1. Purpose and Scope Declaration

### 1.1 What this whitepaper is
A canonical, executable-closed projection of **ETS.K_EA.v1.1** into a readable formal document.

### 1.2 What this whitepaper is not
Not a framework, methodology, outline, outline, refinement guide, or descriptive taxonomy.

### 1.3 Diagnostic-only commitment
All claims are structural and diagnostic. No prescriptive statements are made.

### 1.4 Explicit non-claims
- No empirical validation is claimed.
- No universal numeric thresholds are claimed.
- No predictions are claimed.
- No statements are provided.

---

## 2. Ontological Grounding (OC Context)

This section positions K_EA as a continuum defined by OC primitives, without modifying OC Core.

---

## 3. Formal Definition of the Enterprise Continuum (ETS Projection)

**Definition (ETS.K_EA.v1.1):**

K_EA is defined as a continuum with immutable primitives:
- State space: Omega_EA and boundary dOmega_EA
- Axes: A_EA
- Potentials: P_EA
- Threshold set: Theta_EA (via f_k components)
- Flows: J_EA
- Cycles: C_EA
- Continuity/connectivity: k_EA
- Internal time scale: tau_EA

---

## 4. Axes and Degrees of Freedom (ETS Projection)

From `axes:` in ETS:

- struct: coupling, modularity, centralization, redundancy
- gov: decision_latency, rule_enforceability, escalation_integrity
- ops: delivery_coherence, incident_recovery_loop, change_lead_time
- res: budget_flexibility, skills_coverage, supplier_dependency
- info: observability, traceability, semantic_alignment
- risk: risk_visibility, control_gap_rate

No additional axes are introduced.

---

## 5. Thresholds, Components, and Structural Tension (ETS Projection)

From `structural_tension_f_k:` in ETS:
- components: f_exist, f_stab, f_inertia, f_collapse, f_stop
- mapping: Theta_exist->f_exist, Theta_stab->f_stab, Theta_inertia->f_inertia, Theta_collapse->f_collapse, Theta_stop->f_stop

This whitepaper does not define numeric values; it preserves the inequality-based structure.

---

## 6. Cycles and Closure (ETS Projection)

From `cycles:` in ETS:
- required: governance, value, reproduction, finance, learning
- closure_rule: graph_closed_path; recurrent_pattern_over_tau

---

## 7. Continuity Measure k_EA (ETS Projection)

From `k_EA:` in ETS:
- factorization: H_Omega, S_cycles, S_obs, S_parent, S_thresholds
- aggregation: product
- bounds: [0, 1]
- hard_zero: H_Omega_false

---

## 8. Phase Logic (ETS Projection)

From `phase_logic:` in ETS:
- precedence: STOP, COLLAPSE, INERTIA, SUCCESS
- STOP: f_exist>0 or f_stop>0 or observability_lost
- COLLAPSE: f_collapse>0 and not STOP
- INERTIA: f_inertia>0 and not (STOP or COLLAPSE)
- SUCCESS: all f_k<=0

Allowed transitions (ETS):
- SUCCESS -> INERTIA, COLLAPSE, STOP
- INERTIA -> SUCCESS_via_external_Psi, COLLAPSE, STOP
- COLLAPSE -> STOP
- STOP -> (none)

---

## 9. Parent Coupling (K7) (ETS Projection)

From `coupling_k7:` in ETS:
- fields: law, regulation, market, tech, norms
- effects:
  - law_regulation: Theta_exist, Theta_stop
  - market: P_res, P_fin, Theta_inertia
  - tech: A_struct, A_info
  - norms: S_obs, semantic_alignment
- constraints:
  - Omega_EA_subset_Omega_7
  - no_direct_external_axis_control
  - no_direct_K8_to_EA

---

## 10. Invariants and No-Go Results (ETS Projection)

From `invariants:` in ETS:
- EnergyOfTransformation
- ParentCompatibility

From `no_go:` in ETS:
- MetricSubstitution
- InstantRecovery

These are first-class results. This whitepaper treats them as constraints, not as shortcomings.

---

## 11. Conclusion (Non-Prescriptive)

This whitepaper establishes an executable-closed, diagnostic-only formalization of K_EA consistent with OC Core and ETS.K_EA.v1.1. It explicitly preserves STOP conditions, invariants, and No-Go results, and does not extend its scope beyond structural diagnosis.

---

## Appendix C - Reproducibility Manifest (Pointer)

See `paper/manifest.yml` and `configs/ETS.K_EA.v1.1.sha256`.
