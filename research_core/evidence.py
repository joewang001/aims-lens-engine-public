from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import date
from typing import Dict, Iterable, List, Tuple


@dataclass(frozen=True)
class EvidencePacket:
    evidence_id: str
    source_type: str
    permitted_use: str
    date_collected: str
    collection_method: str
    scope: str
    reviewer: str
    quality_rating: float
    transformation_history: List[str]
    expiry_conditions: str
    supports: List[str]

    def is_valid(self, current_date: str) -> bool:
        return date.fromisoformat(current_date) < date.fromisoformat(self.expiry_conditions)

    def authorizes(self, purpose: str, current_date: str) -> bool:
        return self.permitted_use in {purpose, "research_and_practice"} and self.is_valid(current_date)


def exponential_recency_weight(age: float, decay_rate: float) -> float:
    """Implements exp(-delta * age), matching manuscript Eq. 5.

    `age` and `decay_rate` must use reciprocal units (e.g. months and per-month).
    """
    if age < 0:
        raise ValueError("age must be non-negative")
    if decay_rate < 0:
        raise ValueError("decay_rate must be non-negative")
    return math.exp(-decay_rate * age)


def decay_rate_from_half_life(half_life: float) -> float:
    if half_life <= 0:
        raise ValueError("half_life must be positive")
    return math.log(2.0) / half_life


def weighted_counts(records, categories: Iterable[str], decay_rate: float) -> Tuple[Dict[str, float], float]:
    """Effective counts with a hard authorization gate.

    This is the code analogue of manuscript Eq. 5:
      n_tilde[k] = sum_j a_j * rho_j * exp(-delta * age_j) * y[j,k]
    where `authorized` supplies the binary a_j gate and quality supplies rho_j.
    """
    cats=list(categories)
    counts={k:0.0 for k in cats}
    for record in records:
        record.validate()
        if not record.authorized:
            continue
        if record.category not in counts:
            raise ValueError(f"unknown category: {record.category}")
        weight=record.quality * exponential_recency_weight(record.age_days, decay_rate)
        counts[record.category]+=weight
    return counts, sum(counts.values())
