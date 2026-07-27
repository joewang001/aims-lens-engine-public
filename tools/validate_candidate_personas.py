#!/usr/bin/env python3
"""Validate synthetic candidate persona fixtures."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
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


def validate_fixture(path: Path) -> list[str]:
    data = load_json(path)
    failures = []
    if not data.get("source_policy", {}).get("synthetic"):
        failures.append(f"{path}: source_policy.synthetic must be true")
    if data.get("source_policy", {}).get("contains_private_candidate_data"):
        failures.append(f"{path}: private candidate data is not allowed")
    personas = data.get("personas") or []
    if not personas:
        failures.append(f"{path}: personas must not be empty")
    seen = set()
    for persona in personas:
        persona_id = persona.get("persona_id")
        if not persona_id:
            failures.append(f"{path}: persona missing persona_id")
        if persona_id in seen:
            failures.append(f"{path}: duplicate persona_id {persona_id}")
        seen.add(persona_id)
        prompt = persona.get("mock_prompt") or ""
        if len(prompt.split()) < 25:
            failures.append(f"{path}: {persona_id} mock_prompt is too short")
        profile = persona.get("capability_profile") or {}
        missing = [dim for dim in AIMS_DIMS if dim not in profile]
        if missing:
            failures.append(f"{path}: {persona_id} missing dimensions {missing}")
        for dim in AIMS_DIMS:
            value = profile.get(dim)
            if not isinstance(value, (int, float)) or not 0 <= value <= 10:
                failures.append(f"{path}: {persona_id} invalid {dim}={value!r}")
        company_fit = persona.get("company_fit") or {}
        if not company_fit.get("strong_fit") or not company_fit.get("weak_fit"):
            failures.append(f"{path}: {persona_id} needs strong_fit and weak_fit")
    return failures


def validate_cross_links(files: list[Path]) -> list[str]:
    failures = []
    known_ids = set()
    payloads = {}
    for file_path in files:
        data = load_json(file_path)
        payloads[file_path] = data
        for persona in data.get("personas") or []:
            known_ids.add(persona.get("persona_id"))
    for file_path, data in payloads.items():
        for persona in data.get("personas") or []:
            linked = persona.get("linked_persona_id")
            if linked and linked not in known_ids:
                failures.append(f"{file_path}: {persona.get('persona_id')} linked_persona_id not found: {linked}")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate candidate persona fixture JSON files.")
    parser.add_argument(
        "--path",
        default=str(ROOT / "candidate_personas"),
        help="Fixture file or directory.",
    )
    args = parser.parse_args()
    target = Path(args.path)
    files = [target] if target.is_file() else sorted(target.glob("*/personas.json"))
    failures = []
    for file_path in files:
        failures.extend(validate_fixture(file_path))
    failures.extend(validate_cross_links(files))
    result = {
        "status": "fail" if failures else "ok",
        "files": [str(path.relative_to(ROOT)) for path in files],
        "failures": failures,
    }
    print(json.dumps(result, indent=2))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
