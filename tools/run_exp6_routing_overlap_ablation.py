#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import random
import sys
from pathlib import Path
from typing import Iterable, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from research_core.evaluation import multiclass_brier, multiclass_log_loss, top_label_ece
from research_core.inference import hierarchical_dirichlet_mean
from research_core.models import RoutingLevel
from research_core.routing import route_mixture
from research_core.uncertainty import normalized_entropy

FIXTURE_PATH = ROOT / "examples/paper/experiments/exp6/fixtures.json"
OUT_DIR = ROOT / "examples/paper/experiments/exp6/results"
REPORT_DECIMALS = 10
NORMALIZATION_TOLERANCE = 1e-12
ROUTING_WEIGHT_TOLERANCE = 5e-10
SEED_DIGEST_BYTES = 8


def canonical_float(value: float) -> str:
    return format(float(value), ".12g")


def deterministic_seed(
    protocol_version: str,
    rotation: int,
    n_c: int,
    rho: float,
    kappa_c: float,
    gamma: float,
    replicate: int,
) -> int:
    """Return the prespecified SHA-256 seed.

    Commit B fixes the previously reserved digest-to-integer detail:
    SHA-256 is evaluated over the seven canonical fields in protocol order;
    the first 8 digest bytes are interpreted as an unsigned big-endian integer.
    """
    canonical = "|".join(
        [
            f"protocol_version={protocol_version}",
            f"rotation={int(rotation)}",
            f"n_c={int(n_c)}",
            f"rho={canonical_float(rho)}",
            f"kappa_c={canonical_float(kappa_c)}",
            f"gamma={canonical_float(gamma)}",
            f"replicate={int(replicate)}",
        ]
    )
    digest = hashlib.sha256(canonical.encode("utf-8")).digest()
    return int.from_bytes(digest[:SEED_DIGEST_BYTES], "big", signed=False)


def rotate_left(values: Sequence[float], shift: int) -> list[float]:
    if not values:
        raise ValueError("cannot rotate an empty sequence")
    shift %= len(values)
    return list(values[shift:]) + list(values[:shift])


def distribution_from_values(
    categories: Sequence[str],
    values: Sequence[float],
) -> dict[str, float]:
    if len(categories) != len(values):
        raise ValueError("category/value length mismatch")
    out = {category: float(value) for category, value in zip(categories, values)}
    validate_distribution(out, categories)
    return out


def validate_distribution(
    distribution: Mapping[str, float],
    categories: Sequence[str],
    tolerance: float = NORMALIZATION_TOLERANCE,
) -> None:
    if set(distribution) != set(categories):
        raise ValueError("distribution categories do not match declared categories")
    if any(not math.isfinite(float(distribution[k])) or float(distribution[k]) < 0.0 for k in categories):
        raise ValueError("distribution contains invalid mass")
    if abs(math.fsum(float(distribution[k]) for k in categories) - 1.0) > tolerance:
        raise ValueError("distribution is not normalized")


def blend(
    left: Mapping[str, float],
    right: Mapping[str, float],
    rho: float,
    categories: Sequence[str],
) -> dict[str, float]:
    if not 0.0 <= rho <= 1.0:
        raise ValueError("rho must be in [0,1]")
    out = {
        category: (1.0 - rho) * float(left[category]) + rho * float(right[category])
        for category in categories
    }
    validate_distribution(out, categories)
    return out


def broader_context_distributions(
    truth: Mapping[str, float],
    rho: float,
    categories: Sequence[str],
) -> tuple[dict[str, float], dict[str, float]]:
    truth_values = [float(truth[k]) for k in categories]
    r1 = distribution_from_values(categories, rotate_left(truth_values, 1))
    r2 = distribution_from_values(categories, rotate_left(truth_values, 2))
    return (
        blend(truth, r1, rho, categories),
        blend(truth, r2, rho, categories),
    )


def draw_category(rng: random.Random, probabilities: Sequence[float]) -> int:
    u = rng.random()
    cumulative = 0.0
    for index, probability in enumerate(probabilities):
        cumulative += float(probability)
        if u < cumulative:
            return index
    return len(probabilities) - 1


