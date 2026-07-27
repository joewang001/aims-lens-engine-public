#!/usr/bin/env python3
"""Validate the cross-company candidate persona fit matrix."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MATRIX_PATH = ROOT / "candidate_personas" / "cross_company_fit_matrix.json"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    matrix = load_json(MATRIX_PATH)
    failures: list[str] = []

    source_policy = matrix.get("source_policy") or {}
    if not source_policy.get("synthetic"):
        failures.append("source_policy.synthetic must be true")
    if source_policy.get("contains_private_candidate_data"):
        failures.append("private candidate data is not allowed")

    company_packs = matrix.get("company_packs") or {}
    if not company_packs:
        failures.append("company_packs must not be empty")

    known_personas_by_pack: dict[str, set[str]] = {}
    for pack_key, pack in company_packs.items():
        fixture_path = ROOT / (pack.get("fixture_path") or "")
        if not fixture_path.exists():
            failures.append(f"{pack_key}: fixture_path does not exist: {fixture_path}")
            continue
        fixture = load_json(fixture_path)
        ids = {persona.get("persona_id") for persona in fixture.get("personas") or []}
        ids.discard(None)
        known_personas_by_pack[pack_key] = ids
        if not ids:
            failures.append(f"{pack_key}: fixture has no personas")

    contract = matrix.get("qa_runner_contract") or {}
    recommendation_order = contract.get("recommendation_order") or []
    allowed_recommendations = set(recommendation_order)
    required_case_keys = set(contract.get("required_case_keys") or [])
    if not allowed_recommendations:
        failures.append("qa_runner_contract.recommendation_order must not be empty")
    if not required_case_keys:
        failures.append("qa_runner_contract.required_case_keys must not be empty")

    rows = matrix.get("baseline_personas") or []
    if not rows:
        failures.append("baseline_personas must not be empty")

    seen_canonical = set()
    for row in rows:
        canonical_id = row.get("canonical_persona_id")
        if not canonical_id:
            failures.append("baseline row missing canonical_persona_id")
            continue
        if canonical_id in seen_canonical:
            failures.append(f"duplicate canonical_persona_id: {canonical_id}")
        seen_canonical.add(canonical_id)

        pack_persona_ids = row.get("pack_persona_ids") or {}
        expected_company_fit = row.get("expected_company_fit") or {}
        for pack_key in company_packs:
            persona_id = pack_persona_ids.get(pack_key)
            if not persona_id:
                failures.append(f"{canonical_id}: missing pack_persona_ids.{pack_key}")
            elif persona_id not in known_personas_by_pack.get(pack_key, set()):
                failures.append(f"{canonical_id}: persona id not found for {pack_key}: {persona_id}")

            case = expected_company_fit.get(pack_key)
            if not case:
                failures.append(f"{canonical_id}: missing expected_company_fit.{pack_key}")
                continue

            missing_case_keys = sorted(required_case_keys - set(case))
            if missing_case_keys:
                failures.append(f"{canonical_id}/{pack_key}: missing keys {missing_case_keys}")

            recommendation = case.get("expected_recommendation")
            if recommendation not in allowed_recommendations:
                failures.append(f"{canonical_id}/{pack_key}: invalid expected_recommendation {recommendation!r}")

            score_band = case.get("expected_score_band") or {}
            min_score = score_band.get("overall_min")
            max_score = score_band.get("overall_max")
            if not isinstance(min_score, (int, float)) or not isinstance(max_score, (int, float)):
                failures.append(f"{canonical_id}/{pack_key}: expected_score_band must contain numeric overall_min and overall_max")
            elif not (0 <= min_score <= max_score <= 10):
                failures.append(f"{canonical_id}/{pack_key}: invalid expected_score_band {score_band!r}")

            for list_key in ("must_show", "risk_flags"):
                value = case.get(list_key)
                if not isinstance(value, list) or not value or not all(isinstance(item, str) and item for item in value):
                    failures.append(f"{canonical_id}/{pack_key}: {list_key} must be a non-empty string list")

    result = {
        "status": "fail" if failures else "ok",
        "matrix": str(MATRIX_PATH.relative_to(ROOT)),
        "company_packs": sorted(company_packs),
        "baseline_persona_count": len(rows),
        "failures": failures,
    }
    print(json.dumps(result, indent=2))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
