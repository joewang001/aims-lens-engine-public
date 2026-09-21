#!/usr/bin/env python3
from __future__ import annotations

import copy
import csv
import hashlib
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from research_core.active_learning import (
    expected_information_gain,
    predictive_entropy_reduction,
)
from research_core.compatibility import masked_and_renormalized
from research_core.evaluation import (
    multiclass_brier,
    multiclass_log_loss,
    top_label_ece,
    vector_ece,
)
from research_core.evidence import weighted_counts
from research_core.inference import hierarchical_dirichlet_mean
from research_core.models import EvidenceRecord, PracticeRequest, RoutingLevel
from research_core.routing import route_mixture
from research_core.service import prioritize_followups
from research_core.uncertainty import data_support, normalized_entropy, should_abstain

FIXTURE_PATH = ROOT / "examples/paper/experiments/exp4/fixtures.json"
BASELINE_PATH = ROOT / "examples/paper/followup_priority_request.json"
OUT_DIR = ROOT / "examples/paper/experiments/exp4/results"


def legacy_normalize_v13(values, categories):
    """Frozen v1.3 normalization semantics relevant to F4."""
    cats = list(categories)
    total = sum(max(0.0, float(values.get(k, 0.0))) for k in cats)
    if total <= 0:
        if not cats:
            return {}
        return {k: 1.0 / len(cats) for k in cats}
    return {
        k: max(0.0, float(values.get(k, 0.0))) / total
        for k in cats
    }


def legacy_route_mixture_v13(levels, categories, gamma):
    """Mirror frozen v1.3 Eq.8–9 routing behavior for the adversarial fixture."""
    if not 0 < gamma <= 1:
        raise ValueError("gamma must be in (0,1]")

    cats = list(categories)
    components = []
    for level in levels:
        level.validate()
        authorization = 1.0 if level.authorized else 0.0
        applicability = 1.0 if level.applicable else 0.0
        raw = (
            authorization
            * applicability
            * level.coverage
            * (gamma ** level.backoff_distance)
        )
        if raw > 0:
            components.append(
                (level, raw, legacy_normalize_v13(level.distribution, cats))
            )

    if not components:
        return {}, []

    normalizer = sum(weight for _, weight, _ in components)
    mixture = {category: 0.0 for category in cats}
    provenance = []

    for level, raw, distribution in components:
        omega = raw / normalizer
        for category in cats:
            mixture[category] += omega * distribution[category]
        provenance.append(
            {
                "level": level.name,
                "backoff_distance": level.backoff_distance,
                "authorization": level.authorized,
                "applicability": level.applicable,
                "coverage": round(level.coverage, 6),
                "routing_weight": round(omega, 6),
            }
        )

    return legacy_normalize_v13(mixture, cats), provenance


def legacy_prioritize_followups_v13(request):
    """Mirror the frozen v1.3 service behavior needed for F3/F4."""
    request.validate()

    counts, effective_mass = weighted_counts(
        request.evidence,
        request.categories,
        request.temporal_decay_rate_per_day,
    )
    local = hierarchical_dirichlet_mean(
        request.parent_distribution,
        counts,
        request.categories,
        request.kappa_company,
    )
    local_masked = masked_and_renormalized(
        local,
        request.categories,
        request.permitted_categories,
    )

    if not local_masked:
        return {
            "mode": "abstain",
            "reason": "all_categories_masked",
        }

    routed_levels = list(request.routing_levels)
    l0_index = next(
        i
        for i, level in enumerate(routed_levels)
        if level.backoff_distance == 0
    )
    l0 = routed_levels[l0_index]
    routed_levels[l0_index] = type(l0)(
        l0.name,
        l0.backoff_distance,
        l0.authorized,
        l0.applicable,
        l0.coverage,
        local_masked,
    )

    routed, provenance = legacy_route_mixture_v13(
        routed_levels,
        request.permitted_categories,
        request.routing_gamma,
    )

    if not routed:
        return {
            "mode": "abstain",
            "reason": "no_eligible_routing_level",
        }

    support = data_support(effective_mass, request.support_tau)
    if (
        request.abstention_threshold > 0
        and should_abstain(support, request.abstention_threshold)
    ):
        return {
            "mode": "abstain",
            "reason": "insufficient_data_support",
            "data_support": round(support, 6),
            "effective_evidence_mass": round(effective_mass, 6),
            "routing_provenance": provenance,
        }

    priority = [
        key
        for key, _ in sorted(
            routed.items(),
            key=lambda kv: (-kv[1], kv[0]),
        )
    ]
    return {
        "mode": "ordered_practice_priority",
        "top_category": priority[0],
        "priority_order": priority,
        "diagnostic_distribution": {
            key: round(value, 6)
            for key, value in routed.items()
        },
        "uncertainty_entropy": round(
            normalized_entropy(
                routed,
                len(request.permitted_categories),
            ),
            6,
        ),
        "data_support": round(support, 6),
        "effective_evidence_mass": round(effective_mass, 6),
        "routing_provenance": provenance,
    }