def sample_company_counts(
    rng: random.Random,
    truth: Mapping[str, float],
    categories: Sequence[str],
    n_c: int,
) -> dict[str, float]:
    if n_c < 0:
        raise ValueError("n_c must be non-negative")
    probabilities = [float(truth[k]) for k in categories]
    counts = {category: 0.0 for category in categories}
    for _ in range(n_c):
        counts[categories[draw_category(rng, probabilities)]] += 1.0
    return counts


def sample_outcomes(
    rng: random.Random,
    truth: Mapping[str, float],
    categories: Sequence[str],
    count: int,
) -> list[int]:
    if count <= 0:
        raise ValueError("held-out count must be positive")
    probabilities = [float(truth[k]) for k in categories]
    return [draw_category(rng, probabilities) for _ in range(count)]


def routing_weights(level_specs: Sequence[Mapping[str, object]], gamma: float) -> dict[str, float]:
    if not 0.0 < gamma <= 1.0:
        raise ValueError("gamma must be in (0,1]")
    raw: dict[str, float] = {}
    for level in level_specs:
        authorization = 1.0 if bool(level["authorized"]) else 0.0
        applicability = 1.0 if bool(level["applicable"]) else 0.0
        value = (
            authorization
            * applicability
            * float(level["coverage"])
            * (gamma ** int(level["backoff_distance"]))
        )
        if value > 0.0:
            raw[str(level["name"])] = value
    normalizer = math.fsum(raw.values())
    if normalizer <= 0.0:
        raise ValueError("routing configuration has no positive mass")
    return {name: value / normalizer for name, value in raw.items()}


def path_distributions(
    categories: Sequence[str],
    l3: Mapping[str, float],
    l5: Mapping[str, float],
    company_counts: Mapping[str, float],
    kappa_c: float,
    gamma: float,
    level_specs: Sequence[Mapping[str, object]],
) -> tuple[dict[str, float], dict[str, float], list[dict]]:
    """Compute the two prespecified paths using public v1.4 functions."""
    path_a = hierarchical_dirichlet_mean(
        l3,
        company_counts,
        categories,
        kappa_c,
    )
    validate_distribution(path_a, categories)

    by_name = {str(level["name"]): level for level in level_specs}
    required = ["L0_full_context", "L3_industry_context", "L5_generic_context"]
    if any(name not in by_name for name in required):
        raise ValueError("routing fixture is missing an L0/L3/L5 level")

    level_distributions = {
        "L0_full_context": path_a,
        "L3_industry_context": dict(l3),
        "L5_generic_context": dict(l5),
    }
    levels = [
        RoutingLevel(
            name=name,
            backoff_distance=int(by_name[name]["backoff_distance"]),
            authorized=bool(by_name[name]["authorized"]),
            applicable=bool(by_name[name]["applicable"]),
            coverage=float(by_name[name]["coverage"]),
            distribution=level_distributions[name],
        )
        for name in required
    ]

    path_b, provenance = route_mixture(levels, categories, gamma)
    if not path_b:
        raise ValueError("routing unexpectedly returned no distribution")
    validate_distribution(path_b, categories)
    return path_a, path_b, provenance


def total_variation(
    left: Mapping[str, float],
    right: Mapping[str, float],
    categories: Sequence[str],
) -> float:
    return 0.5 * math.fsum(abs(float(left[k]) - float(right[k])) for k in categories)


def exact_expected_log_loss(
    prediction: Mapping[str, float],
    truth: Mapping[str, float],
    categories: Sequence[str],
) -> float:
    terms = []
    for category in categories:
        theta = float(truth[category])
        q = float(prediction[category])
        if theta > 0.0 and q <= 0.0:
            return math.inf
        if theta > 0.0:
            terms.append(-theta * math.log(q))
    return math.fsum(terms)


def exact_expected_brier(
    prediction: Mapping[str, float],
    truth: Mapping[str, float],
    categories: Sequence[str],
) -> float:
    sum_q2 = math.fsum(float(prediction[k]) ** 2 for k in categories)
    dot = math.fsum(float(truth[k]) * float(prediction[k]) for k in categories)
    return 1.0 + sum_q2 - 2.0 * dot


def prediction_vector(
    prediction: Mapping[str, float],
    categories: Sequence[str],
) -> list[float]:
    return [float(prediction[k]) for k in categories]


def top_category(
    prediction: Mapping[str, float],
    categories: Sequence[str],
) -> str:
    return sorted(categories, key=lambda category: (-float(prediction[category]), category))[0]


