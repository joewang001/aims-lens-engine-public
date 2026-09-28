from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List


def _declared_backoff_distance(name: str) -> int:
    prefix = name.split("_", 1)[0]
    if prefix not in {"L0", "L1", "L2", "L3", "L4", "L5"}:
        raise ValueError("routing level name must begin with L0 through L5")
    return int(prefix[1:])


@dataclass(frozen=True)
class EvidenceRecord:
    category: str
    authorized: bool
    quality: float
    age_days: float

    def validate(self):
        if not self.category:
            raise ValueError("evidence category must not be empty")
        if not 0 <= self.quality <= 1:
            raise ValueError("quality must be in [0,1]")
        if self.age_days < 0:
            raise ValueError("age_days must be non-negative")


@dataclass(frozen=True)
class RoutingLevel:
    name: str
    backoff_distance: int
    authorized: bool
    applicable: bool
    coverage: float
    distribution: Dict[str, float]

    def validate(self):
        declared = _declared_backoff_distance(self.name)
        if not 0 <= self.backoff_distance <= 5:
            raise ValueError("backoff_distance must be in [0,5]")
        if declared != self.backoff_distance:
            raise ValueError("routing level name and backoff_distance disagree")
        if not 0 <= self.coverage <= 1:
            raise ValueError("coverage must be in [0,1]")
        if not self.distribution:
            raise ValueError("distribution must not be empty")
        if any(v < 0 for v in self.distribution.values()):
            raise ValueError("distribution values must be non-negative")
        if sum(self.distribution.values()) <= 0:
            raise ValueError("distribution must have positive mass")


@dataclass(frozen=True)
class PracticeRequest:
    categories: List[str]
    parent_distribution: Dict[str, float]
    evidence: List[EvidenceRecord]
    permitted_categories: List[str]
    kappa_company: float
    temporal_decay_rate_per_day: float
    routing_levels: List[RoutingLevel]
    routing_gamma: float = 0.7
    support_tau: float = 8.0
    abstention_threshold: float = 0.0

    def validate(self):
        if not self.categories:
            raise ValueError("categories must not be empty")
        if len(set(self.categories)) != len(self.categories):
            raise ValueError("categories must be unique")
        if any(not category for category in self.categories):
            raise ValueError("categories must not contain empty values")
        if len(set(self.permitted_categories)) != len(self.permitted_categories):
            raise ValueError("permitted_categories must be unique")
        if set(self.permitted_categories) - set(self.categories):
            raise ValueError("unknown permitted category")
        if set(self.parent_distribution) - set(self.categories):
            raise ValueError("parent_distribution contains an unknown category")
        if sum(max(0.0, float(v)) for v in self.parent_distribution.values()) <= 0:
            raise ValueError("parent_distribution must have positive mass")
        if self.kappa_company <= 0 or self.temporal_decay_rate_per_day < 0 or self.support_tau <= 0:
            raise ValueError("invalid hyperparameters")
        if not 0 < self.routing_gamma <= 1:
            raise ValueError("routing_gamma must be in (0,1]")
        if not 0 <= self.abstention_threshold <= 1:
            raise ValueError("abstention_threshold must be in [0,1]")
        if not self.routing_levels:
            raise ValueError("routing_levels must not be empty")

        seen_levels = set()
        l0_count = 0
        for record in self.evidence:
            record.validate()
            if record.category not in self.categories:
                raise ValueError("evidence contains an unknown category")

        for level in self.routing_levels:
            level.validate()
            if level.backoff_distance == 0:
                l0_count += 1
            if level.name in seen_levels:
                raise ValueError("routing level names must be unique")
            seen_levels.add(level.name)
            if set(level.distribution) - set(self.categories):
                raise ValueError("routing distribution contains an unknown category")

        if l0_count != 1:
            raise ValueError("routing_levels must contain exactly one L0 level")
