#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
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


def fail(message: str) -> None:
    raise AssertionError(message)


def load_request(raw: dict) -> PracticeRequest:
    return PracticeRequest(
        categories=raw["categories"],
        parent_distribution=raw["parent_distribution"],
        evidence=[EvidenceRecord(**item) for item in raw["evidence"]],
        permitted_categories=raw["permitted_categories"],
        kappa_company=float(raw["kappa_company"]),
        temporal_decay_rate_per_day=float(raw["temporal_decay_rate_per_day"]),
        routing_levels=[RoutingLevel(**item) for item in raw["routing_levels"]],
        routing_gamma=float(raw.get("routing_gamma", 0.8)),
        support_tau=float(raw.get("support_tau", 8.0)),
    )


def main() -> int:
    missing = [path for path in REQUIRED_FILES if not (ROOT / path).exists()]
    if missing:
        fail(f"missing required paper artifact files: {missing}")

    openapi = (ROOT / "api" / "openapi.yaml").read_text(encoding="utf-8").lower()
    for term in FORBIDDEN_API_TERMS:
        if term.lower() in openapi:
            fail(f"paper API contains excluded employer-side term: {term}")

    raw = json.loads((ROOT / "examples" / "paper" / "followup_priority_request.json").read_text(encoding="utf-8"))
    expected = json.loads((ROOT / "examples" / "paper" / "expected_followup_priority_response.json").read_text(encoding="utf-8"))
    actual = prioritize_followups(load_request(raw))
    if actual != expected:
        fail("deterministic paper demo output differs from expected response")

    if "not a prediction" not in actual["disclaimer"].lower():
        fail("candidate-side disclaimer is missing")

    print("PAPER_ARTIFACT_VALIDATION_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
