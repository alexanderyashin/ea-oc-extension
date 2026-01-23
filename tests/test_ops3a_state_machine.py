import pytest

from src.ops3a_engine.trace import Trace
from src.ops3a_engine.state_machine import StateMachine, EngineState


def test_init_to_run_allowed():
    tr = Trace()
    sm = StateMachine(trace=tr)
    sm.start()
    assert sm.state == EngineState.RUN


def test_run_to_end_allowed():
    tr = Trace()
    sm = StateMachine(trace=tr)
    sm.start()
    sm.end()
    assert sm.state == EngineState.END


def test_run_to_stop_allowed_and_has_reason_in_trace():
    tr = Trace()
    sm = StateMachine(trace=tr)
    sm.start()
    sm.stop(code="X_STOP", message="because")
    assert sm.state == EngineState.STOP
    assert tr.stop_cause == ("X_STOP", "because")
    assert any(e.action == "STOP" and "X_STOP" in e.detail for e in tr.events)


def test_stop_is_irreversible_forbidden_transitions():
    tr = Trace()
    sm = StateMachine(trace=tr)
    sm.start()
    sm.stop(code="X_STOP", message="because")

    with pytest.raises(RuntimeError):
        sm.end()
    with pytest.raises(RuntimeError):
        sm.start()


def test_invariant_violation_forces_stop_and_reason_present():
    tr = Trace()
    sm = StateMachine(trace=tr)
    sm.start()

    sm.enforce_invariant(False, code="INV_FAIL", message="broken")
    assert sm.state == EngineState.STOP
    assert sm.stop_reason is not None
    assert sm.stop_reason.code == "INV_FAIL"
    assert tr.stop_cause == ("INV_FAIL", "broken")
