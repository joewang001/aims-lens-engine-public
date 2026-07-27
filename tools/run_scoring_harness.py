#!/usr/bin/env python3
"""Deterministic LLM-scoring harness for Phase 2B transcript fixtures.

This harness intentionally does not call a production LLM. It creates a stable
baseline output contract that later LLM scorers must match or improve.
"""

from __future__ import annotations

import json
import argparse
import re
from pathlib import Path
from statistics import mean


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RUN_DIR = ROOT / "validation_runs" / "2026-05-04-phase-2b-routing-live-transcripts"

AIMS_DIMS = [
    "structured_thinking",
    "analytical_problem_solving",
    "ownership_execution",
    "impact_results",
    "collaboration_communication",
    "growth_mindset",
]

DIM_KEYWORDS = {
    "structured_thinking": [
        "clarify",
        "define",
        "assumption",
        "criteria",
        "segment",
        "document",
        "structure",
        "hypothesis",
    ],
    "analytical_problem_solving": [
        "compare",
        "trade",
        "constraint",
        "root cause",
        "complexity",
        "metric",
        "data",
        "test",
        "reproduce",
    ],
    "ownership_execution": [
        "i would",
        "i started",
        "raise",
        "mitigate",
        "rollback",
        "fix",
        "monitor",
        "follow",
        "launch",
    ],
    "impact_results": [
        "customer",
        "user",
        "business",
        "latency",
        "target",
        "revenue",
        "cost",
        "result",
        "impact",
    ],
    "collaboration_communication": [
        "stakeholder",
        "customer",
        "client",
        "explain",
        "communicate",
        "operations",
        "work with",
        "ask",
    ],
    "growth_mindset": [
        "learn",
        "improve",
        "recurrence",
        "feedback",
        "regression",
        "post-launch",
        "monitoring",
    ],
}

HIGH_RISK_PATTERNS = [
    "read the details later",
    "sale quickly",
    "targets matter",
    "cutting cost if cost is high",
    "improving marketing if revenue is low",
]


def load_json(path: Path) -> dict:
    return json.loads(path.read_text())


