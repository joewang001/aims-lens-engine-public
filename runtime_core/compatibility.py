from __future__ import annotations

import math
from typing import Dict, Iterable, Mapping


def masked_and_renormalized(
    distribution: Mapping[str, float],
    categories: Iterable[str],
    permitted_categories: Iterable[str],
) -> Dict[str, float]:
    """Restrict a distribution to permitted categories and renormalize.

    If the permitted set retains no positive mass, return an empty mapping.
    Deliberately do not fabricate a uniform distribution: zero supported mass
    is a fail-closed condition for the caller.
    """

    cats = list(categories)
    permitted = list(permitted_categories)
    if not cats:
        raise ValueError("categories must not be empty")
    if len(set(cats)) != len(cats):
        raise ValueError("categories must be unique")
    if len(set(permitted)) != len(permitted):
        raise ValueError("permitted_categories must be unique")
    if set(permitted) - set(cats):
        raise ValueError("unknown permitted category")
    if set(distribution) - set(cats):
        raise ValueError("distribution contains an unknown category")
    distribution_values = [float(value) for value in distribution.values()]
    if any(not math.isfinite(value) or value < 0.0 for value in distribution_values):
        raise ValueError("distribution values must be non-negative")

    restricted = {
        category: float(distribution.get(category, 0.0))
        for category in permitted
    }
    total = sum(restricted.values())
    if total <= 0.0:
        return {}
    return {category: value / total for category, value in restricted.items()}
