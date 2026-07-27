#!/usr/bin/env python3
"""Export the public AIMS Lens Engine release tree from manifests.

Default behavior is dry-run. Pass --execute to write files.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import shutil
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover - environment guard
    raise SystemExit("PyYAML is required. Run with the lens workspace virtualenv.") from exc


ROOT = Path(__file__).resolve().parents[1]
PUBLIC_MANIFEST = ROOT / "public_manifest.yaml"
PRIVATE_MANIFEST = ROOT / "private_manifest.yaml"


class ExportError(RuntimeError):
    pass


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise ExportError(f"missing manifest: {path.relative_to(ROOT)}")
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ExportError(f"manifest must be a mapping: {path.relative_to(ROOT)}")
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


def normalize_manifest_path(value: str) -> str:
    return value.replace("\\", "/").lstrip("./")


def resolve_repo_path(value: str) -> Path:
    path = (ROOT / normalize_manifest_path(value)).resolve()
    try:
        path.relative_to(ROOT.resolve())
    except ValueError as exc:
        raise ExportError(f"path escapes repository root: {value}") from exc
    return path


def is_glob(pattern: str) -> bool:
    return any(char in pattern for char in "*?[]")


def matches_pattern(rel_path: str, pattern: str) -> bool:
    rel = normalize_manifest_path(rel_path)
    pat = normalize_manifest_path(pattern)
    if pat.endswith("/"):
        return rel == pat.rstrip("/") or rel.startswith(pat)
    if is_glob(pat):
        return fnmatch.fnmatch(rel, pat)
    return rel == pat or rel.startswith(pat.rstrip("/") + "/")


def blocked_path_patterns(private_manifest: dict[str, Any]) -> list[str]:
    return flatten(private_manifest.get("blocked_paths"))


def content_markers(private_manifest: dict[str, Any]) -> list[str]:
    return flatten(private_manifest.get("blocked_content_markers"))


def collect_allow_paths(public_manifest: dict[str, Any]) -> list[str]:
    paths = flatten(public_manifest.get("allow_paths"))
    # Contracts listed outside allow_paths are also public surface.
    paths.extend(flatten(public_manifest.get("allowed_service_public_surface", {}).get("allowed_now")))
    deduped = []
    seen = set()
    for path in paths:
        normalized = normalize_manifest_path(path)
        if normalized not in seen:
            seen.add(normalized)
            deduped.append(normalized)
    return deduped


def source_is_blocked(rel_path: str, patterns: list[str]) -> str | None:
    for pattern in patterns:
        # dist/ is blocked as a source tree, but export_root itself may live under dist/.
        if matches_pattern(rel_path, pattern):
            return pattern
    return None


def list_files_for_path(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    if path.is_dir():
        return sorted(item for item in path.rglob("*") if item.is_file())
    return []


def scan_file_for_markers(path: Path, markers: list[str]) -> list[str]:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return []
    hits = []
    for marker in markers:
        if marker and marker in text:
            hits.append(marker)
    return hits


def validate_company_candidates(public_manifest: dict[str, Any]) -> tuple[list[str], list[str]]:
    errors = []
    warnings = []
    companies = public_manifest.get("initial_public_release", {}).get("company_lenses") or []
    for company in companies:
        path = company.get("path", "")
        status = company.get("status", "")
        slug = company.get("slug", path)
        if not path:
            errors.append(f"company {slug}: missing path")
            continue
        exists = resolve_repo_path(path).exists()
        if status == "existing_candidate" and not exists:
            errors.append(f"company {slug}: existing_candidate path missing: {path}")
        if status == "required_before_first_public_release" and not exists:
            warnings.append(f"company {slug}: required before first public release but not present yet: {path}")
    return errors, warnings


def build_plan(
    public_manifest: dict[str, Any],
    private_manifest: dict[str, Any],
    *,
    scan_content: bool,
) -> dict[str, Any]:
    allow_paths = collect_allow_paths(public_manifest)
    blocked_patterns = blocked_path_patterns(private_manifest)
    markers = content_markers(private_manifest)
    errors, warnings = validate_company_candidates(public_manifest)
    planned_files = []
    skipped_missing = []

    for allow_path in allow_paths:
        source = resolve_repo_path(allow_path)
        rel_allow = source.relative_to(ROOT.resolve()).as_posix()
        blocked_by = source_is_blocked(rel_allow, blocked_patterns)
        if blocked_by:
            errors.append(f"allow path is blocked by private manifest: {rel_allow} matches {blocked_by}")
            continue
        if not source.exists():
            skipped_missing.append(rel_allow)
            warnings.append(f"allow path missing and skipped: {rel_allow}")
            continue
        for file_path in list_files_for_path(source):
            rel_file = file_path.relative_to(ROOT.resolve()).as_posix()
            blocked_file_by = source_is_blocked(rel_file, blocked_patterns)
            if blocked_file_by:
                errors.append(f"file blocked by private manifest: {rel_file} matches {blocked_file_by}")
                continue
            marker_hits = scan_file_for_markers(file_path, markers) if scan_content else []
            if marker_hits:
                errors.append(f"file contains private markers: {rel_file} markers={marker_hits}")
                continue
            planned_files.append(rel_file)

    planned_files = sorted(dict.fromkeys(planned_files))
    return {
        "status": "fail" if errors else "ok",
        "errors": errors,
        "warnings": warnings,
        "skipped_missing": skipped_missing,
        "files": planned_files,
        "file_count": len(planned_files),
    }


def export_files(files: list[str], export_root: Path, *, clean: bool) -> None:
    if clean and export_root.exists():
        shutil.rmtree(export_root)
    export_root.mkdir(parents=True, exist_ok=True)
    for rel_file in files:
        source = ROOT / rel_file
        destination = export_root / rel_file
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)


def main() -> int:
    parser = argparse.ArgumentParser(description="Export public AIMS Lens Engine release tree.")
    parser.add_argument("--execute", action="store_true", help="Write the export tree. Default is dry-run.")
    parser.add_argument("--clean", action="store_true", help="Remove export root before writing. Requires --execute.")
    parser.add_argument(
        "--scan-content",
        action="store_true",
        help="Also scan allowlisted files for private_manifest blocked content markers.",
    )
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    parser.add_argument("--output", type=Path, help="Override export root.")
    args = parser.parse_args()

    if args.clean and not args.execute:
        raise SystemExit("--clean requires --execute")

    try:
        public_manifest = load_yaml(PUBLIC_MANIFEST)
        private_manifest = load_yaml(PRIVATE_MANIFEST)
        export_root = (args.output or ROOT / public_manifest["export_root"]).resolve()
        try:
            export_root.relative_to(ROOT.resolve())
        except ValueError as exc:
            raise ExportError(f"export root must stay inside repository: {export_root}") from exc

        plan = build_plan(public_manifest, private_manifest, scan_content=args.scan_content)
        plan["mode"] = "execute" if args.execute else "dry_run"
        plan["export_root"] = export_root.relative_to(ROOT.resolve()).as_posix()

        if plan["errors"]:
            if args.json:
                print(json.dumps(plan, indent=2, ensure_ascii=False))
            else:
                print(f"public_export_status=fail files={plan['file_count']}")
                for error in plan["errors"]:
                    print(f"ERROR: {error}")
                for warning in plan["warnings"]:
                    print(f"WARNING: {warning}")
            return 1

        if args.execute:
            export_files(plan["files"], export_root, clean=args.clean)

        if args.json:
            print(json.dumps(plan, indent=2, ensure_ascii=False))
        else:
            print(f"public_export_status=ok mode={plan['mode']} files={plan['file_count']}")
            print(f"export_root={plan['export_root']}")
            for warning in plan["warnings"]:
                print(f"WARNING: {warning}")
        return 0
    except ExportError as exc:
        print(f"public_export_status=fail error={exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
