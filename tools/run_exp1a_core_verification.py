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

from research_core.compatibility import masked_and_renormalized
from research_core.evidence import weighted_counts
from research_core.inference import hierarchical_dirichlet_mean, normalize
from research_core.models import EvidenceRecord, PracticeRequest, RoutingLevel
from research_core.routing import route_mixture
from research_core.service import prioritize_followups
from research_core.uncertainty import data_support, normalized_entropy

BASELINE_PATH = ROOT / "examples/paper/followup_priority_request.json"
OUT_DIR = ROOT / "examples/paper/experiments/exp1a/results"
ABSTENTION_THRESHOLD = 0.3

def canonical_hash(obj) -> str:
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()

def total_variation(a: dict, b: dict) -> float:
    keys = sorted(set(a) | set(b))
    return 0.5 * sum(abs(float(a.get(k, 0.0)) - float(b.get(k, 0.0))) for k in keys)

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

def internal_trace(request: PracticeRequest) -> dict:
    request.validate()
    counts, effective_mass = weighted_counts(
        request.evidence, request.categories, request.temporal_decay_rate_per_day
    )
    local = hierarchical_dirichlet_mean(
        request.parent_distribution, counts, request.categories, request.kappa_company
    )
    masked = masked_and_renormalized(
        local, request.categories, request.permitted_categories
    )

    trace = {
        "authorized_evidence": [
            {
                "category": r.category,
                "quality": r.quality,
                "age_days": r.age_days,
            }
            for r in request.evidence
            if r.authorized
        ],
        "weighted_counts": counts,
        "effective_evidence_mass": effective_mass,
        "parent_distribution_normalized": normalize(
            request.parent_distribution, request.categories
        ),
        "local_posterior": local,
        "permitted_categories": list(request.permitted_categories),
        "compatibility_masked_posterior": masked,
        "data_support": data_support(effective_mass, request.support_tau),
        "abstention_threshold": request.abstention_threshold,
    }

    if masked:
        levels = list(request.routing_levels)
        l0_index = next(
            i for i, level in enumerate(levels) if level.backoff_distance == 0
        )
        l0 = levels[l0_index]
        levels[l0_index] = type(l0)(
            l0.name, l0.backoff_distance, l0.authorized, l0.applicable,
            l0.coverage, masked
        )
        routed, provenance = route_mixture(
            levels, request.permitted_categories, request.routing_gamma
        )
        trace["routing_provenance"] = provenance
        trace["routed_distribution"] = routed
        trace["uncertainty_entropy"] = (
            normalized_entropy(routed, len(request.permitted_categories))
            if routed else None
        )
    else:
        trace["routing_provenance"] = []
        trace["routed_distribution"] = {}
        trace["uncertainty_entropy"] = None

    trace["final_result"] = prioritize_followups(request)
    return trace

