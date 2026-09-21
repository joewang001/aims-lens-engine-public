from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Iterable, List, Tuple
from .inference import normalize

BACKOFF_SEQUENCE = [
    ("L0_full_parent_context", 0),
    ("L1_drop_one_parent", 1),
    ("L2_drop_two_parents", 2),
    ("L3_industry_context", 3),
    ("L4_archetype_context", 4),
    ("L5_generic_context", 5),
]


def route_mixture(levels, categories: Iterable[str], gamma: float) -> Tuple[Dict[str, float], List[dict]]:
    """Implements manuscript Eq. 8–9."""
    if not 0 < gamma <= 1:
        raise ValueError("gamma must be in (0,1]")
    cats = list(categories)
    components = []
    for level in levels:
        level.validate()
        authorization = 1.0 if level.authorized else 0.0
        applicability = 1.0 if level.applicable else 0.0
        raw = authorization * applicability * level.coverage * (gamma ** level.backoff_distance)
        if raw > 0:
            components.append((level, raw, normalize(level.distribution, cats)))
    if not components:
        return {}, []

    normalizer = sum(weight for _, weight, _ in components)
    mixture = {category: 0.0 for category in cats}
    provenance = []
    for level, raw, distribution in components:
        omega = raw / normalizer
        for category in cats:
            mixture[category] += omega * distribution[category]
        provenance.append(
            {
                "level": level.name,
                "backoff_distance": level.backoff_distance,
                "authorization": level.authorized,
                "applicability": level.applicable,
                "coverage": round(level.coverage, 6),
                "routing_weight": round(omega, 6),
            }
        )
    return normalize(mixture, cats), provenance


@dataclass(frozen=True)
class LensCandidate:
    lens_id: str
    backoff_distance: int
    authorized: bool
    fresh: bool
    maturity_allows_output: bool
    applicable: bool

    def validate(self):
        if not 0 <= self.backoff_distance <= 5:
            raise ValueError("backoff_distance must be in [0,5]")


def select_highest_specificity(candidates: Iterable[LensCandidate]) -> LensCandidate | None:
    """Select the eligible candidate with the smallest declared backoff distance.

    L0 is most specific and L5 is the generic fallback. This avoids an ambiguous
    numeric 'specificity_rank' convention.
    """
    checked = list(candidates)
    for candidate in checked:
        candidate.validate()
    eligible = [
        candidate
        for candidate in checked
        if candidate.authorized
        and candidate.fresh
        and candidate.maturity_allows_output
        and candidate.applicable
    ]
    return min(eligible, key=lambda candidate: candidate.backoff_distance) if eligible else None
