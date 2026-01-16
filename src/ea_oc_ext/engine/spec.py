from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

import yaml


@dataclass(frozen=True)
class KeaSpec:
    """Immutable executable theory spec ETS.K_EA.v1.1."""
    spec_id: str
    status: str
    axes: Dict[str, List[str]]
    f_components: List[str]
    theta_mapping: Dict[str, str]
    required_cycles: List[str]
    k_factors: List[str]
    phase_precedence: List[str]
    phase_defs: Dict[str, str]
    allowed_transitions: Dict[str, List[str]]
    coupling_fields: List[str]
    invariants: List[str]
    no_go: List[str]


def load_kea_spec(path: str | Path) -> KeaSpec:
    p = Path(path)
    data: Dict[str, Any] = yaml.safe_load(p.read_text(encoding="utf-8"))

    # Minimal structural validation (no invention, only checking presence)
    spec_id = data["id"]
    status = data["status"]

    axes = data["axes"]
    f_components = list(data["structural_tension_f_k"]["components"])
    theta_mapping = dict(data["structural_tension_f_k"]["threshold_mapping"])

    required_cycles = list(data["cycles"]["required"])

    k_factors = list(data["k_EA"]["factorization"])

    phase_precedence = list(data["phase_logic"]["precedence"])
    phase_defs = dict(data["phase_logic"]["definitions"])
    allowed_transitions = dict(data["phase_logic"]["allowed_transitions"])

    coupling_fields = list(data["coupling_k7"]["fields"])

    invariants = list(data.get("invariants", []))
    no_go = list(data.get("no_go", []))

    return KeaSpec(
        spec_id=spec_id,
        status=status,
        axes=axes,
        f_components=f_components,
        theta_mapping=theta_mapping,
        required_cycles=required_cycles,
        k_factors=k_factors,
        phase_precedence=phase_precedence,
        phase_defs=phase_defs,
        allowed_transitions=allowed_transitions,
        coupling_fields=coupling_fields,
        invariants=invariants,
        no_go=no_go,
    )
