#!/usr/bin/env python3
"""Context-aware public release scanner for AIMS Lens Engine.

The scanner classifies findings as:

- blocker: must not be in a public export.
- review: needs manual review or public-safe rewrite.
- allowed_context: expected marker in schemas, policies, or public strategy docs.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover - environment guard
    raise SystemExit("PyYAML is required. Run with the lens workspace virtualenv.") from exc


ROOT = Path(__file__).resolve().parents[1]
PUBLIC_MANIFEST = ROOT / "public_manifest.yaml"
PRIVATE_MANIFEST = ROOT / "private_manifest.yaml"


@dataclass(frozen=True)
class Finding:
    severity: str
    code: str
    path: str
    line: int
    marker: str
    message: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "severity": self.severity,
            "code": self.code,
            "path": self.path,
            "line": self.line,
            "marker": self.marker,
            "message": self.message,
        }


def load_yaml(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"manifest must be a mapping: {path}")
    return payload


def flatten(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        items: list[str] = []
        for item in value:
            items.extend(flatten(item))
        return items
    if isinstance(value, dict):
        items = []
        for item in value.values():
            items.extend(flatten(item))
        return items
    return []


def normalize_path(value: str) -> str:
    return value.replace("\\", "/").lstrip("./")


def is_glob(pattern: str) -> bool:
    return any(char in pattern for char in "*?[]")


def matches_pattern(rel_path: str, pattern: str) -> bool:
    rel = normalize_path(rel_path)
    pat = normalize_path(pattern)
    if pat.endswith("/"):
        return rel == pat.rstrip("/") or rel.startswith(pat)
    if is_glob(pat):
        return fnmatch.fnmatch(rel, pat)
    return rel == pat or rel.startswith(pat.rstrip("/") + "/")


def collect_allow_paths(public_manifest: dict[str, Any]) -> list[str]:
    paths = flatten(public_manifest.get("allow_paths"))
    paths.extend(flatten(public_manifest.get("allowed_service_public_surface", {}).get("allowed_now")))
    deduped = []
    seen = set()
    for path in paths:
        normalized = normalize_path(path)
        if normalized not in seen:
            seen.add(normalized)
            deduped.append(normalized)
    return deduped


def list_files(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    if path.is_dir():
        return sorted(item for item in path.rglob("*") if item.is_file())
    return []


def files_from_allowlist(public_manifest: dict[str, Any]) -> list[Path]:
    files: list[Path] = []
    for manifest_path in collect_allow_paths(public_manifest):
        source = (ROOT / manifest_path).resolve()
        if source.exists():
            files.extend(list_files(source))
    return sorted(dict.fromkeys(files))


def files_from_target(target: Path) -> list[Path]:
    target = target.resolve()
    if not target.exists():
        raise FileNotFoundError(target)
    return list_files(target)


def rel_to_base(path: Path, base: Path) -> str:
    try:
        return path.resolve().relative_to(base.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def is_text_file(path: Path) -> bool:
    if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".webp", ".pdf", ".sqlite", ".db"}:
        return False
    try:
        path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return False
    return True


def classify_path(rel_path: str, private_manifest: dict[str, Any]) -> Finding | None:
    blocked_patterns = flatten(private_manifest.get("blocked_paths"))
    for pattern in blocked_patterns:
        if matches_pattern(rel_path, pattern):
            return Finding(
                severity="blocker",
                code="blocked_path",
                path=rel_path,
                line=0,
                marker=pattern,
                message="Path is blocked by private_manifest.yaml.",
            )
    return None


def is_policy_doc(rel_path: str) -> bool:
    return rel_path in {
        "CONTRIBUTING.md",
        "CONTENT_LICENSE.md",
        "NOTICE",
        "private_manifest.yaml",
        "public_manifest.yaml",
        "docs/public-lens-operations-plan.md",
        "docs/public-lens-refresh-and-expansion.md",
        "docs/refresh-candidates/public-lens-refresh-candidate.md",
        "docs/public-private-split-strategy.md",
        "docs/public-private-split-strategy-zh.md",
        "governance/privacy-and-fairness.md",
        "governance/evidence-standard.md",
    }


def is_schema_or_contract(rel_path: str) -> bool:
    return rel_path.startswith("schemas/") or rel_path == "api/openapi.yaml"


def is_example(rel_path: str) -> bool:
    return rel_path.startswith("examples/")


def is_tool(rel_path: str) -> bool:
    return rel_path.startswith("tools/")


def is_release_boundary_tool(rel_path: str) -> bool:
    return rel_path in {
        "tools/export_public_release.py",
        "tools/scan_public_export.py",
        "tools/generate_public_release_audit_report.py",
    }


def is_lens_source(rel_path: str) -> bool:
    return rel_path.startswith("company_lenses/")


def is_private_distillation_note(rel_path: str) -> bool:
    return "/research/08-private-material-distillation.md" in rel_path


def add(
    findings: list[Finding],
    severity: str,
    code: str,
    rel_path: str,
    line_no: int,
    marker: str,
    message: str,
) -> None:
    findings.append(Finding(severity, code, rel_path, line_no, marker, message))


SECRET_PATTERNS = [
    ("secret_assignment", re.compile(r"(?i)\b(secret|client_secret|api[_-]?key|token|password)\b\s*[:=]\s*['\"][^'\"\s]{8,}")),
    ("bearer_token", re.compile(r"(?i)Authorization:\s*Bearer\s+[A-Za-z0-9._~+/=-]{12,}")),
    ("postgres_password", re.compile(r"(?i)POSTGRES_PASSWORD\s*[:=]\s*.+")),
]

PROD_HOSTS = ("lens-api.jobace.ca", "lens.jobace.ca")
PRIVATE_PATH_MARKERS = (
    "private_materials/",
    "workspace_data/",
    "audit_logs/",
    "review_logs/",
    "tenant_uploads/",
    "candidate_data/",
    ".venv-lens-workspace/",
)


def scan_line(rel_path: str, line_no: int, line: str, findings: list[Finding]) -> None:
    stripped = line.strip()
    lower = stripped.lower()

    for code, pattern in SECRET_PATTERNS:
        if pattern.search(line):
            add(findings, "blocker", code, rel_path, line_no, pattern.pattern, "Possible secret or credential.")

    if re.search(r"['\"]?evidence_visibility['\"]?\s*[:=]\s*['\"]private_only['\"]", line):
        severity = "allowed_context" if is_policy_doc(rel_path) else "blocker"
        add(findings, severity, "private_only_evidence", rel_path, line_no, "private_only", "private_only evidence cannot be exported.")

    if any(term in lower for term in ("candidate resume", "candidate_answer", "candidate resume", "resume_text")):
        severity = "allowed_context" if is_policy_doc(rel_path) or is_schema_or_contract(rel_path) or is_example(rel_path) or is_tool(rel_path) else "blocker"
        add(findings, severity, "candidate_data_marker", rel_path, line_no, stripped[:120], "Candidate or resume marker found.")

    if "\"tenant_id\"" in line or "tenant_id:" in line:
        severity = "allowed_context" if is_policy_doc(rel_path) or is_schema_or_contract(rel_path) or is_example(rel_path) or is_tool(rel_path) else "review"
        add(findings, severity, "tenant_id_marker", rel_path, line_no, "tenant_id", "Tenant marker found; allowed in schemas/contracts/examples, review elsewhere.")

    if "review_decision" in line:
        severity = "allowed_context" if is_policy_doc(rel_path) or is_schema_or_contract(rel_path) or is_example(rel_path) or is_release_boundary_tool(rel_path) else "review"
        add(findings, severity, "review_decision_marker", rel_path, line_no, "review_decision", "Review decision marker found.")

    if "raw_text_path" in line:
        severity = "allowed_context" if is_policy_doc(rel_path) or is_schema_or_contract(rel_path) or is_release_boundary_tool(rel_path) else "blocker"
        add(findings, severity, "raw_text_path_marker", rel_path, line_no, "raw_text_path", "Raw material path marker found.")

    for marker in PRIVATE_PATH_MARKERS:
        if marker not in line:
            continue
        if is_policy_doc(rel_path) or is_release_boundary_tool(rel_path) or rel_path in {"README_ZH.md", "CHANGELOG.md", "docs/aims-lens-distillation-strategy-zh.md"}:
            severity = "allowed_context"
            message = "Private path appears in policy or release-boundary documentation."
        elif is_private_distillation_note(rel_path):
            severity = "review"
            message = "Private path appears in private distillation summary; verify public-safe synthesis."
        elif is_lens_source(rel_path):
            severity = "review"
            message = "Private path appears in a public lens candidate; rewrite or justify as public-safe synthesis."
        else:
            severity = "blocker"
            message = "Private path marker found outside allowed context."
        add(findings, severity, "private_path_marker", rel_path, line_no, marker, message)

    for host in PROD_HOSTS:
        if host not in line:
            continue
        severity = "allowed_context" if is_policy_doc(rel_path) or is_release_boundary_tool(rel_path) or rel_path == "README.md" else "review"
        add(findings, severity, "production_host_marker", rel_path, line_no, host, "Production host marker found.")

    if "private_distillation_public_safe" in line:
        add(
            findings,
            "allowed_context",
            "private_safe_class",
            rel_path,
            line_no,
            "private_distillation_public_safe",
            "Allowed evidence class when non-verbatim and public-safe.",
        )


def scan_file(path: Path, base: Path, private_manifest: dict[str, Any]) -> list[Finding]:
    rel_path = rel_to_base(path, base)
    path_finding = classify_path(rel_path, private_manifest)
    findings = [path_finding] if path_finding else []
    if not is_text_file(path):
        return findings
    text = path.read_text(encoding="utf-8")
    for line_no, line in enumerate(text.splitlines(), 1):
        scan_line(rel_path, line_no, line, findings)
    return findings


def summarize(findings: list[Finding]) -> dict[str, int]:
    summary = {"blocker": 0, "review": 0, "allowed_context": 0}
    for finding in findings:
        summary[finding.severity] = summary.get(finding.severity, 0) + 1
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Scan public release files for private markers.")
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--allowlist", action="store_true", help="Scan files selected by public_manifest.yaml.")
    source.add_argument("--target", type=Path, help="Scan an existing export directory or file.")
    parser.add_argument("--json", action="store_true", help="Print JSON report.")
    parser.add_argument("--include-allowed", action="store_true", help="Include allowed_context findings in text output.")
    args = parser.parse_args()

    public_manifest = load_yaml(PUBLIC_MANIFEST)
    private_manifest = load_yaml(PRIVATE_MANIFEST)
    if args.target:
        base = args.target.resolve()
        files = files_from_target(base)
    else:
        base = ROOT
        files = files_from_allowlist(public_manifest)

    findings: list[Finding] = []
    for file_path in files:
        findings.extend(scan_file(file_path, base, private_manifest))

    summary = summarize(findings)
    report = {
        "status": "fail" if summary["blocker"] else "review" if summary["review"] else "ok",
        "source": args.target.as_posix() if args.target else "public_manifest_allowlist",
        "files_scanned": len(files),
        "summary": summary,
        "findings": [finding.to_dict() for finding in findings],
    }

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(
            "public_scan_status={status} files={files_scanned} blockers={blocker} review={review} allowed_context={allowed_context}".format(
                status=report["status"],
                files_scanned=report["files_scanned"],
                blocker=summary["blocker"],
                review=summary["review"],
                allowed_context=summary["allowed_context"],
            )
        )
        visible = findings if args.include_allowed else [finding for finding in findings if finding.severity != "allowed_context"]
        for finding in visible:
            print(
                f"{finding.severity.upper()}: {finding.path}:{finding.line} {finding.code} "
                f"marker={finding.marker!r} {finding.message}"
            )
    return 1 if summary["blocker"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