def top_label_accuracy(
    predictions: Sequence[Sequence[float]],
    outcomes: Sequence[int],
) -> float:
    if len(predictions) != len(outcomes) or not predictions:
        raise ValueError("shape mismatch or empty input")
    correct = 0
    for prediction, outcome in zip(predictions, outcomes):
        predicted = max(range(len(prediction)), key=lambda j: prediction[j])
        correct += int(predicted == outcome)
    return correct / len(outcomes)


def mean(values: Sequence[float]) -> float:
    if not values:
        raise ValueError("mean requires values")
    return math.fsum(values) / len(values)


def linear_quantile(values: Sequence[float], probability: float) -> float:
    if not values:
        raise ValueError("quantile requires values")
    if not 0.0 <= probability <= 1.0:
        raise ValueError("probability must be in [0,1]")
    ordered = sorted(float(value) for value in values)
    position = probability * (len(ordered) - 1)
    lower = int(math.floor(position))
    upper = min(lower + 1, len(ordered) - 1)
    fraction = position - lower
    return ordered[lower] * (1.0 - fraction) + ordered[upper] * fraction


def summarize(values: Sequence[float], lower_is_better: bool = False) -> dict[str, float]:
    if not values:
        raise ValueError("summary requires values")
    ordered = [float(value) for value in values]
    result = {
        "mean": mean(ordered),
        "median": linear_quantile(ordered, 0.5),
        "p05": linear_quantile(ordered, 0.05),
        "p95": linear_quantile(ordered, 0.95),
    }
    if lower_is_better:
        result["proportion_routing_improves"] = mean(
            [1.0 if value < 0.0 else 0.0 for value in ordered]
        )
    return result


def canonicalize(value, decimals: int = REPORT_DECIMALS):
    if isinstance(value, dict):
        return {key: canonicalize(item, decimals) for key, item in value.items()}
    if isinstance(value, list):
        return [canonicalize(item, decimals) for item in value]
    if isinstance(value, float):
        return round(value, decimals)
    return value


def _assert_exact_list(actual: Sequence[object], expected: Sequence[object], label: str) -> None:
    if list(actual) != list(expected):
        raise ValueError(f"{label} does not match the frozen protocol")


