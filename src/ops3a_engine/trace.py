from typing import List


class ExecutionTrace:
    """
    In-memory execution trace.
    No persistence. No timestamps.
    """

    def __init__(self) -> None:
        self._events: List[str] = []

    def record(self, event: str) -> None:
        self._events.append(event)

    def events(self) -> List[str]:
        return list(self._events)
