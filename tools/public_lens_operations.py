#!/usr/bin/env python3
"""Operate weekly expansion and daily seven-dimension lens maintenance."""

from __future__ import annotations

import argparse
import csv
import json
import re
import subprocess
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

try:
    from tools.collect_public_lens_sources import CATALOG
except ModuleNotFoundError:  # Direct execution from tools/.
    from collect_public_lens_sources import CATALOG


ROOT = Path(__file__).resolve().parents[1]
COMPANY_LENSES = ROOT / "company_lenses"
DEFAULT_GAP_CSV = ROOT / "docs" / "refresh-candidates" / "public-lens-information-gaps.csv"
DEFAULT_GAP_MD = ROOT / "docs" / "refresh-candidates" / "public-lens-information-gaps.md"
DEFAULT_HISTORY_CSV = ROOT / "docs" / "refresh-candidates" / "public-lens-gap-resolution-history.csv"
DEFAULT_HISTORY_MD = ROOT / "docs" / "refresh-candidates" / "public-lens-gap-resolution-history.md"
DEFAULT_PLAN_JSON = ROOT / "docs" / "refresh-candidates" / "public-lens-daily-plan.json"
DEFAULT_PLAN_MD = ROOT / "docs" / "refresh-candidates" / "public-lens-daily-plan.md"

SEVEN_DIMENSIONS = (
    "company_says",
    "company_judges",
    "company_asks",
    "evidence_valued",
    "risk_warnings",
    "role_variation",
    "honest_unknowns",
)

DAILY_FOCUS = {
    0: ("weekly_expansion",),
    1: ("company_says", "evidence_valued"),
    2: ("company_judges", "company_asks"),
    3: ("role_variation",),
    4: ("risk_warnings",),
    5: ("honest_unknowns",),
    6: SEVEN_DIMENSIONS,
}

GAP_FIELDS = (
    "company_slug",
    "company",
    "lens_status",
    "dimension",
    "gap_status",
    "reason_code",
    "reason",
    "source_cutoff",
    "next_action",
    "owner_queue",
    "resolution_status",
    "first_detected",
    "last_checked",
)

HISTORY_FIELDS = (
    "resolution_record_id",
    "company_slug",
    "company",
    "dimension",
    "reason_code",
    "first_detected",
    "last_open_checked",
    "resolved_at",
    "resolution_basis",
    "evidence_refs",
    "source_cutoff",
    "owner_queue",
    "resolution_status",
    "resolution_commit",
    "resolution_pr",
)


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected JSON object: {path}")
    return payload


def display_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT.resolve()))
    except ValueError:
        return str(path)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def company_dirs() -> list[Path]:
    return sorted(
        path
        for path in COMPANY_LENSES.iterdir()
        if path.is_dir() and not path.name.startswith("_")
    )


def count_evidence_rows(path: Path) -> int:
    if not path.is_file():
        return 0
    return sum(
        1
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.startswith("| ")
        and not line.startswith("| ---")
        and "Evidence ID" not in line
    )


