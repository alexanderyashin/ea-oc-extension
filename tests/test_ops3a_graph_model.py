import unittest

from src.ops3a_engine.graph_model import ExecutionGraph, GraphViolation


class TestOPS3AGraphModel(unittest.TestCase):

    def test_stop_has_no_outgoing_edges(self):
        g = ExecutionGraph()
        with self.assertRaises(GraphViolation):
            g.add_edge(ExecutionGraph.STOP_NODE, ExecutionGraph.STOP_NODE)

    def test_unknown_nodes_rejected(self):
        g = ExecutionGraph()
        g.add_node("A")
        with self.assertRaises(GraphViolation):
            g.add_edge("A", "B")  # dst unknown
        with self.assertRaises(GraphViolation):
            g.add_edge("B", "A")  # src unknown

    def test_self_loop_rejected(self):
        g = ExecutionGraph()
        g.add_node("A")
        with self.assertRaises(GraphViolation):
            g.add_edge("A", "A")

    def test_cycle_rejected_with_rollback(self):
        g = ExecutionGraph()
        g.add_node("A")
        g.add_node("B")
        g.add_edge("A", "B")
        with self.assertRaises(GraphViolation):
            g.add_edge("B", "A")  # would create cycle

        # rollback must have removed the failing edge attempt
        self.assertNotIn("A", g.edges().get("B", frozenset()))

    def test_explicit_forbidden_edge_rejected(self):
        g = ExecutionGraph()
        g.add_node("A")
        g.add_node("B")
        g.forbid_edge("A", "B")
        with self.assertRaises(GraphViolation):
            g.add_edge("A", "B")

    def test_validate_accepts_stop_terminal(self):
        g = ExecutionGraph()
        g.add_node("A")
        g.add_edge("A", ExecutionGraph.STOP_NODE)
        g.validate()  # must not raise


if __name__ == "__main__":
    unittest.main()