def build_request(raw):
    return PracticeRequest(
        categories=list(raw["categories"]),
        parent_distribution=dict(raw["parent_distribution"]),
        evidence=[EvidenceRecord(**item) for item in raw["evidence"]],
        permitted_categories=list(raw["permitted_categories"]),
        kappa_company=float(raw["kappa_company"]),
        temporal_decay_rate_per_day=float(
            raw["temporal_decay_rate_per_day"]
        ),
        routing_levels=[
            RoutingLevel(**item)
            for item in raw["routing_levels"]
        ],
        routing_gamma=float(raw.get("routing_gamma", 0.7)),
        support_tau=float(raw.get("support_tau", 8.0)),
        abstention_threshold=float(
            raw.get("abstention_threshold", 0.0)
        ),
    )


def canonicalize(obj, decimals):
    if isinstance(obj, dict):
        return {
            key: canonicalize(value, decimals)
            for key, value in obj.items()
        }
    if isinstance(obj, list):
        return [canonicalize(value, decimals) for value in obj]
    if isinstance(obj, float):
        return round(obj, decimals)
    return obj


def near(a, b, tolerance):
    return abs(float(a) - float(b)) <= tolerance


def case_eq15(raw, tolerance, failures):
    alpha = raw["alpha"]
    legacy = predictive_entropy_reduction(alpha)
    current = expected_information_gain(alpha)
    expected_legacy = float(
        raw["expected_legacy_predictive_reduction"]
    )
    expected_current = float(
        raw["expected_parameter_information_gain"]
    )

    checks = {
        "legacy_matches_declared": near(
            legacy, expected_legacy, tolerance
        ),
        "current_matches_declared": near(
            current, expected_current, tolerance
        ),
        "quantities_are_distinct": abs(current - legacy) > 0.1,
    }

    for name, passed in checks.items():
        if not passed:
            failures.append(f"E4-01:{name}")

    return {
        "case_id": "E4-01",
        "finding": "F1_eq15_information_gain",
        "legacy_v13": {
            "semantic": "predictive_category_entropy_reduction",
            "value": legacy,
        },
        "corrected_v14": {
            "semantic": "parameter_posterior_information_gain",
            "value": current,
        },
        "checks": checks,
        "passed": all(checks.values()),
    }


def case_calibration(raw, tolerance, failures):
    predictions = raw["predictions"]
    outcomes = raw["outcomes"]
    bins = int(raw["bins"])

    legacy = vector_ece(predictions, outcomes, bins=bins)
    current = top_label_ece(predictions, outcomes, bins=bins)
    brier = multiclass_brier(predictions, outcomes)
    log_loss = multiclass_log_loss(predictions, outcomes)

    checks = {
        "legacy_cancellation_reproduced": near(
            legacy,
            float(raw["expected_legacy_vector_ece"]),
            tolerance,
        ),
        "current_top_label_ece_matches_declared": near(
            current,
            float(raw["expected_top_label_ece"]),
            tolerance,
        ),
        "brier_positive": brier > 0.0,
        "log_loss_positive": log_loss > 0.0,
    }

    for name, passed in checks.items():
        if not passed:
            failures.append(f"E4-02:{name}")

    return {
        "case_id": "E4-02",
        "finding": "F2_calibration_cancellation",
        "legacy_v13": {
            "metric": "vector_ece",
            "value": legacy,
        },
        "corrected_v14": {
            "metric": "top_label_ece",
            "value": current,
        },
        "complementary_metrics": {
            "multiclass_brier": brier,
            "multiclass_log_loss": log_loss,
        },
        "checks": checks,
        "passed": all(checks.values()),
    }


