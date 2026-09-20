#!/usr/bin/env python3
from __future__ import annotations

import copy
import csv
import hashlib
import json
import math
import random
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from research_core.compatibility import masked_and_renormalized
from research_core.evidence import weighted_counts
from research_core.inference import (
    hierarchical_dirichlet_mean,
    hierarchical_partial_pooling,
    normalize,
    posterior_alpha,
    posterior_mean,
)
from research_core.models import EvidenceRecord, PracticeRequest, RoutingLevel
from research_core.service import prioritize_followups

BASELINE_PATH = ROOT / "examples/paper/followup_priority_request.json"
OUT_DIR = ROOT / "examples/paper/experiments/exp2/results"
MASTER_SEED = 1729
REPLICATES = 200

def canonical_hash(obj) -> str:
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()

def tv(a: dict, b: dict) -> float:
    keys = sorted(set(a) | set(b))
    return 0.5 * sum(abs(float(a.get(k, 0.0)) - float(b.get(k, 0.0))) for k in keys)

def top_key(d: dict) -> str:
    return sorted(d.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]

def strictly_decreasing(xs) -> bool:
    return all(a > b for a, b in zip(xs, xs[1:]))

def strictly_increasing(xs) -> bool:
    return all(a < b for a, b in zip(xs, xs[1:]))

def build_request(raw: dict) -> PracticeRequest:
    return PracticeRequest(
        categories=list(raw["categories"]),
        parent_distribution=dict(raw["parent_distribution"]),
        evidence=[EvidenceRecord(**x) for x in raw["evidence"]],
        permitted_categories=list(raw["permitted_categories"]),
        kappa_company=float(raw["kappa_company"]),
        temporal_decay_rate_per_day=float(raw["temporal_decay_rate_per_day"]),
        routing_levels=[RoutingLevel(**x) for x in raw["routing_levels"]],
        routing_gamma=float(raw.get("routing_gamma", 0.7)),
        support_tau=float(raw.get("support_tau", 8.0)),
        abstention_threshold=float(raw.get("abstention_threshold", 0.0)),
    )

def sample_multinomial(rng: random.Random, distribution: dict, n: int) -> dict:
    keys = list(distribution)
    cumulative = []
    total = 0.0
    for key in keys:
        total += float(distribution[key])
        cumulative.append(total)
    if abs(total - 1.0) > 1e-12:
        raise ValueError("synthetic generating distribution must sum to 1")
    counts = {key: 0 for key in keys}
    for _ in range(n):
        x = rng.random()
        for key, boundary in zip(keys, cumulative):
            if x <= boundary:
                counts[key] += 1
                break
    return counts

def population_variance(xs):
    return statistics.pvariance(xs) if len(xs) > 1 else 0.0

def mean(xs):
    return statistics.mean(xs)

def sensitivity_gamma(failures, rows):
    baseline = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
    baseline["abstention_threshold"] = 0.0
    gammas = [0.5, 0.7, 0.9]
    records = []
    for gamma in gammas:
        raw = copy.deepcopy(baseline)
        raw["routing_gamma"] = gamma
        result = prioritize_followups(build_request(raw))
        weights = {
            int(item["backoff_distance"]): float(item["routing_weight"])
            for item in result["routing_provenance"]
        }
        record = {
            "parameter_family": "gamma",
            "parameter_value": gamma,
            "mode": result["mode"],
            "top_category": result.get("top_category"),
            "effective_evidence_mass": result["effective_evidence_mass"],
            "data_support": result["data_support"],
            "uncertainty_entropy": result["uncertainty_entropy"],
            "L0_weight": weights.get(0, 0.0),
            "L3_weight": weights.get(3, 0.0),
            "L5_weight": weights.get(5, 0.0),
            "fallback_weight": weights.get(3, 0.0) + weights.get(5, 0.0),
            "L5_to_L3_ratio": weights.get(5, 0.0) / weights.get(3, 1.0),
            "diagnostic_distribution": result["diagnostic_distribution"],
        }
        records.append(record)

    baseline_dist = next(
        x["diagnostic_distribution"] for x in records if x["parameter_value"] == 0.7
    )
    for record in records:
        record["tv_vs_gamma_0_7"] = tv(record["diagnostic_distribution"], baseline_dist)
        rows.append(record)

    if not strictly_decreasing([x["L0_weight"] for x in records]):
        failures.append("S1 gamma: L0 routing weight did not decrease monotonically")
    if not strictly_increasing([x["fallback_weight"] for x in records]):
        failures.append("S1 gamma: total fallback weight did not increase monotonically")
    if not strictly_increasing([x["L5_to_L3_ratio"] for x in records]):
        failures.append("S1 gamma: L5/L3 ratio did not increase monotonically")
    if len({x["effective_evidence_mass"] for x in records}) != 1:
        failures.append("S1 gamma: effective evidence mass changed")
    if len({x["data_support"] for x in records}) != 1:
        failures.append("S1 gamma: data support changed")
    for a, b in zip(records, records[1:]):
        if tv(a["diagnostic_distribution"], b["diagnostic_distribution"]) <= 0:
            failures.append("S1 gamma: adjacent diagnostic distributions were identical")
    return records

