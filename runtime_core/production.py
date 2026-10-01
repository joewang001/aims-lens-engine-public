from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional, Tuple

from .decision import DecisionEnvelope
from .provenance import PublicDecisionProvenance, build_public_provenance
from .shadow_routing import ShadowRoutingDecision


PROMOTION_REQUIRED_GATES: Tuple[str, ...] = (
    "regression_suite_passed",
    "public_safety_scan_passed",
    "external_contract_compatibility_passed",
    "provenance_review_passed",
    "private_production_controls_ready",
    "human_review_calibration_ready",
    "owner_approval_recorded",
)


@dataclass(frozen=True)
class PromotionGateEvidence:
    """Caller-supplied attestations required before promoted-local release.

    The public core cannot verify private production controls or human-review
    calibration. Those gates are therefore explicit attestations, not inferred
    from repository state.
    """

    regression_suite_passed: bool
    public_safety_scan_passed: bool
    external_contract_compatibility_passed: bool
    provenance_review_passed: bool
    private_production_controls_ready: bool
    human_review_calibration_ready: bool
    owner_approval_recorded: bool

    def validate(self) -> None:
        for gate in PROMOTION_REQUIRED_GATES:
            if not isinstance(getattr(self, gate), bool):
                raise ValueError(f"{gate} must be boolean")

    def blocking_gates(self) -> Tuple[str, ...]:
        self.validate()
        return tuple(
            gate for gate in PROMOTION_REQUIRED_GATES if not getattr(self, gate)
        )


@dataclass(frozen=True)
class RuntimeSwitchDecision:
    requested_mode: str
    effective_mode: str
    promoted_live: bool
    blocking_gates: Tuple[str, ...]
    reason: Optional[str]
    shadow_routing_enforcement: str = "shadow"

    def validate(self) -> None:
        valid_modes = {"legacy", "shadow", "promoted_local"}
        if self.requested_mode not in valid_modes:
            raise ValueError("unknown requested runtime mode")
        if self.effective_mode not in valid_modes:
            raise ValueError("unknown effective runtime mode")
        if self.shadow_routing_enforcement != "shadow":
            raise ValueError("PR-C routing policy must remain shadow-only")
        if self.promoted_live != (self.effective_mode == "promoted_local"):
            raise ValueError("promoted_live disagrees with effective_mode")
        if self.promoted_live and self.blocking_gates:
            raise ValueError("live promotion cannot retain blocking gates")


@dataclass(frozen=True)
class DecisionExplanation:
    code: str
    summary: str
    disclaimer: str


@dataclass(frozen=True)
class ProductionDecisionEnvelope:
    """Internal production-candidate envelope; not a public API response schema."""

    release_status: str
    decision: DecisionEnvelope
    provenance: PublicDecisionProvenance
    explanation: DecisionExplanation
    runtime_switch: RuntimeSwitchDecision

    def validate(self) -> None:
        _validate_decision_envelope(self.decision)
        if self.release_status not in {"live_promoted", "shadow_only", "not_released"}:
            raise ValueError("unknown release_status")
        expected_status = {
            "promoted_local": "live_promoted",
            "shadow": "shadow_only",
            "legacy": "not_released",
        }[self.runtime_switch.effective_mode]
        if self.release_status != expected_status:
            raise ValueError("release_status disagrees with runtime switch")
        self.runtime_switch.validate()
        self.provenance.validate()
        if self.provenance.runtime_path != self.runtime_switch.effective_mode:
            raise ValueError("provenance runtime_path disagrees with runtime switch")
        if not self.explanation.code or not self.explanation.summary:
            raise ValueError("decision explanation must be non-empty")
        if not self.explanation.disclaimer:
            raise ValueError("decision explanation disclaimer must be non-empty")
        if self.provenance.decision_mode != self.decision.mode:
            raise ValueError("provenance decision_mode disagrees with decision")
        if self.provenance.decision_reason != self.decision.reason:
            raise ValueError("provenance decision_reason disagrees with decision")
        if self.provenance.data_support != self.decision.data_support:
            raise ValueError("provenance data_support disagrees with decision")
        if (
            self.provenance.effective_evidence_mass
            != self.decision.effective_evidence_mass
        ):
            raise ValueError(
                "provenance effective_evidence_mass disagrees with decision"
            )


