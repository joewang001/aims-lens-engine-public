from __future__ import annotations

import math
from typing import Iterable, Mapping


def effective_permitted_mass(
    counts: Mapping[str, float],
    permitted_categories: Iterable[str],
) -> float:
    """Count support only from categories permitted in the current context."""

    permitted = list(permitted_categories)
    if len(set(permitted)) != len(permitted):
        raise ValueError("permitted_categories must be unique")
    values = [float(counts.get(category, 0.0)) for category in permitted]
    if any(not math.isfinite(value) or value < 0.0 for value in values):
        raise ValueError("counts must be non-negative")
    return sum(values)


def data_support(effective_mass: float, tau: float) -> float:
    """Convert effective evidence mass to a bounded support diagnostic."""

    if not math.isfinite(effective_mass) or effective_mass < 0.0:
        raise ValueError("effective_mass must be non-negative")
    if not math.isfinite(tau) or tau <= 0.0:
        raise ValueError("tau must be positive")
    return 1.0 - math.exp(-effective_mass / tau)


def should_abstain(support: float, threshold: float) -> bool:
    if not math.isfinite(support) or not 0.0 <= support <= 1.0:
        raise ValueError("support must be in [0,1]")
    if not math.isfinite(threshold) or not 0.0 <= threshold <= 1.0:
        raise ValueError("threshold must be in [0,1]")
    return support < threshold
