from __future__ import annotations
from typing import Mapping, Sequence


def generate_explanation(primary: str, lens_type: str, lens_version: str, maturity: str, factors: Mapping[str,str], borrowed_levels: Sequence[str]) -> str:
    parts=[f"Practice priority '{primary}' was produced using a {lens_type} Lens (version {lens_version}).",f"Evidence maturity: {maturity}."]
    if borrowed_levels: parts.append("Broader context contributed through: "+", ".join(borrowed_levels)+".")
    active=[f"{k}={v}" for k,v in factors.items() if v]
    if active: parts.append("Primary declared factors: "+"; ".join(active)+".")
    parts.append("This is a practice priority, not a prediction of a specific employer's interview process or hiring decision.")
    return " ".join(parts)
