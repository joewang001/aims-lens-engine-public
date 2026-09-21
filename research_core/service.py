from __future__ import annotations
from typing import Any, Dict
from .compatibility import masked_and_renormalized
from .evidence import weighted_counts
from .inference import hierarchical_dirichlet_mean
from .models import PracticeRequest
from .routing import route_mixture, routing_distribution_has_permitted_mass
from .uncertainty import data_support, normalized_entropy, should_abstain


def prioritize_followups(request: PracticeRequest) -> Dict[str,Any]:
    request.validate()
    counts,_total_effective_mass=weighted_counts(
        request.evidence,
        request.categories,
        request.temporal_decay_rate_per_day,
    )
    # Release/abstention support is defined only over categories permitted in
    # the current practice context. Evidence assigned to a category that is
    # later compatibility-masked must not increase support for release.
    effective_mass=sum(counts.get(category,0.0) for category in request.permitted_categories)
    local=hierarchical_dirichlet_mean(request.parent_distribution,counts,request.categories,request.kappa_company)
    local_masked=masked_and_renormalized(local,request.categories,request.permitted_categories)
    if not local_masked:
        return {"mode":"abstain","reason":"all_categories_masked","disclaimer":"This system abstained rather than release an invalid practice priority."}
    routed_levels=list(request.routing_levels)
    l0_index=next(i for i,level in enumerate(routed_levels) if level.backoff_distance==0)
    l0=routed_levels[l0_index]
    routed_levels[l0_index]=type(l0)(l0.name,l0.backoff_distance,l0.authorized,l0.applicable,l0.coverage,local_masked)
    routed,provenance=route_mixture(routed_levels,request.permitted_categories,request.routing_gamma)
    if not routed:
        has_massless_eligible_level=any(
            level.authorized
            and level.applicable
            and level.coverage>0
            and not routing_distribution_has_permitted_mass(
                level.distribution,
                request.permitted_categories,
            )
            for level in routed_levels
        )
        if has_massless_eligible_level:
            return {
                "mode":"abstain",
                "reason":"no_supported_routing_mass",
                "disclaimer":"This system abstained because authorized applicable routing levels retained no probability mass on the permitted practice categories.",
            }
        return {"mode":"abstain","reason":"no_eligible_routing_level","disclaimer":"This system abstained because no authorized applicable routing level was available."}
    support=data_support(effective_mass,request.support_tau)
    if request.abstention_threshold>0 and should_abstain(support,request.abstention_threshold):
        return {"mode":"abstain","reason":"insufficient_data_support","data_support":round(support,6),"effective_evidence_mass":round(effective_mass,6),"routing_provenance":provenance,"disclaimer":"This system abstained because evidential support was below the declared release threshold."}
    priority=[k for k,_ in sorted(routed.items(),key=lambda kv:(-kv[1],kv[0]))]
    return {"mode":"ordered_practice_priority","top_category":priority[0],"priority_order":priority,"diagnostic_distribution":{k:round(v,6) for k,v in routed.items()},"uncertainty_entropy":round(normalized_entropy(routed,len(request.permitted_categories)),6),"data_support":round(support,6),"effective_evidence_mass":round(effective_mass,6),"routing_provenance":provenance,"disclaimer":"This output prioritizes interview practice. It is not a prediction of a specific employer's interview process or hiring decision."}
