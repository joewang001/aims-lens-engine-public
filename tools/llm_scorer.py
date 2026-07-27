#!/usr/bin/env python3
"""Optional OpenAI-backed scorer for Phase 3B.

The deterministic scorer remains the safe default. This module is used only
when AIMS_SCORER_MODE=llm and OPENAI_API_KEY is present.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from copy import deepcopy

from env_loader import load_env_file
from run_scoring_harness import validate_screening_report


load_env_file()

OPENAI_RESPONSES_URL = "https://api.openai.com/v1/responses"
DEFAULT_MODEL = os.environ.get("OPENAI_MODEL", "gpt-5.4-mini")


SCREENING_REPORT_RESPONSE_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "report_id",
        "tenant_id",
        "candidate_id",
        "role",
        "lens_id",
        "lens_status",
        "aims_scores",
        "company_lens_adjustments",
        "strengths",
        "risks",
        "recommended_follow_ups",
        "signal_fusion",
        "screening_recommendation",
        "confidence",
        "human_review_required",
        "fairness_review_flags",
        "evidence_notice",
    ],
    "properties": {
        "report_id": {"type": "string"},
        "tenant_id": {"type": "string"},
        "candidate_id": {"type": "string"},
        "role": {"type": "string"},
        "lens_id": {"type": "string"},
        "lens_status": {
            "type": "string",
            "enum": ["FULLY_DISTILLED", "DERIVED_LENS", "LIGHTWEIGHT_SCAN", "GENERIC_AIMS"],
        },
        "aims_scores": {
            "type": "object",
            "additionalProperties": False,
            "required": [
                "structured_thinking",
                "analytical_problem_solving",
                "ownership_execution",
                "impact_results",
                "collaboration_communication",
                "growth_mindset",
            ],
            "properties": {
                "structured_thinking": {"type": "number"},
                "analytical_problem_solving": {"type": "number"},
                "ownership_execution": {"type": "number"},
                "impact_results": {"type": "number"},
                "collaboration_communication": {"type": "number"},
                "growth_mindset": {"type": "number"},
            },
        },
        "company_lens_adjustments": {"type": "array", "items": {"type": "string"}},
        "strengths": {"type": "array", "items": {"type": "string"}},
        "risks": {"type": "array", "items": {"type": "string"}},
        "recommended_follow_ups": {"type": "array", "items": {"type": "string"}},
        "signal_fusion": {
            "type": "object",
            "additionalProperties": False,
            "required": [
                "company_lens_signal",
                "jd_role_signal",
                "candidate_answer_signal",
                "combined_question_strategy",
                "evidence_gap_matrix",
            ],
            "properties": {
                "company_lens_signal": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["company", "overlay", "lens_status", "priorities"],
                    "properties": {
                        "company": {"type": "string"},
                        "overlay": {"type": "string"},
                        "lens_status": {"type": "string"},
                        "priorities": {"type": "array", "items": {"type": "string"}},
                    },
                },
                "jd_role_signal": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["role", "requirements", "jd_excerpt"],
                    "properties": {
                        "role": {"type": "string"},
                        "requirements": {"type": "array", "items": {"type": "string"}},
                        "jd_excerpt": {"type": "string"},
                    },
                },
                "candidate_answer_signal": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["strong_evidence", "gaps_or_risks", "weak_dimensions"],
                    "properties": {
                        "strong_evidence": {"type": "array", "items": {"type": "string"}},
                        "gaps_or_risks": {"type": "array", "items": {"type": "string"}},
                        "weak_dimensions": {"type": "array", "items": {"type": "string"}},
                    },
                },
                "combined_question_strategy": {"type": "string"},
                "evidence_gap_matrix": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "required": ["dimension", "score", "gap", "probe"],
                        "properties": {
                            "dimension": {"type": "string"},
                            "score": {"type": "number"},
                            "gap": {"type": "string"},
                            "probe": {"type": "string"},
                        },
                    },
                },
            },
        },
        "screening_recommendation": {
            "type": "string",
            "enum": ["advance", "hold", "human_review_required"],
        },
        "confidence": {"type": "number"},
        "human_review_required": {"type": "boolean"},
        "fairness_review_flags": {"type": "array", "items": {"type": "string"}},
        "evidence_notice": {"type": "string"},
    },
}


def llm_enabled() -> bool:
    return os.environ.get("AIMS_SCORER_MODE", "deterministic").lower() == "llm" and bool(
        os.environ.get("OPENAI_API_KEY")
    )


def _extract_output_text(response: dict) -> str:
    if isinstance(response.get("output_text"), str):
        return response["output_text"]
    chunks = []
    for item in response.get("output", []):
        if item.get("type") == "message":
            for content in item.get("content", []):
                if content.get("type") in {"output_text", "text"} and content.get("text"):
                    chunks.append(content["text"])
    return "\n".join(chunks)


def _post_openai(payload: dict, timeout: int) -> dict:
    api_key = os.environ["OPENAI_API_KEY"]
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        OPENAI_RESPONSES_URL,
        data=data,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"OpenAI response failed: {exc.code} {detail}") from exc


def sanitize_llm_report(report: dict, deterministic_report: dict) -> dict:
    sanitized = deepcopy(deterministic_report)
    for key in [
        "aims_scores",
        "company_lens_adjustments",
        "strengths",
        "risks",
        "recommended_follow_ups",
        "signal_fusion",
        "screening_recommendation",
        "confidence",
        "human_review_required",
        "fairness_review_flags",
        "evidence_notice",
    ]:
        if key in report:
            sanitized[key] = report[key]
    sanitized["report_id"] = deterministic_report["report_id"]
    sanitized["tenant_id"] = deterministic_report["tenant_id"]
    sanitized["candidate_id"] = deterministic_report["candidate_id"]
    sanitized["role"] = deterministic_report["role"]
    sanitized["lens_id"] = deterministic_report["lens_id"]
    sanitized["lens_status"] = deterministic_report["lens_status"]
    if sanitized.get("screening_recommendation") == "reject":
        sanitized["screening_recommendation"] = "human_review_required"
        sanitized["human_review_required"] = True
        sanitized.setdefault("risks", []).append("Automated rejection is blocked during limited pilot.")
    if deterministic_report.get("human_review_required"):
        sanitized["human_review_required"] = True
        if sanitized.get("screening_recommendation") == "advance":
            sanitized["screening_recommendation"] = "human_review_required"
    sanitized["confidence"] = round(max(0.0, min(1.0, float(sanitized.get("confidence", 0.0)))), 2)
    flags = list(sanitized.get("fairness_review_flags") or [])
    if not any("no automated rejection" in flag.lower() for flag in flags):
        flags.append("Limited pilot output; no automated rejection or final hiring decision.")
    sanitized["fairness_review_flags"] = flags
    errors = validate_screening_report(sanitized)
    if errors:
        raise ValueError("; ".join(errors))
    return sanitized


def score_with_llm(payload: dict, route: dict, deterministic_report: dict, timeout: int = 45) -> dict:
    if not llm_enabled():
        return {
            "scorer_mode": "deterministic",
            "screening_report": deterministic_report,
            "llm_notice": "LLM scorer not enabled; set AIMS_SCORER_MODE=llm and OPENAI_API_KEY.",
        }

    request_payload = {
        "model": DEFAULT_MODEL,
        "store": False,
        "instructions": (
            "You are an internal limited-pilot interview screening assistant. "
            "Return only a screening_report JSON object that follows the schema. "
            "Preserve and improve signal_fusion: company lens, JD/role, and candidate answer "
            "must jointly determine the combined_question_strategy. "
            "Do not emit automated rejection. If evidence is weak, risky, generic, "
            "or low confidence, set human_review_required true. Public community "
            "evidence is aggregate and lower-confidence, not official company policy."
        ),
        "input": json.dumps(
            {
                "candidate_request": payload,
                "route": route,
                "deterministic_baseline_report": deterministic_report,
            },
            indent=2,
        ),
        "text": {
            "format": {
                "type": "json_schema",
                "name": "screening_report",
                "strict": True,
                "schema": SCREENING_REPORT_RESPONSE_SCHEMA,
            }
        },
    }
    response = _post_openai(request_payload, timeout=timeout)
    text = _extract_output_text(response)
    if not text:
        raise RuntimeError("OpenAI response did not include output text")
    llm_report = json.loads(text)
    return {
        "scorer_mode": "llm",
        "model": DEFAULT_MODEL,
        "openai_response_id": response.get("id"),
        "screening_report": sanitize_llm_report(llm_report, deterministic_report),
    }
