from __future__ import annotations

import math
from typing import Dict, Iterable, Sequence, Tuple

from .models import EvidenceRecord


def exponential_recency_weight(age_days: float, decay_rate_per_day: float) -> float:
    """Return exp(-decay_rate * age) using reciprocal day units."""

    if not math.isfinite(age_days) or age_days < 0.0:
        raise ValueError("age_days must be non-negative")
    if not math.isfinite(decay_rate_per_day) or decay_rate_per_day < 0.0:
        raise ValueError("decay_rate_per_day must be non-negative")
    return math.exp(-decay_rate_per_day * age_days)


def weighted_counts(
    records: Sequence[EvidenceRecord],
    categories: Iterable[str],
    decay_rate_per_day: float,
) -> Tuple[Dict[str, float], float]:
    """Compute authorization-gated, quality- and recency-weighted counts.

    Every record is structurally validated. Unauthorized records contribute zero
    mass. Unknown categories are rejected instead of being silently projected
    into the declared taxonomy.
    """

    cats = list(categories)
    if not cats:
        raise ValueError("categories must not be empty")
    if len(set(cats)) != len(cats):
        raise ValueError("categories must be unique")
    if not math.isfinite(decay_rate_per_day) or decay_rate_per_day < 0.0:
        raise ValueError("decay_rate_per_day must be non-negative")

    counts = {category: 0.0 for category in cats}
    for record in records:
        record.validate()
        if record.category not in counts:
            raise ValueError(f"unknown category: {record.category}")
        if not record.authorized:
            continue
        weight = record.quality * exponential_recency_weight(
            record.age_days,
            decay_rate_per_day,
        )
        counts[record.category] += weight

    return counts, sum(counts.values())
