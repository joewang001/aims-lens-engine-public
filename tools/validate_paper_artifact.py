#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from dataclasses import replace
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from research_core import EvidenceRecord, PracticeRequest, RoutingLevel, prioritize_followups

REQUIRED_FILES = [
    "CITATION.cff",
    "VERSION",
    "README.md",
    "README.zh-CN.md",
    "PAPER_RELEASE_READINESS.md",
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
    "docs/IMPLEMENTATION_INTEGRATION_COVERAGE_MATRIX.md",
    "docs/experiments/EXPERIMENT_4_PROTOCOL.md",
    "docs/experiments/EXPERIMENT_5_PROTOCOL.md",
    "schemas/interview_dna.schema.json",
    "schemas/evidence_packet.schema.json",
    "schemas/minimized_context.schema.json",
    "examples/paper/interview_dna.example.json",
    "schemas/followup_priority_request.schema.json",
    "schemas/followup_priority_response.schema.json",
    "examples/paper/followup_priority_request.json",
    "examples/paper/expected_followup_priority_response.json",
    "tools/run_exp4_adversarial_alignment.py",
    "tools/run_exp5_hierarchy_approximation.py",
    "tools/validate_documentation_alignment.py",
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


def parse_manifest_scalar(text: str, key: str) -> str:
    prefix = f"{key}:"
    for line in text.splitlines():
        if line.startswith(prefix):
            return line.split(":", 1)[1].strip().strip('"').strip("'")
    fail(f"paper manifest is missing scalar: {key}")


def validate_manifest() -> None:
    text = (ROOT / "paper_artifact_manifest.yaml").read_text(encoding="utf-8")

    required_policy_markers = [
        "paper_version: v1.4",
        "artifact_version: 0.10.0-paper-v1.4",
        "candidate_side_practice_only: true",
        "employer_selection_decisions_allowed: false",
        "private_data_allowed: false",
        "network_required_for_demo: false",
        "branch_base_commit: f7fcb6a3129cb58fe20c414f1abe519376def8e1",
        "experimental_bundle_commit: c18899b469e1d579391306872d5834ebf6e3caf3",
        "target_release_tag: v0.10.0-paper-v1.4",
    ]
    for marker in required_policy_markers:
        if marker not in text:
            fail(f"paper manifest is missing required declaration: {marker}")

    release_status = parse_manifest_scalar(text, "release_status")
    frozen_ref = parse_manifest_scalar(text, "frozen_artifact_ref")
    target_tag = parse_manifest_scalar(text, "target_release_tag")
    artifact_version = parse_manifest_scalar(text, "artifact_version")

    version_text = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    if version_text != artifact_version:
        fail(f"VERSION / manifest artifact-version mismatch: {version_text!r} != {artifact_version!r}")

    citation_text = (ROOT / "CITATION.cff").read_text(encoding="utf-8")
    citation_match = re.search(r'^version:\s*["\']?([^"\'\n]+)["\']?\s*$', citation_text, re.MULTILINE)
    if not citation_match:
        fail("CITATION.cff is missing version")
    if citation_match.group(1).strip() != artifact_version:
        fail("CITATION.cff version does not match paper manifest artifact_version")

    if release_status == "candidate":
        if frozen_ref != "pending_until_release_freeze":
            fail("candidate release status requires pending_until_release_freeze")
        if "date-released:" in citation_text:
            fail("candidate release must not declare date-released in CITATION.cff")
    elif release_status == "frozen":
        immutable_commit = bool(re.fullmatch(r"[0-9a-f]{40}", frozen_ref))
        immutable_tag = bool(re.fullmatch(r"v[0-9][A-Za-z0-9._+-]*", frozen_ref))
        if not (immutable_commit or immutable_tag):
            fail("frozen release status requires an immutable-looking tag or 40-character commit SHA")
        if frozen_ref == "pending_until_release_freeze":
            fail("frozen release status cannot use the pending marker")
        if frozen_ref != target_tag:
            fail("frozen release must use target_release_tag as frozen_artifact_ref")
        if "date-released:" not in citation_text:
            fail("frozen release requires date-released in CITATION.cff")
    else:
        fail(f"unsupported release_status: {release_status!r}")

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
