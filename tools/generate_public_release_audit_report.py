#!/usr/bin/env python3
"""Generate a Markdown public release audit report from scanner findings."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from scan_public_export import (
    PRIVATE_MANIFEST,
    PUBLIC_MANIFEST,
    ROOT,
    files_from_allowlist,
    files_from_target,
    load_yaml,
    scan_file,
    summarize,
)


DEFAULT_OUTPUT = ROOT / "docs" / "public-release-audit-report.md"


def company_for_path(path: str) -> str:
    parts = path.split("/")
    if len(parts) >= 2 and parts[0] == "company_lenses":
        return parts[1]
    if parts[0] == "tools":
        return "_tools"
    if parts[0] == "schemas":
        return "_schemas"
    if parts[0] == "examples":
        return "_examples"
    if parts[0] == "docs":
        return "_docs"
    if parts[0] == "api":
        return "_api"
    return "_general"


def file_type_for_path(path: str) -> str:
    if path.endswith(".json"):
        return "json"
    if path.endswith(".md"):
        return "markdown"
    if path.endswith(".yaml") or path.endswith(".yml"):
        return "yaml"
    if path.endswith(".py"):
        return "python"
    return Path(path).suffix.lstrip(".") or "unknown"


def bullet(text: str) -> str:
    return f"- {text}"


def table(rows: list[list[Any]], headers: list[str]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(cell) for cell in row) + " |")
    return "\n".join(lines)


def format_finding(finding: dict[str, Any]) -> str:
    return (
        f"- `{finding['path']}:{finding['line']}` "
        f"`{finding['code']}` marker `{finding['marker']}`: {finding['message']}"
    )


def release_file_status() -> dict[str, bool]:
    return {
        "LICENSE": (ROOT / "LICENSE").is_file(),
        "NOTICE": (ROOT / "NOTICE").is_file(),
        "CONTENT_LICENSE.md": (ROOT / "CONTENT_LICENSE.md").is_file(),
        "CONTRIBUTING.md": (ROOT / "CONTRIBUTING.md").is_file(),
    }


def build_report(scan_report: dict[str, Any], *, source_label: str) -> str:
    findings = scan_report["findings"]
    actionable = [item for item in findings if item["severity"] in {"blocker", "review"}]
    blockers = [item for item in findings if item["severity"] == "blocker"]
    reviews = [item for item in findings if item["severity"] == "review"]
    allowed = [item for item in findings if item["severity"] == "allowed_context"]

    by_company = defaultdict(list)
    by_code = defaultdict(list)
    by_file_type = defaultdict(list)
    for item in actionable:
        by_company[company_for_path(item["path"])].append(item)
        by_code[item["code"]].append(item)
        by_file_type[file_type_for_path(item["path"])].append(item)

    company_rows = []
    for company, items in sorted(by_company.items()):
        counts = Counter(item["severity"] for item in items)
        company_rows.append([company, counts.get("blocker", 0), counts.get("review", 0), len(items)])

    code_rows = []
    for code, items in sorted(by_code.items()):
        counts = Counter(item["severity"] for item in items)
        code_rows.append([code, counts.get("blocker", 0), counts.get("review", 0), len(items)])

    file_type_rows = []
    for file_type, items in sorted(by_file_type.items()):
        counts = Counter(item["severity"] for item in items)
        file_type_rows.append([file_type, counts.get("blocker", 0), counts.get("review", 0), len(items)])

    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    summary = scan_report["summary"]

    lines = [
        "# Public Release Audit Report",
        "",
        f"Generated at: `{generated_at}`",
        "",
        f"Source: `{source_label}`",
        "",
        "## Summary",
        "",
        table(
            [
                ["files_scanned", scan_report["files_scanned"]],
                ["status", scan_report["status"]],
                ["blocker", summary.get("blocker", 0)],
                ["review", summary.get("review", 0)],
                ["allowed_context", summary.get("allowed_context", 0)],
            ],
            ["Metric", "Value"],
        ),
        "",
    ]

    if blockers:
        lines.extend(
            [
                "## Blockers",
                "",
                "These must be resolved before any public repository push.",
                "",
                *[format_finding(item) for item in blockers],
                "",
            ]
        )
    else:
        lines.extend(["## Blockers", "", "No blockers found by the current scanner.", ""])

    lines.extend(
        [
            "## Review Queue By Area",
            "",
            table(company_rows, ["Area", "Blocker", "Review", "Total"]) if company_rows else "No actionable findings.",
            "",
            "## Review Queue By Finding Type",
            "",
            table(code_rows, ["Finding Type", "Blocker", "Review", "Total"]) if code_rows else "No actionable findings.",
            "",
            "## Review Queue By File Type",
            "",
            table(file_type_rows, ["File Type", "Blocker", "Review", "Total"]) if file_type_rows else "No actionable findings.",
            "",
            "## Company Lens Review Items",
            "",
        ]
    )

    company_names = [name for name in sorted(by_company) if not name.startswith("_")]
    if company_names:
        for company in company_names:
            lines.extend([f"### `{company}`", ""])
            for item in by_company[company]:
                lines.append(format_finding(item))
            lines.append("")
    else:
        lines.extend(["No company lens review items.", ""])

    non_company_names = [name for name in sorted(by_company) if name.startswith("_")]
    if non_company_names:
        lines.extend(["## Non-Company Review Items", ""])
        for area in non_company_names:
            lines.extend([f"### `{area}`", ""])
            for item in by_company[area]:
                lines.append(format_finding(item))
            lines.append("")

    lines.extend(
        [
            "## Allowed Context Summary",
            "",
            "Allowed-context findings are not release blockers. They are included so reviewers can see why sensitive-looking markers were tolerated.",
            "",
            table(
                [[code, count] for code, count in sorted(Counter(item["code"] for item in allowed).items())],
                ["Allowed Context Type", "Count"],
            )
            if allowed
            else "No allowed-context findings.",
            "",
            "## Recommended Next Actions",
            "",
        ]
    )

    if actionable:
        lines.extend(
            [
                bullet("Rewrite or justify company lens references to `private_materials/` as public-safe synthesis."),
                bullet("Decide whether `tenant_id` belongs in public company lens profile files or should be moved to private/tenant-only overlays."),
                bullet("Review public tools that mention `candidate_answer` or `candidate_answer_signal` and confirm they use synthetic fixtures only."),
                bullet("Create or replace the missing `company_lenses/shopify/` candidate before first public release."),
                bullet("Rerun `tools/scan_public_export.py --allowlist` after each rewrite batch."),
                "",
            ]
        )
    else:
        release_files = release_file_status()
        missing_release_files = [name for name, exists in release_files.items() if not exists]
        if missing_release_files:
            license_action = "Add missing release files: " + ", ".join(f"`{name}`" for name in missing_release_files) + "."
        else:
            license_action = "Perform final legal/copyright review of `LICENSE`, `NOTICE`, `CONTENT_LICENSE.md`, and `CONTRIBUTING.md`."
        lines.extend(
            [
                bullet("Run final schema and JSON validation on the exported public tree."),
                bullet(license_action),
                bullet("Manually spot-check the 12 exported company lenses before the first public push."),
                bullet("Create a clean public repository from `dist/public/aims-lens-engine/`; do not open the private source repository."),
                bullet("Keep `public_manifest.yaml` and `private_manifest.yaml` as the release boundary for future updates."),
                "",
            ]
        )

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate public release audit report.")
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--allowlist", action="store_true", help="Scan public_manifest allowlist. Default.")
    source.add_argument("--target", type=Path, help="Scan an existing export directory or file.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    public_manifest = load_yaml(PUBLIC_MANIFEST)
    private_manifest = load_yaml(PRIVATE_MANIFEST)
    if args.target:
        base = args.target.resolve()
        files = files_from_target(base)
        source_label = args.target.as_posix()
    else:
        base = ROOT
        files = files_from_allowlist(public_manifest)
        source_label = "public_manifest_allowlist"

    findings = []
    for file_path in files:
        findings.extend(scan_file(file_path, base, private_manifest))
    scan_report = {
        "status": "fail" if summarize(findings)["blocker"] else "review" if summarize(findings)["review"] else "ok",
        "files_scanned": len(files),
        "summary": summarize(findings),
        "findings": [finding.to_dict() for finding in findings],
    }
    report = build_report(scan_report, source_label=source_label)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(report, encoding="utf-8", newline="\n")
    print(f"audit_report={args.output.relative_to(ROOT)}")
    print(f"status={scan_report['status']} files={scan_report['files_scanned']} summary={scan_report['summary']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
