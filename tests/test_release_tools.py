import unittest
from pathlib import Path

from tools import export_public_release
from tools import generate_public_release_audit_report
from tools import scan_public_export


class ReleasePathNormalizationTests(unittest.TestCase):
    def test_dot_github_path_is_preserved_by_export_tool(self):
        self.assertEqual(
            export_public_release.normalize_manifest_path(
                ".github/workflows/public-lens-maintenance.yml"
            ),
            ".github/workflows/public-lens-maintenance.yml",
        )

    def test_dot_github_path_is_preserved_by_scanner(self):
        self.assertEqual(
            scan_public_export.normalize_path(
                ".github/workflows/runtime-core-ci.yml"
            ),
            ".github/workflows/runtime-core-ci.yml",
        )

    def test_explicit_relative_prefix_is_removed(self):
        self.assertEqual(
            export_public_release.normalize_manifest_path("./README.md"),
            "README.md",
        )
        self.assertEqual(
            scan_public_export.normalize_path("./README.md"),
            "README.md",
        )

    def test_allowlist_resolves_public_workflow(self):
        manifest = scan_public_export.load_yaml(
            scan_public_export.PUBLIC_MANIFEST
        )
        files = scan_public_export.files_from_allowlist(manifest)
        relative = {
            path.resolve()
            .relative_to(scan_public_export.ROOT.resolve())
            .as_posix()
            for path in files
        }
        self.assertIn(
            ".github/workflows/public-lens-maintenance.yml",
            relative,
        )


class ReleaseContentPolicyTests(unittest.TestCase):
    def test_contract_tenant_marker_is_allowed_context_not_blocker(self):
        private_manifest = scan_public_export.load_yaml(
            scan_public_export.PRIVATE_MANIFEST
        )
        path = (
            scan_public_export.ROOT
            / "schemas"
            / "jobace_adapter_contract.schema.json"
        )
        findings = scan_public_export.scan_file(
            path,
            scan_public_export.ROOT,
            private_manifest,
        )
        self.assertFalse(
            any(finding.severity == "blocker" for finding in findings)
        )
        self.assertFalse(
            any(finding.severity == "review" for finding in findings)
        )
        self.assertTrue(
            any(
                finding.severity == "allowed_context"
                and finding.code == "tenant_id_marker"
                for finding in findings
            )
        )

    def test_export_plan_scans_each_overlapping_file_once(self):
        public_manifest = {
            "allow_paths": {
                "runtime": [
                    "runtime_core/",
                    "runtime_core/__init__.py",
                ]
            },
            "initial_public_release": {"company_lenses": []},
        }
        private_manifest = {"blocked_paths": []}
        original_scan_file = export_public_release.scan_file
        seen = []

        def counting_scan(path, base, private):
            seen.append(
                path.resolve()
                .relative_to(export_public_release.ROOT.resolve())
                .as_posix()
            )
            return []

        export_public_release.scan_file = counting_scan
        try:
            plan = export_public_release.build_plan(
                public_manifest,
                private_manifest,
                scan_content=True,
            )
        finally:
            export_public_release.scan_file = original_scan_file

        self.assertEqual(plan["status"], "ok")
        self.assertEqual(
            seen.count("runtime_core/__init__.py"),
            1,
        )


class ReleaseAuditToolTests(unittest.TestCase):
    def test_relative_audit_output_resolves_inside_repository(self):
        output, relative = (
            generate_public_release_audit_report.resolve_output_path(
                Path("dist/public/test-audit.md")
            )
        )
        self.assertEqual(
            relative.as_posix(),
            "dist/public/test-audit.md",
        )
        self.assertEqual(
            output,
            (
                generate_public_release_audit_report.ROOT
                / "dist/public/test-audit.md"
            ).resolve(),
        )


if __name__ == "__main__":
    unittest.main()
