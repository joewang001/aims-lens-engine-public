#!/usr/bin/env python3
"""Validate dual-layer evaluation rendering examples."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_EXAMPLE = ROOT / "examples" / "dual-layer-evaluation-example.json"
AIMS_DIMS = [
    "structured_thinking",
    "analytical_problem_solving",
    "ownership_execution",
    "impact_results",
    "collaboration_communication",
    "growth_mindset",
]


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, failures: list[str], message: str) -> None:
    if not condition:
        failures.append(message)


def validate_evidence_list(name: str, items: object, failures: list[str]) -> None:
    require(isinstance(items, list) and bool(items), failures, f"{name} must be a non-empty list")
    if not isinstance(items, list):
        return
    for index, item in enumerate(items):
        prefix = f"{name}[{index}]"
        require(isinstance(item, dict), failures, f"{prefix} must be an object")
        if not isinstance(item, dict):
            continue
        for key in ("id", "dimension", "claim", "evidence", "confidence"):
            require(key in item, failures, f"{prefix} missing {key}")
        if "dimension" in item:
            require(item["dimension"] in AIMS_DIMS, failures, f"{prefix} invalid dimension {item['dimension']!r}")
        confidence = item.get("confidence")
        require(isinstance(confidence, (int, float)) and 0 <= confidence <= 1, failures, f"{prefix} invalid confidence")


def validate_string_list(name: str, value: object, failures: list[str], *, min_items: int = 1) -> None:
    require(isinstance(value, list) and len(value) >= min_items, failures, f"{name} must contain at least {min_items} item(s)")
    if isinstance(value, list):
        for index, item in enumerate(value):
            require(isinstance(item, str) and bool(item.strip()), failures, f"{name}[{index}] must be a non-empty string")


def validate_payload(payload: dict) -> list[str]:
    failures: list[str] = []
    for key in ("evaluation_id", "tenant_id", "candidate_id", "role", "core_evaluation", "candidate_final_assessment", "b2b_reviewer_report", "rendering_policy"):
        require(key in payload, failures, f"missing {key}")

    core = payload.get("core_evaluation") or {}
    scores = core.get("aims_scores") or {}
    for dim in AIMS_DIMS:
        value = scores.get(dim)
        require(isinstance(value, (int, float)) and 0 <= value <= 10, failures, f"invalid aims_scores.{dim}")

    average = core.get("average_score")
    require(isinstance(average, (int, float)) and 0 <= average <= 10, failures, "invalid core_evaluation.average_score")
    confidence = core.get("confidence")
    require(isinstance(confidence, (int, float)) and 0 <= confidence <= 1, failures, "invalid core_evaluation.confidence")

    validate_evidence_list("core_evaluation.strength_evidence", core.get("strength_evidence"), failures)
    validate_evidence_list("core_evaluation.weakness_evidence", core.get("weakness_evidence"), failures)
    validate_string_list("core_evaluation.risk_signals", core.get("risk_signals"), failures)
    validate_string_list("core_evaluation.follow_up_questions", core.get("follow_up_questions"), failures)
    require(isinstance(core.get("evidence_notice"), str) and bool(core.get("evidence_notice", "").strip()), failures, "core_evaluation.evidence_notice required")

    priorities = core.get("improvement_priorities")
    require(isinstance(priorities, list) and bool(priorities), failures, "core_evaluation.improvement_priorities must be non-empty")
    if isinstance(priorities, list):
        for index, item in enumerate(priorities):
            prefix = f"core_evaluation.improvement_priorities[{index}]"
            require(isinstance(item, dict), failures, f"{prefix} must be an object")
            if isinstance(item, dict):
                require(item.get("dimension") in AIMS_DIMS, failures, f"{prefix} invalid dimension")
                require(item.get("priority") in {"high", "medium", "low"}, failures, f"{prefix} invalid priority")
                require(bool(item.get("issue")), failures, f"{prefix} missing issue")
                require(bool(item.get("practice_action")), failures, f"{prefix} missing practice_action")

    candidate = payload.get("candidate_final_assessment") or {}
    validate_string_list("candidate_final_assessment.strengths", candidate.get("strengths"), failures)
    validate_string_list("candidate_final_assessment.priority_improvement_points", candidate.get("priority_improvement_points"), failures)
    validate_string_list("candidate_final_assessment.practice_plan", candidate.get("practice_plan"), failures)
    require(isinstance(candidate.get("summary"), str) and bool(candidate.get("summary", "").strip()), failures, "candidate_final_assessment.summary required")

    b2b = payload.get("b2b_reviewer_report") or {}
    validate_string_list("b2b_reviewer_report.verified_strengths", b2b.get("verified_strengths"), failures)
    validate_string_list("b2b_reviewer_report.unverified_or_weak_areas", b2b.get("unverified_or_weak_areas"), failures)
    validate_string_list("b2b_reviewer_report.recommended_verification_questions", b2b.get("recommended_verification_questions"), failures)
    require(isinstance(b2b.get("summary"), str) and bool(b2b.get("summary", "").strip()), failures, "b2b_reviewer_report.summary required")
    require(isinstance(b2b.get("human_review_required"), bool), failures, "b2b_reviewer_report.human_review_required must be boolean")
    require("automated" in (b2b.get("decision_boundary_notice") or "").lower(), failures, "b2b decision boundary must mention automated use boundary")

    policy = payload.get("rendering_policy") or {}
    require(policy.get("same_core_evaluation_required") is True, failures, "rendering_policy.same_core_evaluation_required must be true")
    validate_string_list("rendering_policy.blocked_uses", policy.get("blocked_uses"), failures)

    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a dual-layer evaluation rendering payload.")
    parser.add_argument("--path", default=str(DEFAULT_EXAMPLE), help="Path to payload JSON.")
    args = parser.parse_args()
    path = Path(args.path)
    payload = load_json(path)
    failures = validate_payload(payload)
    result = {
        "status": "fail" if failures else "ok",
        "path": str(path.relative_to(ROOT) if path.is_relative_to(ROOT) else path),
        "failures": failures,
    }
    print(json.dumps(result, indent=2))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
