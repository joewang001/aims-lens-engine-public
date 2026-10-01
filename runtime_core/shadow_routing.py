from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, Iterable, Mapping, Optional, Sequence, Tuple

from .compatibility import masked_and_renormalized
from .support import data_support


def _declared_backoff_distance(name: str) -> int:
    prefix = name.split("_", 1)[0]
    if prefix not in {"L0", "L1", "L2", "L3", "L4", "L5"}:
        raise ValueError("backoff level name must begin with L0 through L5")
    return int(prefix[1:])


@dataclass(frozen=True)
class BackoffCandidate:
    """One shadow candidate in the L0-to-L5 support-aware backoff sequence."""

    name: str
    backoff_distance: int
    authorized: bool
    applicable: bool
    fresh: bool
    maturity_allows_output: bool
    effective_permitted_evidence_mass: float
    distribution: Mapping[str, float]

    def validate(self) -> None:
        if not self.name:
            raise ValueError("backoff level name must not be empty")
        declared = _declared_backoff_distance(self.name)
        if not 0 <= self.backoff_distance <= 5:
            raise ValueError("backoff_distance must be in [0,5]")
        if declared != self.backoff_distance:
            raise ValueError("backoff level name and backoff_distance disagree")
        if (
            not math.isfinite(self.effective_permitted_evidence_mass)
            or self.effective_permitted_evidence_mass < 0.0
        ):
            raise ValueError(
                "effective_permitted_evidence_mass must be finite and non-negative"
            )
        if not self.distribution:
            raise ValueError("distribution must not be empty")
        for value in self.distribution.values():
            numeric = float(value)
            if not math.isfinite(numeric) or numeric < 0.0:
                raise ValueError(
                    "distribution values must be finite and non-negative"
                )


@dataclass(frozen=True)
class BackoffSelection:
    """Result of the proposed support-aware shadow backoff policy."""

    selected_level: Optional[str]
    backoff_distance: Optional[int]
    diagnostic_distribution: Dict[str, float]
    data_support: Optional[float]
    effective_evidence_mass: Optional[float]
    reason: Optional[str]
    enforcement_mode: str = "shadow"


@dataclass(frozen=True)
class ContextDivergenceObservation:
    """Observe-only divergence signal; it never changes the selected level."""

    metric: str
    value: float
    threshold: float
    triggered: bool
    enforcement_mode: str = "shadow"


@dataclass(frozen=True)
class ShadowRoutingDecision:
    """Combined shadow result for backoff selection and divergence observation."""

    selection: BackoffSelection
    divergence: Optional[ContextDivergenceObservation]


def _validate_taxonomy(
    categories: Iterable[str],
    permitted_categories: Iterable[str],
) -> Tuple[Tuple[str, ...], Tuple[str, ...]]:
    cats = tuple(categories)
    permitted = tuple(permitted_categories)
    if not cats:
        raise ValueError("categories must not be empty")
    if any(not category for category in cats):
        raise ValueError("categories must not contain empty values")
    if len(set(cats)) != len(cats):
        raise ValueError("categories must be unique")
    if len(set(permitted)) != len(permitted):
        raise ValueError("permitted_categories must be unique")
    if set(permitted) - set(cats):
        raise ValueError("unknown permitted category")
    return cats, permitted


