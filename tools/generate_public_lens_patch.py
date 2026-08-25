#!/usr/bin/env python3
"""Apply public-safe source packets to public company lens files."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
COMPANY_LENSES = ROOT / "company_lenses"
DEFAULT_PACKET_DIR = ROOT / "docs" / "refresh-candidates" / "source-packets"
PUBLIC_MANIFEST = ROOT / "public_manifest.yaml"
AIMS_WEIGHTING = {
    "structured_thinking": 0.1667,
    "analytical_problem_solving": 0.1667,
    "ownership_execution": 0.1667,
    "impact_results": 0.1667,
    "collaboration_communication": 0.1667,
    "growth_mindset": 0.1665,
}
REQUIRED_POLICY = {
    "public_safe": True,
    "contains_private_material": False,
    "contains_candidate_data": False,
    "contains_raw_job_posting_body": False,
    "contains_paywalled_text": False,
}


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected JSON object: {path}")
    return payload


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")


def validate_packet(packet: dict[str, Any], source: Path) -> None:
    policy = packet.get("source_policy")
    if policy != REQUIRED_POLICY:
        raise ValueError(f"unsafe source_policy in {source}")
    if not packet.get("company_slug") or not packet.get("company"):
        raise ValueError(f"missing company identity in {source}")
    sources = packet.get("sources")
    if not isinstance(sources, list) or not sources:
        raise ValueError(f"packet must include at least one source: {source}")
    for item in sources:
        if not isinstance(item, dict):
            raise ValueError(f"source item must be an object: {source}")
        signal = str(item.get("public_safe_signal", ""))
        if len(signal) < 20:
            raise ValueError(f"source signal too short: {source}")
        if "\n" in signal:
            raise ValueError(f"source signal must be a short non-verbatim summary: {source}")


def evidence_ids(packet: dict[str, Any]) -> list[str]:
    return [str(item["evidence_id"]) for item in packet["sources"]]


def md_escape(value: Any) -> str:
    return str(value).replace("\n", " ").replace("|", "\\|").strip()


def evidence_rows(packet: dict[str, Any]) -> list[str]:
    rows = []
    for item in packet["sources"]:
        rows.append(
            "| {evidence_id} | {source_type} | {title} | {date_accessed} | {confidence:.2f} | {signal} |".format(
                evidence_id=md_escape(item["evidence_id"]),
                source_type=md_escape(item["source_type"]),
                title=md_escape(item["title"]),
                date_accessed=md_escape(item["date_accessed"]),
                confidence=float(item["confidence"]),
                signal=md_escape(item["public_safe_signal"]),
            )
        )
    return rows


def source_urls(packet: dict[str, Any]) -> list[str]:
    seen: set[str] = set()
    urls = []
    for item in packet["sources"]:
        url = str(item["url"])
        if url not in seen:
            seen.add(url)
            urls.append(url)
    return urls


def source_cutoff(packet: dict[str, Any]) -> str:
    dates = [str(item["date_accessed"]) for item in packet["sources"]]
    return max(dates)


def default_culture_principles(packet: dict[str, Any]) -> list[dict[str, Any]]:
    ids = evidence_ids(packet)
    return [
        {
            "name": "Public mission and customer-impact alignment",
            "description": f"{packet['company']} fit should connect work to the company outcomes and users described in cited public sources.",
            "confidence": 0.72,
            "evidence_ids": ids[:2],
        },
        {
            "name": "Evidence-backed execution",
            "description": "Strong answers should show practical judgment, clear tradeoffs, ownership, and outcomes rather than generic enthusiasm.",
            "confidence": 0.68,
            "evidence_ids": ids,
        },
    ]


def default_hiring_signals(packet: dict[str, Any]) -> list[dict[str, Any]]:
    ids = evidence_ids(packet)
    return [
        {
            "signal": "Connects decisions to the users, customers, products, or markets named in public company sources.",
            "aims_dimensions": ["impact_results", "structured_thinking"],
            "confidence": 0.7,
            "evidence_ids": ids[:2],
        },
        {
            "signal": "Uses concrete examples to show ownership, learning, and measurable improvement.",
            "aims_dimensions": ["ownership_execution", "analytical_problem_solving", "growth_mindset"],
            "confidence": 0.68,
            "evidence_ids": ids,
        },
    ]


def default_anti_signals(packet: dict[str, Any]) -> list[dict[str, Any]]:
    ids = evidence_ids(packet)
    return [
        {
            "anti_signal": "Generic admiration for the company without a concrete role, customer, product, or business mechanism.",
            "risk_reason": "Public lens usage should stay grounded in cited source signals and role-relevant evidence.",
            "confidence": 0.66,
            "evidence_ids": ids,
        }
    ]


def normalize_question(packet: dict[str, Any], item: dict[str, Any], index: int) -> dict[str, Any]:
    slug = str(packet["company_slug"]).upper().replace("-", "_")
    ids = evidence_ids(packet)
    return {
        "question_id": str(item.get("question_id") or f"{slug}-Q-{index:03d}"),
        "type": str(item.get("type") or "behavioral"),
        "generated_question": str(item["generated_question"]),
        "aims_dimensions": list(item.get("aims_dimensions") or ["structured_thinking", "impact_results"]),
        "strong_answer_signals": list(item.get("strong_answer_signals") or []),
        "evidence_ids": list(item.get("evidence_ids") or ids),
    }


def create_company_lens(packet: dict[str, Any]) -> list[Path]:
    company_dir = COMPANY_LENSES / str(packet["company_slug"])
    if company_dir.exists():
        return update_company_lens(packet)

    company_dir.mkdir(parents=True)
    cutoff = source_cutoff(packet)
    profile_data = packet.get("company_profile") if isinstance(packet.get("company_profile"), dict) else {}
    updates = packet["lens_updates"]
    profile = {
        "lens_id": f"{packet['company_slug']}_public_v0_1",
        "company": packet["company"],
        "canonical_company_name": packet["company"],
        "lens_status": "LIGHTWEIGHT_SCAN",
        "visibility": "PUBLIC_COMPANY_LENS",
        "version": "0.1.0-public-release-candidate",
        "source_cutoff": cutoff,
        "industries": list(profile_data.get("industries") or []),
        "regions": list(profile_data.get("regions") or ["global"]),
        "company_stage": str(profile_data.get("company_stage") or "public company"),
        "culture_principles": list(updates.get("culture_principles") or default_culture_principles(packet)),
        "aims_weighting": dict(AIMS_WEIGHTING),
        "hiring_signals": list(updates.get("hiring_signals") or default_hiring_signals(packet)),
        "anti_signals": list(updates.get("anti_signals") or default_anti_signals(packet)),
        "interview_patterns": [
            {
                "pattern": "Use cited public source signals to test role-relevant judgment, ownership, communication, and impact.",
                "role_families": ["all"],
                "aims_dimensions": ["structured_thinking", "ownership_execution", "impact_results"],
                "confidence": 0.62,
            }
        ],
        "evidence_summary": {
            "source_count": len(packet["sources"]),
            "official_source_count": sum(1 for item in packet["sources"] if str(item["source_type"]).startswith("official_")),
            "interview_source_count": 0,
            "employee_voice_source_count": 0,
            "last_reviewed": cutoff,
        },
        "honest_limits": [
            f"This is a lightweight public-source lens and does not represent an official {packet['company']} hiring standard.",
            "It contains source metadata and non-verbatim public-safe signals only.",
            "Role, team, seniority, location, and hiring manager can materially change interview emphasis.",
            "This lens requires deeper multi-source validation before being promoted to FULLY_DISTILLED.",
        ],
    }

    questions = [
        normalize_question(packet, item, index)
        for index, item in enumerate(updates.get("questions") or [], start=1)
    ]
    if not questions:
        questions = [
            normalize_question(
                packet,
                {
                    "generated_question": "Tell me about a time you used evidence and ownership to create a measurable result for users, customers, or stakeholders.",
                    "aims_dimensions": ["structured_thinking", "ownership_execution", "impact_results"],
                    "strong_answer_signals": [
                        "Defines the problem and stakeholder clearly.",
                        "Explains tradeoffs and concrete action.",
                        "Connects the work to a measurable result.",
                        "Shows learning from feedback or new evidence.",
                    ],
                },
                1,
            )
        ]

    changed = [
        company_dir / "README.md",
        company_dir / "evidence.md",
        company_dir / "limits.md",
        company_dir / "profile.json",
        company_dir / "question_bank.json",
        company_dir / "rewrite_rules.md",
        company_dir / "rubric.md",
        company_dir / "validation_report.md",
    ]

    (company_dir / "README.md").write_text(f"# {packet['company']} Public Lens\n\nStatus: `LIGHTWEIGHT_SCAN`\n\nThis lens is generated from public source packets and should be improved through evidence-backed pull requests.\n", encoding="utf-8", newline="\n")
    write_evidence(company_dir / "evidence.md", packet, create=True)
    (company_dir / "limits.md").write_text(f"# {packet['company']} Lens Limits\n\n- This is a `LIGHTWEIGHT_SCAN` based on public-safe source packets.\n- It does not include private interview reports, paid source bodies, candidate data, tenant data, or user-submitted job postings.\n- It should be used for interview preparation and public lens validation, not for official hiring decisions.\n- The lens should be promoted only after multi-source evidence review, role-specific validation, and answer backtesting.\n", encoding="utf-8", newline="\n")
    write_json(company_dir / "profile.json", profile)
    write_json(
        company_dir / "question_bank.json",
        {
            "company": packet["company"],
            "lens_id": profile["lens_id"],
            "version": profile["version"],
            "visibility": "PUBLIC_COMPANY_LENS",
            "source_policy": {
                "public_safe": True,
                "contains_private_material": False,
                "contains_candidate_data": False,
                "contains_user_submitted_job_postings": False,
            },
            "questions": questions,
        },
    )
    (company_dir / "rewrite_rules.md").write_text(f"# {packet['company']} Rewrite Rules\n\n- Ground advice in cited public source IDs.\n- Convert generic company enthusiasm into role-relevant evidence and outcomes.\n- Do not quote source bodies, job postings, paid materials, candidate answers, or tenant data.\n", encoding="utf-8", newline="\n")
    write_rubric(company_dir / "rubric.md", packet)
    (company_dir / "validation_report.md").write_text(f"# {packet['company']} Validation Report\n\n- Status: `LIGHTWEIGHT_SCAN`\n- Source packet applied: `{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}`\n- Public-safety policy: pass\n- Promotion status: not promoted\n", encoding="utf-8", newline="\n")

    for overlay in updates.get("role_overlays") or []:
        path = write_role_overlay(company_dir, packet, overlay)
        changed.append(path)

    update_manifest_for_company(str(packet["company_slug"]))
    changed.append(PUBLIC_MANIFEST)
    return changed


def write_evidence(path: Path, packet: dict[str, Any], *, create: bool) -> None:
    header = [
        f"# {packet['company']} Evidence",
        "",
        "This evidence file is public-safe and contains no private source bodies, paid article text, user-submitted job postings, candidate answers, or tenant data.",
        "",
        "| Evidence ID | Source Type | Title | Date Accessed | Confidence | Public-Safe Signal |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    rows = evidence_rows(packet)
    urls = ["", "## Public Source URLs", "", *[f"- {url}" for url in source_urls(packet)]]
    limits = [
        "",
        "## Limits",
        "",
        "- This lens uses source metadata and non-verbatim public-safe signals.",
        "- It should not be used as an official company hiring policy.",
    ]
    if create or not path.exists():
        path.write_text("\n".join(header + rows + urls + limits) + "\n", encoding="utf-8", newline="\n")
        return

    existing = path.read_text(encoding="utf-8")
    existing_ids = {str(item["evidence_id"]) for item in packet["sources"] if str(item["evidence_id"]) in existing}
    new_rows = [row for row in rows if row.split("|", 3)[1].strip() not in existing_ids]
    if not new_rows:
        return
    marker = "| --- | --- | --- | --- | --- | --- |"
    if marker in existing:
        existing = existing.replace(marker, marker + "\n" + "\n".join(new_rows), 1)
    else:
        existing = existing.rstrip() + "\n\n" + "\n".join(new_rows) + "\n"
    for url in source_urls(packet):
        if url not in existing:
            existing = existing.rstrip() + f"\n- {url}\n"
    path.write_text(existing, encoding="utf-8", newline="\n")


def update_company_lens(packet: dict[str, Any]) -> list[Path]:
    company_dir = COMPANY_LENSES / str(packet["company_slug"])
    changed = []
    evidence_path = company_dir / "evidence.md"
    before = evidence_path.read_text(encoding="utf-8") if evidence_path.exists() else ""
    write_evidence(evidence_path, packet, create=not evidence_path.exists())
    if not evidence_path.exists() or evidence_path.read_text(encoding="utf-8") != before:
        changed.append(evidence_path)

    profile_path = company_dir / "profile.json"
    profile = load_json(profile_path)
    cutoff = source_cutoff(packet)
    profile["source_cutoff"] = max(str(profile.get("source_cutoff", "")), cutoff)
    summary = profile.setdefault("evidence_summary", {})
    summary["last_reviewed"] = cutoff
    summary["source_count"] = max(int(summary.get("source_count", 0)), count_evidence_rows(evidence_path))
    summary["official_source_count"] = max(
        int(summary.get("official_source_count", 0)),
        sum(1 for item in packet["sources"] if str(item["source_type"]).startswith("official_")),
    )
    write_json(profile_path, profile)
    changed.append(profile_path)
    return changed


def count_evidence_rows(path: Path) -> int:
    if not path.exists():
        return 0
    count = 0
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("| "):
            continue
        if line.startswith("| ---") or "Evidence ID" in line:
            continue
        count += 1
    return count


def write_rubric(path: Path, packet: dict[str, Any]) -> None:
    path.write_text(f"""# {packet['company']} Rubric

