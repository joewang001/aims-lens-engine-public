#!/usr/bin/env python3
"""Validate public company lens coverage and refresh readiness."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
COMPANY_LENSES = ROOT / "company_lenses"


@dataclass
class Finding:
    severity: str
    company: str
    code: str
    message: str


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"expected JSON object: {path}")
    return payload


def has_items(value: Any) -> bool:
    return isinstance(value, list) and len(value) > 0


def has_mapping(value: Any) -> bool:
    return isinstance(value, dict) and len(value) > 0


def company_dirs() -> list[Path]:
    return sorted(
        path
        for path in COMPANY_LENSES.iterdir()
        if path.is_dir() and not path.name.startswith("_")
    )


def days_since(source_cutoff: str) -> int | None:
    try:
        cutoff = date.fromisoformat(source_cutoff)
    except ValueError:
        return None
    return (date.today() - cutoff).days


def validate_company(path: Path, *, max_stale_days: int) -> list[Finding]:
    findings: list[Finding] = []
    company = path.name
    profile_path = path / "profile.json"
    question_bank_path = path / "question_bank.json"
    rubric_path = path / "rubric.md"
    limits_path = path / "limits.md"
    evidence_path = path / "evidence.md"
    validation_path = path / "validation_report.md"
    role_overlay_path = path / "role_overlays"

    if not profile_path.is_file():
        return [Finding("blocker", company, "missing_profile", "profile.json is required.")]

    profile = load_json(profile_path)
    status = str(profile.get("lens_status", ""))

    required_profile_fields = {
        "lens_id",
        "company",
        "lens_status",
        "version",
        "source_cutoff",
        "aims_weighting",
        "hiring_signals",
        "anti_signals",
        "evidence_summary",
        "honest_limits",
    }
    for field in sorted(required_profile_fields):
        if field not in profile:
            findings.append(Finding("blocker", company, "missing_profile_field", f"Missing `{field}`."))

    dimension_checks = [
        ("company_says", has_items(profile.get("culture_principles")) and evidence_path.is_file()),
        ("company_judges", has_items(profile.get("hiring_signals")) and rubric_path.is_file()),
        ("company_asks", question_bank_path.is_file()),
        ("evidence_valued", has_mapping(profile.get("aims_weighting")) and rubric_path.is_file()),
        ("risk_warnings", has_items(profile.get("anti_signals")) and limits_path.is_file()),
        ("honest_unknowns", has_items(profile.get("honest_limits")) and validation_path.is_file()),
    ]
    for code, ok in dimension_checks:
        if not ok:
            findings.append(Finding("blocker", company, code, "Seven-dimension coverage is incomplete."))

    if role_overlay_path.is_dir() and any(role_overlay_path.glob("*.json")):
        pass
    elif status == "LIGHTWEIGHT_SCAN":
        findings.append(
            Finding(
                "warning",
                company,
                "role_variation_lightweight",
                "No role overlay yet; acceptable for LIGHTWEIGHT_SCAN, but expansion should add one.",
            )
        )
    else:
        findings.append(Finding("blocker", company, "role_variation_missing", "Role overlay is required."))

    cutoff_days = days_since(str(profile.get("source_cutoff", "")))
    if cutoff_days is None:
        findings.append(Finding("blocker", company, "invalid_source_cutoff", "source_cutoff must be ISO date."))
    elif cutoff_days > max_stale_days:
        findings.append(
            Finding(
                "warning",
                company,
                "stale_source_cutoff",
                f"source_cutoff is {cutoff_days} days old; refresh public sources.",
            )
        )

    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate public lens coverage.")
    parser.add_argument("--min-companies", type=int, default=12)
    parser.add_argument("--max-stale-days", type=int, default=180)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    companies = company_dirs()
    findings: list[Finding] = []
    if len(companies) < args.min_companies:
        findings.append(
            Finding(
                "blocker",
                "_catalog",
                "minimum_company_count",
                f"Expected at least {args.min_companies} company lenses, found {len(companies)}.",
            )
        )

    for company in companies:
        findings.extend(validate_company(company, max_stale_days=args.max_stale_days))

    summary = {
        "companies": len(companies),
        "blockers": sum(1 for item in findings if item.severity == "blocker"),
        "warnings": sum(1 for item in findings if item.severity == "warning"),
    }

    if args.json:
        print(
            json.dumps(
                {
                    "status": "fail" if summary["blockers"] else "ok",
                    "summary": summary,
                    "findings": [item.__dict__ for item in findings],
                },
                indent=2,
                ensure_ascii=False,
            )
        )
    else:
        print(
            "public_lens_coverage_status={status} companies={companies} blockers={blockers} warnings={warnings}".format(
                status="fail" if summary["blockers"] else "ok",
                **summary,
            )
        )
        for item in findings:
            print(f"{item.severity.upper()}: {item.company} {item.code}: {item.message}")

    return 1 if summary["blockers"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