def sensitivity_delta(failures, rows):
    categories = ["ownership", "evidence", "tradeoff", "reflection"]
    ages = {
        "ownership": 7.0,
        "evidence": 30.0,
        "tradeoff": 180.0,
        "reflection": 365.0,
    }
    parent = {k: 0.25 for k in categories}
    deltas = [0.01, 0.02, 0.05]
    records = []

    for delta_month in deltas:
        delta_day = delta_month / 30.44
        evidence = [
            EvidenceRecord(k, True, 1.0, ages[k])
            for k in categories
        ]
        counts, mass = weighted_counts(evidence, categories, delta_day)
        raw = {
            "categories": categories,
            "parent_distribution": parent,
            "evidence": [
                {
                    "category": r.category,
                    "authorized": r.authorized,
                    "quality": r.quality,
                    "age_days": r.age_days,
                }
                for r in evidence
            ],
            "permitted_categories": categories,
            "kappa_company": 10.0,
            "temporal_decay_rate_per_day": delta_day,
            "routing_levels": [
                {
                    "name": "L0_full_context",
                    "backoff_distance": 0,
                    "authorized": True,
                    "applicable": True,
                    "coverage": 1.0,
                    "distribution": parent,
                }
            ],
            "routing_gamma": 0.7,
            "support_tau": 8.0,
            "abstention_threshold": 0.0,
        }
        result = prioritize_followups(build_request(raw))
        record = {
            "parameter_family": "delta_per_month",
            "parameter_value": delta_month,
            "delta_per_day": delta_day,
            "mode": result["mode"],
            "top_category": result.get("top_category"),
            "effective_evidence_mass": mass,
            "data_support": result["data_support"],
            "uncertainty_entropy": result["uncertainty_entropy"],
            "ownership_weight": counts["ownership"],
            "evidence_weight": counts["evidence"],
            "tradeoff_weight": counts["tradeoff"],
            "reflection_weight": counts["reflection"],
            "recent_to_old_ratio": counts["ownership"] / counts["reflection"],
            "diagnostic_distribution": result["diagnostic_distribution"],
        }
        records.append(record)
        rows.append(record)

    if not strictly_decreasing([x["effective_evidence_mass"] for x in records]):
        failures.append("S2 delta: effective mass did not decrease monotonically")
    if not strictly_decreasing([x["data_support"] for x in records]):
        failures.append("S2 delta: data support did not decrease monotonically")
    for key in [
        "ownership_weight", "evidence_weight", "tradeoff_weight", "reflection_weight"
    ]:
        if not strictly_decreasing([x[key] for x in records]):
            failures.append(f"S2 delta: {key} did not decrease monotonically")
    if not strictly_increasing([x["recent_to_old_ratio"] for x in records]):
        failures.append("S2 delta: recent/old weight ratio did not increase monotonically")
    return records

def sensitivity_lambda(failures, rows):
    categories = ["ownership", "evidence", "tradeoff", "reflection"]
    prior = {k: 0.25 for k in categories}
    counts = {
        "ownership": 1.0,
        "evidence": 8.0,
        "tradeoff": 1.0,
        "reflection": 0.0,
    }
    empirical = normalize(counts, categories)
    lambdas = [1, 5, 10, 20, 50]
    records = []

    for lambda0 in lambdas:
        alpha = posterior_alpha(prior, counts, categories, float(lambda0))
        posterior = posterior_mean(alpha)
        record = {
            "parameter_family": "lambda0_prior_concentration",
            "parameter_value": lambda0,
            "tv_to_prior": tv(posterior, prior),
            "tv_to_empirical": tv(posterior, empirical),
            "posterior": posterior,
        }
        records.append(record)
        rows.append(record)

    if not strictly_decreasing([x["tv_to_prior"] for x in records]):
        failures.append("S3 lambda0: TV to prior did not decrease monotonically")
    if not strictly_increasing([x["tv_to_empirical"] for x in records]):
        failures.append("S3 lambda0: TV to empirical did not increase monotonically")
    return records