def validate_fixture(raw: dict) -> None:
    required = {
        "experiment_id",
        "protocol_version",
        "frozen_base",
        "categories",
        "company_truth",
        "broader_context",
        "company_training",
        "shrinkage",
        "routing",
        "isolation",
        "replication",
        "seed_contract",
        "metrics",
        "aggregate_reporting",
        "execution_pass",
        "claim_boundary",
        "planned_later_artifacts",
    }
    missing = sorted(required - set(raw))
    if missing:
        raise ValueError(f"fixture missing keys: {missing}")

    if raw["experiment_id"] != "exp6":
        raise ValueError("unexpected experiment_id")
    if raw["protocol_version"] != "0.1.0-pre-specified":
        raise ValueError("unexpected protocol_version")
    if raw["frozen_base"]["tag"] != "v0.10.0-paper-v1.4":
        raise ValueError("unexpected frozen base tag")
    if raw["frozen_base"]["commit"] != "a0d89f33aaa7303404a9b26cc7bec5a331a6e82f":
        raise ValueError("unexpected frozen base commit")

    categories = list(raw["categories"])
    _assert_exact_list(
        categories,
        ["ownership", "evidence", "tradeoff", "collaboration", "reflection"],
        "categories",
    )
    if len(set(categories)) != 5:
        raise ValueError("categories must contain five unique entries")

    base_truth = [float(value) for value in raw["company_truth"]["base"]]
    if any(value <= 0.0 for value in base_truth):
        raise ValueError("base truth must have strictly positive mass")
    if abs(math.fsum(base_truth) - 1.0) > NORMALIZATION_TOLERANCE:
        raise ValueError("base truth must sum to one")
    _assert_exact_list(raw["company_truth"]["rotations"], [0, 1, 2, 3, 4], "rotations")
    if raw["company_truth"]["rotation_operator"] != "cyclic_left":
        raise ValueError("unexpected rotation operator")

    mismatch = raw["broader_context"]["mismatch_levels"]
    if [item["name"] for item in mismatch] != [
        "high_agreement",
        "moderate_mismatch",
        "strong_mismatch",
    ]:
        raise ValueError("unexpected mismatch regime names")
    if [float(item["rho"]) for item in mismatch] != [0.1, 0.4, 0.8]:
        raise ValueError("unexpected rho values")

    sample_sizes = raw["company_training"]["sample_sizes"]
    if [item["name"] for item in sample_sizes] != ["sparse", "intermediate", "dense"]:
        raise ValueError("unexpected sample-size regime names")
    if [int(item["n"]) for item in sample_sizes] != [2, 10, 50]:
        raise ValueError("unexpected company sample sizes")
    defaults = raw["company_training"]["evidence_record_defaults"]
    if defaults != {"authorized": True, "quality": 1.0, "age_days": 0.0}:
        raise ValueError("evidence defaults do not isolate routing/shrinkage")

    if [float(value) for value in raw["shrinkage"]["kappa_company"]] != [2.0, 6.0, 20.0]:
        raise ValueError("unexpected kappa_company values")
    if raw["shrinkage"]["parent_level"] != "L3":
        raise ValueError("company shrinkage parent must be L3")

    levels = raw["routing"]["levels"]
    if [level["name"] for level in levels] != [
        "L0_full_context",
        "L3_industry_context",
        "L5_generic_context",
    ]:
        raise ValueError("unexpected routing levels")
    if [int(level["backoff_distance"]) for level in levels] != [0, 3, 5]:
        raise ValueError("unexpected routing distances")
    if [float(level["coverage"]) for level in levels] != [0.78, 0.92, 1.0]:
        raise ValueError("unexpected routing coverage fixtures")
    if any(not level["authorized"] or not level["applicable"] for level in levels):
        raise ValueError("all routing levels must be authorized and applicable")
    if [float(value) for value in raw["routing"]["gamma"]] != [0.4, 0.7, 0.9]:
        raise ValueError("unexpected gamma values")

    for gamma in raw["routing"]["gamma"]:
        calculated = routing_weights(levels, float(gamma))
        expected = raw["routing"]["expected_weights"][canonical_float(float(gamma))]
        for name, expected_value in expected.items():
            if abs(calculated[name] - float(expected_value)) > ROUTING_WEIGHT_TOLERANCE:
                raise ValueError(f"routing-weight fixture mismatch for gamma={gamma} {name}")

    isolation = raw["isolation"]
    expected_isolation = {
        "all_categories_permitted": True,
        "compatibility_masking": False,
        "runtime_data_support_gate": False,
        "runtime_abstention_gate": False,
        "all_routing_components_positive_permitted_mass": True,
    }
    if isolation != expected_isolation:
        raise ValueError("isolation flags differ from the frozen protocol")

    replication = raw["replication"]
    if int(replication["training_replicates_per_rotation_condition"]) != 100:
        raise ValueError("unexpected training replicate count")
    if int(replication["heldout_observations_per_training_replicate"]) != 200:
        raise ValueError("unexpected held-out count")
    if int(replication["primary_factorial_conditions"]) != 81:
        raise ValueError("unexpected factorial condition count")
    if int(replication["truth_rotations"]) != 5:
        raise ValueError("unexpected truth rotation count")
    if int(replication["total_paired_training_realizations"]) != 40500:
        raise ValueError("unexpected paired realization count")
    if int(replication["total_heldout_observations"]) != 8100000:
        raise ValueError("unexpected total held-out observation count")

    seed_contract = raw["seed_contract"]
    if seed_contract["algorithm"] != "sha256" or not seed_contract["python_hash_forbidden"]:
        raise ValueError("unexpected seed contract")
    _assert_exact_list(
        seed_contract["canonical_fields"],
        ["protocol_version", "rotation", "n_c", "rho", "kappa_c", "gamma", "replicate"],
        "seed fields",
    )

    ece = raw["metrics"]["top_label_ece"]
    if int(ece["bins"]) != 10 or ece["binning"] != "equal_width":
        raise ValueError("top-label ECE configuration differs from protocol")

    if raw["execution_pass"]["routing_performance_direction_required"] is not False:
        raise ValueError("routing performance direction must not be a PASS criterion")


def truth_distribution(raw: dict, rotation: int) -> dict[str, float]:
    categories = list(raw["categories"])
    rotated = rotate_left([float(value) for value in raw["company_truth"]["base"]], rotation)
    return distribution_from_values(categories, rotated)


