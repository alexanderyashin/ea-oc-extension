from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class InvariantViolation(Exception):
    code: str
    message: str

    def __str__(self) -> str:
        return f"{self.code}: {self.message}"


def ensure(condition: bool, code: str, message: str) -> None:
    """
    Deterministic, side-effect-free invariant guard.
    No retries, no recovery, no I/O.
    """
    if not condition:
        raise InvariantViolation(code=code, message=message)
