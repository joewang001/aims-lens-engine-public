from __future__ import annotations
import math
from typing import Mapping


def normalized_entropy(distribution: Mapping[str,float], permitted_count: int | None=None) -> float:
    """Manuscript Eq. 10; denominator uses K_L, the number of permitted categories."""
    if permitted_count is None: permitted_count=len(distribution)
    if permitted_count <= 1: return 0.0
    h=-sum(p*math.log(p) for p in distribution.values() if p>0)
    return h/math.log(permitted_count)


def data_support(effective_mass: float, tau: float) -> float:
    """Manuscript Eq. 11: 1 - exp(-n_eff/tau). Not correctness probability."""
    if effective_mass < 0: raise ValueError("effective_mass must be non-negative")
    if tau <= 0: raise ValueError("tau must be positive")
    return 1.0-math.exp(-effective_mass/tau)


def should_abstain(data_support_score: float, threshold: float) -> bool:
    if not 0<=data_support_score<=1 or not 0<=threshold<=1:
        raise ValueError("support score and threshold must be in [0,1]")
    return data_support_score < threshold