def hierarchy_ablation(failures, replicate_rows, summary_rows):
    cats = ["c1", "c2", "c3", "c4"]
    generic = {"c1": 0.25, "c2": 0.25, "c3": 0.25, "c4": 0.25}
    archetype_truth = {"c1": 0.35, "c2": 0.30, "c3": 0.20, "c4": 0.15}
    industry_truth = {"c1": 0.20, "c2": 0.50, "c3": 0.20, "c4": 0.10}
    company_truth = {"c1": 0.18, "c2": 0.55, "c3": 0.17, "c4": 0.10}
    company_ns = [1, 3, 5, 10, 20]
    truth_top = top_key(company_truth)

    synthetic_truth = {
        "generic": generic,
        "archetype": archetype_truth,
        "industry": industry_truth,
        "company": company_truth,
        "archetype_n": 80,
        "industry_n": 50,
        "company_n": company_ns,
        "kappa_archetype": 10.0,
        "kappa_industry": 10.0,
        "kappa_company": 10.0,
    }

    for n in company_ns:
        a2_full, a2_ablated = [], []
        a4_full, a4_ablated = [], []
        a2_full_top, a2_ab_top = [], []
        a4_full_top, a4_ab_top = [], []

        for rep in range(REPLICATES):
            seed = MASTER_SEED + n * 10000 + rep
            rng = random.Random(seed)
            archetype_counts = sample_multinomial(rng, archetype_truth, 80)
            industry_counts = sample_multinomial(rng, industry_truth, 50)
            company_counts = sample_multinomial(rng, company_truth, n)

            levels = hierarchical_partial_pooling(
                generic,
                archetype_counts,
                industry_counts,
                company_counts,
                cats,
                10.0,
                10.0,
                10.0,
            )
            full = levels["company"]
            archetype = levels["archetype"]
            no_industry = hierarchical_dirichlet_mean(
                archetype, company_counts, cats, 10.0
            )
            local_only = normalize(company_counts, cats)

            e_full = tv(full, company_truth)
            e_no_ind = tv(no_industry, company_truth)
            e_local = tv(local_only, company_truth)

            a2_full.append(e_full)
            a2_ablated.append(e_no_ind)
            a4_full.append(e_full)
            a4_ablated.append(e_local)
            a2_full_top.append(top_key(full) == truth_top)
            a2_ab_top.append(top_key(no_industry) == truth_top)
            a4_full_top.append(top_key(full) == truth_top)
            a4_ab_top.append(top_key(local_only) == truth_top)

            replicate_rows.append({
                "ablation": "A2_remove_industry_prior",
                "sample_size": n,
                "replicate": rep,
                "seed": seed,
                "full_tv_error": e_full,
                "ablated_tv_error": e_no_ind,
                "full_better": e_full < e_no_ind,
            })
            replicate_rows.append({
                "ablation": "A4_remove_hierarchical_pooling",
                "sample_size": n,
                "replicate": rep,
                "seed": seed,
                "full_tv_error": e_full,
                "ablated_tv_error": e_local,
                "full_better": e_full < e_local,
            })

        for ablation, fulls, ablateds, ftops, atops in [
            ("A2_remove_industry_prior", a2_full, a2_ablated, a2_full_top, a2_ab_top),
            ("A4_remove_hierarchical_pooling", a4_full, a4_ablated, a4_full_top, a4_ab_top),
        ]:
            row = {
                "ablation": ablation,
                "sample_size": n,
                "replicates": REPLICATES,
                "full_mean_tv": mean(fulls),
                "ablated_mean_tv": mean(ablateds),
                "full_tv_variance": population_variance(fulls),
                "ablated_tv_variance": population_variance(ablateds),
                "paired_full_win_rate": mean(
                    [a < b for a, b in zip(fulls, ablateds)]
                ),
                "full_top1_accuracy": mean(ftops),
                "ablated_top1_accuracy": mean(atops),
            }
            summary_rows.append(row)
            if not row["full_mean_tv"] < row["ablated_mean_tv"]:
                failures.append(
                    f"{ablation} n={n}: full mean TV is not lower than ablated"
                )

    return synthetic_truth

