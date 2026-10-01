from __future__ import annotations

from .compatibility import masked_and_renormalized
from .decision import DecisionEnvelope, LocalDecisionRequest
from .evidence import weighted_counts
from .inference import hierarchical_dirichlet_mean
from .support import data_support, effective_permitted_mass, should_abstain


def decide_local_practice_priority(request: LocalDecisionRequest) -> DecisionEnvelope:
    """Compose promoted v1.5 primitives into a local decision envelope.

    This function implements the pre-routing portion of the manuscript service:
    evidence weighting -> local hierarchical shrinkage -> compatibility masking ->
    permitted evidence support -> abstention or ordered practice priority.

    It does not implement routing mixtures, support-aware backoff, divergence
    guards, JobACE adapters, or language-model realization.
    """

    request.validate()

    counts, _total_effective_mass = weighted_counts(
        request.evidence,
        request.categories,
        request.temporal_decay_rate_per_day,
    )
    effective_mass = effective_permitted_mass(
        counts,
        request.permitted_categories,
    )
    local_distribution = hierarchical_dirichlet_mean(
        request.parent_distribution,
        counts,
        request.categories,
        request.kappa_company,
    )
    permitted_distribution = masked_and_renormalized(
        local_distribution,
        request.categories,
        request.permitted_categories,
    )
    support = data_support(effective_mass, request.support_tau)

    if not permitted_distribution:
        return DecisionEnvelope(
            mode="abstain",
            reason="all_categories_masked",
            top_category=None,
            priority_order=(),
            diagnostic_distribution={},
            data_support=support,
            effective_evidence_mass=effective_mass,
        )

    if should_abstain(support, request.abstention_threshold):
        return DecisionEnvelope(
            mode="abstain",
            reason="insufficient_data_support",
            top_category=None,
            priority_order=(),
            diagnostic_distribution={},
            data_support=support,
            effective_evidence_mass=effective_mass,
        )

    priority = tuple(
        category
        for category, _value in sorted(
            permitted_distribution.items(),
            key=lambda item: (-item[1], item[0]),
        )
    )
    return DecisionEnvelope(
        mode="ordered_practice_priority",
        reason=None,
        top_category=priority[0],
        priority_order=priority,
        diagnostic_distribution=dict(permitted_distribution),
        data_support=support,
        effective_evidence_mass=effective_mass,
    )
