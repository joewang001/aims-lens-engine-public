#!/usr/bin/env python3
"""Build B2C interview-prep improvement plans from template assets."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import mean


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_ROOT = ROOT / "interview_prep_templates"

AIMS_DIMS = [
    "structured_thinking",
    "analytical_problem_solving",
    "ownership_execution",
    "impact_results",
    "collaboration_communication",
    "growth_mindset",
]

DIMENSION_LABELS = {
    "structured_thinking": "Structured Thinking",
    "analytical_problem_solving": "Analytical Problem Solving",
    "ownership_execution": "Ownership and Execution",
    "impact_results": "Impact and Results",
    "collaboration_communication": "Collaboration and Communication",
    "growth_mindset": "Growth Mindset",
}

DEFAULT_DIMENSION_ISSUES = {
    "structured_thinking": "The answer needs a clearer opening structure, sharper prioritization, and stronger fit to the role question.",
    "analytical_problem_solving": "The answer needs clearer decision logic, metric reasoning, trade-off analysis, or root-cause explanation.",
    "ownership_execution": "The answer needs stronger personal ownership, execution detail, and follow-through under constraints.",
    "impact_results": "The answer needs clearer baseline, result, attribution, and business impact.",
    "collaboration_communication": "The answer needs cleaner communication, stakeholder framing, and concise professional wording.",
    "growth_mindset": "The answer needs stronger reflection, learning loop, and evidence of improvement after feedback.",
}

DEFAULT_SUCCESS_STANDARDS = {
    "structured_thinking": "Open with context, objective, and a two or three point answer structure within 20 seconds.",
    "analytical_problem_solving": "Explain metric, decision, trade-off, and business implication in one coherent answer.",
    "ownership_execution": "Make personal responsibility, action, obstacle, and follow-through explicit.",
    "impact_results": "State baseline, action, measurable result, and attribution without exaggeration.",
    "collaboration_communication": "Use concise signposting and role-appropriate language so the interviewer can follow the answer on the first pass.",
    "growth_mindset": "State what was learned, what changed afterward, and how the lesson improved later performance.",
}

MCKINSEY_DIMENSION_ISSUES = {
    "structured_thinking": "Case opening or issue tree is not yet specific enough to the business objective.",
    "analytical_problem_solving": "Analysis, exhibit interpretation, or math needs clearer logic and business implication.",
    "ownership_execution": "The answer needs stronger case leadership, next-step control, and recovery when challenged.",
    "impact_results": "The response needs a sharper business recommendation, impact ranking, and practical next step.",
    "collaboration_communication": "The answer needs cleaner top-down communication and stronger interviewer alignment.",
    "growth_mindset": "The user needs a tighter practice loop from feedback to targeted drill to measured improvement.",
}

MCKINSEY_SUCCESS_STANDARDS = {
    "structured_thinking": "Open with objective, tailored structure, and prioritized first branch within two minutes.",
    "analytical_problem_solving": "State formula or exhibit takeaway first, then explain calculation and business meaning.",
    "ownership_execution": "After each finding, state the next analysis step without waiting passively.",
    "impact_results": "End with a clear recommendation supported by evidence, risk, and next step.",
    "collaboration_communication": "Use concise signposting so the interviewer can follow the answer on the first pass.",
    "growth_mindset": "Complete a reflection after each mock and reduce recurrence of the same issue in the next mock.",
}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_company(value: str) -> str:
    text = (value or "").strip().lower()
    if text in {"mckinsey", "mckinsey & company", "mckinsey and company"}:
        return "mckinsey"
    if text in {"amazon", "aws"}:
        return "amazon"
    if text in {"google", "alphabet"}:
        return "google"
    if text in {"microsoft", "msft"}:
        return "microsoft"
    if text in {"rbc", "royal bank of canada"}:
        return "rbc"
    return text or "generic"


def normalize_interview_type(value: str) -> str:
    text = (value or "").strip().lower().replace("_", " ")
    if "case" in text:
        return "case"
    if "behavior" in text:
        return "behavioral"
    if "product" in text:
        return "product"
    if "risk" in text or "compliance" in text:
        return "risk_compliance"
    return text or "general"


def normalize_role_family(value: str) -> str:
    text = (value or "").strip().lower().replace("-", "_").replace(" ", "_")
    aliases = {
        "marketing": "marketing_growth",
        "growth_marketing": "marketing_growth",
        "product": "product_management",
        "pm": "product_management",
        "risk": "risk_compliance",
        "compliance": "risk_compliance",
        "consulting": "consulting_case",
        "case": "consulting_case",
        "analytics": "data_analytics",
        "data": "data_analytics",
    }
    return aliases.get(text, text or "general")


def is_mckinsey_case(company: str, interview_type: str) -> bool:
    return normalize_company(company) == "mckinsey" and normalize_interview_type(interview_type) == "case"


def template_dir_for(company: str, interview_type: str) -> Path:
    if is_mckinsey_case(company, interview_type):
        return TEMPLATE_ROOT / "mckinsey_case"
    return TEMPLATE_ROOT / "generic"


def clean_scores(scores: dict) -> dict[str, float]:
    cleaned = {}
    for dim in AIMS_DIMS:
        try:
            value = float(scores.get(dim, 0.0))
        except (TypeError, ValueError):
            value = 0.0
        cleaned[dim] = round(max(0.0, min(10.0, value)), 1)
    return cleaned


def normalize_plan_tier(value: str | None) -> str:
    text = (value or "").strip().lower()
    if text in {"free", "trial", "guest"}:
        return "free"
    return "paid"


def selected_plan(days_until_interview: int | None, plan_selector: dict, plan_tier: str) -> dict:
    if plan_tier == "free":
        plan_key = "3_day_mini_plan"
    elif days_until_interview is not None and days_until_interview >= 22:
        plan_key = "30_day_plan"
    else:
        plan_key = "14_day_plan"
    selected = plan_selector[plan_key]
    return {
        "plan_key": plan_key,
        "template_file": selected["template_file"],
        "required_time_per_day_minutes": selected["required_time_per_day_minutes"],
        "selection_reason": selected["best_for"],
    }


def entitlement_policy(plan_tier: str, selected: dict) -> dict:
    if plan_tier == "free":
        return {
            "plan_tier": "free",
            "mock_allowance": "one mock",
            "diagnosis_depth": "brief",
            "included_features": [
                "one mock",
                "brief diagnosis",
                "3-day mini plan",
            ],
            "gated_features": [
                "14/30 day improvement plan",
                "daily drills",
                "replay scoring",
                "case-specific rubric",
                "weekly progress report",
            ],
            "upsell_trigger": "Unlock the full improvement plan to get daily drills, replay scoring, role/company rubric, and weekly progress tracking.",
        }
    return {
        "plan_tier": "paid",
        "mock_allowance": "subscription or package dependent",
        "diagnosis_depth": "full",
        "included_features": [
            "14/30 day improvement plan",
            "daily drills",
            "replay scoring",
            "case-specific rubric",
            "weekly progress report",
        ],
        "gated_features": [],
        "upsell_trigger": "",
    }


def matching_modules(dim: str, modules: list[dict]) -> list[dict]:
    return [
        module
        for module in modules
        if dim in module.get("primary_aims_dimensions", [])
    ]


def generic_dimension_mapping() -> dict:
    return load_json(TEMPLATE_ROOT / "generic" / "aims_mapping.json")


def build_priority_points(
    scores: dict[str, float],
    mapping: dict,
    template: dict,
    *,
    mckinsey_case: bool,
) -> list[dict]:
    sorted_dims = sorted(AIMS_DIMS, key=lambda dim: (scores[dim], AIMS_DIMS.index(dim)))
    issues = MCKINSEY_DIMENSION_ISSUES if mckinsey_case else DEFAULT_DIMENSION_ISSUES
    standards = MCKINSEY_SUCCESS_STANDARDS if mckinsey_case else DEFAULT_SUCCESS_STANDARDS
    points = []
    for dim in sorted_dims[:3]:
        dim_mapping = mapping["aims_dimensions"].get(dim, {})
        modules = matching_modules(dim, template.get("modules", []))
        drills = []
        for drill in dim_mapping.get("drills", []):
            if drill not in drills:
                drills.append(drill)
        for module in modules:
            for drill in module.get("recommended_drills", []):
                if drill not in drills:
                    drills.append(drill)
        points.append(
            {
                "dimension": dim,
                "label": DIMENSION_LABELS[dim],
                "current_score": scores[dim],
                "issue": dim_mapping.get("weak_signal") or issues[dim],
                "recommended_drills": drills[:4],
                "next_action": f"Run {drills[0] if drills else 'a focused answer drill'} and record the result in the reflection template.",
                "success_standard": dim_mapping.get("success_standard") or standards[dim],
            }
        )
    return points


def build_daily_drills(priority_points: list[dict], selected: dict, *, mckinsey_case: bool) -> list[dict]:
    plan_key = selected["plan_key"]
    if plan_key == "3_day_mini_plan":
        points = priority_points[:1]
        return [
            {
                "day_range": "Day 1",
                "focus_dimension": points[0]["dimension"],
                "drills": points[0]["recommended_drills"][:1],
                "output": "Rewrite one weak answer and identify the missing evidence.",
            },
            {
                "day_range": "Day 2",
                "focus_dimension": points[0]["dimension"],
                "drills": points[0]["recommended_drills"][1:2] or points[0]["recommended_drills"][:1],
                "output": "Record one concise answer and compare it against the success standard.",
            },
            {
                "day_range": "Day 3",
                "focus_dimension": "mini_plan_review",
                "drills": ["Brief diagnosis review", "Next paid-plan focus selection"],
                "output": "One next-step recommendation for a 14-day or 30-day plan.",
            },
        ]
    plan_days = 30 if plan_key == "30_day_plan" else 14
    fourteen_day_ranges = ["Days 1-2", "Days 3-4", "Days 5-6"]
    thirty_day_ranges = ["Days 1-5", "Days 6-10", "Days 11-15"]
    drills = []
    for index, point in enumerate(priority_points, start=1):
        day_range = thirty_day_ranges[index - 1] if plan_days == 30 else fourteen_day_ranges[index - 1]
        drills.append(
            {
                "day_range": day_range,
                "focus_dimension": point["dimension"],
                "drills": point["recommended_drills"][:2],
                "output": "Completed drill notes plus one reflection entry.",
            }
        )
    drills.append(
        {
            "day_range": "Final week" if plan_days == 30 else "Final 2 days",
            "focus_dimension": "integrated_mock_performance",
            "drills": [
                "Full mock case" if mckinsey_case else "Full company-role mock",
                "Priority improvement review",
                "Next mock focus selection",
            ],
            "output": "Updated Priority Improvement Points and next mock recommendation.",
        }
    )
    return drills


def load_overlay_drills(company: str, role_family: str) -> tuple[list[dict], list[dict]]:
    company_templates = load_json(TEMPLATE_ROOT / "generic" / "company_lens_drills.json")
    role_templates = load_json(TEMPLATE_ROOT / "generic" / "role_family_drills.json")
    company_key = normalize_company(company)
    role_key = normalize_role_family(role_family)
    company_drills = company_templates.get(company_key) or company_templates["generic"]
    role_drills = role_templates.get(role_key) or role_templates["general"]
    return company_drills, role_drills


def build_overlay_drills(
    priority_points: list[dict],
    overlay_drills: list[dict],
    *,
    max_items: int = 3,
) -> list[dict]:
    priority_dims = {point["dimension"] for point in priority_points}
    selected = []
    for drill in overlay_drills:
        if priority_dims.intersection(drill.get("aims_dimensions", [])):
            selected.append(drill)
    for drill in overlay_drills:
        if drill not in selected:
            selected.append(drill)
    return selected[:max_items]


def build_next_mock_recommendation(priority_points: list[dict], company: str, interview_type: str, role_family: str) -> dict:
    focus = [point["dimension"] for point in priority_points[:2]]
    labels = [point["label"] for point in priority_points[:2]]
    normalized_company = normalize_company(company)
    normalized_interview = normalize_interview_type(interview_type)
    normalized_role = normalize_role_family(role_family)
    if is_mckinsey_case(company, interview_type):
        instruction = (
            f"Run a McKinsey-style case mock that specifically tests {', '.join(labels)}. "
            "Use one question at a time, keep prompts concise, and force synthesis after each major case module."
        )
        mock_mode = "case_module_then_full_mock"
        stop_condition = "End after the planned case module sequence or 10 scored candidate answers, whichever comes first."
    else:
        company_label = normalized_company.upper() if normalized_company == "rbc" else normalized_company.title()
        role_label = normalized_role.replace("_", " ")
        instruction = (
            f"Run a {company_label} {role_label} mock that specifically tests {', '.join(labels)}. "
            "Use the company lens, the JD signals, and one question at a time. Ask follow-ups that verify evidence, not generic confidence."
        )
        mock_mode = "company_role_behavioral_mock"
        stop_condition = "End after 8 to 10 scored candidate answers or when the top two weak dimensions have both been tested."
    return {
        "target_company": normalized_company,
        "interview_type": normalized_interview,
        "mock_mode": mock_mode,
        "focus_dimensions": focus,
        "role_family": normalized_role,
        "interviewer_instruction": instruction,
        "stop_condition": stop_condition,
    }


def build_interview_prep_plan(payload: dict) -> dict:
    company = payload.get("target_company") or payload.get("company") or "mckinsey"
    interview_type = payload.get("interview_type") or "case"
    role_family = payload.get("role_family") or payload.get("role") or payload.get("job_family") or "general"
    plan_tier = normalize_plan_tier(payload.get("plan_tier") or payload.get("subscription_tier"))
    template_dir = template_dir_for(company, interview_type)
    template = load_json(template_dir / "improvement_plan_template.json")
    mapping = load_json(template_dir / "aims_mapping.json") if (template_dir / "aims_mapping.json").exists() else generic_dimension_mapping()
    scores = clean_scores(payload.get("aims_scores") or {})
    days_until_interview = payload.get("days_until_interview")
    if days_until_interview is not None:
        days_until_interview = int(days_until_interview)
    selected = selected_plan(days_until_interview, template["plan_selector"], plan_tier)
    mckinsey_case = is_mckinsey_case(company, interview_type)
    priority_points = build_priority_points(scores, mapping, template, mckinsey_case=mckinsey_case)
    company_drill_pool, role_drill_pool = load_overlay_drills(company, role_family)
    company_specific_drills = [] if mckinsey_case else build_overlay_drills(priority_points, company_drill_pool)
    role_specific_drills = [] if mckinsey_case else build_overlay_drills(priority_points, role_drill_pool)
    average_score = round(mean(scores.values()), 1)
    entitlement = entitlement_policy(plan_tier, selected)
    return {
        "plan_id": template["plan_id"],
        "template_status": "community_template",
        "target_company": normalize_company(company),
        "interview_type": normalize_interview_type(interview_type),
        "role_family": normalize_role_family(role_family),
        "selected_plan": selected,
        "entitlement": entitlement,
        "average_aims_score": average_score,
        "priority_improvement_points": priority_points,
        "company_specific_drills": company_specific_drills,
        "role_specific_drills": role_specific_drills,
        "daily_drills": build_daily_drills(priority_points, selected, mckinsey_case=mckinsey_case),
        "reflection_template": str((template_dir / "reflection_template.md").relative_to(ROOT)),
        "next_mock_recommendation": build_next_mock_recommendation(priority_points, company, interview_type, role_family),
        "plan_generation_signals": {
            "weakest_aims_dimensions": [point["dimension"] for point in priority_points],
            "company_lens_used": normalize_company(company),
            "role_family_used": normalize_role_family(role_family),
            "job_description_signals": payload.get("job_description_signals", []),
            "recent_feedback": payload.get("recent_feedback", []),
        },
        "product_notice": (
            "Interview prep guidance only. This plan is for deliberate practice and should not be used "
            "as a hiring decision or offer prediction."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build an interview prep improvement plan.")
    parser.add_argument("--request", required=True, help="Path to JSON request payload.")
    args = parser.parse_args()
    payload = load_json(Path(args.request))
    print(json.dumps(build_interview_prep_plan(payload), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