def compatibility_ablation(failures, replicate_rows, summary_rows):
    cats = ["c1", "c2", "c3", "c4"]
    scenarios = [
        ({"c1": 0.55, "c2": 0.20, "c3": 0.15, "c4": 0.10}, "c1"),
        ({"c1": 0.20, "c2": 0.50, "c3": 0.20, "c4": 0.10}, "c2"),
        ({"c1": 0.20, "c2": 0.20, "c3": 0.45, "c4": 0.15}, "c3"),
        ({"c1": 0.18, "c2": 0.18, "c3": 0.16, "c4": 0.48}, "c4"),
    ]

    full_invalid_masses = []
    ab_invalid_masses = []
    full_invalid_top = []
    ab_invalid_top = []

    for idx, (distribution, invalid) in enumerate(scenarios, start=1):
        permitted = [k for k in cats if k != invalid]
        full = masked_and_renormalized(distribution, cats, permitted)
        ablated = normalize(distribution, cats)

        fim = float(full.get(invalid, 0.0))
        aim = float(ablated.get(invalid, 0.0))
        fit = top_key(full) == invalid if full else False
        ait = top_key(ablated) == invalid

        full_invalid_masses.append(fim)
        ab_invalid_masses.append(aim)
        full_invalid_top.append(fit)
        ab_invalid_top.append(ait)

        replicate_rows.append({
            "ablation": "A3_remove_compatibility_mask",
            "sample_size": idx,
            "replicate": 0,
            "seed": "",
            "full_tv_error": "",
            "ablated_tv_error": "",
            "full_better": "",
            "invalid_category": invalid,
            "full_invalid_mass": fim,
            "ablated_invalid_mass": aim,
            "full_invalid_top1": fit,
            "ablated_invalid_top1": ait,
        })

    row = {
        "ablation": "A3_remove_compatibility_mask",
        "sample_size": len(scenarios),
        "replicates": len(scenarios),
        "full_invalid_mass_mean": mean(full_invalid_masses),
        "ablated_invalid_mass_mean": mean(ab_invalid_masses),
        "full_invalid_top1_rate": mean(full_invalid_top),
        "ablated_invalid_top1_rate": mean(ab_invalid_top),
    }
    summary_rows.append(row)

    if any(x != 0 for x in full_invalid_masses):
        failures.append("A3: full model released non-zero invalid probability mass")
    if any(full_invalid_top):
        failures.append("A3: full model selected an invalid top category")
    if any(x <= 0 for x in ab_invalid_masses):
        failures.append("A3: ablated model had zero invalid mass in a constructed scenario")
    if not all(ab_invalid_top):
        failures.append("A3: ablated invalid-top1 rate was not 1.0")

