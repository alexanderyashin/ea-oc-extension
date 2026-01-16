from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional, Set

import networkx as nx

from .spec import KeaSpec


Phase = str


@dataclass
class KeaState:
    """
    Minimal engine state container.

    IMPORTANT: This is not a KPI store; axes exist as dimensions, while state holds
    only what ETS requires to compute:
    - f_k components
    - cycle closure S_cycles
    - observability S_obs
    - parent compatibility S_parent
    - thresholds satisfaction S_thresholds
    """
    # Dependency graph used for cycle closure (ETS §3)
    dep_graph: nx.DiGraph

    # Observability status (ETS §5 STOP trigger)
    observability_lost: bool

    # Parent compatibility Ω_EA ⊆ Ω_7 (ETS §4 factor S_parent)
    parent_compatible: bool

    # Threshold violation indicators (S_thresholds: "no violated Θ")
    # Here we represent per-component violation by f_component value > 0.
    f: Dict[str, float]

    # Optional: closed cycle types discovered via graph logic or recurrence proxy.
    closed_cycles: Set[str]


def H_Omega(state: KeaState) -> int:
    """
    ETS §4: H_Omega ∈ {0,1}. Hard rule:
    - if STOP triggers (exist/stop/observability) then H_Omega=0 for diagnosis.
    Here we implement H_Omega as: alive iff not (f_exist>0 or f_stop>0 or observability_lost).
    """
    f_exist = state.f.get("f_exist", 0.0)
    f_stop = state.f.get("f_stop", 0.0)
    if (f_exist > 0.0) or (f_stop > 0.0) or state.observability_lost:
        return 0
    return 1


def S_cycles(spec: KeaSpec, state: KeaState) -> float:
    """
    ETS §4: fraction of required cycles closed.
    ETS §3: closure can be graph closed path or recurrent pattern over tau.
    We implement graph closed path detection via closed_cycles set, which can be
    computed externally by cycle detector (sim/graph module).
    """
    req = spec.required_cycles
    if not req:
        return 1.0
    closed = sum(1 for c in req if c in state.closed_cycles)
    return closed / float(len(req))


def S_obs(state: KeaState) -> float:
    """ETS §4: observability invariant factor."""
    return 0.0 if state.observability_lost else 1.0


def S_parent(state: KeaState) -> float:
    """ETS §4: parent compatibility factor."""
    return 1.0 if state.parent_compatible else 0.0


def S_thresholds(state: KeaState) -> float:
    """
    ETS §4: 'no violated Θ' → score 1 else 0.
    Since ETS defines f_k components and success requires all f_k ≤ 0,
    we interpret any f_component > 0 as a violated threshold.
    """
    violated = any(v > 0.0 for v in state.f.values())
    return 0.0 if violated else 1.0


def k_EA(spec: KeaSpec, state: KeaState) -> float:
    """
    ETS §4: k_EA = H_Omega · S_cycles · S_obs · S_parent · S_thresholds
    """
    h = float(H_Omega(state))
    if h == 0.0:
        return 0.0
    k = h * S_cycles(spec, state) * S_obs(state) * S_parent(state) * S_thresholds(state)
    # Numeric safety clamp (ETS bounds)
    if k < 0.0:
        return 0.0
    if k > 1.0:
        return 1.0
    return k


def classify_phase(spec: KeaSpec, state: KeaState) -> Phase:
    """
    ETS §5: precedence STOP > COLLAPSE > INERTIA > SUCCESS
    Definitions:
      STOP: f_exist>0 OR f_stop>0 OR observability lost
      COLLAPSE: f_collapse>0 AND NOT STOP
      INERTIA: f_inertia>0 AND NOT (STOP or COLLAPSE)
      SUCCESS: all f_k <= 0
    """
    f_exist = state.f.get("f_exist", 0.0)
    f_stop = state.f.get("f_stop", 0.0)
    f_collapse = state.f.get("f_collapse", 0.0)
    f_inertia = state.f.get("f_inertia", 0.0)

    stop = (f_exist > 0.0) or (f_stop > 0.0) or state.observability_lost
    if stop:
        return "STOP"
    if (f_collapse > 0.0):
        return "COLLAPSE"
    if (f_inertia > 0.0):
        return "INERTIA"
    # SUCCESS iff all f_k <= 0
    if all(v <= 0.0 for v in state.f.values()):
        return "SUCCESS"
    # If we reach here: not STOP/COLLAPSE/INERTIA, but some f>0 (e.g., f_stab)
    # ETS §5 says SUCCESS only when all f<=0, so treat as INERTIA? No: ETS doesn't define.
    # Strict behavior: if any violation exists, it is NOT SUCCESS; classify as INERTIA if f_inertia>0 else COLLAPSE if f_collapse>0 else STOP if f_exist/f_stop/obs.
    # Since none apply, we classify as INERTIA-equivalent "INERTIA" only if f_inertia>0, otherwise "COLLAPSE"? Not allowed.
    # Therefore: raise explicit error to prevent silent invention.
    raise ValueError("Phase undefined by ETS.K_EA.v1.1 for this f-vector (non-success violation without STOP/COLLAPSE/INERTIA triggers).")
