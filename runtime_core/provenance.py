from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional

from .decision import DecisionEnvelope
from .shadow_routing import ShadowRoutingDecision


PUBLIC_PROVENANCE_SCOPE = "public_safe_decision_summary"


@dataclass(frozen=True)
class PublicShadowRoutingProvenance:
    """Public-safe summary of a shadow routing observation.

    Raw routing distributions, evidence identifiers, context hashes, tenant
    identifiers, and parent configuration are intentionally excluded.
    """

    selected_level: Optional[str]
    backoff_distance: Optional[int]
    selection_reason: Optional[str]
    data_support: Optional[float]
    effective_evidence_mass: Optional[float]
    divergence_metric: Optional[str]
    divergence_value: Optional[float]
    divergence_threshold: Optional[float]
    divergence_triggered: Optional[bool]
    enforcement_mode: str = "shadow"

    def validate(self) -> None:
        if self.enforcement_mode != "shadow":
            raise ValueError("shadow routing provenance must remain shadow-only")
        if (self.selected_level is None) != (self.backoff_distance is None):
            raise ValueError(
                "selected_level and backoff_distance must be present together"
            )
        if self.selected_level is None:
            if self.selection_reason is None:
                raise ValueError(
                    "unselected shadow routing provenance must include a reason"
                )
            if self.data_support is not None or self.effective_evidence_mass is not None:
                raise ValueError(
                    "unselected shadow routing provenance must not include support"
                )
        else:
            prefix = self.selected_level.split("_", 1)[0]
            if prefix not in {"L0", "L1", "L2", "L3", "L4", "L5"}:
                raise ValueError("selected_level must begin with L0 through L5")
            if int(prefix[1:]) != self.backoff_distance:
                raise ValueError(
                    "selected_level and backoff_distance disagree"
                )
            if self.selection_reason is not None:
                raise ValueError(
                    "selected shadow routing provenance must not include a reason"
                )
            if self.data_support is None or self.effective_evidence_mass is None:
                raise ValueError(
                    "selected shadow routing provenance must include support"
                )
        if self.backoff_distance is not None and not 0 <= self.backoff_distance <= 5:
            raise ValueError("backoff_distance must be in [0,5]")
        for field_name, value in (
            ("data_support", self.data_support),
            ("effective_evidence_mass", self.effective_evidence_mass),
            ("divergence_value", self.divergence_value),
            ("divergence_threshold", self.divergence_threshold),
        ):
            if value is not None and not math.isfinite(value):
                raise ValueError(f"{field_name} must be finite when present")
        if self.data_support is not None and not 0.0 <= self.data_support <= 1.0:
            raise ValueError("data_support must be in [0,1]")
        if (
            self.effective_evidence_mass is not None
            and self.effective_evidence_mass < 0.0
        ):
            raise ValueError("effective_evidence_mass must be non-negative")
        if self.divergence_value is not None and not 0.0 <= self.divergence_value <= 1.0:
            raise ValueError("divergence_value must be in [0,1]")
        if (
            self.divergence_threshold is not None
            and not 0.0 <= self.divergence_threshold <= 1.0
        ):
            raise ValueError("divergence_threshold must be in [0,1]")
        divergence_fields = (
            self.divergence_metric,
            self.divergence_value,
            self.divergence_threshold,
            self.divergence_triggered,
        )
        if self.selected_level is None and any(
            value is not None for value in divergence_fields
        ):
            raise ValueError(
                "unselected shadow routing provenance must not include divergence"
            )
        if any(value is not None for value in divergence_fields) and not all(
            value is not None for value in divergence_fields
        ):
            raise ValueError("divergence provenance fields must be present together")
        if (
            self.divergence_metric is not None
            and self.divergence_metric != "total_variation"
        ):
            raise ValueError("unsupported public divergence metric")


@dataclass(frozen=True)
class PublicDecisionProvenance:
    """Decision-level provenance safe for the public runtime envelope."""

    runtime_path: str
    decision_mode: str
    decision_reason: Optional[str]
    data_support: float
    effective_evidence_mass: float
    shadow_routing: Optional[PublicShadowRoutingProvenance]
    scope: str = PUBLIC_PROVENANCE_SCOPE

    def validate(self) -> None:
        if self.scope != PUBLIC_PROVENANCE_SCOPE:
            raise ValueError("unexpected public provenance scope")
        if self.runtime_path not in {"legacy", "shadow", "promoted_local"}:
            raise ValueError("unknown runtime path")
        if self.decision_mode not in {"abstain", "ordered_practice_priority"}:
            raise ValueError("unknown decision mode")
        if not math.isfinite(self.data_support) or not 0.0 <= self.data_support <= 1.0:
            raise ValueError("data_support must be finite and in [0,1]")
        if (
            not math.isfinite(self.effective_evidence_mass)
            or self.effective_evidence_mass < 0.0
        ):
            raise ValueError("effective_evidence_mass must be finite and non-negative")
        if self.shadow_routing is not None:
            self.shadow_routing.validate()


def _summarize_shadow_routing(
    shadow_routing: ShadowRoutingDecision,
) -> PublicShadowRoutingProvenance:
    selection = shadow_routing.selection
    if selection.enforcement_mode != "shadow":
        raise ValueError("support-aware backoff must remain shadow-only")

    divergence = shadow_routing.divergence
    if divergence is not None and divergence.enforcement_mode != "shadow":
        raise ValueError("context divergence guard must remain shadow-only")

    summary = PublicShadowRoutingProvenance(
        selected_level=selection.selected_level,
        backoff_distance=selection.backoff_distance,
        selection_reason=selection.reason,
        data_support=selection.data_support,
        effective_evidence_mass=selection.effective_evidence_mass,
        divergence_metric=divergence.metric if divergence else None,
        divergence_value=divergence.value if divergence else None,
        divergence_threshold=divergence.threshold if divergence else None,
        divergence_triggered=divergence.triggered if divergence else None,
    )
    summary.validate()
    return summary


def build_public_provenance(
    decision: DecisionEnvelope,
    runtime_path: str,
    shadow_routing: ShadowRoutingDecision | None = None,
) -> PublicDecisionProvenance:
    """Build a non-identifying provenance summary for one runtime decision."""

    summary = PublicDecisionProvenance(
        runtime_path=runtime_path,
        decision_mode=decision.mode,
        decision_reason=decision.reason,
        data_support=decision.data_support,
        effective_evidence_mass=decision.effective_evidence_mass,
        shadow_routing=(
            _summarize_shadow_routing(shadow_routing)
            if shadow_routing is not None
            else None
        ),
    )
    summary.validate()
    return summary
