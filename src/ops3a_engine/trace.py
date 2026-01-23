from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Tuple, Any


@dataclass(frozen=True)
class TraceEvent:
    index: int
    state: str
    action: str
    detail: str


class Trace:
    """
    In-memory trace only (D.3):
      - No I/O
      - Each step recorded
      - STOP always has cause
      - Trace does not influence execution semantics (append-only)

    IMPORTANT: No imports from state_machine to avoid circular dependencies.
    State is recorded as string.
    """

    def __init__(self) -> None:
        self._events: List[TraceEvent] = []
        self._stop_cause: Optional[Tuple[str, str]] = None

    def record_state(self, state: Any, action: str, detail: str) -> None:
        # Accept Enum or string; store as deterministic string
        s = getattr(state, "value", state)
        self._events.append(
            TraceEvent(
                index=len(self._events),
                state=str(s),
                action=str(action),
                detail=str(detail),
            )
        )

    def record_stop(self, code: str, message: str) -> None:
        if self._stop_cause is None:
            self._stop_cause = (str(code), str(message))
        self.record_state("STOP", action="STOP", detail=f"{code}: {message}")

    @property
    def events(self) -> Tuple[TraceEvent, ...]:
        return tuple(self._events)

    @property
    def stop_cause(self) -> Optional[Tuple[str, str]]:
        return self._stop_cause

# Backwards-compatible alias for existing repo tests (e.g., test_ops3a_engine_smoke.py)
ExecutionTrace = Trace