def corrected_permitted_support(request):
    counts, _ = weighted_counts(
        request.evidence,
        request.categories,
        request.temporal_decay_rate_per_day,
    )
    mass = math.fsum(
        counts.get(category, 0.0)
        for category in request.permitted_categories
    )
    return mass, data_support(mass, request.support_tau)


def legacy_all_category_support(request):
    _, mass = weighted_counts(
        request.evidence,
        request.categories,
        request.temporal_decay_rate_per_day,
    )
    return mass, data_support(mass, request.support_tau)


def case_masked_support(raw, tolerance, failures):
    baseline = json.loads(
        BASELINE_PATH.read_text(encoding="utf-8")
    )

    permitted_category = raw["permitted_record_category"]
    masked_category = raw["masked_record_category"]
    quality = float(raw["quality"])
    age_days = float(raw["age_days"])

    below = copy.deepcopy(baseline)
    below["abstention_threshold"] = float(raw["below_threshold"])
    below["evidence"] = [
        {
            "category": permitted_category,
            "authorized": True,
            "quality": quality,
            "age_days": age_days,
        }
        for _ in range(int(raw["below_threshold_base_records"]))
    ]
    below["evidence"].extend(
        {
            "category": masked_category,
            "authorized": True,
            "quality": quality,
            "age_days": age_days,
        }
        for _ in range(int(raw["below_threshold_masked_records"]))
    )
    below_request = build_request(below)

    legacy_below = legacy_prioritize_followups_v13(below_request)
    current_below = prioritize_followups(below_request)
    legacy_below_mass, legacy_below_support = (
        legacy_all_category_support(below_request)
    )
    current_below_mass, current_below_support = (
        corrected_permitted_support(below_request)
    )

    above_base = copy.deepcopy(baseline)
    above_base_request = build_request(above_base)
    above_attack = copy.deepcopy(above_base)
    above_attack["evidence"].extend(
        {
            "category": masked_category,
            "authorized": True,
            "quality": quality,
            "age_days": age_days,
        }
        for _ in range(int(raw["above_threshold_masked_records"]))
    )
    above_attack_request = build_request(above_attack)

    current_above_base = prioritize_followups(above_base_request)
    current_above_attack = prioritize_followups(above_attack_request)

    corrected_base_mass, corrected_base_support = (
        corrected_permitted_support(above_base_request)
    )
    corrected_attack_mass, corrected_attack_support = (
        corrected_permitted_support(above_attack_request)
    )
    legacy_base_mass, legacy_base_support = (
        legacy_all_category_support(above_base_request)
    )
    legacy_attack_mass, legacy_attack_support = (
        legacy_all_category_support(above_attack_request)
    )

    checks = {
        "below_legacy_releases": (
            legacy_below.get("mode")
            == "ordered_practice_priority"
        ),
        "below_current_abstains": (
            current_below.get("mode") == "abstain"
            and current_below.get("reason")
            == "insufficient_data_support"
        ),
        "below_current_support_below_threshold": (
            current_below_support < float(raw["below_threshold"])
        ),
        "below_legacy_support_above_threshold": (
            legacy_below_support >= float(raw["below_threshold"])
        ),
        "above_corrected_mass_invariant": near(
            corrected_base_mass,
            corrected_attack_mass,
            tolerance,
        ),
        "above_corrected_support_invariant": near(
            corrected_base_support,
            corrected_attack_support,
            tolerance,
        ),
        "above_distribution_invariant": (
            current_above_base.get("diagnostic_distribution")
            == current_above_attack.get("diagnostic_distribution")
        ),
        "above_priority_invariant": (
            current_above_base.get("priority_order")
            == current_above_attack.get("priority_order")
        ),
        "legacy_mass_inflates": (
            legacy_attack_mass > legacy_base_mass
        ),
        "legacy_support_inflates": (
            legacy_attack_support > legacy_base_support
        ),
    }

    for name, passed in checks.items():
        if not passed:
            failures.append(f"E4-03:{name}")

    return {
        "case_id": "E4-03",
        "finding": "F3_masked_evidence_support",
        "below_threshold_attack": {
            "legacy_v13": {
                "mode": legacy_below.get("mode"),
                "effective_evidence_mass": legacy_below_mass,
                "data_support": legacy_below_support,
            },
            "corrected_v14": {
                "mode": current_below.get("mode"),
                "reason": current_below.get("reason"),
                "effective_evidence_mass": current_below_mass,
                "data_support": current_below_support,
            },
            "threshold": float(raw["below_threshold"]),
        },
        "above_threshold_invariance": {
            "corrected_base_mass": corrected_base_mass,
            "corrected_attack_mass": corrected_attack_mass,
            "corrected_base_support": corrected_base_support,
            "corrected_attack_support": corrected_attack_support,
            "legacy_base_mass": legacy_base_mass,
            "legacy_attack_mass": legacy_attack_mass,
            "legacy_base_support": legacy_base_support,
            "legacy_attack_support": legacy_attack_support,
        },
        "checks": checks,
        "passed": all(checks.values()),
    }