def condition_key(n_c: int, rho: float, kappa_c: float, gamma: float) -> str:
    return (
        f"n{int(n_c)}"
        f"_rho{canonical_float(rho)}"
        f"_kappa{canonical_float(kappa_c)}"
        f"_gamma{canonical_float(gamma)}"
    )


def run_experiment(raw: dict) -> tuple[dict, list[dict], list[dict], list[str]]:
    validate_fixture(raw)
    categories = list(raw["categories"])
    protocol_version = str(raw["protocol_version"])
    levels = list(raw["routing"]["levels"])
    replicates = int(raw["replication"]["training_replicates_per_rotation_condition"])
    heldout_n = int(raw["replication"]["heldout_observations_per_training_replicate"])

    paired_rows: list[dict] = []
    condition_rows: list[dict] = []
    result_conditions: list[dict] = []
    failures: list[str] = []

    for sample_size in raw["company_training"]["sample_sizes"]:
        n_c = int(sample_size["n"])
        sample_name = str(sample_size["name"])
        for mismatch in raw["broader_context"]["mismatch_levels"]:
            rho = float(mismatch["rho"])
            mismatch_name = str(mismatch["name"])
            for kappa_c in [float(value) for value in raw["shrinkage"]["kappa_company"]]:
                for gamma in [float(value) for value in raw["routing"]["gamma"]]:
                    key = condition_key(n_c, rho, kappa_c, gamma)
                    delta_ll_values: list[float] = []
                    delta_bs_values: list[float] = []
                    delta_tv_values: list[float] = []
                    routing_shift_values: list[float] = []
                    entropy_a_values: list[float] = []
                    entropy_b_values: list[float] = []
                    top_retained_values: list[float] = []

                    pooled_predictions_a: list[list[float]] = []
                    pooled_predictions_b: list[list[float]] = []
                    pooled_outcomes: list[int] = []
                    heldout_brier_a: list[float] = []
                    heldout_brier_b: list[float] = []
                    heldout_logloss_a: list[float] = []
                    heldout_logloss_b: list[float] = []

                    condition_tv_l3: list[float] = []
                    condition_tv_l5: list[float] = []
                    routing_weight_reference = routing_weights(levels, gamma)

                    for rotation in raw["company_truth"]["rotations"]:
                        rotation = int(rotation)
                        truth = truth_distribution(raw, rotation)
                        l3, l5 = broader_context_distributions(truth, rho, categories)
                        tv_l3 = total_variation(l3, truth, categories)
                        tv_l5 = total_variation(l5, truth, categories)
                        condition_tv_l3.append(tv_l3)
                        condition_tv_l5.append(tv_l5)

                        for replicate in range(replicates):
                            seed = deterministic_seed(
                                protocol_version,
                                rotation,
                                n_c,
                                rho,
                                kappa_c,
                                gamma,
                                replicate,
                            )
                            rng = random.Random(seed)
                            company_counts = sample_company_counts(rng, truth, categories, n_c)

                            path_a, path_b, provenance = path_distributions(
                                categories,
                                l3,
                                l5,
                                company_counts,
                                kappa_c,
                                gamma,
                                levels,
                            )

                            ll_a = exact_expected_log_loss(path_a, truth, categories)
                            ll_b = exact_expected_log_loss(path_b, truth, categories)
                            bs_a = exact_expected_brier(path_a, truth, categories)
                            bs_b = exact_expected_brier(path_b, truth, categories)
                            tv_a = total_variation(path_a, truth, categories)
                            tv_b = total_variation(path_b, truth, categories)
                            routing_shift = total_variation(path_b, path_a, categories)
                            entropy_a = normalized_entropy(path_a, len(categories))
                            entropy_b = normalized_entropy(path_b, len(categories))
                            top_a = top_category(path_a, categories)
                            top_b = top_category(path_b, categories)
                            top_retained = top_a == top_b

                            metrics = [
                                ll_a,
                                ll_b,
                                bs_a,
                                bs_b,
                                tv_a,
                                tv_b,
                                routing_shift,
                                entropy_a,
                                entropy_b,
                            ]
                            if any(not math.isfinite(value) for value in metrics):
                                failures.append(f"{key} rotation={rotation} replicate={replicate}: non-finite metric")

                            delta_ll = ll_b - ll_a
                            delta_bs = bs_b - bs_a
                            delta_tv = tv_b - tv_a
                            delta_ll_values.append(delta_ll)
                            delta_bs_values.append(delta_bs)
                            delta_tv_values.append(delta_tv)
                            routing_shift_values.append(routing_shift)
                            entropy_a_values.append(entropy_a)
                            entropy_b_values.append(entropy_b)
                            top_retained_values.append(1.0 if top_retained else 0.0)

                            outcomes = sample_outcomes(rng, truth, categories, heldout_n)
                            vector_a = prediction_vector(path_a, categories)
                            vector_b = prediction_vector(path_b, categories)
                            predictions_a = [vector_a] * heldout_n
                            predictions_b = [vector_b] * heldout_n

                            brier_a = multiclass_brier(predictions_a, outcomes)
                            brier_b = multiclass_brier(predictions_b, outcomes)
                            logloss_a = multiclass_log_loss(predictions_a, outcomes)
                            logloss_b = multiclass_log_loss(predictions_b, outcomes)
                            if any(
                                not math.isfinite(value)
                                for value in [brier_a, brier_b, logloss_a, logloss_b]
                            ):
                                failures.append(
                                    f"{key} rotation={rotation} replicate={replicate}: "
                                    "non-finite held-out metric"
                                )
                            heldout_brier_a.append(brier_a)
                            heldout_brier_b.append(brier_b)
                            heldout_logloss_a.append(logloss_a)
                            heldout_logloss_b.append(logloss_b)

                            pooled_predictions_a.extend(predictions_a)
                            pooled_predictions_b.extend(predictions_b)
                            pooled_outcomes.extend(outcomes)

                            paired_rows.append(
                                {
                                    "condition": key,
                                    "sample_regime": sample_name,
                                    "mismatch_regime": mismatch_name,
                                    "n_c": n_c,
                                    "rho": rho,
                                    "kappa_c": kappa_c,
                                    "gamma": gamma,
                                    "rotation": rotation,
                                    "replicate": replicate,
                                    "seed": seed,
                                    "delta_exact_log_loss": delta_ll,
                                    "delta_exact_brier": delta_bs,
                                    "delta_tv_to_truth": delta_tv,
                                    "tv_routed_vs_l0": routing_shift,
                                    "exact_log_loss_l0": ll_a,
                                    "exact_log_loss_routed": ll_b,
                                    "exact_brier_l0": bs_a,
                                    "exact_brier_routed": bs_b,
                                    "tv_truth_l0": tv_a,
                                    "tv_truth_routed": tv_b,
                                    "entropy_l0": entropy_a,
                                    "entropy_routed": entropy_b,
                                    "top_category_l0": top_a,
                                    "top_category_routed": top_b,
                                    "top_category_retained": top_retained,
                                    "tv_l3_to_truth": tv_l3,
                                    "tv_l5_to_truth": tv_l5,
                                    "heldout_brier_l0": brier_a,
                                    "heldout_brier_routed": brier_b,
                                    "heldout_log_loss_l0": logloss_a,
                                    "heldout_log_loss_routed": logloss_b,
                                    "routing_weights": routing_weight_reference,
                                    "routing_provenance": provenance,
                                }
                            )

                    if not pooled_predictions_a or not pooled_predictions_b or not pooled_outcomes:
                        failures.append(f"{key}: empty held-out pool")
                        continue

                    heldout_summary = {
                        "brier_l0": mean(heldout_brier_a),
                        "brier_routed": mean(heldout_brier_b),
                        "log_loss_l0": mean(heldout_logloss_a),
                        "log_loss_routed": mean(heldout_logloss_b),
                        "top_label_ece_l0": top_label_ece(
                            pooled_predictions_a,
                            pooled_outcomes,
                            bins=10,
                        ),
                        "top_label_ece_routed": top_label_ece(
                            pooled_predictions_b,
                            pooled_outcomes,
                            bins=10,
                        ),
                        "top_label_accuracy_l0": top_label_accuracy(
                            pooled_predictions_a,
                            pooled_outcomes,
                        ),
                        "top_label_accuracy_routed": top_label_accuracy(
                            pooled_predictions_b,
                            pooled_outcomes,
                        ),
                    }
                    if any(not math.isfinite(float(value)) for value in heldout_summary.values()):
                        failures.append(f"{key}: non-finite pooled held-out metric")

                    condition_summary = {
                        "condition": key,
                        "sample_regime": sample_name,
                        "mismatch_regime": mismatch_name,
                        "n_c": n_c,
                        "rho": rho,
                        "kappa_c": kappa_c,
                        "gamma": gamma,
                        "paired_replicates": len(delta_ll_values),
                        "heldout_observations": len(pooled_outcomes),
                        "routing_weights": routing_weight_reference,
                        "tv_l3_to_truth": mean(condition_tv_l3),
                        "tv_l5_to_truth": mean(condition_tv_l5),
                        "delta_exact_log_loss": summarize(delta_ll_values, lower_is_better=True),
                        "delta_exact_brier": summarize(delta_bs_values, lower_is_better=True),
                        "delta_tv_to_truth": summarize(delta_tv_values, lower_is_better=True),
                        "tv_routed_vs_l0": summarize(routing_shift_values, lower_is_better=False),
                        "entropy_l0": summarize(entropy_a_values, lower_is_better=False),
                        "entropy_routed": summarize(entropy_b_values, lower_is_better=False),
                        "top_category_retention_rate": mean(top_retained_values),
                        "heldout": heldout_summary,
                    }
                    result_conditions.append(condition_summary)
                    condition_rows.append(flatten_condition(condition_summary))

    expected_conditions = int(raw["replication"]["primary_factorial_conditions"])
    expected_pairs = int(raw["replication"]["total_paired_training_realizations"])
    expected_heldout = int(raw["replication"]["total_heldout_observations"])
    observed_heldout = sum(int(row["heldout_observations"]) for row in result_conditions)

    if len(result_conditions) != expected_conditions:
        failures.append(
            f"expected {expected_conditions} conditions, observed {len(result_conditions)}"
        )
    if len(paired_rows) != expected_pairs:
        failures.append(f"expected {expected_pairs} paired rows, observed {len(paired_rows)}")
    if observed_heldout != expected_heldout:
        failures.append(f"expected {expected_heldout} held-out observations, observed {observed_heldout}")

    result = {
        "experiment_id": "exp6",
        "protocol_version": protocol_version,
        "frozen_base": raw["frozen_base"],
        "comparison": {
            "path_a": "hierarchically_shrunken_L0_only",
            "path_b": "same_L0_plus_frozen_v1.4_L3_L5_routing",
        },
        "seed_contract": {
            "algorithm": "sha256",
            "canonical_fields": raw["seed_contract"]["canonical_fields"],
            "canonical_float_format": ".12g",
            "digest_slice": "first_8_bytes",
            "integer_encoding": "unsigned_big_endian",
        },
        "report_decimal_places": REPORT_DECIMALS,
        "ece": {
            "bins": 10,
            "binning": "equal_width",
            "role": "secondary_diagnostic_not_proper_scoring_rule",
        },
        "conditions": result_conditions,
        "execution_scope": (
            "PASS concerns protocol execution and reproducibility only; "
            "routing is not required to outperform L0-only."
        ),
        "claim_boundary": raw["claim_boundary"],
        "failures": failures,
        "passed": not failures,
    }
    return result, condition_rows, paired_rows, failures


