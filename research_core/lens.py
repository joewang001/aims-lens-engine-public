from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

REQUIRED_TOP_LEVEL = {
    "lens_id", "lens_type", "maturity", "role", "interview_stage",
    "competency_dimensions", "followup_taxonomy", "evidence_register",
    "constraints", "uncertainty_settings",
}


def validate_interview_dna(data: Dict[str, Any]) -> None:
    missing = REQUIRED_TOP_LEVEL - set(data)
    if missing:
        raise ValueError(f"missing Interview DNA fields: {sorted(missing)}")
    if data["lens_type"] not in {"company", "industry", "derived", "archetype", "general"}:
        raise ValueError("unsupported lens_type")
    if data["maturity"] not in {"exploratory", "reviewed_practice", "evaluation_ready", "empirically_supported"}:
        raise ValueError("unsupported maturity")
    if not data["followup_taxonomy"]:
        raise ValueError("followup_taxonomy must not be empty")
    settings = data["uncertainty_settings"]
    for key in ("support_ceiling", "abstention_threshold"):
        if key in settings and not 0 <= float(settings[key]) <= 1:
            raise ValueError(f"{key} must be in [0,1]")
    if "backoff_discount" in settings and not 0 < float(settings["backoff_discount"]) <= 1:
        raise ValueError("backoff_discount must be in (0,1]")


def load_lens(path: str | Path) -> Dict[str, Any]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    validate_interview_dna(data)
    return data
