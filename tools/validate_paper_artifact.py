#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from dataclasses import replace
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from research_core import EvidenceRecord, PracticeRequest, RoutingLevel, prioritize_followups

REQUIRED_FILES = [
    "CITATION.cff",
    "RESEARCH_BOUNDARY.md",
    "REPRODUCIBILITY.md",
    "paper_artifact_manifest.yaml",
    "api/openapi.yaml",
    "architecture/system-design.md",
    "architecture/lens-router.md",
    "governance/evidence-standard.md",
    "governance/privacy-and-fairness.md",
    "research_core/__init__.py",
    "research_core/models.py",
    "research_core/inference.py",
    "research_core/service.py",
    "research_core/dag.py",
    "research_core/stopping.py",
    "research_core/compatibility.py",
    "research_core/routing.py",
    "research_core/uncertainty.py",
    "research_core/evaluation.py",
    "research_core/active_learning.py",
    "research_core/evidence.py",
    "research_core/candidate_state.py",
    "research_core/privacy.py",
    "research_core/explanation.py",
    "research_core/audit.py",
    "research_core/lens.py",
    "research_core/policy.py",
    "config/paper_defaults.json",
    "docs/PAPER_TO_CODE_MAP.md",
    "docs/MATH_TO_CODE_COMPLETENESS_AUDIT.md",
    "schemas/interview_dna.schema.json",
    "schemas/evidence_packet.schema.json",
    "schemas/minimized_context.schema.json",
    "examples/paper/interview_dna.example.json",
    "schemas/followup_priority_request.schema.json",
    "schemas/followup_priority_response.schema.json",
    "examples/paper/followup_priority_request.json",
    "examples/paper/expected_followup_priority_response.json",
]

FORBIDDEN_API_TERMS = [
    "/v1/screen-candidate",
    "reject_after_human_review",
    "advance_after_human_review",
    "automatic final hiring",
]

REQUIRED_MANIFEST_EXCLUSIONS = {
    "schemas/screening_report.schema.json",
    "schemas/review_decision.schema.json",
    "schemas/jobace_adapter_contract.schema.json",
    "tools/llm_scorer.py",
    "tools/run_scoring_harness.py",
    "legacy/employer_decision_support/**",
}


def fail(message: str) -> None:
    raise AssertionError(message)


def parse_manifest_list(text: str, section: str) -> list[str]:
    lines = text.splitlines()
    marker = f"{section}:"
    try:
        start = lines.index(marker) + 1
    except ValueError:
        fail(f"paper manifest is missing section: {section}")

    items = []
    for line in lines[start:]:
        if line and not line.startswith(" "):
            break
        stripped = line.strip()
        if stripped.startswith("- "):
            items.append(stripped[2:].strip().strip('"').strip("'"))
    return items


def validate_manifest() -> None:
    text = (ROOT / "paper_artifact_manifest.yaml").read_text(encoding="utf-8")

    required_policy_markers = [
        "candidate_side_practice_only: true",
        "employer_selection_decisions_allowed: false",
        "private_data_allowed: false",
        "network_required_for_demo: false",
        "frozen_artifact_ref: pending_until_release_freeze",
    ]
    for marker in required_policy_markers:
        if marker not in text:
            fail(f"paper manifest is missing required declaration: {marker}")

    include_paths = parse_manifest_list(text, "include_paths")
    exclude_paths = parse_manifest_list(text, "exclude_from_paper_core")

    missing_exclusions = REQUIRED_MANIFEST_EXCLUSIONS - set(exclude_paths)
    if missing_exclusions:
        fail(f"paper manifest is missing required exclusions: {sorted(missing_exclusions)}")

    overlap = set(include_paths) & set(exclude_paths)
    if overlap:
        fail(f"paper manifest includes and excludes the same paths: {sorted(overlap)}")

    missing_includes = []
    for item in include_paths:
        if "*" in item:
            fail(f"include_paths must be concrete for the frozen artifact: {item}")
        target = ROOT / item.rstrip("/")
        if not target.exists():
            missing_includes.append(item)
    if missing_includes:
        fail(f"paper manifest include_paths do not exist: {missing_includes}")


def load_request(raw: dict) -> PracticeRequest:
    return PracticeRequest(
        categories=raw["categories"],
        parent_distribution=raw["parent_distribution"],
        evidence=[EvidenceRecord(**item) for item in raw["evidence"]],
        permitted_categories=raw["permitted_categories"],
        kappa_company=float(raw["kappa_company"]),
        temporal_decay_rate_per_day=float(raw["temporal_decay_rate_per_day"]),
        routing_levels=[RoutingLevel(**item) for item in raw["routing_levels"]],
        routing_gamma=float(raw.get("routing_gamma", 0.7)),
        support_tau=float(raw.get("support_tau", 8.0)),
        abstention_threshold=float(raw.get("abstention_threshold", 0.0)),
    )


def main() -> int:
    missing = [path for path in REQUIRED_FILES if not (ROOT / path).exists()]
    if missing:
        fail(f"missing required paper artifact files: {missing}")

    validate_manifest()

    openapi = (ROOT / "api" / "openapi.yaml").read_text(encoding="utf-8").lower()
    for term in FORBIDDEN_API_TERMS:
        if term.lower() in openapi:
            fail(f"paper API contains excluded employer-side term: {term}")

    raw = json.loads(
        (ROOT / "examples" / "paper" / "followup_priority_request.json").read_text(encoding="utf-8")
    )
    expected = json.loads(
        (ROOT / "examples" / "paper" / "expected_followup_priority_response.json").read_text(encoding="utf-8")
    )

    request = load_request(raw)
    request.validate()
    if request.abstention_threshold != float(raw["abstention_threshold"]):
        fail("validator did not preserve the declared abstention threshold")

    actual = prioritize_followups(request)
    if actual != expected:
        fail("deterministic paper demo output differs from expected response")

    if "not a prediction" not in actual["disclaimer"].lower():
        fail("candidate-side disclaimer is missing")

    abstention_probe = replace(request, evidence=[], abstention_threshold=0.3)
    abstained = prioritize_followups(abstention_probe)
    if abstained.get("mode") != "abstain" or abstained.get("reason") != "insufficient_data_support":
        fail("abstention gate is not exercised by the validation probe")

    print("PAPER_ARTIFACT_VALIDATION_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
