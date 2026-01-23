from src.ops3a_engine.trace import Trace
from src.ops3a_engine.state_machine import StateMachine, EngineState


def test_trace_records_each_step_in_memory_no_io():
    tr = Trace()
    sm = StateMachine(trace=tr)

    sm.start()
    sm.enforce_invariant(True, code="X", message="ok")  # no stop
    sm.end()

    events = tr.events
    assert len(events) >= 3
    assert events[0].action == "init"
    assert any(e.state == EngineState.RUN.value for e in events)
    assert any(e.state == EngineState.END.value for e in events)


def test_stop_always_has_cause_and_trace_contains_it():
    tr = Trace()
    sm = StateMachine(trace=tr)
    sm.start()
    sm.stop(code="STOP_CAUSE", message="reason")

    assert tr.stop_cause == ("STOP_CAUSE", "reason")
    assert any(e.action == "STOP" and "STOP_CAUSE" in e.detail for e in tr.events)


def test_trace_is_append_only_and_does_not_change_semantics():
    tr = Trace()
    sm = StateMachine(trace=tr)

    sm.start()
    assert sm.state == EngineState.RUN

    # recording does not affect state transitions
    tr.record_state(EngineState.RUN, action="noop", detail="manual trace event")
    sm.end()
    assert sm.state == EngineState.END
