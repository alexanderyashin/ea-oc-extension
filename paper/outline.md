# Whitepaper Outline — K_EA (Executable-Closed, Diagnostic-Only)

## Front matter
- Title
- Version / Status
- Repository + Commit (pinned)
- ETS id + ETS sha256
- License / Citation pointer
- Scope lock statement (OC Core frozen; ESTRA v1 frozen; ETS immutable)

## Abstract
- What is defined (K_EA as OC-continuum)
- What is NOT claimed (no prescriptions, no empirical claims)
- What is provided (executable-closed spec + phase logic + stop/no-go + reproducibility pointers)

## 1. Purpose and Scope
1.1 Purpose (canonical ETS projection)
1.2 Audience (readers needing a diagnostic formalism; no “framework shoppers”)
1.3 Scope lock (immutable inputs)
1.4 Non-claims (explicit list)
1.5 Terminology and notation (ASCII-only: Omega, dOmega, Theta, tau)

## 2. Position in OC / ESTRA (Non-modifying)
2.1 OC primitives used (Omega, dOmega, A, P, Theta, J, C, k, tau) — referenced, not redefined
2.2 Relation to ESTRA v1 (diagnostic method layer; no new primitives)
2.3 Observability vs essence (Sigma_obs / manifestation operator pointer, if already frozen elsewhere)

## 3. Formal Definition of K_EA (ETS projection)
3.1 Continuum tuple (Omega_EA, dOmega_EA, A_EA, P_EA, Theta_EA, J_EA, C_EA, k_EA, tau_EA)
3.2 Identity condition (enterprise-as-continuum, not legal entity)
3.3 Hard-zero / STOP boundaries (H_Omega_false etc.)

## 4. Axes A_EA (complete, ETS-only)
4.1 Axis families (struct, gov, ops, res, info, risk)
4.2 Enumerated axis list (exactly from ETS)
4.3 “No additional axes” rule + typical invalid substitutions (links to No-Go: MetricSubstitution)

## 5. Structural Tension and Threshold Components (f_k)
5.1 Components f_exist, f_stab, f_inertia, f_collapse, f_stop
5.2 Threshold mapping (Theta_* -> f_*)
5.3 Inequality-only commitment (no numeric thresholds)

## 6. Cycles C_EA and Closure
6.1 Required cycles (governance, value, reproduction, finance, learning)
6.2 Closure rules (graph_closed_path; recurrent_pattern_over_tau)
6.3 What “cycle failure” means structurally (without prescriptions)

## 7. Continuity Measure k_EA
7.1 Factorization (H_Omega, S_cycles, S_obs, S_parent, S_thresholds)
7.2 Aggregation rule (product), bounds [0,1]
7.3 Hard-zero rule

## 8. Phase Logic
8.1 Precedence rule: STOP > COLLAPSE > INERTIA > SUCCESS
8.2 Definitions (exact ETS expressions)
8.3 Allowed transitions (exact ETS list)
8.4 Interpretation notes (diagnostic only; no “what to do”)

## 9. Parent Coupling (K7)
9.1 Exogenous fields (law, regulation, market, tech, norms)
9.2 Effects mapping (only as ETS declares)
9.3 Constraints (Omega_EA_subset_Omega_7; no_direct_external_axis_control; no_direct_K8_to_EA)

## 10. Invariants and No-Go Results
10.1 Invariants (EnergyOfTransformation; ParentCompatibility)
10.2 No-Go (MetricSubstitution; InstantRecovery)
10.3 STOP as first-class outcome (not a “failure”, but an integrity result)

## 11. Synthetic Demonstrations (Optional, clearly marked)
11.1 What counts as synthetic demo (non-empirical, non-predictive)
11.2 Reference to repo artifacts (e.g., sim03c summaries) — no new claims
11.3 How demos relate to ETS (sanity checks, pipeline checks)

## 12. Limits of Applicability
12.1 Evidence requirements and STOP triggers
12.2 What the model cannot infer
12.3 Common misuses (prescription drift, KPI substitution, external override myths)

## 13. Reproducibility and Artifact Index
13.1 Manifest pointer (paper/manifest.yml)
13.2 Run index (.runs/)
13.3 ETS hash pinning + commit pinning
13.4 Build instructions pointer (future; may be empty at v0.1)

## Appendices
A. ETS snapshot excerpt (non-normative; pointer to configs file)
B. Glossary (minimal)
C. Change log (from RUN meta layer)
