from src.ops3a_engine.scheduler import deterministic_toposort
from src.ops3a_engine.invariants import InvariantViolation


def test_scheduler_deterministic_same_graph_same_order():
    g1 = {
        "C": ["A", "B"],
        "B": ["A"],
        "A": [],
    }
    g2 = {
        "A": [],
        "B": ["A"],
        "C": ["B", "A"],  # different dependency order
    }

    o1 = deterministic_toposort(g1).order
    o2 = deterministic_toposort(g2).order
    assert o1 == o2


def test_scheduler_independent_of_insertion_order_and_container_order():
    # Same DAG, different insertion order + deps container order
    gA = {
        "N3": ["N1", "N2"],
        "N2": ["N1"],
        "N1": [],
        "N4": ["N2"],
    }
    gB = {
        "N4": ["N2"],
        "N1": [],
        "N3": ["N2", "N1"],
        "N2": ["N1"],
    }

    oA = deterministic_toposort(gA).order
    oB = deterministic_toposort(gB).order
    assert oA == oB


def test_scheduler_explicit_tiebreak_lexical():
    # Two independent nodes -> lexical tie-break
    g = {"B": [], "A": []}
    order = deterministic_toposort(g).order
    assert order == ("A", "B")


def test_scheduler_cycle_raises_invariant_violation():
    g = {"A": ["B"], "B": ["A"]}
    try:
        deterministic_toposort(g)
        assert False, "Expected InvariantViolation for cycle"
    except InvariantViolation as e:
        assert e.code == "SCH_CYCLE"
