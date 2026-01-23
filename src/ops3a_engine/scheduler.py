from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Mapping, Set, Tuple
import heapq

from .invariants import ensure


@dataclass(frozen=True)
class ScheduleResult:
    order: Tuple[str, ...]


def deterministic_toposort(deps_graph: Mapping[str, Iterable[str]]) -> ScheduleResult:
    """
    Deterministic scheduler: stable topological ordering with explicit tie-break.

    Input form:
      deps_graph[node] = iterable of dependency node IDs (predecessors)

    Determinism guarantees (D.2):
      - Same graph => same order
      - Independent of insertion order of nodes and container iteration order
      - Tie-break is explicit: lexical order of node IDs

    Raises:
      - InvariantViolation (via ensure) if graph contains a cycle
    """
    # Collect all nodes including those appearing only as dependencies
    nodes: Set[str] = set(deps_graph.keys())
    for _, ds in deps_graph.items():
        for d in ds:
            nodes.add(str(d))

    # Normalize dependency sets deterministically
    dep_sets: Dict[str, Tuple[str, ...]] = {}
    for n in nodes:
        raw = deps_graph.get(n, [])
        dep_sets[n] = tuple(sorted(str(x) for x in raw))

    # Build indegree and adjacency (outgoing edges)
    indeg: Dict[str, int] = {n: 0 for n in nodes}
    outgoing: Dict[str, List[str]] = {n: [] for n in nodes}

    for n in nodes:
        for d in dep_sets[n]:
            outgoing[d].append(n)  # edge d -> n
            indeg[n] += 1

    # Deterministic adjacency iteration
    for n in nodes:
        outgoing[n].sort()

    # Heap = deterministic tie-break (lexical)
    heap: List[str] = []
    for n in sorted(nodes):
        if indeg[n] == 0:
            heapq.heappush(heap, n)

    order: List[str] = []
    while heap:
        cur = heapq.heappop(heap)
        order.append(cur)
        for nxt in outgoing[cur]:
            indeg[nxt] -= 1
            if indeg[nxt] == 0:
                heapq.heappush(heap, nxt)

    ensure(len(order) == len(nodes), "SCH_CYCLE", "Dependency graph contains a cycle; scheduling must STOP")
    return ScheduleResult(order=tuple(order))


class Scheduler:
    """
    Backwards-compatible scheduler wrapper (for existing smoke tests).

    NOTE:
      - Pure, deterministic: delegates to deterministic_toposort.
      - No time/random/env, no recovery/retry/resume.
    """

    def schedule(self, deps_graph: Mapping[str, Iterable[str]]) -> Tuple[str, ...]:
        return deterministic_toposort(deps_graph).order