def flatten_condition(condition: Mapping[str, object]) -> dict:
    delta_ll = condition["delta_exact_log_loss"]
    delta_bs = condition["delta_exact_brier"]
    delta_tv = condition["delta_tv_to_truth"]
    shift = condition["tv_routed_vs_l0"]
    heldout = condition["heldout"]
    return {
        "condition": condition["condition"],
        "sample_regime": condition["sample_regime"],
        "mismatch_regime": condition["mismatch_regime"],
        "n_c": condition["n_c"],
        "rho": condition["rho"],
        "kappa_c": condition["kappa_c"],
        "gamma": condition["gamma"],
        "paired_replicates": condition["paired_replicates"],
        "heldout_observations": condition["heldout_observations"],
        "routing_weights": condition["routing_weights"],
        "tv_l3_to_truth": condition["tv_l3_to_truth"],
        "tv_l5_to_truth": condition["tv_l5_to_truth"],
        "delta_ll_mean": delta_ll["mean"],
        "delta_ll_median": delta_ll["median"],
        "delta_ll_p05": delta_ll["p05"],
        "delta_ll_p95": delta_ll["p95"],
        "delta_ll_routing_improves": delta_ll["proportion_routing_improves"],
        "delta_brier_mean": delta_bs["mean"],
        "delta_brier_median": delta_bs["median"],
        "delta_brier_p05": delta_bs["p05"],
        "delta_brier_p95": delta_bs["p95"],
        "delta_brier_routing_improves": delta_bs["proportion_routing_improves"],
        "delta_tv_mean": delta_tv["mean"],
        "delta_tv_median": delta_tv["median"],
        "delta_tv_p05": delta_tv["p05"],
        "delta_tv_p95": delta_tv["p95"],
        "delta_tv_routing_improves": delta_tv["proportion_routing_improves"],
        "routing_shift_mean": shift["mean"],
        "routing_shift_median": shift["median"],
        "routing_shift_p05": shift["p05"],
        "routing_shift_p95": shift["p95"],
        "entropy_l0_mean": condition["entropy_l0"]["mean"],
        "entropy_routed_mean": condition["entropy_routed"]["mean"],
        "top_category_retention_rate": condition["top_category_retention_rate"],
        "heldout_brier_l0": heldout["brier_l0"],
        "heldout_brier_routed": heldout["brier_routed"],
        "heldout_log_loss_l0": heldout["log_loss_l0"],
        "heldout_log_loss_routed": heldout["log_loss_routed"],
        "heldout_top_label_ece_l0": heldout["top_label_ece_l0"],
        "heldout_top_label_ece_routed": heldout["top_label_ece_routed"],
        "heldout_top_label_accuracy_l0": heldout["top_label_accuracy_l0"],
        "heldout_top_label_accuracy_routed": heldout["top_label_accuracy_routed"],
    }