def _validate_decision_envelope(decision: DecisionEnvelope) -> None:
    if decision.mode not in {"abstain", "ordered_practice_priority"}:
        raise ValueError("unknown decision mode")
    if (
        not math.isfinite(decision.data_support)
        or not 0.0 <= decision.data_support <= 1.0
    ):
        raise ValueError("decision data_support must be finite and in [0,1]")
    if (
        not math.isfinite(decision.effective_evidence_mass)
        or decision.effective_evidence_mass < 0.0
    ):
        raise ValueError(
            "decision effective_evidence_mass must be finite and non-negative"
        )

    if decision.mode == "abstain":
        if not decision.reason:
            raise ValueError("abstention must include a reason")
        if decision.top_category is not None:
            raise ValueError("abstention must not include top_category")
        if decision.priority_order:
            raise ValueError("abstention must not include priority_order")
        if decision.diagnostic_distribution:
            raise ValueError(
                "abstention must not release diagnostic_distribution"
            )
        return

    if decision.reason is not None:
        raise ValueError("ordered practice priority must not include a reason")
    if not decision.priority_order:
        raise ValueError("ordered practice priority must not be empty")
    if len(set(decision.priority_order)) != len(decision.priority_order):
        raise ValueError("priority_order must be unique")
    if decision.top_category != decision.priority_order[0]:
        raise ValueError("top_category must equal first priority_order item")
    if set(decision.priority_order) != set(decision.diagnostic_distribution):
        raise ValueError(
            "priority_order and diagnostic_distribution keys must agree"
        )
    values = [
        float(value) for value in decision.diagnostic_distribution.values()
    ]
    if any(not math.isfinite(value) or value < 0.0 for value in values):
        raise ValueError(
            "diagnostic_distribution values must be finite and non-negative"
        )
    if abs(sum(values) - 1.0) > 1e-9:
        raise ValueError("diagnostic_distribution must sum to 1")


def resolve_runtime_mode(
    requested_mode: str,
    gates: PromotionGateEvidence | None = None,
) -> RuntimeSwitchDecision:
    """Resolve legacy/shadow/promoted-local mode with fail-closed promotion."""

    if requested_mode not in {"legacy", "shadow", "promoted_local"}:
        raise ValueError("requested_mode must be legacy, shadow, or promoted_local")

    if requested_mode == "legacy":
        result = RuntimeSwitchDecision(
            requested_mode=requested_mode,
            effective_mode="legacy",
            promoted_live=False,
            blocking_gates=(),
            reason=None,
        )
    elif requested_mode == "shadow":
        result = RuntimeSwitchDecision(
            requested_mode=requested_mode,
            effective_mode="shadow",
            promoted_live=False,
            blocking_gates=(),
            reason=None,
        )
    else:
        if gates is None:
            blockers = PROMOTION_REQUIRED_GATES
        elif not isinstance(gates, PromotionGateEvidence):
            raise ValueError("gates must be PromotionGateEvidence")
        else:
            blockers = gates.blocking_gates()

        if blockers:
            result = RuntimeSwitchDecision(
                requested_mode=requested_mode,
                effective_mode="shadow",
                promoted_live=False,
                blocking_gates=tuple(blockers),
                reason="promotion_gates_not_satisfied",
            )
        else:
            result = RuntimeSwitchDecision(
                requested_mode=requested_mode,
                effective_mode="promoted_local",
                promoted_live=True,
                blocking_gates=(),
                reason=None,
            )

    result.validate()
    return result


def explain_decision(
    decision: DecisionEnvelope,
    runtime_switch: RuntimeSwitchDecision,
) -> DecisionExplanation:
    """Return deterministic, non-employer-predictive explanation text."""

    runtime_switch.validate()
    disclaimer = (
        "This output prioritizes interview practice. It is not a prediction of "
        "a specific employer's interview process or hiring decision."
    )

    if runtime_switch.effective_mode == "legacy":
        return DecisionExplanation(
            code="promoted_output_not_released",
            summary="The promoted local decision was not released; the existing runtime path remains live.",
            disclaimer=disclaimer,
        )
    if runtime_switch.effective_mode == "shadow":
        return DecisionExplanation(
            code="promoted_output_shadow_only",
            summary="The promoted local decision was evaluated for comparison only and remains shadow-only.",
            disclaimer=disclaimer,
        )
    if decision.mode == "abstain":
        if decision.reason == "all_categories_masked":
            summary = (
                "The promoted local decision abstained because no permitted "
                "practice category retained valid probability mass."
            )
        elif decision.reason == "insufficient_data_support":
            summary = (
                "The promoted local decision abstained because permitted "
                "evidence support was below the caller-declared release threshold."
            )
        else:
            summary = "The promoted local decision abstained under a fail-closed condition."
        return DecisionExplanation(
            code=f"abstain:{decision.reason or 'unspecified'}",
            summary=summary,
            disclaimer=disclaimer,
        )

    return DecisionExplanation(
        code="ordered_practice_priority",
        summary=(
            "The promoted local path released an ordered practice priority from "
            "the compatibility-permitted local decision after support checks."
        ),
        disclaimer=disclaimer,
    )


def build_production_envelope(
    decision: DecisionEnvelope,
    runtime_switch: RuntimeSwitchDecision,
    shadow_routing: ShadowRoutingDecision | None = None,
) -> ProductionDecisionEnvelope:
    """Assemble the gated production-candidate envelope.

    Passing a PR-C shadow observation adds only public-safe provenance. It never
    changes the local decision or the runtime switch outcome.
    """

    runtime_switch.validate()
    provenance = build_public_provenance(
        decision=decision,
        runtime_path=runtime_switch.effective_mode,
        shadow_routing=shadow_routing,
    )
    release_status = {
        "promoted_local": "live_promoted",
        "shadow": "shadow_only",
        "legacy": "not_released",
    }[runtime_switch.effective_mode]
    envelope = ProductionDecisionEnvelope(
        release_status=release_status,
        decision=decision,
        provenance=provenance,
        explanation=explain_decision(decision, runtime_switch),
        runtime_switch=runtime_switch,
    )
    envelope.validate()
    return envelope