def select_support_aware_backoff(
    candidates: Sequence[BackoffCandidate],
    categories: Iterable[str],
    permitted_categories: Iterable[str],
    support_tau: float,
    support_threshold: float,
) -> BackoffSelection:
    """Select the most specific eligible level whose declared support is adequate.

    This is a proposed production policy evaluated in shadow mode. It is not the
    v1.5 manuscript routing mixture and is not claimed to be experimentally
    validated as an optimal routing rule.
    """

    cats, permitted = _validate_taxonomy(categories, permitted_categories)
    if not math.isfinite(support_tau) or support_tau <= 0.0:
        raise ValueError("support_tau must be positive")
    if (
        not math.isfinite(support_threshold)
        or not 0.0 <= support_threshold <= 1.0
    ):
        raise ValueError("support_threshold must be in [0,1]")

    seen_names = set()
    seen_distances = set()
    checked = []
    for candidate in candidates:
        candidate.validate()
        if candidate.name in seen_names:
            raise ValueError("backoff level names must be unique")
        if candidate.backoff_distance in seen_distances:
            raise ValueError("backoff distances must be unique")
        if set(candidate.distribution) - set(cats):
            raise ValueError("routing distribution contains an unknown category")
        seen_names.add(candidate.name)
        seen_distances.add(candidate.backoff_distance)
        checked.append(candidate)

    for candidate in sorted(checked, key=lambda item: item.backoff_distance):
        if not (
            candidate.authorized
            and candidate.applicable
            and candidate.fresh
            and candidate.maturity_allows_output
        ):
            continue

        permitted_distribution = masked_and_renormalized(
            dict(candidate.distribution),
            cats,
            permitted,
        )
        if not permitted_distribution:
            continue

        support = data_support(
            candidate.effective_permitted_evidence_mass,
            support_tau,
        )
        if support < support_threshold:
            continue

        return BackoffSelection(
            selected_level=candidate.name,
            backoff_distance=candidate.backoff_distance,
            diagnostic_distribution=dict(permitted_distribution),
            data_support=support,
            effective_evidence_mass=candidate.effective_permitted_evidence_mass,
            reason=None,
        )

    return BackoffSelection(
        selected_level=None,
        backoff_distance=None,
        diagnostic_distribution={},
        data_support=None,
        effective_evidence_mass=None,
        reason="no_supported_backoff_level",
    )


def observe_context_divergence(
    reference_distribution: Mapping[str, float],
    candidate_distribution: Mapping[str, float],
    categories: Iterable[str],
    threshold: float,
) -> ContextDivergenceObservation:
    """Measure total-variation divergence without enforcing any routing action."""

    cats = tuple(categories)
    if not cats:
        raise ValueError("categories must not be empty")
    if any(not category for category in cats):
        raise ValueError("categories must not contain empty values")
    if len(set(cats)) != len(cats):
        raise ValueError("categories must be unique")
    if not math.isfinite(threshold) or not 0.0 <= threshold <= 1.0:
        raise ValueError("divergence threshold must be in [0,1]")

    reference = masked_and_renormalized(
        dict(reference_distribution),
        cats,
        cats,
    )
    candidate = masked_and_renormalized(
        dict(candidate_distribution),
        cats,
        cats,
    )
    if not reference or not candidate:
        raise ValueError("divergence distributions must retain positive mass")

    value = 0.5 * sum(
        abs(reference[category] - candidate[category])
        for category in cats
    )
    return ContextDivergenceObservation(
        metric="total_variation",
        value=value,
        threshold=threshold,
        triggered=value > threshold,
    )


def evaluate_shadow_routing(
    candidates: Sequence[BackoffCandidate],
    local_reference_distribution: Mapping[str, float],
    categories: Iterable[str],
    permitted_categories: Iterable[str],
    support_tau: float,
    support_threshold: float,
    divergence_threshold: float,
) -> ShadowRoutingDecision:
    """Evaluate proposed backoff and divergence guard without changing live output."""

    cats, permitted = _validate_taxonomy(categories, permitted_categories)
    selection = select_support_aware_backoff(
        candidates=candidates,
        categories=cats,
        permitted_categories=permitted,
        support_tau=support_tau,
        support_threshold=support_threshold,
    )
    if selection.selected_level is None:
        return ShadowRoutingDecision(selection=selection, divergence=None)

    reference = masked_and_renormalized(
        dict(local_reference_distribution),
        cats,
        permitted,
    )
    if not reference:
        raise ValueError("local_reference_distribution has no permitted mass")

    divergence = observe_context_divergence(
        reference_distribution=reference,
        candidate_distribution=selection.diagnostic_distribution,
        categories=permitted,
        threshold=divergence_threshold,
    )
    return ShadowRoutingDecision(
        selection=selection,
        divergence=divergence,
    )
