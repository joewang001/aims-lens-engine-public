#!/usr/bin/env python3
"""Prepare a public lens refresh candidate report for an automated PR.

This script intentionally does not invent new lens content. It creates a
maintainer-readable candidate report from repository facts: lens status, source
cutoff age, industry coverage, role-overlay gaps, and validation warnings.
Future sourcing agents can write public-safe evidence updates before this script
runs; the report will then travel with the PR as the audit trail.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
COMPANY_LENSES = ROOT / "company_lenses"
DEFAULT_OUTPUT = ROOT / "docs" / "refresh-candidates" / "public-lens-refresh-candidate.md"


EXPANSION_CANDIDATES = [
    {
        "company": "NVIDIA",
        "industry": "AI infrastructure and semiconductors",
        "reason": "Adds a leading AI compute and semiconductor company to an undercovered public lens area.",
        "review": "new_company",
    },
    {
        "company": "Accenture",
        "industry": "consulting and professional services",
        "reason": "Broadens consulting coverage beyond McKinsey with a public, high-volume hiring benchmark.",
        "review": "new_company",
    },
    {
        "company": "Salesforce",
        "industry": "enterprise software",
        "reason": "Adds a major SaaS employer with strong public material around customer success and platform work.",
        "review": "new_company",
    },
    {
        "company": "Johnson & Johnson",
        "industry": "healthcare and pharma",
        "reason": "Opens healthcare and regulated life-sciences coverage.",
        "review": "new_industry",
    },
    {
        "company": "Enbridge",
        "industry": "energy and utilities",
        "reason": "Improves Canadian energy and infrastructure coverage.",
        "review": "new_industry",
    },
    {
        "company": "Walmart",
        "industry": "retail, ecommerce, and logistics",
        "reason": "Adds a high-volume retail and supply-chain benchmark with broad frontline, corporate, and technology hiring relevance.",
        "review": "new_industry",
    },
    {
        "company": "Costco",
        "industry": "membership retail and operations",
        "reason": "Broadens retail coverage with a differentiated membership, service, and operations model.",
        "review": "new_company",
    },
    {
        "company": "Tesla",
        "industry": "automotive, energy, manufacturing, and AI",
        "reason": "Adds a fast-execution manufacturing and technology benchmark across product, operations, software, and energy roles.",
        "review": "new_industry",
    },
    {
        "company": "Pfizer",
        "industry": "pharma and biotechnology",
        "reason": "Deepens regulated healthcare coverage with a leading pharmaceutical employer.",
        "review": "new_company",
    },
    {
        "company": "Deloitte",
        "industry": "consulting and professional services",
        "reason": "Adds another major consulting and professional-services benchmark with high hiring relevance.",
        "review": "new_company",
    },
    {
        "company": "IBM",
        "industry": "enterprise technology, cloud, AI, and consulting",
        "reason": "Broadens enterprise technology coverage with public signals around hybrid cloud, AI, consulting, and client transformation.",
        "review": "new_company",
    },
    {
        "company": "Oracle",
        "industry": "enterprise software, database, and cloud",
        "reason": "Adds a major enterprise software and cloud infrastructure benchmark.",
        "review": "new_company",
    },
    {
        "company": "Adobe",
        "industry": "creative software, documents, digital experience, and AI",
        "reason": "Adds a creative software and digital-experience benchmark with product, design, engineering, sales, and customer roles.",
        "review": "new_company",
    },
]


@dataclass
class CompanySnapshot:
    slug: str
    company: str
    status: str
    source_cutoff: str
    source_age_days: int | None
    industries: list[str]
    has_role_overlay: bool
    refresh_priority: int
    refresh_reason: str


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected object in {path}")
    return payload


def days_since(value: str) -> int | None:
    try:
        cutoff = date.fromisoformat(value)
    except ValueError:
        return None
    return (date.today() - cutoff).days


def company_dirs() -> list[Path]:
    return sorted(
        item
        for item in COMPANY_LENSES.iterdir()
        if item.is_dir() and not item.name.startswith("_")
    )


def snapshot_company(path: Path, *, stale_days: int) -> CompanySnapshot:
    profile = load_json(path / "profile.json")
    source_cutoff = str(profile.get("source_cutoff", ""))
    source_age = days_since(source_cutoff)
    status = str(profile.get("lens_status", ""))
    has_role_overlay = (path / "role_overlays").is_dir() and any((path / "role_overlays").glob("*.json"))
    industries = [str(item) for item in profile.get("industries", []) if str(item).strip()]

    priority = 0
    reasons: list[str] = []
    if source_age is None:
        priority += 50
        reasons.append("invalid source_cutoff")
    elif source_age > stale_days:
        priority += 30
        reasons.append(f"source cutoff is {source_age} days old")
    if status == "LIGHTWEIGHT_SCAN":
        priority += 20
        reasons.append("lightweight lens should receive evidence deepening")
    if not has_role_overlay:
        priority += 10
        reasons.append("missing role overlay")
    if not reasons:
        reasons.append("routine public-source freshness check")

    return CompanySnapshot(
        slug=path.name,
        company=str(profile.get("company", path.name)),
        status=status,
        source_cutoff=source_cutoff,
        source_age_days=source_age,
        industries=industries,
        has_role_overlay=has_role_overlay,
        refresh_priority=priority,
        refresh_reason="; ".join(reasons),
    )


def industry_counts(snapshots: list[CompanySnapshot]) -> Counter[str]:
    counts: Counter[str] = Counter()
    for snapshot in snapshots:
        for industry in snapshot.industries:
            counts[industry] += 1
    return counts


def build_report(snapshots: list[CompanySnapshot], *, stale_days: int) -> str:
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    counts = industry_counts(snapshots)
    priority = sorted(snapshots, key=lambda item: (-item.refresh_priority, item.slug))

    lines = [
        "# Public Lens Refresh Candidate",
        "",
        f"Generated at: `{generated_at}`",
        "",
        "This file is generated by `tools/prepare_public_lens_refresh.py` for the scheduled public-lens maintenance PR.",
        "It proposes refresh and expansion targets from repository metadata only; it does not import private material or invent new lens content.",
        "",
        "## Summary",
        "",
        f"- Company lenses: `{len(snapshots)}`",
        f"- Stale threshold: `{stale_days}` days",
        f"- Lightweight lenses: `{sum(1 for item in snapshots if item.status == 'LIGHTWEIGHT_SCAN')}`",
        f"- Missing role overlays: `{sum(1 for item in snapshots if not item.has_role_overlay)}`",
        "",
        "## Existing Lens Refresh Queue",
        "",
        "| Company | Status | Source cutoff | Age days | Role overlay | Priority | Reason |",
        "| --- | --- | --- | ---: | --- | ---: | --- |",
    ]
    for item in priority:
        lines.append(
            "| {company} | `{status}` | `{cutoff}` | {age} | {overlay} | {priority} | {reason} |".format(
                company=item.company,
                status=item.status,
                cutoff=item.source_cutoff or "unknown",
                age="unknown" if item.source_age_days is None else item.source_age_days,
                overlay="yes" if item.has_role_overlay else "no",
                priority=item.refresh_priority,
                reason=item.refresh_reason,
            )
        )

    lines.extend(
        [
            "",
            "## Industry Coverage Snapshot",
            "",
            "| Industry | Lens count |",
            "| --- | ---: |",
        ]
    )
    for industry, count in sorted(counts.items(), key=lambda pair: (-pair[1], pair[0])):
        lines.append(f"| {industry} | {count} |")

    lines.extend(
        [
            "",
            "## Expansion Candidates",
            "",
            "| Company | Industry | Why now | Review class |",
            "| --- | --- | --- | --- |",
        ]
    )
    for item in EXPANSION_CANDIDATES:
        lines.append(
            f"| {item['company']} | {item['industry']} | {item['reason']} | `{item['review']}` |"
        )

    lines.extend(
        [
            "",
            "## Automation Boundary",
            "",
            "This PR is safe to auto-create because it changes only allowlisted public maintenance files and public company lens files generated from approved source packets.",
            "Routine new-company additions are eligible for auto-merge when they come from the approved expansion catalog, cite public source URLs, and contain only non-verbatim public-safe signals.",
            "",
            "Escalate to manual review before merge if this PR is extended to include:",
            "",
            "- a company or source packet outside the approved expansion catalog;",
            "- a new evidence class or private-derived public-safe signal;",
            "- lens status promotion beyond `LIGHTWEIGHT_SCAN`;",
            "- schema, routing, scoring, or license changes;",
            "- any scanner blocker or review finding.",
            "",
            "## Required Checks",
            "",
            "```bash",
            "python tools/scan_public_export.py --allowlist",
            "python tools/validate_public_lens_coverage.py --min-companies 12",
            "```",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare an automated public lens refresh PR report.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--stale-days", type=int, default=180)
    args = parser.parse_args()

    snapshots = [snapshot_company(path, stale_days=args.stale_days) for path in company_dirs()]
    report = build_report(snapshots, stale_days=args.stale_days)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(report, encoding="utf-8", newline="\n")
    print(f"refresh_candidate={args.output.relative_to(ROOT)} companies={len(snapshots)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
