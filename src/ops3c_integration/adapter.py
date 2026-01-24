from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, Optional, Set, Tuple
import hashlib
import json

from .core_api import run_core, CoreResult


class MisuseError(RuntimeError):
    """Hard-fail for misuse at integration boundary (NOT inside core)."""


def _stable_json_hash(obj: Any) -> str:
    """
    Deterministic hash of spec-like structures.
    - No env/time/random.
    - Sort keys.
    """
    data = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def _detect_cycle(edges: Iterable[Tuple[str, str]]) -> bool:
    """
    Cycle detection for a directed graph given as edge list (u->v).
    No external deps.
    """
    adj: Dict[str, Set[str]] = {}
    nodes: Set[str] = set()
    for u, v in edges:
        nodes.add(u)
        nodes.add(v)
        adj.setdefault(u, set()).add(v)
        adj.setdefault(v, set())

    temp: Set[str] = set()
    perm: Set[str] = set()

    def visit(n: str) -> bool:
        if n in perm:
            return False
        if n in temp:
            return True
        temp.add(n)
        for m in adj.get(n, ()):
            if visit(m):
                return True
        temp.remove(n)
        perm.add(n)
        return False

    return any(visit(n) for n in nodes)


def _extract_edges(spec: Dict[str, Any]) -> Iterable[Tuple[str, str]]:
    """
    Integration-level assumption: spec may contain a graph.
    Supported minimal forms (boundary-only):
      - spec["graph"]["edges"] as list of [u,v] or {"from":u,"to":v}
      - spec["edges"] same
    If no graph present, returns empty list (no cycle proof possible for that spec).
    """
    g = spec.get("graph", spec)
    edges = g.get("edges") if isinstance(g, dict) else None
    if not edges:
        return []

    out = []
    for e in edges:
        if isinstance(e, (list, tuple)) and len(e) == 2:
            out.append((str(e[0]), str(e[1])))
        elif isinstance(e, dict) and "from" in e and "to" in e:
            out.append((str(e["from"]), str(e["to"])))
        else:
            raise MisuseError(f"Invalid edge encoding: {e!r}")
    return out


def _trace_has_stop(trace: Any) -> bool:
    """
    Best-effort STOP detection without assuming trace schema.
    """
    if trace is None:
        return False
    if isinstance(trace, str):
        return "STOP" in trace
    if isinstance(trace, dict):
        # common patterns
        if trace.get("stop") is True:
            return True
        if str(trace.get("status", "")).upper() == "STOP":
            return True
        # scan events if present
        ev = trace.get("events")
        if isinstance(ev, list):
            return any(("STOP" in str(x)) for x in ev)
    if isinstance(trace, list):
        return any(("STOP" in str(x)) for x in trace)
    return False


def _wrap_trace(trace: Any, *, envelope_hash: str) -> Any:
    """
    Wrapper-side trace envelope to support determinism tests.
    Does not mutate dict/list in-place to avoid accidental nondeterminism.
    """
    if trace is None:
        return {"ops3c_envelope_hash": envelope_hash, "trace": None}
    if isinstance(trace, dict):
        merged = dict(trace)
        merged["ops3c_envelope_hash"] = envelope_hash
        return merged
    return {"ops3c_envelope_hash": envelope_hash, "trace": trace}


@dataclass
class IntegrationWrapper:
    """
    Boundary wrapper for OPS-3A:
    - Misuse rejection (C.1) at boundary
    - Integration correctness (C.2): no recovery, no reorder, no STOP weakening
    - Pipeline determinism (C.3): stable hashing + trace capture
    """
    registered_extensions: Set[str]

    _stopped: bool = False
    _in_call: bool = False

    def run(self, spec: Dict[str, Any], *, extensions: Optional[Dict[str, Any]] = None) -> CoreResult:
        if self._stopped:
            raise MisuseError("STOP already observed in this wrapper instance: further calls forbidden.")
        if self._in_call:
            raise MisuseError("Re-entry / execution loop detected: wrapper is non-reentrant.")

        # ---- Misuse checks at boundary (no core edits) ----
        # 1) Extensions must be registered (unregistered => hard fail)
        if extensions:
            unknown = set(extensions.keys()) - set(self.registered_extensions)
            if unknown:
                raise MisuseError(f"Unregistered extensions: {sorted(unknown)}")

        # 2) Graph must be acyclic if graph present
        edges = list(_extract_edges(spec))
        if edges and _detect_cycle(edges):
            raise MisuseError("Invalid graph: cycle detected (execution loops forbidden).")

        # 3) If caller tries to smuggle nondeterminism markers, hard fail (boundary policy)
        #    This does not assert core uses them; it enforces "no quiet nondeterminism" at integration.
        forbidden_keys = {"time", "timestamp", "rand", "random", "env", "seed"}
        if any(k in spec for k in forbidden_keys):
            raise MisuseError(
                f"Spec contains forbidden nondeterminism key(s): {sorted(set(spec.keys()) & forbidden_keys)}"
            )

        # Determinism envelope: stable hash for spec+extensions
        envelope = {"spec": spec, "extensions": sorted(list(extensions.keys())) if extensions else []}
        envelope_hash = _stable_json_hash(envelope)

        # ---- Core call (no reordering, no retry) ----
        self._in_call = True
        try:
            res = run_core(spec, extensions=extensions)
        finally:
            self._in_call = False

        # ---- STOP propagation (terminal) ----
        # If core signals stop OR trace contains STOP marker, wrapper becomes terminal.
        if res.stop or _trace_has_stop(res.trace):
            self._stopped = True

        # Attach envelope hash to trace wrapper-side (NO mutation; CoreResult may be frozen)
        wrapped_trace = _wrap_trace(res.trace, envelope_hash=envelope_hash)
        return CoreResult(trace=wrapped_trace, output=res.output, stop=res.stop)
