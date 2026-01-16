from __future__ import annotations

from typing import Set

import networkx as nx


def detect_any_cycle_types(dep_graph: nx.DiGraph) -> bool:
    """Generic closed-path existence in the dependency graph."""
    try:
        next(nx.simple_cycles(dep_graph))
        return True
    except StopIteration:
        return False


def cycle_closed_by_graph(dep_graph: nx.DiGraph) -> bool:
    """ETS §3: closed path exists -> CycleClosed TRUE (graph branch)."""
    return detect_any_cycle_types(dep_graph)
