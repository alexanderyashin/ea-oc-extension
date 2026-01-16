from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple
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
    tau_EA: int = 25  # recurrence window proxy (synthetic)
    shock_scale: float = 0.25

    # Guardrail test: if True, create a stability-only violation (ETS undefined surface)
    allow_undefined_surface: bool = False

    # Optional forced injections (synthetic driver knobs)
    force_stop_at: int | None = None
    force_inertia_at: tuple[int, ...] = (60, 120)
    force_collapse_at: tuple[int, ...] = (90, 150)
    force_recover_at: tuple[int, ...] = (80, 110, 140, 160)


def _rand_graph(rng: random.Random, nodes: int, p_edge: float) -> nx.DiGraph:
    g = nx.DiGraph()
    g.add_nodes_from(range(nodes))
    for i in range(nodes):
        for j in range(nodes):
            if i != j and rng.random() < p_edge:
                g.add_edge(i, j)
    return g


def _required_cycles_from_graph(spec: KeaSpec, g: nx.DiGraph, rng: random.Random) -> set[str]:
    """Synthetic closure proxy: if graph has any directed cycle, cycles are likely closed."""
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

    NOTE: This is a synthetic demonstration driver. It does NOT add theory.
    It only produces trajectories to exercise ETS-defined engine logic.
    """
    rng = random.Random(cfg.seed)
    out: List[Tuple[int, KeaState, K7Fields]] = []

    # initialize all f-components known to the spec
    f = {c: 0.0 for c in spec.f_components}
    # some tests also use f_stab even if not listed by spec tooling
    f.setdefault("f_stab", 0.0)

    parent_ok = True
    obs_lost = False

    for t in range(cfg.steps):
        fields = K7Fields(
            law=rng.uniform(-1, 1) * cfg.shock_scale,
            regulation=rng.uniform(-1, 1) * cfg.shock_scale,
            market=rng.uniform(-1, 1) * cfg.shock_scale,
            tech=rng.uniform(-1, 1) * cfg.shock_scale,
            norms=rng.uniform(-1, 1) * cfg.shock_scale,
        )

        g = _rand_graph(rng, cfg.nodes, cfg.p_edge)
        closed_cycles = _required_cycles_from_graph(spec, g, rng)

        # synthetic injections (config-driven)
        if t in cfg.force_inertia_at:
            f["f_inertia"] = 1.0
        if t in cfg.force_collapse_at:
            f["f_collapse"] = 1.0
        if t in cfg.force_recover_at:
            f["f_inertia"] = 0.0
            f["f_collapse"] = 0.0
        if cfg.force_stop_at is not None and t == cfg.force_stop_at:
            f["f_stop"] = 1.0

        # optional ETS-undefined surface (stability-only violation)
        if cfg.allow_undefined_surface:
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