def load_questions(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    payload = load_json(path)
    questions = payload.get("questions")
    return questions if isinstance(questions, list) else []


def prior_first_detected(path: Path) -> dict[tuple[str, str, str], str]:
    if not path.is_file():
        return {}
    with path.open("r", encoding="utf-8", newline="") as handle:
        return {
            (row["company_slug"], row["dimension"], row["reason_code"]): row["first_detected"]
            for row in csv.DictReader(handle)
            if row.get("company_slug") and row.get("dimension") and row.get("reason_code")
        }


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def gap_key(row: dict[str, str]) -> tuple[str, str, str]:
    return (row["company_slug"], row["dimension"], row["reason_code"])


def collect_evidence_refs(value: Any) -> set[str]:
    refs: set[str] = set()
    if isinstance(value, dict):
        for key, nested in value.items():
            if key in {"evidence_ids", "evidence_refs"} and isinstance(nested, list):
                refs.update(str(item) for item in nested if item)
            else:
                refs.update(collect_evidence_refs(nested))
    elif isinstance(value, list):
        for nested in value:
            refs.update(collect_evidence_refs(nested))
    return refs


def resolution_details(row: dict[str, str]) -> tuple[str, str, str]:
    slug = row["company_slug"]
    dimension = row["dimension"]
    if slug == "_catalog":
        existing = set(current_company_names())
        unused = sum(1 for candidate in CATALOG if candidate not in existing)
        return (
            f"Approved candidate reserve now contains {unused} unused companies.",
            "catalog_inventory",
            "n/a",
        )

    path = COMPANY_LENSES / slug
    if not path.is_dir():
        return (
            "Gap no longer appears in the current audit; company lens directory is not present.",
            "none",
            row.get("source_cutoff", "unknown"),
        )

    profile = load_json(path / "profile.json")
    evidence_count = count_evidence_rows(path / "evidence.md")
    questions_count = len(load_questions(path / "question_bank.json"))
    overlay_dir = path / "role_overlays"
    overlay_count = len(list(overlay_dir.glob("*.json"))) if overlay_dir.is_dir() else 0
    metrics = {
        "company_says": f"culture principles={len(profile.get('culture_principles') or [])}, evidence rows={evidence_count}",
        "company_judges": f"hiring signals={len(profile.get('hiring_signals') or [])}, rubric={str((path / 'rubric.md').is_file()).lower()}",
        "company_asks": f"original questions={questions_count}",
        "evidence_valued": (
            f"AIMS weights={len(profile.get('aims_weighting') or {})}, "
            f"official sources={int((profile.get('evidence_summary') or {}).get('official_source_count', 0) or 0)}"
        ),
        "risk_warnings": f"anti-signals={len(profile.get('anti_signals') or [])}, limits={str((path / 'limits.md').is_file()).lower()}",
        "role_variation": f"role overlays={overlay_count}",
        "honest_unknowns": (
            f"honest limits={len(profile.get('honest_limits') or [])}, "
            f"validation report={str((path / 'validation_report.md').is_file()).lower()}"
        ),
    }
    refs = collect_evidence_refs(profile)
    questions_path = path / "question_bank.json"
    if questions_path.is_file():
        refs.update(collect_evidence_refs(load_json(questions_path)))
    for overlay in sorted(overlay_dir.glob("*.json")) if overlay_dir.is_dir() else []:
        refs.update(collect_evidence_refs(load_json(overlay)))
    return (
        f"Current lens passed the automated `{dimension}` threshold: {metrics.get(dimension, 'gap absent')}.",
        ";".join(sorted(refs)) or "none_recorded",
        str(profile.get("source_cutoff", "unknown")),
    )


def reconcile_resolution_provenance(rows: list[dict[str, str]], history_path: Path) -> None:
    try:
        relative_path = history_path.resolve().relative_to(ROOT.resolve())
    except ValueError:
        return
    for row in rows:
        commit_pending = row.get("resolution_commit", "").startswith("pending:")
        pr_pending = row.get("resolution_pr", "").startswith("pending:")
        if not commit_pending and not pr_pending:
            continue
        result = subprocess.run(
            [
                "git",
                "-C",
                str(ROOT),
                "log",
                "--first-parent",
                "--diff-merges=first-parent",
                "--reverse",
                "--format=%H%x09%s",
                "-S",
                row["resolution_record_id"],
                "--",
                str(relative_path),
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        first = next((line for line in result.stdout.splitlines() if "\t" in line), "")
        if not first:
            continue
        commit, subject = first.split("\t", 1)
        if commit_pending:
            row["resolution_commit"] = commit
        match = re.search(r"(?:\(#|pull request #)(\d+)\)?", subject, re.IGNORECASE)
        if match:
            row["resolution_pr"] = (
                "https://github.com/joewang001/aims-lens-engine-public/pull/"
                + match.group(1)
            )


def write_resolution_history(
    *,
    prior_rows: list[dict[str, str]],
    current_rows: list[dict[str, str]],
    csv_path: Path,
    md_path: Path,
    resolved_on: str | None = None,
) -> int:
    resolved_date = resolved_on or date.today().isoformat()
    current_keys = {gap_key(row) for row in current_rows}
    history = read_csv_rows(csv_path)
    known_ids = {row.get("resolution_record_id", "") for row in history}
    added = 0
    for prior in prior_rows:
        if gap_key(prior) in current_keys:
            continue
        record_id = "|".join(
            (
                prior["company_slug"],
                prior["dimension"],
                prior["reason_code"],
                prior.get("first_detected", "unknown"),
                resolved_date,
            )
        )
        if record_id in known_ids:
            continue
        basis, evidence_refs, source_cutoff = resolution_details(prior)
        history.append(
            {
                "resolution_record_id": record_id,
                "company_slug": prior["company_slug"],
                "company": prior.get("company", prior["company_slug"]),
                "dimension": prior["dimension"],
                "reason_code": prior["reason_code"],
                "first_detected": prior.get("first_detected", "unknown"),
                "last_open_checked": prior.get("last_checked", "unknown"),
                "resolved_at": resolved_date,
                "resolution_basis": basis,
                "evidence_refs": evidence_refs,
                "source_cutoff": source_cutoff,
                "owner_queue": prior.get("owner_queue", "public-lens-sourcing-and-distillation"),
                "resolution_status": "resolved",
                "resolution_commit": "pending:first_commit_containing_record",
                "resolution_pr": "pending:merge_pr",
            }
        )
        known_ids.add(record_id)
        added += 1

    reconcile_resolution_provenance(history, csv_path)
    history.sort(key=lambda row: (row["resolved_at"], row["company_slug"], row["dimension"], row["reason_code"]))
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=HISTORY_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(history)

    lines = [
        "# Public Lens Gap Resolution History",
        "",
        f"Generated: `{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}`",
        "",
        "This append-only operational view records gaps that disappeared after a lens passed its automated threshold. The first Git commit containing each record is the authoritative resolution change; commit and PR fields are backfilled on a later audit.",
        "",
        f"- Resolved records: `{len(history)}`",
        f"- Added in this audit: `{added}`",
        "",
        "| Company | Dimension | First detected | Resolved | Basis | Evidence refs | Commit | PR |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in history:
        clean = {key: str(value).replace("|", "\\|").replace("\n", " ") for key, value in row.items()}
        lines.append(
            "| {company} | `{dimension}` | `{first_detected}` | `{resolved_at}` | {resolution_basis} | `{evidence_refs}` | `{resolution_commit}` | {resolution_pr} |".format(**clean)
        )
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    return added


def add_gap(
    rows: list[dict[str, str]],
    *,
    profile: dict[str, Any],
    slug: str,
    dimension: str,
    status: str,
    code: str,
    reason: str,
    action: str,
) -> None:
    rows.append(
        {
            "company_slug": slug,
            "company": str(profile.get("company", slug)),
            "lens_status": str(profile.get("lens_status", "unknown")),
            "dimension": dimension,
            "gap_status": status,
            "reason_code": code,
            "reason": reason,
            "source_cutoff": str(profile.get("source_cutoff", "unknown")),
            "next_action": action,
            "owner_queue": "public-lens-sourcing-and-distillation",
            "resolution_status": "open",
            "first_detected": "",
            "last_checked": "",
        }
    )


def audit_company(path: Path) -> list[dict[str, str]]:
    profile = load_json(path / "profile.json")
    slug = path.name
    rows: list[dict[str, str]] = []
    evidence_count = count_evidence_rows(path / "evidence.md")
    culture_count = len(profile.get("culture_principles") or [])
    hiring_count = len(profile.get("hiring_signals") or [])
    anti_count = len(profile.get("anti_signals") or [])
    questions_count = len(load_questions(path / "question_bank.json"))
    overlay_count = len(list((path / "role_overlays").glob("*.json"))) if (path / "role_overlays").is_dir() else 0
    honest_count = len(profile.get("honest_limits") or [])
    weighting_count = len(profile.get("aims_weighting") or {})
    official_count = int((profile.get("evidence_summary") or {}).get("official_source_count", 0) or 0)

    if culture_count < 3 or evidence_count < 3:
        add_gap(
            rows,
            profile=profile,
            slug=slug,
            dimension="company_says",
            status="thin",
            code="insufficient_public_company_evidence",
            reason=f"Culture principles={culture_count}, evidence rows={evidence_count}; target is at least 3 of each.",
            action="Collect additional official company, values, leadership, or strategy sources and add cited non-verbatim principles.",
        )
    if hiring_count < 3 or not (path / "rubric.md").is_file():
        add_gap(
            rows,
            profile=profile,
            slug=slug,
            dimension="company_judges",
            status="thin" if hiring_count else "missing",
            code="insufficient_hiring_signals",
            reason=f"Hiring signals={hiring_count}; target is at least 3 with a rubric.",
            action="Collect official careers or hiring-process evidence and add cited evaluation signals without claiming an official standard.",
        )
    if questions_count < 3:
        add_gap(
            rows,
            profile=profile,
            slug=slug,
            dimension="company_asks",
            status="thin" if questions_count else "missing",
            code="insufficient_question_coverage",
            reason=f"Original question count={questions_count}; target is at least 3.",
            action="Create original, evidence-grounded questions and follow-ups covering multiple AIMS dimensions.",
        )
    if weighting_count < 6 or official_count < 2:
        add_gap(
            rows,
            profile=profile,
            slug=slug,
            dimension="evidence_valued",
            status="thin",
            code="insufficient_evidence_depth",
            reason=f"AIMS weights={weighting_count}, official sources={official_count}; targets are 6 and at least 2.",
            action="Add official evidence with confidence and dimension tags, then verify scoring emphasis remains evidence-bounded.",
        )
    if anti_count < 2 or not (path / "limits.md").is_file():
        add_gap(
            rows,
            profile=profile,
            slug=slug,
            dimension="risk_warnings",
            status="thin" if anti_count else "missing",
            code="insufficient_risk_signals",
            reason=f"Anti-signals={anti_count}; target is at least 2 with explicit limits.",
            action="Add source-bounded risk and anti-signal guidance plus clear non-official-use limits.",
        )
    if overlay_count < 2:
        add_gap(
            rows,
            profile=profile,
            slug=slug,
            dimension="role_variation",
            status="thin" if overlay_count else "missing",
            code="insufficient_role_overlays",
            reason=f"Role overlays={overlay_count}; target is at least 2 materially different role families.",
            action="Collect role-family evidence and add another role overlay, or record why the role distinction cannot yet be supported.",
        )
    if honest_count < 4 or not (path / "validation_report.md").is_file():
        add_gap(
            rows,
            profile=profile,
            slug=slug,
            dimension="honest_unknowns",
            status="thin" if honest_count else "missing",
            code="insufficient_unknowns_and_validation",
            reason=f"Honest limits={honest_count}; target is at least 4 with a validation report.",
            action="Record unresolved source, role, location, seniority, and validation limits for downstream investigation.",
        )
    return rows


def build_gap_rows(*, reserve_target: int) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for path in company_dirs():
        rows.extend(audit_company(path))

    existing = {path.name for path in company_dirs()}
    remaining = [slug for slug in CATALOG if slug not in existing]
    if len(remaining) < reserve_target:
        rows.append(
            {
                "company_slug": "_catalog",
                "company": "Approved expansion catalog",
                "lens_status": "operations",
                "dimension": "catalog_capacity",
                "gap_status": "at_risk",
                "reason_code": "insufficient_candidate_reserve",
                "reason": f"Only {len(remaining)} unused approved candidates remain; reserve target is {reserve_target}.",
                "source_cutoff": "n/a",
                "next_action": "Research and approve additional industry-leading companies with official public sources before the reserve is exhausted.",
                "owner_queue": "public-lens-catalog-research",
                "resolution_status": "open",
                "first_detected": "",
                "last_checked": "",
            }
        )
    return rows


def write_gap_register(
    rows: list[dict[str, str]],
    *,
    csv_path: Path,
    md_path: Path,
    history_csv_path: Path = DEFAULT_HISTORY_CSV,
    history_md_path: Path = DEFAULT_HISTORY_MD,
) -> int:
    today = date.today().isoformat()
    prior_rows = read_csv_rows(csv_path)
    previous = prior_first_detected(csv_path)
    for row in rows:
        key = (row["company_slug"], row["dimension"], row["reason_code"])
        row["first_detected"] = previous.get(key, today)
        row["last_checked"] = today

    resolved = write_resolution_history(
        prior_rows=prior_rows,
        current_rows=rows,
        csv_path=history_csv_path,
        md_path=history_md_path,
        resolved_on=today,
    )

    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=GAP_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    by_dimension = Counter(row["dimension"] for row in rows)
    lines = [
        "# Public Lens Information Gaps",
        "",
        f"Generated: `{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}`",
        "",
        "This register records information that automation could not responsibly infer. The downstream sourcing and distillation teams own resolution using public-safe evidence.",
        "",
        "## Summary",
        "",
        f"- Open gaps: `{len(rows)}`",
        f"- Companies affected: `{len({row['company_slug'] for row in rows if not row['company_slug'].startswith('_')})}`",
    ]
    for dimension in (*SEVEN_DIMENSIONS, "catalog_capacity"):
        if by_dimension[dimension]:
            lines.append(f"- `{dimension}`: `{by_dimension[dimension]}`")
    lines.extend(
        [
            "",
            "## Open Queue",
            "",
            "| Company | Dimension | Status | Reason | Next action | Owner queue | First detected |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for row in rows:
        clean = {key: value.replace("|", "\\|").replace("\n", " ") for key, value in row.items()}
        lines.append(
            "| {company} | `{dimension}` | `{gap_status}` | {reason} | {next_action} | `{owner_queue}` | `{first_detected}` |".format(**clean)
        )
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    return resolved


def current_company_names() -> list[str]:
    return [path.name for path in company_dirs()]


def command_snapshot(args: argparse.Namespace) -> int:
    write_json(
        args.output,
        {
            "captured_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "company_count": len(current_company_names()),
            "company_slugs": current_company_names(),
        },
    )
    print(f"public_lens_baseline={args.output} companies={len(current_company_names())}")
    return 0


def command_verify_growth(args: argparse.Namespace) -> int:
    baseline = load_json(args.baseline)
    before = {str(value) for value in baseline.get("company_slugs", [])}
    after = set(current_company_names())
    added = sorted(after - before)
    print(
        f"public_lens_growth_status={'ok' if len(added) >= args.min_new_companies else 'fail'} "
        f"before={len(before)} after={len(after)} added={len(added)} "
        f"minimum={args.min_new_companies} companies={','.join(added) or 'none'}"
    )
    return 0 if len(added) >= args.min_new_companies else 1


def command_verify_weekly_cohort(args: argparse.Namespace) -> int:
    run_date = date.fromisoformat(args.run_date) if args.run_date else date.today()
    start = week_start(run_date)
    introduced = []
    for path in company_dirs():
        profile = load_json(path / "profile.json")
        if introduced_this_week(profile, start=start):
            introduced.append(path.name)
    introduced.sort()
    status = "ok" if len(introduced) >= args.min_new_companies else "fail"
    print(
        f"public_lens_weekly_cohort_status={status} week_start={start.isoformat()} "
        f"introduced={len(introduced)} minimum={args.min_new_companies} "
        f"companies={','.join(introduced) or 'none'}"
    )
    return 0 if status == "ok" else 1


def command_verify_reserve(args: argparse.Namespace) -> int:
    existing = set(current_company_names())
    remaining = sorted(slug for slug in CATALOG if slug not in existing)
    status = "ok" if len(remaining) >= args.min_unused else "fail"
    print(
        f"public_lens_catalog_reserve_status={status} unused={len(remaining)} "
        f"minimum={args.min_unused} companies={','.join(remaining) or 'none'}"
    )
    return 0 if status == "ok" else 1


def command_audit(args: argparse.Namespace) -> int:
    rows = build_gap_rows(reserve_target=args.catalog_reserve_target)
    resolved = write_gap_register(
        rows,
        csv_path=args.csv_output,
        md_path=args.markdown_output,
        history_csv_path=args.history_csv_output,
        history_md_path=args.history_markdown_output,
    )
    print(
        f"public_lens_gap_status=ok open_gaps={len(rows)} "
        f"resolved_added={resolved} csv={display_path(args.csv_output)} "
        f"markdown={display_path(args.markdown_output)} "
        f"history_csv={display_path(args.history_csv_output)} "
        f"history_markdown={display_path(args.history_markdown_output)}"
    )
    return 0


def week_start(value: date) -> date:
    return value - timedelta(days=value.weekday())


def introduced_this_week(profile: dict[str, Any], *, start: date) -> bool:
    raw = str(profile.get("introduced_at", ""))
    try:
        return date.fromisoformat(raw) >= start
    except ValueError:
        return False


def command_plan_daily(args: argparse.Namespace) -> int:
    run_date = date.fromisoformat(args.run_date) if args.run_date else date.today()
    weekday = run_date.weekday() if args.weekday == "auto" else int(args.weekday)
    focus = DAILY_FOCUS[weekday]
    start = week_start(run_date)
    profiles: dict[str, dict[str, Any]] = {
        path.name: load_json(path / "profile.json") for path in company_dirs()
    }
    weekly = sorted(
        slug for slug, profile in profiles.items() if introduced_this_week(profile, start=start)
    )[: args.weekly_cohort_limit]

    gaps = build_gap_rows(reserve_target=args.catalog_reserve_target)
    gap_counts: dict[str, int] = defaultdict(int)
    focus_gap_counts: dict[str, int] = defaultdict(int)
    for row in gaps:
        slug = row["company_slug"]
        if slug.startswith("_"):
            continue
        gap_counts[slug] += 1
        if row["dimension"] in focus:
            focus_gap_counts[slug] += 1
    historical = sorted(
        (slug for slug in profiles if slug not in weekly),
        key=lambda slug: (-focus_gap_counts[slug], -gap_counts[slug], slug),
    )[: args.historical_limit]

    payload = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "run_date": run_date.isoformat(),
        "weekday": weekday,
        "week_start": start.isoformat(),
        "focus_dimensions": list(focus),
        "weekly_new_company_targets": weekly,
        "historical_company_targets": historical,
        "open_gap_count": len(gaps),
        "rules": {
            "weekly_new_company_target": 2,
            "daily_historical_company_target": args.historical_limit,
            "public_safe_only": True,
            "unresolved_items_enter_gap_register": True,
        },
    }
    write_json(args.json_output, payload)

    lines = [
        "# Public Lens Daily Plan",
        "",
        f"Generated: `{payload['generated_at']}`",
        f"Run date: `{run_date.isoformat()}`",
        f"Week start: `{start.isoformat()}`",
        "",
        "## Today's Focus",
        "",
        *[f"- `{dimension}`" for dimension in focus],
        "",
        "## This Week's New Companies",
        "",
        *([f"- `{slug}`" for slug in weekly] or ["- No company has an `introduced_at` date in the current week. Record this as an operations exception."]),
        "",
        "## Historical Company Targets",
        "",
        *[f"- `{slug}`" for slug in historical],
        "",
        "## Execution Contract",
        "",
        "- Collect only approved public sources and store source metadata plus non-verbatim signals.",
        "- Patch supported dimensions for the weekly cohort first, then the historical targets.",
        "- Do not infer unsupported company hiring standards.",
        "- Keep every unresolved item in `public-lens-information-gaps.csv` with a reason and next action.",
        "- Run public boundary and seven-dimension validators before creating a PR.",
        "",
    ]
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    print(
        f"public_lens_daily_plan_status=ok weekday={weekday} focus={','.join(focus)} "
        f"weekly_targets={len(weekly)} historical_targets={len(historical)} gaps={len(gaps)}"
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Operate recurring public lens expansion and maintenance.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    snapshot = subparsers.add_parser("snapshot", help="Capture company count before weekly expansion.")
    snapshot.add_argument("--output", type=Path, required=True)
    snapshot.set_defaults(func=command_snapshot)

    growth = subparsers.add_parser("verify-growth", help="Enforce the weekly new-company target.")
    growth.add_argument("--baseline", type=Path, required=True)
    growth.add_argument("--min-new-companies", type=int, default=2)
    growth.set_defaults(func=command_verify_growth)

    cohort = subparsers.add_parser(
        "verify-weekly-cohort",
        help="Confirm the current calendar week contains the required new-company cohort.",
    )
    cohort.add_argument("--run-date")
    cohort.add_argument("--min-new-companies", type=int, default=2)
    cohort.set_defaults(func=command_verify_weekly_cohort)

    reserve = subparsers.add_parser(
        "verify-reserve",
        help="Enforce a minimum unused approved-candidate reserve.",
    )
    reserve.add_argument("--min-unused", type=int, default=8)
    reserve.set_defaults(func=command_verify_reserve)

    audit = subparsers.add_parser("audit-gaps", help="Generate the information-gap register.")
    audit.add_argument("--csv-output", type=Path, default=DEFAULT_GAP_CSV)
    audit.add_argument("--markdown-output", type=Path, default=DEFAULT_GAP_MD)
    audit.add_argument("--history-csv-output", type=Path, default=DEFAULT_HISTORY_CSV)
    audit.add_argument("--history-markdown-output", type=Path, default=DEFAULT_HISTORY_MD)
    audit.add_argument("--catalog-reserve-target", type=int, default=8)
    audit.set_defaults(func=command_audit)

    plan = subparsers.add_parser("plan-daily", help="Generate a daily seven-dimension work plan.")
    plan.add_argument("--run-date")
    plan.add_argument("--weekday", default="auto", choices=("auto", "0", "1", "2", "3", "4", "5", "6"))
    plan.add_argument("--weekly-cohort-limit", type=int, default=2)
    plan.add_argument("--historical-limit", type=int, default=2)
    plan.add_argument("--catalog-reserve-target", type=int, default=8)
    plan.add_argument("--json-output", type=Path, default=DEFAULT_PLAN_JSON)
    plan.add_argument("--markdown-output", type=Path, default=DEFAULT_PLAN_MD)
    plan.set_defaults(func=command_plan_daily)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
