import unittest

from src.ops3a_engine.graph_model import ExecutionGraph
from src.ops3a_engine.state_machine import ExecutionStateMachine
from src.ops3a_engine.scheduler import Scheduler
from src.ops3a_engine.trace import ExecutionTrace


class TestOPS3AEngineSmoke(unittest.TestCase):

    def test_import_and_basic_construction(self):
        graph = ExecutionGraph()
        state = ExecutionStateMachine()
        scheduler = Scheduler()
        trace = ExecutionTrace()

        self.assertIsNotNone(graph)
        self.assertIsNotNone(state)
        self.assertIsNotNone(scheduler)
        self.assertIsNotNone(trace)


if __name__ == "__main__":
    unittest.main()
