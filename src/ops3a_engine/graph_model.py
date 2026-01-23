from typing import Dict, Set


class GraphViolation(Exception):
    pass


class ExecutionGraph:
    """
    DAG-only execution graph with mandatory STOP terminal node.
    No cycles. No forbidden edges. STOP is absorbing.
    """

    STOP_NODE = "STOP"

    def __init__(self) -> None:
        self._edges: Dict[str, Set[str]] = {}
        self._nodes: Set[str] = set([self.STOP_NODE])

    def add_node(self, node: str) -> None:
        if node == self.STOP_NODE:
            return
        self._nodes.add(node)
        self._edges.setdefault(node, set())

    def add_edge(self, src: str, dst: str) -> None:
        if src == self.STOP_NODE:
            raise GraphViolation("STOP node cannot have outgoing edges")

        if dst not in self._nodes:
            raise GraphViolation(f"Unknown destination node: {dst}")

        self._edges.setdefault(src, set()).add(dst)

        if self._has_cycle():
            raise GraphViolation("Cycle detected: DAG violation")

    def nodes(self) -> Set[str]:
        return set(self._nodes)

    def edges(self) -> Dict[str, Set[str]]:
        return {k: set(v) for k, v in self._edges.items()}

    def _has_cycle(self) -> bool:
        visited = set()
        stack = set()

        def visit(n: str) -> bool:
            if n in stack:
                return True
            if n in visited:
                return False
            visited.add(n)
            stack.add(n)
            for m in self._edges.get(n, ()):
                if visit(m):
                    return True
            stack.remove(n)
            return False

        return any(visit(n) for n in self._edges)
