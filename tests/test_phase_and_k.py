import networkx as nx

from ea_oc_ext.engine.spec import load_kea_spec
from ea_oc_ext.engine.model import KeaState, classify_phase, k_EA


def _spec():
    return load_kea_spec("configs/ETS.K_EA.v1.1.yaml")


def test_phase_precedence_stop_overrides_all():
    spec = _spec()
    g = nx.DiGraph()
    s = KeaState(
        dep_graph=g,
        observability_lost=False,
        parent_compatible=True,
        f={"f_exist": 1.0, "f_stop": 0.0, "f_inertia": 1.0, "f_collapse": 1.0, "f_stab": 1.0},
        closed_cycles=set(spec.required_cycles),
    )
    assert classify_phase(spec, s) == "STOP"


def test_phase_precedence_collapse_over_inertia():
    spec = _spec()
    g = nx.DiGraph()
    s = KeaState(
        dep_graph=g,
        observability_lost=False,
        parent_compatible=True,
        f={"f_exist": 0.0, "f_stop": 0.0, "f_inertia": 1.0, "f_collapse": 1.0, "f_stab": 0.0},
        closed_cycles=set(spec.required_cycles),
    )
    assert classify_phase(spec, s) == "COLLAPSE"


def test_success_requires_all_fk_le_zero():
    spec = _spec()
    g = nx.DiGraph()
    s = KeaState(
        dep_graph=g,
        observability_lost=False,
        parent_compatible=True,
        f={c: 0.0 for c in ["f_exist","f_stop","f_inertia","f_collapse","f_stab"]},
        closed_cycles=set(spec.required_cycles),
    )
    assert classify_phase(spec, s) == "SUCCESS"


def test_k_hard_zero_on_stop_conditions():
    spec = _spec()
    g = nx.DiGraph()
    s = KeaState(
        dep_graph=g,
        observability_lost=True,   # STOP trigger
        parent_compatible=True,
        f={"f_exist": 0.0, "f_stop": 0.0, "f_inertia": 0.0, "f_collapse": 0.0, "f_stab": 0.0},
        closed_cycles=set(spec.required_cycles),
    )
    assert k_EA(spec, s) == 0.0


def test_k_product_structure_on_success_case():
    spec = _spec()
    g = nx.DiGraph()
    # close only 3 of 5 required cycles
    closed = set(spec.required_cycles[:3])
    s = KeaState(
        dep_graph=g,
        observability_lost=False,
        parent_compatible=True,
        f={"f_exist": 0.0, "f_stop": 0.0, "f_inertia": 0.0, "f_collapse": 0.0, "f_stab": 0.0},
        closed_cycles=closed,
    )
    # H_Omega=1, S_cycles=3/5, S_obs=1, S_parent=1, S_thresholds=1 => 0.6
    assert abs(k_EA(spec, s) - 0.6) < 1e-12
