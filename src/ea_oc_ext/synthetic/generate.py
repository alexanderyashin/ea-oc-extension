from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple
import random

import networkx as nx

from ea_oc_ext.engine.model import KeaState
from ea_oc_ext.engine.spec import KeaSpec
from ea_oc_ext.coupling.k7 import K7Fields


@dataclass(frozen=True)
class SyntheticConfig:
    seed: int = 7
    steps: int = 200
    p_edge: float = 0.03
    nodes: int = 40
    tau_EA: int = 25  # used as recurrence window proxy in synthetic mode
    # intensity scalars for synthetic effects
    shock_scale: float = 0.25


def _rand_graph(rng: random.Random, nodes: int, p_edge: float) -> nx.DiGraph:
    g = nx.DiGraph()
    g.add_nodes_from(range(nodes))
    for i in range(nodes):
        for j in range(nodes):
            if i != j and rng.random() < p_edge:
                g.add_edge(i, j)
    return g


def _required_cycles_from_graph(spec: KeaSpec, g: nx.DiGraph, rng: random.Random) -> set[str]:
    """
    Synthetic: we do not have cycle-type ontology. We approximate closure by
    random assignment conditioned on 'graph has any cycle'.
    """
    has_any_cycle = False
    try:
        next(nx.simple_cycles(g))
        has_any_cycle = True
    except StopIteration:
        has_any_cycle = False

    closed = set()
    for c in spec.required_cycles:
        if has_any_cycle and rng.random() < 0.7:
            closed.add(c)
        elif rng.random() < 0.05:
            closed.add(c)
    return closed


def generate_trajectory(spec: KeaSpec, cfg: SyntheticConfig) -> List[Tuple[int, KeaState, K7Fields]]:
    """
    Generates (t, state, fields) triples.
    f_k dynamics are synthetic: they create regimes where each phase can appear.
    """
    rng = random.Random(cfg.seed)
    out: List[Tuple[int, KeaState, K7Fields]] = []

    # start with mostly healthy f
    f = {c: 0.0 for c in spec.f_components}
    if "f_stab" not in f:
        f["f_stab"] = 0.0

    parent_ok = True
    obs_lost = False

    for t in range(cfg.steps):
        # fields (synthetic)
        fields = K7Fields(
            law=rng.uniform(-1, 1) * cfg.shock_scale,
            regulation=rng.uniform(-1, 1) * cfg.shock_scale,
            market=rng.uniform(-1, 1) * cfg.shock_scale,
            tech=rng.uniform(-1, 1) * cfg.shock_scale,
            norms=rng.uniform(-1, 1) * cfg.shock_scale,
        )

        # synthetic graph & cycle closure
        g = _rand_graph(rng, cfg.nodes, cfg.p_edge)
        closed_cycles = _required_cycles_from_graph(spec, g, rng)

        # synthetic f updates: push occasionally into inertia/collapse/stop
        # (explicitly a demo driver, not a claim about enterprises)
        if t in (60, 120):
            f["f_inertia"] = 1.0  # inertia regime
        if t in (90, 150):
            f["f_collapse"] = 1.0  # collapse regime
        if t == 170:
            f["f_stop"] = 1.0  # STOP trigger

        # recovery waves (synthetic)
        if t in (80, 110, 140, 160):
            f["f_inertia"] = 0.0
            f["f_collapse"] = 0.0

        # occasional stability violation without inertia/collapse/stop (to surface ETS undefined)
        if t == 30:
            f["f_stab"] = 1.0
        if t == 35:
            f["f_stab"] = 0.0

        state = KeaState(
            dep_graph=g,
            observability_lost=obs_lost,
            parent_compatible=parent_ok,
            f=dict(f),
            closed_cycles=set(closed_cycles),
        )
        out.append((t, state, fields))

    return out
