import pytest

from src.ops3c_integration.adapter import IntegrationWrapper, MisuseError


def test_misuse_unregistered_extension_hard_fails():
    w = IntegrationWrapper(registered_extensions={"ext_ok"})
    spec = {"edges": [["A", "B"]]}  # minimal, no cycle
    with pytest.raises(MisuseError, match="Unregistered extensions"):
        w.run(spec, extensions={"ext_BAD": object()})


def test_misuse_cycle_in_graph_hard_fails():
    w = IntegrationWrapper(registered_extensions=set())
    spec = {"edges": [["A", "B"], ["B", "A"]]}
    with pytest.raises(MisuseError, match="cycle detected"):
        w.run(spec)


def test_misuse_nondeterminism_keys_hard_fail():
    w = IntegrationWrapper(registered_extensions=set())
    spec = {"edges": [["A", "B"]], "time": "2026-01-01T00:00:00Z"}
    with pytest.raises(MisuseError, match="forbidden nondeterminism"):
        w.run(spec)


def test_misuse_reentry_loop_hard_fails(monkeypatch):
    """
    Prove wrapper is non-reentrant (execution loops via integration are blocked).
    """
    w = IntegrationWrapper(registered_extensions=set())
    spec = {"edges": [["A", "B"]]}

    # Force internal state to simulate re-entry attempt.
    w._in_call = True
    with pytest.raises(MisuseError, match="non-reentrant"):
        w.run(spec)


def test_calls_after_stop_hard_fail():
    """
    Boundary-level STOP terminality proof:
    once STOP observed, further calls are rejected at boundary.
    """
    w = IntegrationWrapper(registered_extensions=set())

    # We don't assume core produces STOP in this test.
    # We manually set wrapper STOP state to prove enforcement is at boundary.
    w._stopped = True
    with pytest.raises(MisuseError, match="STOP already observed"):
        w.run({"edges": [["A", "B"]]})
