#!/usr/bin/env python3
"""Validate the Phase B2C-2 improvement plan adapter with the sample request."""

from __future__ import annotations

import json
from pathlib import Path

from interview_prep_planner import build_interview_prep_plan


ROOT = Path(__file__).resolve().parents[1]
SAMPLE_REQUEST = ROOT / "examples" / "b2c-mckinsey-improvement-plan-request.json"
GENERIC_SAMPLE_REQUEST = ROOT / "examples" / "b2c-amazon-marketing-improvement-plan-request.json"


def main() -> int:
    payload = json.loads(SAMPLE_REQUEST.read_text(encoding="utf-8"))
    plan = build_interview_prep_plan(payload)
    generic_payload = json.loads(GENERIC_SAMPLE_REQUEST.read_text(encoding="utf-8"))
    generic_plan = build_interview_prep_plan(generic_payload)
    failures = []
    if plan["selected_plan"]["plan_key"] != "14_day_plan":
        failures.append("expected 14_day_plan for sample request")
    if len(plan["priority_improvement_points"]) != 3:
        failures.append("expected exactly 3 priority improvement points")
    dimensions = [point["dimension"] for point in plan["priority_improvement_points"]]
    if dimensions[0] != "impact_results":
        failures.append(f"expected weakest sample dimension impact_results, got {dimensions[0] if dimensions else 'none'}")
    if not plan["next_mock_recommendation"].get("interviewer_instruction"):
        failures.append("missing next mock interviewer instruction")
    if plan["entitlement"]["plan_tier"] != "paid":
        failures.append("expected paid entitlement for McKinsey sample request")
    if generic_plan["selected_plan"]["plan_key"] != "3_day_mini_plan":
        failures.append("expected 3_day_mini_plan for free generic sample request")
    if generic_plan["entitlement"]["plan_tier"] != "free":
        failures.append("expected free entitlement for generic sample request")
    if "14/30 day improvement plan" not in generic_plan["entitlement"].get("gated_features", []):
        failures.append("expected free plan to gate 14/30 day improvement plan")
    if "daily drills" not in generic_plan["entitlement"].get("gated_features", []):
        failures.append("expected free plan to gate daily drills")
    if generic_plan["target_company"] != "amazon":
        failures.append(f"expected amazon generic target company, got {generic_plan['target_company']}")
    if generic_plan["role_family"] != "marketing_growth":
        failures.append(f"expected marketing_growth role family, got {generic_plan['role_family']}")
    if not generic_plan.get("company_specific_drills"):
        failures.append("expected generic sample to include company_specific_drills")
    if not generic_plan.get("role_specific_drills"):
        failures.append("expected generic sample to include role_specific_drills")
    if generic_plan["next_mock_recommendation"].get("role_family") != "marketing_growth":
        failures.append("expected next mock recommendation to preserve role family")
    result = {
        "phase": "B2C-2",
        "status": "fail" if failures else "ok",
        "selected_plan": plan["selected_plan"]["plan_key"],
        "priority_dimensions": dimensions,
        "generic_selected_plan": generic_plan["selected_plan"]["plan_key"],
        "generic_target_company": generic_plan["target_company"],
        "generic_role_family": generic_plan["role_family"],
        "generic_plan_tier": generic_plan["entitlement"]["plan_tier"],
        "failures": failures,
    }
    print(json.dumps(result, indent=2))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
