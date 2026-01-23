from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional

from .trace import Trace
from .invariants import InvariantViolation, ensure


class EngineState(str, Enum):
    INIT = "INIT"
    RUN = "RUN"
    END = "END"
    STOP = "STOP"


@dataclass(frozen=True)
class StopReason:
    code: str
    message: str


class StateMachine:
    """
    OPS-3A engine state machine.

    Proof obligations (D.1):
      - INIT -> RUN allowed
      - RUN -> END allowed
      - RUN -> STOP allowed
      - STOP -> * forbidden (irreversible)
      - invariant violation => STOP
    """

    def __init__(self, trace: Optional[Trace] = None) -> None:
        # Default in-memory trace for compatibility with existing smoke tests.
        self._trace = trace if trace is not None else Trace()

        self._state: EngineState = EngineState.INIT
        self._stop_reason: Optional[StopReason] = None

        self._trace.record_state(self._state, action="init", detail="StateMachine created")

    @property
    def trace(self) -> Trace:
        return self._trace

    @property
    def state(self) -> EngineState:
        return self._state

    @property
    def stop_reason(self) -> Optional[StopReason]:
        return self._stop_reason

    def start(self) -> None:
        self._assert_not_stopped("start")
        ensure(self._state == EngineState.INIT, "SM_INVALID_TRANSITION", "start() allowed only from INIT")
        self._state = EngineState.RUN
        self._trace.record_state(self._state, action="transition", detail="INIT->RUN")

    def end(self) -> None:
        self._assert_not_stopped("end")
        ensure(self._state == EngineState.RUN, "SM_INVALID_TRANSITION", "end() allowed only from RUN")
        self._state = EngineState.END
        self._trace.record_state(self._state, action="transition", detail="RUN->END")

    def stop(self, code: str, message: str) -> None:
        """
        STOP is terminal. Once STOP, no further transitions.
        """
        if self._state == EngineState.STOP:
            return
        ensure(self._state in (EngineState.RUN, EngineState.INIT), "SM_INVALID_TRANSITION", "stop() allowed only from INIT/RUN")
        self._state = EngineState.STOP
        self._stop_reason = StopReason(code=code, message=message)
        self._trace.record_stop(code=code, message=message)

    def enforce_invariant(self, condition: bool, code: str, message: str) -> None:
        """
        If invariant violated => STOP with explicit reason.
        """
        if self._state == EngineState.STOP:
            return
        try:
            ensure(condition, code, message)
        except InvariantViolation as e:
            self.stop(code=e.code, message=e.message)

    def _assert_not_stopped(self, op_name: str) -> None:
        if self._state == EngineState.STOP:
            raise RuntimeError(f"STOP is terminal; operation '{op_name}' is forbidden")


# Backwards-compatible alias for existing repo tests (e.g., test_ops3a_engine_smoke.py)
ExecutionStateMachine = StateMachine
