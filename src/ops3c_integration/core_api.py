from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, Mapping, Optional, Tuple

from src.ops3a_engine.scheduler import deterministic_toposort
from src.ops3a_engine.state_machine import StateMachine
from src.ops3a_engine.invariants import InvariantViolation


@dataclass(frozen=True)
class CoreResult:
    """
    Minimal carrier for outputs from OPS-3A primitives.

    Note: OPS-3A (as currently in repo) exposes deterministic primitives
    (scheduler + state machine), not a single monolithic `run()` entrypoint.
    This adapter is a THIN bridge that composes those primitives WITHOUT:
      - recovery/retry
      - reordering beyond deterministic scheduling
      - time/random/env dependencies
    """
    trace: Any
    output: Any = None
    stop: bool = False


def _extract_edges(spec: Dict[str, Any]) -> Iterable[Tuple[str, str]]:
    """
    Supported minimal forms:
      - spec["graph"]["edges"] as list of [u,v] or {"from":u,"to":v}
      - spec["edges"] same
    If no edges present => empty.
    """
    g = spec.get("graph", spec)
    edges = g.get("edges") if isinstance(g, dict) else None
    if not edges:
        return []

    out: list[tuple[str, str]] = []
    for e in edges:
        if isinstance(e, (list, tuple)) and len(e) == 2:
            out.append((str(e[0]), str(e[1])))
        elif isinstance(e, dict) and "from" in e and "to" in e:
            out.append((str(e["from"]), str(e["to"])))
        else:
            raise ValueError(f"Invalid edge encoding: {e!r}")
    return out


def _edges_to_deps_graph(edges: Iterable[Tuple[str, str]]) -> Mapping[str, Tuple[str, ...]]:
    """
    Convert edge list (u -> v) into scheduler input:
      deps_graph[node] = predecessors

    Deterministic normalization is handled by deterministic_toposort,
    but we still build stable tuples here.
    """
    preds: Dict[str, set[str]] = {}
    nodes: set[str] = set()

    for u, v in edges:
        u = str(u)
        v = str(v)
        nodes.add(u)
        nodes.add(v)
        preds.setdefault(v, set()).add(u)
        preds.setdefault(u, set())

    return {n: tuple(sorted(preds.get(n, set()))) for n in sorted(nodes)}


def run_core(spec: Dict[str, Any], *, extensions: Optional[Dict[str, Any]] = None) -> CoreResult:
    """
    THIN bridge: compose OPS-3A primitives deterministically.

    extensions are accepted only for signature compatibility, but NOT used as data
    (to avoid smuggling nondeterminism via object repr / identity).
    Only extension KEYS are relevant and are handled by wrapper envelope hash.
    """
    _ = extensions  # intentionally unused (no semantics here)

    sm = StateMachine()
    try:
        sm.start()

        edges = list(_extract_edges(spec))
        deps_graph = _edges_to_deps_graph(edges)
        order = deterministic_toposort(deps_graph).order

        sm.end()

        trace = {
            "state": str(sm.state),
            "order": list(order),
            "stop": False,
        }
        return CoreResult(trace=trace, output={"order": list(order)}, stop=False)

    except InvariantViolation as e:
        # Core primitive invariant => STOP (terminal). No recovery.
        sm.stop(code=e.code, message=e.message)
        trace = {
            "state": str(sm.state),
            "order": [],
            "stop": True,
            "stop_reason": {"code": e.code, "message": e.message},
        }
        return CoreResult(trace=trace, output=None, stop=True)

    except Exception as e:  # noqa: BLE001
        # Any unexpected integration exception => STOP (hard-fail posture)
        sm.stop(code="OPS3C_UNEXPECTED", message=f"{type(e).__name__}: {e}")
        trace = {
            "state": str(sm.state),
            "order": [],
            "stop": True,
            "stop_reason": {"code": "OPS3C_UNEXPECTED", "message": f"{type(e).__name__}: {e}"},
        }
        return CoreResult(trace=trace, output=None, stop=True)
