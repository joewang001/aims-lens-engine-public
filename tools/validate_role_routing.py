#!/usr/bin/env python3
"""Deterministic validation for Phase 2B role routing fixtures."""

from __future__ import annotations

import json
import argparse
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ROUTER_PATH = ROOT / "routing" / "role_router.json"
DEFAULT_RUN_DIR = ROOT / "validation_runs" / "2026-05-04-phase-2b-routing-live-transcripts"


def norm(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def detect_company(router: dict, company_text: str) -> str:
    text = norm(company_text)
    for company, aliases in router["company_aliases"].items():
        if any(norm(alias) in text for alias in aliases):
            return company
    return "generic"


def detect_overlay(router: dict, company: str, role_title: str, answer: str) -> str | None:
    title_text = norm(role_title)
    full_text = norm(f"{role_title} {answer}")
    matches = []
    for route in router["role_routes"]:
        title_match = any(norm(keyword) in title_text for keyword in route["keywords"])
        keyword_match = title_match or any(norm(keyword) in full_text for keyword in route["keywords"])
        company_match = company in route["companies"]
        generic_company = company == "generic"
        if keyword_match and (company_match or generic_company):
            matches.append((route["overlay"], title_match))
    if not matches:
        return None
    title_matches = [overlay for overlay, title_match in matches if title_match]
    if title_matches:
        if "swe" in title_matches:
            return "swe"
        if "data_analytics" in title_matches:
            return "data_analytics"
        if "risk_compliance" in title_matches:
            return "risk_compliance"
        if "retail_banking" in title_matches:
            return "retail_banking"
        if "consulting_case_pei" in title_matches:
            return "consulting_case_pei"
        return title_matches[0]
    matches = [overlay for overlay, _ in matches]
    priority = ["consulting_case_pei", "risk_compliance", "retail_banking", "data_analytics", "swe"]
    for overlay in priority:
        if overlay in matches:
            return overlay
    return matches[0]


def route_confidence(company: str, overlay: str | None) -> float:
    if company != "generic" and overlay:
        return 0.86
    if company != "generic":
        return 0.70
    if overlay:
        return 0.62
    return 0.40


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate role routing fixtures.")
    parser.add_argument("--run-dir", type=Path, default=DEFAULT_RUN_DIR)
    args = parser.parse_args()
    cases_path = args.run_dir / "transcript_cases.json"
    router = json.loads(ROUTER_PATH.read_text())
    cases = json.loads(cases_path.read_text())["cases"]
    failures = []
    routed = []
    for case in cases:
        company = detect_company(router, case["company"])
        overlay = detect_overlay(router, company, case["role_title"], case["candidate_answer"])
        confidence = route_confidence(company, overlay)
        result = {
            "case_id": case["case_id"],
            "company": company,
            "overlay": overlay,
            "confidence": confidence,
            "expected_company": case["expected_company"],
            "expected_overlay": case["expected_overlay"],
        }
        routed.append(result)
        if company != case["expected_company"]:
            failures.append({**result, "failure": "company"})
        if overlay != case["expected_overlay"]:
            failures.append({**result, "failure": "overlay"})
        if confidence < case["expected_confidence_min"]:
            failures.append({**result, "failure": "confidence"})

    out_dir = cases_path.parent
    (out_dir / "router_results.json").write_text(json.dumps({"results": routed, "failures": failures}, indent=2) + "\n")
    print(f"routing_cases={len(cases)} failures={len(failures)}")
    if failures:
        print(json.dumps(failures, indent=2))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
