from __future__ import annotations

import math
from typing import Dict, Iterable, Mapping


def _normalize_positive(
    values: Mapping[str, float],
    categories: Iterable[str],
) -> Dict[str, float]:
    cats = list(categories)
    if not cats:
        raise ValueError("categories must not be empty")
    if len(set(cats)) != len(cats):
        raise ValueError("categories must be unique")
    if set(values) - set(cats):
        raise ValueError("parent distribution contains an unknown category")
    parent_values = [float(value) for value in values.values()]
    if any(not math.isfinite(value) or value < 0.0 for value in parent_values):
        raise ValueError("parent distribution values must be non-negative")
    total = sum(float(values.get(category, 0.0)) for category in cats)
    if total <= 0.0:
        raise ValueError("parent distribution must retain positive mass")
    return {
        category: float(values.get(category, 0.0)) / total
        for category in cats
    }


def hierarchical_dirichlet_mean(
    parent_distribution: Mapping[str, float],
    counts: Mapping[str, float],
    categories: Iterable[str],
    kappa_company: float,
) -> Dict[str, float]:
    """Company-level shrinkage against a declared parent distribution.

    This is the production primitive corresponding to the local level of the
    manuscript hierarchy. Full multi-level uncertainty propagation is not
    implied or implemented here.
    """

    if not math.isfinite(kappa_company) or kappa_company <= 0.0:
        raise ValueError("kappa_company must be positive")
    cats = list(categories)
    if set(counts) - set(cats):
        raise ValueError("counts contain an unknown category")
    count_values = [float(value) for value in counts.values()]
    if any(not math.isfinite(value) or value < 0.0 for value in count_values):
        raise ValueError("counts must be non-negative")
    parent = _normalize_positive(parent_distribution, cats)
    alpha = {
        category: (
            kappa_company * parent[category]
            + float(counts.get(category, 0.0))
        )
        for category in cats
    }
    total = sum(alpha.values())
    if total <= 0.0:
        raise ValueError("posterior mass must be positive")
    return {category: value / total for category, value in alpha.items()}
