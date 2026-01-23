from typing import List
from .graph_model import ExecutionGraph, GraphViolation


class Scheduler:
    """
    Deterministic scheduler.
    Order is defined solely by graph structure.
    """

    def order(self, graph: ExecutionGraph) -> List[str]:
        edges = graph.edges()
        nodes = sorted(graph.nodes())

        incoming = {n: 0 for n in nodes}
        for src, dsts in edges.items():
            for d in dsts:
                incoming[d] += 1

        queue = sorted([n for n in nodes if incoming[n] == 0])
        result: List[str] = []

        while queue:
            n = queue.pop(0)
            result.append(n)
            for m in sorted(edges.get(n, ())):
                incoming[m] -= 1
                if incoming[m] == 0:
                    queue.append(m)
                    queue.sort()

        if len(result) != len(nodes):
            raise GraphViolation("Non-deterministic or cyclic graph")

        return result