def temporal_ablation(failures, replicate_rows, summary_rows):
    cats = ["c1", "c2", "c3", "c4"]
    parent = {"c1": 0.25, "c2": 0.25, "c3": 0.25, "c4": 0.25}
    old_truth = {"c1": 0.55, "c2": 0.15, "c3": 0.20, "c4": 0.10}
    current_truth = {"c1": 0.15, "c2": 0.55, "c3": 0.20, "c4": 0.10}
    delta_day = 0.02 / 30.44
    full_errors, ablated_errors = [], []

    for rep in range(REPLICATES):
        seed = MASTER_SEED + 600000 + rep
        rng = random.Random(seed)
        old_counts = sample_multinomial(rng, old_truth, 60)
        current_counts = sample_multinomial(rng, current_truth, 20)

        records = []
        for category in cats:
            records.extend(
                EvidenceRecord(category, True, 1.0, 1095.0)
                for _ in range(old_counts[category])
            )
            records.extend(
                EvidenceRecord(category, True, 1.0, 7.0)
                for _ in range(current_counts[category])
            )

        full_counts, _ = weighted_counts(records, cats, delta_day)
        ablated_counts, _ = weighted_counts(records, cats, 0.0)
        full = hierarchical_dirichlet_mean(parent, full_counts, cats, 10.0)
        ablated = hierarchical_dirichlet_mean(parent, ablated_counts, cats, 10.0)

        e_full = tv(full, current_truth)
        e_ablated = tv(ablated, current_truth)
        full_errors.append(e_full)
        ablated_errors.append(e_ablated)

        replicate_rows.append({
            "ablation": "A6_remove_temporal_decay",
            "sample_size": 80,
            "replicate": rep,
            "seed": seed,
            "full_tv_error": e_full,
            "ablated_tv_error": e_ablated,
            "full_better": e_full < e_ablated,
        })

    row = {
        "ablation": "A6_remove_temporal_decay",
        "sample_size": 80,
        "replicates": REPLICATES,
        "full_mean_tv": mean(full_errors),
        "ablated_mean_tv": mean(ablated_errors),
        "full_tv_variance": population_variance(full_errors),
        "ablated_tv_variance": population_variance(ablated_errors),
        "paired_full_win_rate": mean(
            [a < b for a, b in zip(full_errors, ablated_errors)]
        ),
    }
    summary_rows.append(row)

    if not row["full_mean_tv"] < row["ablated_mean_tv"]:
        failures.append("A6: temporal-decay model did not have lower mean TV error")
    if not row["paired_full_win_rate"] > 0.5:
        failures.append("A6: temporal-decay paired win rate was not above 0.5")

    return {
        "old_truth": old_truth,
        "current_truth": current_truth,
        "old_n": 60,
        "recent_n": 20,
        "old_age_days": 1095,
        "recent_age_days": 7,
        "delta_per_month": 0.02,
        "delta_per_day": delta_day,
    }

def write_csv(path: Path, rows: list[dict]):
    fields = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            cooked = {}
            for key in fields:
                value = row.get(key, "")
                if isinstance(value, (dict, list)):
                    value = json.dumps(value, sort_keys=True, separators=(",", ":"))
                cooked[key] = value
            writer.writerow(cooked)

def main() -> int:
    failures = []
    sensitivity_rows = []
    replicate_rows = []
    summary_rows = []

    gamma_records = sensitivity_gamma(failures, sensitivity_rows)
    delta_records = sensitivity_delta(failures, sensitivity_rows)
    lambda_records = sensitivity_lambda(failures, sensitivity_rows)

    hierarchy_truth = hierarchy_ablation(
        failures, replicate_rows, summary_rows
    )
    compatibility_ablation(failures, replicate_rows, summary_rows)
    temporal_truth = temporal_ablation(failures, replicate_rows, summary_rows)

    result = {
        "protocol_version": "0.1-pre-registered",
        "experiment_base_commit": "ce3346642bc03a939115f506abada9443303438c",
        "master_seed": MASTER_SEED,
        "replicates": REPLICATES,
        "sensitivity": {
            "gamma": gamma_records,
            "delta": delta_records,
            "lambda0": lambda_records,
        },
        "synthetic_truth": {
            "hierarchy": hierarchy_truth,
            "temporal_drift": temporal_truth,
        },
        "ablation_summary": summary_rows,
        "not_executed": {
            "A1_similar_company_retrieval":
                "Requires external corpus and relevance ground truth.",
            "A5_evidence_lineage_human_explainability":
                "Requires external labels or human evaluation.",
        },
        "failures": failures,
        "passed": not failures,
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    json_path = OUT_DIR / "exp2_results.json"
    sensitivity_path = OUT_DIR / "exp2_sensitivity.csv"
    summary_path = OUT_DIR / "exp2_ablation_summary.csv"
    replicate_path = OUT_DIR / "exp2_ablation_replicates.csv"

    json_path.write_text(
        json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8"
    )
    write_csv(sensitivity_path, sensitivity_rows)
    write_csv(summary_path, summary_rows)
    write_csv(replicate_path, replicate_rows)

    print(f"exp2_failures={len(failures)}")
    print(f"ablation_replicate_rows={len(replicate_rows)}")
    for path in [json_path, sensitivity_path, summary_path, replicate_path]:
        print(f"{path.name}_sha256={hashlib.sha256(path.read_bytes()).hexdigest()}")

    if failures:
        for failure in failures:
            print("FAIL:", failure)
        return 1

    print("EXPERIMENT_2_PASS")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
