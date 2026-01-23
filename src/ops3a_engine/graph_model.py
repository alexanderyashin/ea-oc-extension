from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, FrozenSet, Set


class GraphViolation(Exception):
    """Raised on any execution-graph structural violation (DAG/STOP/forbidden edges)."""


@dataclass(frozen=True)
class ForbiddenEdge:
    src: str
    dst: str


class ExecutionGraph:
    """
    OPS-3A execution graph model (structural only).

    Guarantees:
    - DAG-only: cycles are rejected.
    - STOP is mandatory and terminal (absorbing sink): no outgoing edges.
    - Forbidden edges are explicit and enforced (hard fail).
    """

    STOP_NODE = "STOP"

    def __init__(self) -> None:
        self._nodes: Set[str] = {self.STOP_NODE}
        self._edges: Dict[str, Set[str]] = {self.STOP_NODE: set()}
        self._forbidden: Set[ForbiddenEdge] = set()

    # -------------------------
    # Nodes / edges
    # -------------------------

    def add_node(self, node: str) -> None:
        if not node:
            raise GraphViolation("Node id must be non-empty")
        if node == self.STOP_NODE:
            return
        self._nodes.add(node)
        self._edges.setdefault(node, set())

    def forbid_edge(self, src: str, dst: str) -> None:
        if not src or not dst:
            raise GraphViolation("Forbidden edge endpoints must be non-empty")
        self._forbidden.add(ForbiddenEdge(src=src, dst=dst))

    def add_edge(self, src: str, dst: str) -> None:
        if not src or not dst:
            raise GraphViolation("Edge endpoints must be non-empty")

        if src not in self._nodes:
            raise GraphViolation(f"Unknown source node: {src}")
        if dst not in self._nodes:
            raise GraphViolation(f"Unknown destination node: {dst}")

        if src == self.STOP_NODE:
            raise GraphViolation("STOP node cannot have outgoing edges")
        if src == dst:
            raise GraphViolation("Self-loop is forbidden (cycle)")

        if ForbiddenEdge(src=src, dst=dst) in self._forbidden:
            raise GraphViolation(f"Forbidden edge: {src} -> {dst}")

        self._edges.setdefault(src, set()).add(dst)

        if self._has_cycle():
            # rollback
            self._edges[src].remove(dst)
            raise GraphViolation("Cycle detected: DAG violation")

    # -------------------------
    # Introspection (read-only)
    # -------------------------

    def nodes(self) -> FrozenSet[str]:
        return frozenset(self._nodes)

    def edges(self) -> Dict[str, FrozenSet[str]]:
        return {k: frozenset(v) for k, v in self._edges.items()}

    def forbidden_edges(self) -> FrozenSet[ForbiddenEdge]:
        return frozenset(self._forbidden)

    # -------------------------
    # Validation (structural)
    # -------------------------

    def validate(self) -> None:
        if self.STOP_NODE not in self._nodes:
            raise GraphViolation("STOP node missing")

        if len(self._edges.get(self.STOP_NODE, set())) > 0:
            raise GraphViolation("STOP node must not have outgoing edges")

        for src, dsts in self._edges.items():
            if src not in self._nodes:
                raise GraphViolation(f"Edge source not declared as node: {src}")

            if src == self.STOP_NODE and len(dsts) > 0:
                raise GraphViolation("STOP node cannot have outgoing edges")

            for dst in dsts:
                if dst not in self._nodes:
                    raise GraphViolation(f"Edge target not declared as node: {dst}")
                if ForbiddenEdge(src=src, dst=dst) in self._forbidden:
                    raise GraphViolation(f"Forbidden edge present in graph: {src} -> {dst}")

        if self._has_cycle():
            raise GraphViolation("Cycle detected in validate(): DAG violation")

    # -------------------------
    # Internal: cycle detection
    # -------------------------

    def _has_cycle(self) -> bool:
        visited: Set[str] = set()
        active: Set[str] = set()

        def visit(n: str) -> bool:
            if n in active:
                return True
            if n in visited:
                return False
            visited.add(n)
            active.add(n)
            for m in self._edges.get(n, ()):
                if visit(m):
                    return True
            active.remove(n)
            return False

        return any(visit(n) for n in self._nodes)