## Strong Signals

- Connects answers to cited public source signals and role-relevant outcomes.
- Shows structured thinking, practical tradeoffs, ownership, and measurable impact.
- Communicates clearly without hiding behind generic process language.

## Medium Signals

- Shows useful execution but weak connection to cited public evidence.
- Mentions customer, product, or business impact without enough mechanism.

## Weak Signals

- Generic company admiration with no role-specific fit.
- Unsupported claims about company culture, interview standards, or hiring policy.
- Copied source language, job posting bodies, paid material, or private evidence.

## AIMS Emphasis

- `structured_thinking`: medium
- `analytical_problem_solving`: medium
- `ownership_execution`: high
- `impact_results`: high
- `collaboration_communication`: medium
- `growth_mindset`: medium
""", encoding="utf-8", newline="\n")


def write_role_overlay(company_dir: Path, packet: dict[str, Any], overlay: dict[str, Any]) -> Path:
    role_slug = str(overlay.get("role_slug") or "public_role").lower().replace(" ", "_")
    path = company_dir / "role_overlays" / f"{role_slug}.json"
    payload = {
        "company": packet["company"],
        "role_family": overlay.get("role_family") or role_slug.replace("_", " ").title(),
        "lens_status": "LIGHTWEIGHT_SCAN",
        "visibility": "PUBLIC_COMPANY_LENS",
        "source_policy": {
            "public_safe": True,
            "contains_private_material": False,
            "contains_candidate_data": False,
            "contains_user_submitted_job_postings": False,
        },
        "focus_signals": list(overlay.get("signals") or []),
        "evidence_ids": evidence_ids(packet),
    }
    write_json(path, payload)
    return path


def update_manifest_for_company(slug: str) -> None:
    text = PUBLIC_MANIFEST.read_text(encoding="utf-8")
    if f"slug: {slug}" not in text:
        marker = "\nallow_paths:\n"
        entry = f"    - slug: {slug}\n      path: company_lenses/{slug}/\n      status: existing_candidate\n"
        if marker not in text:
            raise ValueError("public_manifest.yaml is missing allow_paths marker")
        text = text.replace(marker, entry + marker, 1)

    paths = [
        f"company_lenses/{slug}/README.md",
        f"company_lenses/{slug}/profile.json",
        f"company_lenses/{slug}/evidence.md",
        f"company_lenses/{slug}/rubric.md",
        f"company_lenses/{slug}/question_bank.json",
        f"company_lenses/{slug}/rewrite_rules.md",
        f"company_lenses/{slug}/limits.md",
        f"company_lenses/{slug}/validation_report.md",
        f"company_lenses/{slug}/role_overlays/",
    ]
    missing = [path for path in paths if path not in text]
    if missing:
        marker = "\n  public_tools:\n"
        if marker not in text:
            raise ValueError("public_manifest.yaml is missing public_tools marker")
        block = "".join(f"    - {path}\n" for path in missing)
        text = text.replace(marker, block + marker, 1)
    PUBLIC_MANIFEST.write_text(text, encoding="utf-8", newline="\n")


def required_company_paths(slug: str) -> list[str]:
    required = [
        f"company_lenses/{slug}/README.md",
        f"company_lenses/{slug}/profile.json",
        f"company_lenses/{slug}/evidence.md",
        f"company_lenses/{slug}/rubric.md",
        f"company_lenses/{slug}/question_bank.json",
        f"company_lenses/{slug}/rewrite_rules.md",
        f"company_lenses/{slug}/limits.md",
        f"company_lenses/{slug}/validation_report.md",
        f"company_lenses/{slug}/role_overlays/",
    ]
    return required


def packet_paths(args: argparse.Namespace) -> list[Path]:
    paths: list[Path] = []
    for path in args.packet or []:
        paths.append(path)
    if args.packet_dir.exists():
        paths.extend(sorted(args.packet_dir.glob("*.source-packet.json")))
    return sorted(set(paths))


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate public lens patches from source packets.")
    parser.add_argument("--packet", type=Path, action="append")
    parser.add_argument("--packet-dir", type=Path, default=DEFAULT_PACKET_DIR)
    parser.add_argument("--expansion-limit", type=int, default=0)
    parser.add_argument("--existing-limit", type=int, default=0)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--allow-empty", action="store_true", help="Exit successfully when no source packet applies.")
    args = parser.parse_args()

    paths = packet_paths(args)
    if args.expansion_limit:
        paths = [path for path in paths if not (COMPANY_LENSES / path.name.replace(".source-packet.json", "")).exists()][: args.expansion_limit]
    elif args.existing_limit:
        paths = [path for path in paths if (COMPANY_LENSES / path.name.replace(".source-packet.json", "")).exists()][: args.existing_limit]

    if not paths and args.allow_empty:
        print("lens_patch_status=empty")
        return 0
    if not paths:
        raise SystemExit("No source packets found.")

    all_changed: list[Path] = []
    for path in paths:
        packet = load_json(path)
        validate_packet(packet, path)
        if args.execute:
            all_changed.extend(create_company_lens(packet))
        else:
            status = "update" if (COMPANY_LENSES / str(packet["company_slug"])).exists() else "create"
            print(f"plan={status} company={packet['company']} packet={path.relative_to(ROOT)}")

    if args.execute:
        unique = sorted({path for path in all_changed})
        for path in unique:
            print(f"changed={path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
