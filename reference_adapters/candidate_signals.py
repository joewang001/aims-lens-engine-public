from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Tuple


AIMS_DIMENSIONS: Tuple[str, ...] = (
    "structured_thinking",
    "analytical_problem_solving",
    "ownership_execution",
    "impact_results",
    "collaboration_communication",
    "growth_mindset",
)


def _finite_number(value: Any, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field} must be numeric")
    numeric = float(value)
    if not math.isfinite(numeric):
        raise ValueError(f"{field} must be finite")
    return numeric


@dataclass(frozen=True)
class CandidateSignal:
    """One upstream AIMS observation carried into the reference adapter layer.

    The score remains on the existing public 0-10 AIMS scale. Confidence is
    metadata about the observation, not a calibrated hiring probability.
    No runtime routing category is inferred here.
    """

    dimension: str
    score: float
    confidence: float
    authorized: bool
    age_days: float
    evidence_refs: Tuple[str, ...] = ()

    def validate(self) -> None:
        if self.dimension not in AIMS_DIMENSIONS:
            raise ValueError("unknown AIMS dimension")
        score = _finite_number(self.score, "score")
        if not 0.0 <= score <= 10.0:
            raise ValueError("score must be finite and in [0,10]")
        confidence = _finite_number(self.confidence, "confidence")
        if not 0.0 <= confidence <= 1.0:
            raise ValueError("confidence must be finite and in [0,1]")
        if not isinstance(self.authorized, bool):
            raise ValueError("authorized must be boolean")
        age_days = _finite_number(self.age_days, "age_days")
        if age_days < 0.0:
            raise ValueError("age_days must be finite and non-negative")
        if len(set(self.evidence_refs)) != len(self.evidence_refs):
            raise ValueError("evidence_refs must be unique")
        if any(
            not isinstance(ref, str) or not ref.strip()
            for ref in self.evidence_refs
        ):
            raise ValueError("evidence_refs must contain non-empty strings")


@dataclass(frozen=True)
class CandidateSignalPacket:
    """Institution-agnostic packet of candidate-side AIMS observations.

    This packet deliberately stops before mapping AIMS dimensions to the
    manuscript follow-up taxonomy or to runtime evidence categories. Such a
    mapping must be supplied by an explicitly reviewed downstream policy.
    """

    signals: Tuple[CandidateSignal, ...]
    taxonomy: str = "aims-six-dimension-v1"
    decision_binding_status: str = "unbound"

    def validate(self) -> None:
        if self.taxonomy != "aims-six-dimension-v1":
            raise ValueError("unsupported candidate signal taxonomy")
        if self.decision_binding_status != "unbound":
            raise ValueError(
                "candidate signals must remain unbound in this adapter"
            )
        if not self.signals:
            raise ValueError("candidate signal packet must not be empty")

        seen = set()
        for signal in self.signals:
            signal.validate()
            if signal.dimension in seen:
                raise ValueError("candidate signal dimensions must be unique")
            seen.add(signal.dimension)


def _confidence_for_dimension(
    confidence: float | Mapping[str, float],
    dimension: str,
) -> float:
    if isinstance(confidence, Mapping):
        if dimension not in confidence:
            raise ValueError(
                "missing confidence for candidate signal dimension"
            )
        value = _finite_number(
            confidence[dimension],
            f"confidence[{dimension}]",
        )
    else:
        value = _finite_number(confidence, "confidence")
    return value


def adapt_current_aims_scores(
    aims_scores: Mapping[str, float],
    confidence: float | Mapping[str, float],
    authorized_dimensions: Iterable[str],
    evidence_refs_by_dimension: Mapping[str, Iterable[str]] | None = None,
) -> CandidateSignalPacket:
    """Normalize current-turn AIMS scores into an unbound signal packet.

    Authorization must be explicit. Current-turn observations are assigned
    age_days=0. This function does not derive practice gaps, weakness scores,
    follow-up categories, or runtime evidence weights from the AIMS scores.
    """

    if not isinstance(aims_scores, Mapping) or not aims_scores:
        raise ValueError("aims_scores must not be empty")
    unknown = set(aims_scores) - set(AIMS_DIMENSIONS)
    if unknown:
        raise ValueError("aims_scores contains an unknown AIMS dimension")

    if isinstance(confidence, Mapping):
        extra_confidence = set(confidence) - set(aims_scores)
        if extra_confidence:
            raise ValueError(
                "confidence contains a dimension without a score"
            )

    if isinstance(authorized_dimensions, str):
        raise ValueError("authorized_dimensions must be an iterable of dimensions")
    try:
        authorized = set(authorized_dimensions)
    except TypeError as exc:
        raise ValueError(
            "authorized_dimensions must be an iterable of dimensions"
        ) from exc
    unknown_authorized = authorized - set(AIMS_DIMENSIONS)
    if unknown_authorized:
        raise ValueError(
            "authorized_dimensions contains an unknown AIMS dimension"
        )
    if authorized - set(aims_scores):
        raise ValueError(
            "authorized_dimensions contains a dimension without a score"
        )

    refs = evidence_refs_by_dimension or {}
    if not isinstance(refs, Mapping):
        raise ValueError("evidence_refs_by_dimension must be a mapping")
    if set(refs) - set(aims_scores):
        raise ValueError("evidence refs contain a dimension without a score")

    signals = []
    for dimension in AIMS_DIMENSIONS:
        if dimension not in aims_scores:
            continue
        raw_refs = refs.get(dimension, ())
        if isinstance(raw_refs, str):
            raise ValueError(
                "evidence refs for a dimension must be an iterable of strings"
            )
        try:
            evidence_refs = tuple(raw_refs)
        except TypeError as exc:
            raise ValueError(
                "evidence refs for a dimension must be an iterable of strings"
            ) from exc
        signal = CandidateSignal(
            dimension=dimension,
            score=_finite_number(
                aims_scores[dimension],
                f"aims_scores[{dimension}]",
            ),
            confidence=_confidence_for_dimension(confidence, dimension),
            authorized=dimension in authorized,
            age_days=0.0,
            evidence_refs=evidence_refs,
        )
        signal.validate()
        signals.append(signal)

    packet = CandidateSignalPacket(signals=tuple(signals))
    packet.validate()
    return packet
