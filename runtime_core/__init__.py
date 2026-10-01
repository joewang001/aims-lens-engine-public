"""Production-oriented reasoning primitives for AIMS Lens Engine.

This package contains selected mechanisms promoted from the research artifact.
It intentionally does not expose paper experiments, JobACE-specific objects, or
language-model generation logic.
"""

from .compatibility import masked_and_renormalized
from .decision import DecisionEnvelope, LocalDecisionRequest
from .evidence import exponential_recency_weight, weighted_counts
from .inference import hierarchical_dirichlet_mean
from .models import EvidenceRecord
from .service import decide_local_practice_priority
from .shadow_routing import (
    BackoffCandidate,
    BackoffSelection,
    ContextDivergenceObservation,
    ShadowRoutingDecision,
    evaluate_shadow_routing,
    observe_context_divergence,
    select_support_aware_backoff,
)
from .support import data_support, effective_permitted_mass, should_abstain

__all__ = [
    "BackoffCandidate",
    "BackoffSelection",
    "ContextDivergenceObservation",
    "DecisionEnvelope",
    "EvidenceRecord",
    "LocalDecisionRequest",
    "ShadowRoutingDecision",
    "data_support",
    "decide_local_practice_priority",
    "effective_permitted_mass",
    "evaluate_shadow_routing",
    "exponential_recency_weight",
    "hierarchical_dirichlet_mean",
    "masked_and_renormalized",
    "observe_context_divergence",
    "select_support_aware_backoff",
    "should_abstain",
    "weighted_counts",
]