def write_csv(path: Path, rows: Sequence[Mapping[str, object]]) -> None:
    if not rows:
        raise ValueError("cannot write empty CSV")
    fieldnames = list(rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            cooked = {}
            for key in fieldnames:
                value = row.get(key, "")
                if isinstance(value, (dict, list)):
                    value = json.dumps(
                        canonicalize(value),
                        sort_keys=True,
                        separators=(",", ":"),
                    )
                elif isinstance(value, float):
                    value = round(value, REPORT_DECIMALS)
                cooked[key] = value
            writer.writerow(cooked)


def write_results(result: dict, condition_rows: list[dict], paired_rows: list[dict]) -> list[Path]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    paths = [
        OUT_DIR / "exp6_results.json",
        OUT_DIR / "exp6_condition_matrix.csv",
        OUT_DIR / "exp6_paired_deltas.csv",
    ]
    paths[0].write_text(
        json.dumps(canonicalize(result), sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    write_csv(paths[1], canonicalize(condition_rows))
    write_csv(paths[2], canonicalize(paired_rows))
    return paths


def validate_only(raw: dict) -> None:
    validate_fixture(raw)

    categories = list(raw["categories"])
    truth = truth_distribution(raw, 0)
    l3, l5 = broader_context_distributions(truth, 0.4, categories)
    company_counts = {category: 0.0 for category in categories}
    company_counts[categories[0]] = 2.0
    path_a, path_b, _ = path_distributions(
        categories,
        l3,
        l5,
        company_counts,
        6.0,
        0.7,
        raw["routing"]["levels"],
    )
    validate_distribution(path_a, categories)
    validate_distribution(path_b, categories)

    fixed_seed = deterministic_seed(
        raw["protocol_version"],
        0,
        2,
        0.1,
        2.0,
        0.4,
        0,
    )
    if fixed_seed != 2307452519820928386:
        raise ValueError("deterministic seed contract mismatch")


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Experiment 6 routing-shrinkage overlap ablation.")
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Validate the frozen fixture and implementation invariants without generating result artifacts.",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    raw = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))

    if args.validate_only:
        validate_only(raw)
        print("EXPERIMENT_6_FIXTURE_VALIDATION_PASS")
        return 0

    result, condition_rows, paired_rows, failures = run_experiment(raw)
    paths = write_results(result, condition_rows, paired_rows)

    print(f"exp6_failures={len(failures)}")
    print(f"condition_rows={len(condition_rows)}")
    print(f"paired_rows={len(paired_rows)}")
    for path in paths:
        print(f"{path.name}_sha256={hashlib.sha256(path.read_bytes()).hexdigest()}")

    if failures:
        for failure in failures:
            print("FAIL:", failure)
        return 1

    print("EXPERIMENT_6_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
