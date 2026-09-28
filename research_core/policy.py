from __future__ import annotations

LENS_SUPPORT_CLASSES={
    "company":"high",
    "industry":"moderate",
    "derived":"moderate_high",
    "archetype":"low_moderate",
    "general":"low",
}

MATURITY_OUTPUTS={
    "exploratory":"internal_only",
    "reviewed_practice":"ordered_practice_priorities",
    "evaluation_ready":"probabilistic_estimates_with_uncertainty",
    "empirically_supported":"full_probabilistic_output",
}


def apply_support_ceiling(value: float, ceiling: float) -> float:
    """Deployment release cap only; never label the result a correctness probability."""
    if not 0<=ceiling<=1: raise ValueError("ceiling must be in [0,1]")
    return min(value,ceiling)
