#!/usr/bin/env python3
"""Generate Phase 2C production-gate transcript validation fixtures."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUN_DIR = ROOT / "validation_runs" / "2026-05-04-phase-2c-production-gates"
OUT_PATH = RUN_DIR / "transcript_cases.json"

COMPANY_ROLES = {
    "amazon": ("Amazon", [("swe", "Software Development Engineer"), ("data_analytics", "Business Intelligence Engineer")]),
    "google": ("Google", [("swe", "Software Engineer"), ("data_analytics", "Data Analyst")]),
    "apple": ("Apple", [("swe", "iOS Software Engineer")]),
    "microsoft": ("Microsoft", [("swe", "Software Engineer"), ("data_analytics", "Data Analyst")]),
    "mckinsey": (
        "McKinsey",
        [
            ("consulting_case_pei", "Business Analyst"),
            ("data_analytics", "Data Analyst"),
            ("consulting_case_pei", "Associate Consultant"),
            ("consulting_case_pei", "Implementation Consultant"),
        ],
    ),
    "td": ("TD Bank", [("retail_banking", "Customer Service Representative"), ("risk_compliance", "Operational Risk Analyst"), ("data_analytics", "Data Analyst")]),
    "rbc": ("RBC", [("retail_banking", "Client Advisor"), ("risk_compliance", "Operational Risk Analyst"), ("data_analytics", "Data Analyst")]),
    "cibc": ("CIBC", [("retail_banking", "Banking Advisor"), ("risk_compliance", "Compliance Analyst")]),
    "bmo": ("BMO", [("retail_banking", "Personal Banker"), ("risk_compliance", "Risk Analyst")]),
    "scotiabank": ("Scotiabank", [("retail_banking", "Customer Service Representative"), ("risk_compliance", "AML Analyst")]),
    "jpmorgan": ("JPMorgan Chase", [("swe", "Software Engineer II"), ("retail_banking", "Personal Banker"), ("risk_compliance", "Controls Analyst")]),
}

ROLE_SIGNALS = {
    "swe": ["analytical_problem_solving", "ownership_execution", "impact_results"],
    "data_analytics": ["analytical_problem_solving", "structured_thinking", "impact_results"],
    "retail_banking": ["collaboration_communication", "ownership_execution", "impact_results"],
    "risk_compliance": ["ownership_execution", "analytical_problem_solving", "structured_thinking"],
    "consulting_case_pei": ["structured_thinking", "analytical_problem_solving", "collaboration_communication"],
}

ANSWERS = {
    "swe": {
        "strong": "I clarified requirements, latency targets, edge cases, and ownership boundaries, then compared synchronous and async designs. I chose the safer approach, added tests, monitoring, rollback, and post-launch dashboards. The release reduced incident risk and improved customer-facing reliability.",
        "average": "I would choose a common data structure, test empty and large inputs, and explain the complexity. I can compare another approach if the interviewer gives the exact constraints.",
        "weak": "I would start coding quickly and fix issues later if tests fail. I do not know the complexity yet, but I think the solution should work.",
        "risk": "I would ship the feature quickly without much monitoring because speed matters more than rollback planning unless customers complain.",
    },
    "data_analytics": {
        "strong": "I would define the metric, check source tables and joins, segment the population, test data quality, and quantify uncertainty before recommending a decision to stakeholders.",
        "average": "I would look at the dashboard, compare the current month to last month, and ask for more data before making a recommendation.",
        "weak": "I would pull a chart and tell the team the number changed, but I am not sure which table or join created the metric.",
        "risk": "I would choose the number that supports the business goal and avoid mentioning uncertainty because stakeholders want a simple answer.",
    },
    "retail_banking": {
        "strong": "I would listen to the client, confirm their need, explain options clearly, check suitability and compliance, and escalate if the issue affects trust or account safety.",
        "average": "I would be polite, ask what the customer needs, and explain the product I think fits best. If they are upset, I would ask my manager.",
        "weak": "I would complete the sale quickly because targets matter and the customer can read the details later.",
        "risk": "I would push the highest target product first and avoid discussing drawbacks unless the customer asks directly.",
    },
    "risk_compliance": {
        "strong": "I would document the control gap, estimate exposure, identify impacted customers and processes, escalate through the risk channel, implement a temporary control, and monitor recurrence after root cause fix.",
        "average": "I would report the risk to my manager, review the policy, and help the team fix the issue once we know what happened.",
        "weak": "I would wait until the issue becomes clearer before escalating because raising too many risks can slow the team down.",
        "risk": "I would keep the issue informal if the business owner promises to fix it later, so the team can avoid extra governance work.",
    },
    "consulting_case_pei": {
        "strong": "I would frame the client objective, split the issue tree into revenue, cost, market, and execution drivers, test hypotheses with data, then recommend a prioritized action with risks and next steps.",
        "average": "I would look at revenue and costs, ask for more data, and recommend improving marketing if revenue is low or cutting cost if cost is high.",
        "weak": "I would ask the client what they want and then suggest a few ideas based on what seems easiest.",
        "risk": "I would give a confident recommendation early and avoid spending time on assumptions because the client wants speed.",
    },
}

RECOMMENDATION = {
    "strong": "advance",
    "average": "hold",
    "weak": "human_review_required",
    "risk": "human_review_required",
}


def unsupported_checks(company: str, role: str, quality: str) -> list[str]:
    checks = [
        "Do not claim this fixture is an official company interview transcript.",
        "Do not cite private material.",
    ]
    if quality in {"weak", "risk"}:
        checks.append("Must require human review and avoid automated rejection.")
    if role in {"retail_banking", "risk_compliance"}:
        checks.append("Must preserve suitability, trust, compliance, and controls context.")
    if company == "generic":
        checks.append("Must not infer a company lens.")
    return checks


def make_case(
    case_id: str,
    company: str,
    display: str,
    overlay: str,
    role_title: str,
    quality: str,
    group: str | None = None,
    answer_override: str | None = None,
) -> dict:
    case = {
        "case_id": case_id,
        "company": display,
        "role_title": role_title,
        "candidate_answer": answer_override or ANSWERS[overlay][quality],
        "expected_company": company,
        "expected_overlay": overlay,
        "expected_recommendation": RECOMMENDATION[quality],
        "expected_confidence_min": 0.8 if company != "generic" else 0.55,
        "expected_signals": ROLE_SIGNALS[overlay],
        "unsupported_claim_checks": unsupported_checks(company, overlay, quality),
    }
    if group:
        case["same_answer_group"] = group
    return case


def build_cases() -> list[dict]:
    cases = []
    for company, (display, roles) in COMPANY_ROLES.items():
        for index in range(20):
            overlay, role_title = roles[index % len(roles)]
            quality = ("strong", "average", "weak", "risk")[index % 4]
            group = None
            if index < 4:
                group = f"cross_company_{overlay}_{quality}"
            if index in {4, 5, 6, 7}:
                group = f"cross_role_{company}_{quality}"
            cases.append(
                make_case(
                    f"p2c-{len(cases)+1:03d}-{company}-{overlay}-{quality}",
                    company,
                    display,
                    overlay,
                    role_title,
                    quality,
                    group,
                )
            )
    generic_inputs = [
        ("Unknown Fintech", "Data Analyst", "data_analytics", "strong"),
        ("Unknown Retail Bank", "Customer Service Representative", "retail_banking", "average"),
        ("Unknown Software Company", "Software Engineer", "swe", "average"),
        ("Unknown Consulting Firm", "Business Analyst", "consulting_case_pei", "average"),
        ("Unknown Bank", "Risk Analyst", "risk_compliance", "strong"),
    ]
    for display, role_title, overlay, quality in generic_inputs:
        cases.append(
            make_case(
                f"p2c-{len(cases)+1:03d}-generic-{overlay}-{quality}",
                "generic",
                display,
                overlay,
                role_title,
                "weak" if quality == "strong" else quality,
                f"generic_fallback_{overlay}",
            )
        )
    cross_role_answer = (
        "I would first clarify the goal, define success criteria, identify the key risk or constraint, "
        "compare options, communicate trade-offs to stakeholders, and monitor the outcome after the decision."
    )
    cross_role_cases = [
        ("Amazon", "amazon", "Software Engineer", "swe"),
        ("Google", "google", "Data Analyst", "data_analytics"),
        ("TD Bank", "td", "Customer Service Representative", "retail_banking"),
        ("RBC", "rbc", "Risk Analyst", "risk_compliance"),
        ("McKinsey", "mckinsey", "Business Analyst", "consulting_case_pei"),
    ]
    for display, company, role_title, overlay in cross_role_cases:
        cases.append(
            make_case(
                f"p2c-{len(cases)+1:03d}-cross-role-{company}-{overlay}",
                company,
                display,
                overlay,
                role_title,
                "average",
                "cross_role_shared_average",
                answer_override=cross_role_answer,
            )
        )
    return cases


def main() -> int:
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    cases = build_cases()
    OUT_PATH.write_text(json.dumps({"version": "0.2.0-phase-2c-production-gates", "cases": cases}, indent=2) + "\n")
    print(f"wrote_cases={len(cases)} path={OUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
