from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from ea_oc_ext.engine.model import Phase


@dataclass(frozen=True)
class TransitionContext:
    """
    External Ψ is a boolean signal:
    - It does NOT directly control axes (forbidden by ETS).
    - It only indicates whether 'external restoration of potentials' is present,
      allowing INERTIA -> SUCCESS (ETS §5).
    """
    external_psi_restores_potentials: bool = False


def is_transition_allowed(prev: Phase, nxt: Phase, ctx: TransitionContext) -> bool:
    """
    ETS §5 allowed transitions:
      SUCCESS -> INERTIA | COLLAPSE | STOP
      INERTIA -> SUCCESS only via external Ψ; or -> COLLAPSE | STOP
      COLLAPSE -> STOP
      STOP -> none
    """
    if prev == "STOP":
        return False
    if prev == "COLLAPSE":
        return nxt == "STOP"
    if prev == "INERTIA":
        if nxt == "SUCCESS":
            return ctx.external_psi_restores_potentials
        return nxt in ("COLLAPSE", "STOP")
    if prev == "SUCCESS":
        return nxt in ("INERTIA", "COLLAPSE", "STOP")
    return False


def guard_transition_or_stop(prev: Phase, nxt: Phase, ctx: TransitionContext) -> Phase:
    """
    ETS §7: No-Go violation => STOP.
    Here we implement the transition-related No-Go family:
      - NoFreeTransformation / InstantRecovery / ExternalOverride (transition aspect)
    as: if transition is not allowed => STOP.
    """
    return nxt if is_transition_allowed(prev, nxt, ctx) else "STOP"
