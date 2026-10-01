from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, Mapping, Optional, Sequence, Tuple

from .models import EvidenceRecord


@dataclass(frozen=True)
class LocalDecisionRequest:
    """Inputs for the local, pre-routing practice-priority decision layer."""

    categories: Sequence[str]
    parent_distribution: Mapping[str, float]
    evidence: Sequence[EvidenceRecord]
    permitted_categories: Sequence[str]
    kappa_company: float
    temporal_decay_rate_per_day: float
    support_tau: float
    abstention_threshold: float

    def validate(self) -> None:
        categories = list(self.categories)
        permitted = list(self.permitted_categories)

        if not categories:
            raise ValueError("categories must not be empty")
        if any(not category for category in categories):
            raise ValueError("categories must not contain empty values")
        if len(set(categories)) != len(categories):
            raise ValueError("categories must be unique")
        if len(set(permitted)) != len(permitted):
            raise ValueError("permitted_categories must be unique")
        if set(permitted) - set(categories):
            raise ValueError("unknown permitted category")
        if set(self.parent_distribution) - set(categories):
            raise ValueError("parent_distribution contains an unknown category")

        parent_values = [float(value) for value in self.parent_distribution.values()]
        if any(not math.isfinite(value) or value < 0.0 for value in parent_values):
            raise ValueError("parent_distribution values must be finite and non-negative")
        if sum(parent_values) <= 0.0:
            raise ValueError("parent_distribution must retain positive mass")

        if not math.isfinite(self.kappa_company) or self.kappa_company <= 0.0:
            raise ValueError("kappa_company must be positive")
        if (
            not math.isfinite(self.temporal_decay_rate_per_day)
            or self.temporal_decay_rate_per_day < 0.0
        ):
            raise ValueError("temporal_decay_rate_per_day must be non-negative")
        if not math.isfinite(self.support_tau) or self.support_tau <= 0.0:
            raise ValueError("support_tau must be positive")
        if (
            not math.isfinite(self.abstention_threshold)
            or not 0.0 <= self.abstention_threshold <= 1.0
        ):
            raise ValueError("abstention_threshold must be in [0,1]")

        for record in self.evidence:
            record.validate()
            if record.category not in categories:
                raise ValueError("evidence contains an unknown category")


@dataclass(frozen=True)
class DecisionEnvelope:
    """Stable internal output of the local practice-priority decision layer.

    The envelope deliberately stops before cross-level routing, backoff, provenance
    assembly, adapter translation, or natural-language generation.
    """

    mode: str
    reason: Optional[str]
    top_category: Optional[str]
    priority_order: Tuple[str, ...]
    diagnostic_distribution: Dict[str, float]
    data_support: float
    effective_evidence_mass: float