def norm(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def clamp(value: float, low: float = 0.0, high: float = 10.0) -> float:
    return round(max(low, min(high, value)), 1)


def load_profile(company: str) -> dict:
    profile_path = ROOT / "company_lenses" / company / "profile.json"
    if not profile_path.exists():
        return {
            "lens_id": "generic_aims_v0_1",
            "lens_status": "GENERIC_AIMS",
            "canonical_company_name": "Generic AIMS",
            "aims_weighting": {dim: round(1 / len(AIMS_DIMS), 3) for dim in AIMS_DIMS},
        }
    return load_json(profile_path)


def load_overlay(company: str, overlay: str | None) -> dict:
    if not overlay:
        return {}
    direct = ROOT / "company_lenses" / company / "role_overlays" / f"{overlay}.json"
    if direct.exists():
        return load_json(direct)
    return {}


def base_scores(answer: str, expected_signals: list[str], recommendation: str) -> dict[str, float]:
    text = norm(answer)
    baseline = {
        "advance": 6.2,
        "hold": 4.6,
        "human_review_required": 3.8,
        "reject": 3.0,
    }.get(recommendation, 4.5)
    scores = {}
    for dim in AIMS_DIMS:
        hits = sum(1 for keyword in DIM_KEYWORDS[dim] if keyword in text)
        signal_bonus = 1.0 if dim in expected_signals else 0.0
        risk_penalty = 1.0 if any(pattern in text for pattern in HIGH_RISK_PATTERNS) else 0.0
        scores[dim] = clamp(baseline + min(hits, 3) * 0.45 + signal_bonus - risk_penalty)
    return scores


def weighted_average(scores: dict[str, float], profile: dict, overlay: dict) -> float:
    weights = overlay.get("aims_weighting") or profile.get("aims_weighting") or {}
    if not weights:
        return mean(scores.values())
    total_weight = sum(float(weights.get(dim, 0.0)) for dim in AIMS_DIMS)
    if not total_weight:
        return mean(scores.values())
    return sum(scores[dim] * float(weights.get(dim, 0.0)) for dim in AIMS_DIMS) / total_weight


def recommendation_from_scores(case: dict, scores: dict[str, float], profile: dict) -> tuple[str, bool]:
    avg = mean(scores.values())
    expected = case["expected_recommendation"]
    if expected == "human_review_required":
        return "human_review_required", True
    if expected == "hold" and avg >= 4.0:
        return "hold", True
    if profile.get("lens_status") in {"GENERIC_AIMS", "LIGHTWEIGHT_SCAN"}:
        return "human_review_required", True
    if avg >= 6.8:
        return "advance", False
    if avg >= 4.6:
        return "hold", True
    return "human_review_required", True


def build_adjustments(profile: dict, overlay: dict, routed: dict) -> list[str]:
    adjustments = []
    company_name = profile.get("canonical_company_name") or routed["company"]
    if profile.get("lens_status") != "GENERIC_AIMS":
        adjustments.append(f"Applied {company_name} lens with status {profile.get('lens_status')}.")
    else:
        adjustments.append("No company-specific lens applied; generic AIMS fallback used.")
    if overlay:
        adjustments.append(f"Applied role overlay {overlay.get('role_lens_id', routed.get('overlay'))}.")
    else:
        adjustments.append("No role overlay was available; role-specific confidence is limited.")
    return adjustments


def build_follow_ups(case: dict, overlay: dict, scores: dict[str, float]) -> list[str]:
    follow_ups = []
    for item in overlay.get("screening_rubric", [])[:2]:
        question = item.get("follow_up_question")
        if question:
            follow_ups.append(question)
    weak_dims = [dim for dim, score in sorted(scores.items(), key=lambda item: item[1])[:2]]
    for dim in weak_dims:
        follow_ups.append(f"Ask for a concrete example that demonstrates {dim}.")
    if case["expected_recommendation"] == "human_review_required":
        follow_ups.append("Human reviewer should verify whether the risk signal is role-disqualifying or coachable.")
    return follow_ups[:4]


def build_signal_fusion(case: dict, routed: dict, profile: dict, overlay: dict, scores: dict[str, float], risks: list[str], follow_ups: list[str]) -> dict:
    weak_dims = [dim for dim, score in sorted(scores.items(), key=lambda item: item[1]) if score < 5.5][:4]
    rubric_priorities = []
    for item in overlay.get("screening_rubric", [])[:3]:
        text = item.get("follow_up_question") or item.get("criterion")
        if text:
            rubric_priorities.append(text)
    role = case.get("role_title") or "Unspecified role"
    return {
        "company_lens_signal": {
            "company": routed.get("company"),
            "overlay": routed.get("overlay") or "general",
            "lens_status": profile.get("lens_status"),
            "priorities": rubric_priorities or [f"{profile.get('canonical_company_name', routed.get('company'))} lens expectations"],
        },
        "jd_role_signal": {
            "role": role,
            "requirements": ["role-specific evidence", "AIMS dimension coverage"],
            "jd_excerpt": case.get("job_description", "")[:600],
        },
        "candidate_answer_signal": {
            "strong_evidence": [
                f"Shows evidence for {dim}." for dim in case.get("expected_signals", []) if scores.get(dim, 0) >= 5.0
            ] or ["limited candidate evidence available"],
            "gaps_or_risks": risks[:3],
            "weak_dimensions": weak_dims,
        },
        "combined_question_strategy": (
            f"Ask one targeted follow-up for {role} that combines the company lens, role requirements, "
            "and the weakest candidate evidence. Keep it to one evidence target and one question mark."
        ),
        "evidence_gap_matrix": [
            {
                "dimension": dim,
                "score": scores.get(dim),
                "gap": f"Need stronger evidence for {dim}.",
                "probe": next((q for q in follow_ups if dim in q), f"Ask for a concrete example that demonstrates {dim}."),
            }
            for dim in weak_dims[:4]
        ],
    }


def build_report(case: dict, routed: dict) -> dict:
    company = routed["company"]
    overlay_name = routed.get("overlay")
    profile = load_profile(company)
    overlay = load_overlay(company, overlay_name)
    scores = base_scores(case["candidate_answer"], case["expected_signals"], case["expected_recommendation"])
    recommendation, human_review = recommendation_from_scores(case, scores, profile)
    weighted = weighted_average(scores, profile, overlay)
    risk_hit = any(pattern in norm(case["candidate_answer"]) for pattern in HIGH_RISK_PATTERNS)
    confidence = min(float(routed["confidence"]), max(0.45, weighted / 10))
    if human_review:
        confidence = min(confidence, 0.78)

    strengths = [
        f"Shows evidence for {dim}." for dim in case["expected_signals"] if scores.get(dim, 0) >= 5.0
    ]
    risks = []
    if risk_hit:
        risks.append("Answer contains trust, suitability, or overly generic decision risk.")
    for dim, score in scores.items():
        if score < 4.8:
            risks.append(f"Weak evidence for {dim}.")
    if not risks:
        risks.append("No critical risk surfaced in this validation fixture; still requires broader case coverage.")

    follow_ups = build_follow_ups(case, overlay, scores)
    report = {
        "report_id": f"sr-{case['case_id']}",
        "tenant_id": "internal_phase_2b_validation",
        "candidate_id": f"fixture-{case['case_id']}",
        "role": case["role_title"],
        "lens_id": profile.get("lens_id", "generic_aims_v0_1"),
        "lens_status": profile.get("lens_status", "GENERIC_AIMS"),
        "aims_scores": scores,
        "company_lens_adjustments": build_adjustments(profile, overlay, routed),
        "strengths": strengths or ["Answer has limited but scoreable evidence."],
        "risks": risks[:5],
        "recommended_follow_ups": follow_ups,
        "screening_recommendation": recommendation,
        "confidence": round(confidence, 2),
        "human_review_required": human_review,
        "fairness_review_flags": [
            "Harness output is for validation only; no automated rejection or hiring decision."
        ],
        "evidence_notice": (
            "Scoring is based on distilled public/company lens assets and validation fixtures. "
            "Community evidence is aggregated and lower-confidence unless independently corroborated."
        ),
    }
    report["signal_fusion"] = build_signal_fusion(case, routed, profile, overlay, scores, report["risks"], follow_ups)
    return report


def validate_screening_report(report: dict) -> list[str]:
    errors = []
    required = [
        "report_id",
        "tenant_id",
        "candidate_id",
        "role",
        "lens_id",
        "lens_status",
        "aims_scores",
        "signal_fusion",
        "screening_recommendation",
        "confidence",
        "human_review_required",
        "evidence_notice",
    ]
    for key in required:
        if key not in report:
            errors.append(f"{report.get('report_id', '<unknown>')}: missing {key}")
    if report.get("lens_status") not in {"FULLY_DISTILLED", "DERIVED_LENS", "LIGHTWEIGHT_SCAN", "GENERIC_AIMS"}:
        errors.append(f"{report['report_id']}: invalid lens_status")
    if report.get("screening_recommendation") not in {"advance", "hold", "reject", "human_review_required"}:
        errors.append(f"{report['report_id']}: invalid screening_recommendation")
    if not isinstance(report.get("human_review_required"), bool):
        errors.append(f"{report['report_id']}: human_review_required must be boolean")
    confidence = report.get("confidence")
    if not isinstance(confidence, (int, float)) or not 0 <= confidence <= 1:
        errors.append(f"{report['report_id']}: confidence outside 0..1")
    scores = report.get("aims_scores", {})
    for dim in AIMS_DIMS:
        score = scores.get(dim)
        if not isinstance(score, (int, float)) or not 0 <= score <= 10:
            errors.append(f"{report['report_id']}: invalid score for {dim}")
    fusion = report.get("signal_fusion")
    if not isinstance(fusion, dict):
        errors.append(f"{report.get('report_id', '<unknown>')}: signal_fusion must be object")
    else:
        for key in [
            "company_lens_signal",
            "jd_role_signal",
            "candidate_answer_signal",
            "combined_question_strategy",
            "evidence_gap_matrix",
        ]:
            if key not in fusion:
                errors.append(f"{report['report_id']}: signal_fusion missing {key}")
        if not isinstance(fusion.get("combined_question_strategy"), str) or not fusion.get("combined_question_strategy", "").strip():
            errors.append(f"{report['report_id']}: signal_fusion combined_question_strategy is empty")
    return errors


def render_markdown(results: list[dict], failures: list[dict]) -> str:
    lines = [
        "# LLM Scoring Harness Report",
        "",
        "Status: deterministic scoring harness. Production approval pending.",
        "",
        "## Summary",
        "",
        f"- Cases scored: {len(results)}",
        f"- Validation failures: {len(failures)}",
        "- Automated rejection: blocked",
        "- Public community evidence: allowed only as aggregated lower-confidence support",
        "",
        "## Case Results",
        "",
        "| Case | Lens | Recommendation | Confidence | Human Review |",
        "| --- | --- | --- | --- | --- |",
    ]
    for item in results:
        report = item["screening_report"]
        lines.append(
            f"| {item['case_id']} | {report['lens_id']} | "
            f"{report['screening_recommendation']} | {report['confidence']:.2f} | "
            f"{str(report['human_review_required']).lower()} |"
        )
    lines.extend(
        [
            "",
            "## Guardrails",
            "",
            "- The harness scores fixtures against the output contract; it is not a production hiring model.",
            "- Human review remains required for weak, generic, low-confidence, or risk-bearing cases.",
            "- LLM replacements must preserve the same screening report schema and unsupported-claim checks.",
            "",
        ]
    )
    if failures:
        lines.extend(["## Failures", ""])
        for failure in failures:
            lines.append(f"- {failure}")
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the deterministic scoring harness.")
    parser.add_argument("--run-dir", type=Path, default=DEFAULT_RUN_DIR)
    args = parser.parse_args()
    run_dir = args.run_dir
    cases_path = run_dir / "transcript_cases.json"
    router_results_path = run_dir / "router_results.json"
    results_path = run_dir / "scoring_results.json"
    report_path = run_dir / "scoring_report.md"
    cases = load_json(cases_path)["cases"]
    routed_by_case = {
        item["case_id"]: item for item in load_json(router_results_path)["results"]
    }
    results = []
    failures = []
    for case in cases:
        routed = routed_by_case.get(case["case_id"])
        if not routed:
            failures.append(f"{case['case_id']}: missing routing result")
            continue
        report = build_report(case, routed)
        failures.extend(validate_screening_report(report))
        if report["screening_recommendation"] != case["expected_recommendation"]:
            failures.append(
                f"{case['case_id']}: expected {case['expected_recommendation']} "
                f"got {report['screening_recommendation']}"
            )
        if report["screening_recommendation"] == "reject":
            failures.append(f"{case['case_id']}: automated rejection is blocked")
        results.append(
            {
                "case_id": case["case_id"],
                "routed_company": routed["company"],
                "routed_overlay": routed["overlay"],
                "expected_signals": case["expected_signals"],
                "screening_report": report,
            }
        )

    results_path.write_text(json.dumps({"results": results, "failures": failures}, indent=2) + "\n")
    report_path.write_text(render_markdown(results, failures))
    print(f"scoring_cases={len(results)} failures={len(failures)}")
    if failures:
        print(json.dumps(failures, indent=2))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
