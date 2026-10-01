"""Production-oriented reasoning primitives for AIMS Lens Engine.

This package contains selected mechanisms promoted from the research artifact.
It intentionally does not expose paper experiments, JobACE-specific objects, or
language-model generation logic.
"""

from .compatibility import masked_and_renormalized
from .evidence import exponential_recency_weight, weighted_counts
from .inference import hierarchical_dirichlet_mean
from .models import EvidenceRecord
from .support import data_support, effective_permitted_mass, should_abstain

__all__ = [
    "EvidenceRecord",
    "data_support",
    "effective_permitted_mass",
    "exponential_recency_weight",
    "hierarchical_dirichlet_mean",
    "masked_and_renormalized",
    "should_abstain",
    "weighted_counts",
]