def case_zero_mass_routing(raw, failures):
    levels = [
        RoutingLevel(**item)
        for item in raw["mixed_levels"]
    ]
    permitted = list(raw["permitted_categories"])
    gamma = float(raw["gamma"])

    legacy_mix, legacy_provenance = legacy_route_mixture_v13(
        levels,
        permitted,
        gamma,
    )
    current_mix, current_provenance = route_mixture(
        levels,
        permitted,
        gamma,
    )

    baseline = json.loads(
        BASELINE_PATH.read_text(encoding="utf-8")
    )
    baseline["permitted_categories"] = ["ownership"]
    baseline["abstention_threshold"] = 0.0
    baseline["routing_levels"] = [
        {
            "name": "L0_full_context",
            "backoff_distance": 0,
            "authorized": True,
            "applicable": True,
            "coverage": 0.0,
            "distribution": {"ownership": 1.0},
        },
        {
            "name": "L3_industry_context",
            "backoff_distance": 3,
            "authorized": True,
            "applicable": True,
            "coverage": 1.0,
            "distribution": {"collaboration": 1.0},
        },
        {
            "name": "L5_generic_context",
            "backoff_distance": 5,
            "authorized": True,
            "applicable": True,
            "coverage": 1.0,
            "distribution": {"collaboration": 1.0},
        },
    ]
    service_request = build_request(baseline)
    legacy_service = legacy_prioritize_followups_v13(
        service_request
    )
    current_service = prioritize_followups(service_request)

    legacy_l5_weight = next(
        (
            item["routing_weight"]
            for item in legacy_provenance
            if item["level"] == "L5"
        ),
        0.0,
    )

    checks = {
        "legacy_mixed_has_two_components": (
            len(legacy_provenance) == 2
        ),
        "legacy_zero_mass_component_gets_weight": (
            legacy_l5_weight > 0.0
        ),
        "current_mixed_excludes_zero_mass_component": (
            len(current_provenance) == 1
            and current_provenance[0]["level"] == "L0"
        ),
        "current_mixed_is_normalized": near(
            math.fsum(current_mix.values()),
            1.0,
            1e-12,
        ),
        "legacy_all_massless_service_releases": (
            legacy_service.get("mode")
            == "ordered_practice_priority"
        ),
        "current_all_massless_service_abstains": (
            current_service.get("mode") == "abstain"
            and current_service.get("reason")
            == "no_supported_routing_mass"
        ),
    }

    for name, passed in checks.items():
        if not passed:
            failures.append(f"E4-04:{name}")

    return {
        "case_id": "E4-04",
        "finding": "F4_zero_permitted_mass_routing",
        "mixed_component": {
            "legacy_v13": {
                "mixture": legacy_mix,
                "routing_provenance": legacy_provenance,
            },
            "corrected_v14": {
                "mixture": current_mix,
                "routing_provenance": current_provenance,
            },
        },
        "all_massless_service": {
            "legacy_v13": {
                "mode": legacy_service.get("mode"),
                "reason": legacy_service.get("reason"),
            },
            "corrected_v14": {
                "mode": current_service.get("mode"),
                "reason": current_service.get("reason"),
            },
        },
        "checks": checks,
        "passed": all(checks.values()),
    }


