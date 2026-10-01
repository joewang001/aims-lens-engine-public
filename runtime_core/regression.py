from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Tuple

from .decision import DecisionEnvelope


@dataclass(frozen=True)
class DecisionRegressionResult:
    passed: bool
    mismatches: Tuple[str, ...]


def compare_decision_envelopes(
    expected: DecisionEnvelope,
    actual: DecisionEnvelope,
    tolerance: float = 1e-9,
) -> DecisionRegressionResult:
    """Compare stable decision semantics for regression gating."""

    if not math.isfinite(tolerance) or tolerance < 0.0:
        raise ValueError("tolerance must be finite and non-negative")

    mismatches = []
    for field_name in ("mode", "reason", "top_category", "priority_order"):
        if getattr(expected, field_name) != getattr(actual, field_name):
            mismatches.append(field_name)

    expected_keys = set(expected.diagnostic_distribution)
    actual_keys = set(actual.diagnostic_distribution)
    if expected_keys != actual_keys:
        mismatches.append("diagnostic_distribution.keys")
    else:
        for key in sorted(expected_keys):
            expected_value = float(expected.diagnostic_distribution[key])
            actual_value = float(actual.diagnostic_distribution[key])
            if not math.isfinite(expected_value) or not math.isfinite(actual_value):
                mismatches.append(f"diagnostic_distribution[{key}]")
            elif abs(expected_value - actual_value) > tolerance:
                mismatches.append(f"diagnostic_distribution[{key}]")

    for field_name in ("data_support", "effective_evidence_mass"):
        expected_value = float(getattr(expected, field_name))
        actual_value = float(getattr(actual, field_name))
        if not math.isfinite(expected_value) or not math.isfinite(actual_value):
            mismatches.append(field_name)
        elif abs(expected_value - actual_value) > tolerance:
            mismatches.append(field_name)

    return DecisionRegressionResult(
        passed=not mismatches,
        mismatches=tuple(mismatches),
    )
