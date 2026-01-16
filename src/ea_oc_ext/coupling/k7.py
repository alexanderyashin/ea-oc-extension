from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Literal


K7Field = Literal["law", "regulation", "market", "tech", "norms"]


@dataclass(frozen=True)
class K7Fields:
    """
    Exogenous fields F7(t) per ETS §6.
    Values are dimensionless intensities for synthetic experiments.
    In real-data mode these will be estimated/calibrated externally.
    """
    law: float = 0.0
    regulation: float = 0.0
    market: float = 0.0
    tech: float = 0.0
    norms: float = 0.0

    def as_dict(self) -> Dict[str, float]:
        return {
            "law": float(self.law),
            "regulation": float(self.regulation),
            "market": float(self.market),
            "tech": float(self.tech),
            "norms": float(self.norms),
        }


@dataclass(frozen=True)
class CouplingEffects:
    """
    ETS §6 effects are *targets*, not implementations:
      - law/regulation -> Theta_exist, Theta_stop
      - market -> P_res, P_fin, Theta_inertia
      - tech -> constrain A_struct, A_info
      - norms -> affect S_obs, semantic_alignment

    This structure is a wiring map. Numeric models live ONLY in synthetic layer.
    """
    targets: Dict[str, list[str]]


def default_effect_map() -> CouplingEffects:
    return CouplingEffects(
        targets={
            "law_regulation": ["Theta_exist", "Theta_stop"],
            "market": ["P_res", "P_fin", "Theta_inertia"],
            "tech": ["A_struct", "A_info"],
            "norms": ["S_obs", "semantic_alignment"],
        }
    )
