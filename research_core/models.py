from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List

@dataclass(frozen=True)
class EvidenceRecord:
    category: str
    authorized: bool
    quality: float
    age_days: float
    def validate(self):
        if not 0<=self.quality<=1: raise ValueError("quality must be in [0,1]")
        if self.age_days<0: raise ValueError("age_days must be non-negative")

@dataclass(frozen=True)
class RoutingLevel:
    name: str; backoff_distance: int; authorized: bool; applicable: bool; coverage: float; distribution: Dict[str,float]
    def validate(self):
        if self.backoff_distance<0: raise ValueError("backoff_distance must be non-negative")
        if not 0<=self.coverage<=1: raise ValueError("coverage must be in [0,1]")
        if any(v<0 for v in self.distribution.values()): raise ValueError("distribution values must be non-negative")

@dataclass(frozen=True)
class PracticeRequest:
    categories: List[str]
    parent_distribution: Dict[str,float]
    evidence: List[EvidenceRecord]
    permitted_categories: List[str]
    kappa_company: float
    temporal_decay_rate_per_day: float
    routing_levels: List[RoutingLevel]
    routing_gamma: float=0.7
    support_tau: float=8.0
    abstention_threshold: float=0.0
    def validate(self):
        if not self.categories: raise ValueError("categories must not be empty")
        if self.kappa_company<=0 or self.temporal_decay_rate_per_day<0 or self.support_tau<=0: raise ValueError("invalid hyperparameters")
        if not 0<self.routing_gamma<=1: raise ValueError("routing_gamma must be in (0,1]")
        if not 0<=self.abstention_threshold<=1: raise ValueError("abstention_threshold must be in [0,1]")
        if set(self.permitted_categories)-set(self.categories): raise ValueError("unknown permitted category")
        for r in self.evidence: r.validate()
        for l in self.routing_levels: l.validate()