def write_csv(path, rows):
    fieldnames = [
        "case_id",
        "finding",
        "legacy_behavior",
        "corrected_behavior",
        "passed",
    ]
    with path.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=fieldnames,
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)


def main():
    raw = json.loads(
        FIXTURE_PATH.read_text(encoding="utf-8")
    )
    tolerance = float(raw["absolute_tolerance"])
    decimals = int(raw["report_decimal_places"])
    failures = []

    cases = [
        case_eq15(raw["eq15"], tolerance, failures),
        case_calibration(
            raw["calibration"],
            tolerance,
            failures,
        ),
        case_masked_support(
            raw["masked_support"],
            tolerance,
            failures,
        ),
        case_zero_mass_routing(
            raw["zero_mass_routing"],
            failures,
        ),
    ]

    summary_rows = [
        {
            "case_id": cases[0]["case_id"],
            "finding": cases[0]["finding"],
            "legacy_behavior": (
                f"predictive_reduction="
                f"{cases[0]['legacy_v13']['value']:.12f}"
            ),
            "corrected_behavior": (
                f"parameter_ig="
                f"{cases[0]['corrected_v14']['value']:.12f}"
            ),
            "passed": cases[0]["passed"],
        },
        {
            "case_id": cases[1]["case_id"],
            "finding": cases[1]["finding"],
            "legacy_behavior": (
                f"vector_ece="
                f"{cases[1]['legacy_v13']['value']:.12f}"
            ),
            "corrected_behavior": (
                f"top_label_ece="
                f"{cases[1]['corrected_v14']['value']:.12f}"
            ),
            "passed": cases[1]["passed"],
        },
        {
            "case_id": cases[2]["case_id"],
            "finding": cases[2]["finding"],
            "legacy_behavior": (
                "below_threshold="
                + cases[2]["below_threshold_attack"]
                ["legacy_v13"]["mode"]
            ),
            "corrected_behavior": (
                "below_threshold="
                + cases[2]["below_threshold_attack"]
                ["corrected_v14"]["mode"]
            ),
            "passed": cases[2]["passed"],
        },
        {
            "case_id": cases[3]["case_id"],
            "finding": cases[3]["finding"],
            "legacy_behavior": (
                "all_massless="
                + cases[3]["all_massless_service"]
                ["legacy_v13"]["mode"]
            ),
            "corrected_behavior": (
                "all_massless="
                + cases[3]["all_massless_service"]
                ["corrected_v14"]["mode"]
            ),
            "passed": cases[3]["passed"],
        },
    ]

    result = {
        "protocol_version": raw["protocol_version"],
        "legacy_reference": raw["legacy_reference"],
        "absolute_tolerance": tolerance,
        "case_count": len(cases),
        "cases": cases,
        "failures": failures,
        "passed": not failures,
        "claim_boundary": (
            "Internal mathematical-implementation alignment only; "
            "no external empirical validity claim."
        ),
    }
    result = canonicalize(result, decimals)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    json_path = OUT_DIR / "exp4_results.json"
    csv_path = OUT_DIR / "exp4_case_matrix.csv"

    json_path.write_text(
        json.dumps(result, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    write_csv(csv_path, summary_rows)

    print(f"exp4_failures={len(failures)}")
    print(f"case_count={len(cases)}")
    print(
        "exp4_results_sha256="
        + hashlib.sha256(json_path.read_bytes()).hexdigest()
    )
    print(
        "exp4_case_matrix_sha256="
        + hashlib.sha256(csv_path.read_bytes()).hexdigest()
    )

    if failures:
        for failure in failures:
            print("FAIL:", failure)
        return 1

    print("EXPERIMENT_4_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