def main() -> int:
    baseline_raw = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
    baseline_raw["abstention_threshold"] = ABSTENTION_THRESHOLD

    cases = {}

    # E1A-01 supported baseline.
    cases["E1A-01"] = copy.deepcopy(baseline_raw)

    # E1A-02 unauthorized evidence flood.
    unauthorized = copy.deepcopy(baseline_raw)
    unauthorized["evidence"].extend(
        [
            {
                "category": "tradeoff",
                "authorized": False,
                "quality": 1.0,
                "age_days": 0.0,
            }
            for _ in range(100)
        ]
    )
    cases["E1A-02"] = unauthorized

    # E1A-03 age every authorized evidence record by 730 days.
    aged = copy.deepcopy(baseline_raw)
    for item in aged["evidence"]:
        if item["authorized"]:
            item["age_days"] = float(item["age_days"]) + 730.0
    cases["E1A-03"] = aged

    # E1A-04 zero local evidence.
    zero = copy.deepcopy(baseline_raw)
    zero["evidence"] = []
    cases["E1A-04"] = zero

    # E1A-05 all categories masked.
    masked = copy.deepcopy(baseline_raw)
    masked["permitted_categories"] = []
    cases["E1A-05"] = masked

    # E1A-06 no eligible route, but exactly one declared L0 remains.
    no_route = copy.deepcopy(baseline_raw)
    for level in no_route["routing_levels"]:
        level["authorized"] = False
        level["applicable"] = True
    cases["E1A-06"] = no_route

    # E1A-07 low support.
    low_support = copy.deepcopy(baseline_raw)
    low_support["evidence"] = [
        {
            "category": "ownership",
            "authorized": True,
            "quality": 0.10,
            "age_days": 365.0,
        }
    ]
    cases["E1A-07"] = low_support

    traces = {case_id: internal_trace(build_request(raw)) for case_id, raw in cases.items()}
    failures = []

    b = traces["E1A-01"]
    if b["final_result"].get("mode") != "ordered_practice_priority":
        failures.append("E1A-01 baseline did not release ordered practice priority")
    if b["data_support"] < ABSTENTION_THRESHOLD:
        failures.append("E1A-01 baseline support fell below declared threshold")
    released = set(b["final_result"].get("diagnostic_distribution", {}))
    if released - set(cases["E1A-01"]["permitted_categories"]):
        failures.append("E1A-01 released a prohibited category")
    if not b["routing_provenance"]:
        failures.append("E1A-01 routing provenance is empty")

    # Authorization hard gate.
    u = traces["E1A-02"]
    if u["weighted_counts"] != b["weighted_counts"]:
        failures.append("E1A-02 unauthorized evidence changed weighted counts")
    if u["effective_evidence_mass"] != b["effective_evidence_mass"]:
        failures.append("E1A-02 unauthorized evidence changed effective mass")
    if u["local_posterior"] != b["local_posterior"]:
        failures.append("E1A-02 unauthorized evidence changed local posterior")
    if u["final_result"] != b["final_result"]:
        failures.append("E1A-02 unauthorized evidence changed final result")
    auth_tv = total_variation(
        u["final_result"].get("diagnostic_distribution", {}),
        b["final_result"].get("diagnostic_distribution", {}),
    )
    if auth_tv != 0:
        failures.append(f"E1A-02 TV from baseline is {auth_tv}, expected 0")

    # Temporal aging.
    a = traces["E1A-03"]
    if not a["effective_evidence_mass"] < b["effective_evidence_mass"]:
        failures.append("E1A-03 aging did not reduce effective evidence mass")
    if not a["data_support"] < b["data_support"]:
        failures.append("E1A-03 aging did not reduce data support")

    # Zero local evidence.
    z = traces["E1A-04"]
    if any(v != 0 for v in z["weighted_counts"].values()):
        failures.append("E1A-04 zero-evidence counts are not all zero")
    if z["effective_evidence_mass"] != 0:
        failures.append("E1A-04 effective evidence mass is not zero")
    parent = z["parent_distribution_normalized"]
    if any(abs(z["local_posterior"][k] - parent[k]) > 1e-15 for k in parent):
        failures.append("E1A-04 local posterior does not equal normalized parent")
    if z["final_result"].get("mode") != "abstain":
        failures.append("E1A-04 did not abstain")
    if z["final_result"].get("reason") != "insufficient_data_support":
        failures.append("E1A-04 wrong abstention reason")

    # All masked.
    m = traces["E1A-05"]
    if m["final_result"].get("mode") != "abstain":
        failures.append("E1A-05 did not abstain")
    if m["final_result"].get("reason") != "all_categories_masked":
        failures.append("E1A-05 wrong abstention reason")

    # No eligible route.
    n = traces["E1A-06"]
    if n["final_result"].get("mode") != "abstain":
        failures.append("E1A-06 did not abstain")
    if n["final_result"].get("reason") != "no_eligible_routing_level":
        failures.append("E1A-06 wrong abstention reason")
    if "diagnostic_distribution" in n["final_result"]:
        failures.append("E1A-06 released a diagnostic distribution")

    # Low support.
    l = traces["E1A-07"]
    if not l["data_support"] < ABSTENTION_THRESHOLD:
        failures.append("E1A-07 support is not below abstention threshold")
    if l["final_result"].get("mode") != "abstain":
        failures.append("E1A-07 did not abstain")
    if l["final_result"].get("reason") != "insufficient_data_support":
        failures.append("E1A-07 wrong abstention reason")

    rows = []
    for case_id, trace in traces.items():
        result = trace["final_result"]
        rows.append({
            "case_id": case_id,
            "mode": result.get("mode"),
            "reason": result.get("reason"),
            "top_category": result.get("top_category"),
            "effective_evidence_mass": round(trace["effective_evidence_mass"], 12),
            "data_support": round(trace["data_support"], 12),
            "uncertainty_entropy": result.get("uncertainty_entropy"),
            "result_sha256": canonical_hash(result),
        })

    output = {
        "protocol_version": "0.1-pre-registered",
        "experiment_base_commit": "4594b88ca9915c69e527ca5e52e8e733ad1752c7",
        "case_count": len(rows),
        "authorization_tv_from_baseline": auth_tv,
        "cases": rows,
        "failures": failures,
        "passed": not failures,
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    results_json = OUT_DIR / "exp1a_results.json"
    results_csv = OUT_DIR / "exp1a_results.csv"
    baseline_trace = OUT_DIR / "exp1a_baseline_trace.json"

    results_json.write_text(
        json.dumps(output, sort_keys=True, indent=2) + "\n", encoding="utf-8"
    )
    baseline_trace.write_text(
        json.dumps(b, sort_keys=True, indent=2) + "\n", encoding="utf-8"
    )

    with results_csv.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=[
                "case_id", "mode", "reason", "top_category",
                "effective_evidence_mass", "data_support",
                "uncertainty_entropy", "result_sha256",
            ],
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"exp1a_cases={len(rows)} failures={len(failures)}")
    for path in (results_json, results_csv, baseline_trace):
        print(f"{path.name}_sha256={hashlib.sha256(path.read_bytes()).hexdigest()}")

    if failures:
        for failure in failures:
            print("FAIL:", failure)
        return 1

    print("EXPERIMENT_1A_PASS")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
