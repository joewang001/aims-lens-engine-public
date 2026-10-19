import argparse
import csv
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from tools import collect_public_lens_sources
from tools import generate_public_lens_patch
from tools import public_lens_operations


class ExpansionCatalogTests(unittest.TestCase):
    def test_catalog_extension_has_eight_weeks_of_candidates(self):
        payload = json.loads(
            collect_public_lens_sources.CATALOG_EXTENSION.read_text(encoding="utf-8")
        )
        candidates = payload["candidates"]
        self.assertGreaterEqual(len(candidates), 16)
        self.assertEqual([item["slug"] for item in candidates[:2]], ["amd", "intel"])

    def test_each_unused_candidate_has_public_sources_and_role_overlay(self):
        extension_slugs = {
            item["slug"]
            for item in json.loads(
                collect_public_lens_sources.CATALOG_EXTENSION.read_text(encoding="utf-8")
            )["candidates"]
        }
        for slug in extension_slugs:
            candidate = collect_public_lens_sources.CATALOG[slug]
            self.assertGreaterEqual(len(candidate["sources"]), 2, slug)
            self.assertTrue(candidate["role_overlays"], slug)
            self.assertTrue(candidate["questions"], slug)
            for source in candidate["sources"]:
                self.assertTrue(source["url"].startswith("https://"), slug)
                self.assertTrue(source["source_type"].startswith("official_"), slug)


class GrowthGateTests(unittest.TestCase):
    def test_growth_gate_passes_only_when_minimum_is_met(self):
        current = public_lens_operations.current_company_names()
        with tempfile.TemporaryDirectory() as directory:
            baseline = Path(directory) / "baseline.json"
            baseline.write_text(
                json.dumps(
                    {
                        "company_slugs": [
                            slug for slug in current if slug not in {"amd", "intel"}
                        ]
                    }
                ),
                encoding="utf-8",
            )
            args = argparse.Namespace(baseline=baseline, min_new_companies=2)
            self.assertEqual(public_lens_operations.command_verify_growth(args), 0)

            baseline.write_text(
                json.dumps({"company_slugs": current}),
                encoding="utf-8",
            )
            self.assertEqual(public_lens_operations.command_verify_growth(args), 1)

    def test_weekly_cohort_and_reserve_hard_gates(self):
        cohort_args = argparse.Namespace(run_date="2026-10-18", min_new_companies=2)
        self.assertEqual(
            public_lens_operations.command_verify_weekly_cohort(cohort_args),
            0,
        )
        reserve_args = argparse.Namespace(min_unused=8)
        self.assertEqual(public_lens_operations.command_verify_reserve(reserve_args), 0)


class ExistingLensMergeTests(unittest.TestCase):
    def test_mapping_merge_updates_existing_identity_and_adds_new_identity(self):
        merged = generate_public_lens_patch.merge_mapping_list(
            [{"signal": "A", "confidence": 0.5}],
            [
                {"signal": "A", "confidence": 0.8},
                {"signal": "B", "confidence": 0.7},
            ],
            identity_key="signal",
        )
        self.assertEqual(
            merged,
            [
                {"signal": "A", "confidence": 0.8},
                {"signal": "B", "confidence": 0.7},
            ],
        )


class DailyOperationsTests(unittest.TestCase):
    @staticmethod
    def _thin_lens(directory: str) -> Path:
        """Build a synthetic thin lens so tests do not depend on repo gap state."""
        path = Path(directory) / "thin-co"
        path.mkdir()
        (path / "profile.json").write_text(
            json.dumps(
                {
                    "company": "Thin Co",
                    "lens_status": "LIGHTWEIGHT_SCAN",
                    "source_cutoff": "2026-10-19",
                    "culture_principles": [],
                    "hiring_signals": [],
                    "anti_signals": [],
                    "honest_limits": [],
                    "aims_weighting": {},
                    "evidence_summary": {},
                }
            ),
            encoding="utf-8",
        )
        return path

    def test_tuesday_through_sunday_cover_all_seven_dimensions(self):
        covered = {
            dimension
            for weekday in range(1, 7)
            for dimension in public_lens_operations.DAILY_FOCUS[weekday]
        }
        self.assertEqual(covered, set(public_lens_operations.SEVEN_DIMENSIONS))

    def test_gap_audit_records_reason_and_downstream_action(self):
        with tempfile.TemporaryDirectory() as directory:
            rows = public_lens_operations.audit_company(self._thin_lens(directory))
        self.assertTrue(rows)
        for row in rows:
            self.assertTrue(row["reason"])
            self.assertTrue(row["next_action"])
            self.assertTrue(row["owner_queue"])
            self.assertEqual(row["resolution_status"], "open")

    def test_resolved_gap_is_appended_once_to_history(self):
        with tempfile.TemporaryDirectory() as directory:
            prior = public_lens_operations.audit_company(self._thin_lens(directory))[0]
        prior["first_detected"] = "2026-10-01"
        prior["last_checked"] = "2026-10-18"
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            history_csv = root / "history.csv"
            history_md = root / "history.md"
            added = public_lens_operations.write_resolution_history(
                prior_rows=[prior],
                current_rows=[],
                csv_path=history_csv,
                md_path=history_md,
                resolved_on="2026-10-19",
            )
            self.assertEqual(added, 1)
            with history_csv.open("r", encoding="utf-8", newline="") as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["resolution_status"], "resolved")
            self.assertEqual(rows[0]["resolved_at"], "2026-10-19")
            self.assertTrue(rows[0]["resolution_basis"])

            added = public_lens_operations.write_resolution_history(
                prior_rows=[prior],
                current_rows=[],
                csv_path=history_csv,
                md_path=history_md,
                resolved_on="2026-10-19",
            )
            self.assertEqual(added, 0)
            with history_csv.open("r", encoding="utf-8", newline="") as handle:
                self.assertEqual(len(list(csv.DictReader(handle))), 1)

    def test_resolution_provenance_supports_github_merge_titles(self):
        subjects = (
            ("Track resolved gaps (#27)", "27"),
            ("Merge pull request #28 from automation/gaps", "28"),
        )
        for subject, expected_pr in subjects:
            with self.subTest(subject=subject), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                history_path = root / "history.csv"
                rows = [
                    {
                        "resolution_record_id": "record-id",
                        "resolution_commit": "pending:first_commit_containing_record",
                        "resolution_pr": "pending:merge_pr",
                    }
                ]
                completed = SimpleNamespace(
                    stdout=f"{'a' * 40}\t{subject}\n",
                )
                with (
                    patch.object(public_lens_operations, "ROOT", root),
                    patch.object(
                        public_lens_operations.subprocess,
                        "run",
                        return_value=completed,
                    ) as run,
                ):
                    public_lens_operations.reconcile_resolution_provenance(
                        rows,
                        history_path,
                    )
                self.assertEqual(rows[0]["resolution_commit"], "a" * 40)
                self.assertTrue(rows[0]["resolution_pr"].endswith(f"/{expected_pr}"))
                self.assertIn("--first-parent", run.call_args.args[0])

    def test_workflow_has_separate_weekly_and_daily_schedules(self):
        workflow = (
            public_lens_operations.ROOT
            / ".github"
            / "workflows"
            / "public-lens-maintenance.yml"
        ).read_text(encoding="utf-8")
        self.assertIn('cron: "0 13 * * 1"', workflow)
        self.assertIn('cron: "0 13 * * 0,2-6"', workflow)
        self.assertNotIn("--expansion-limit \"$WEEKLY_NEW_COMPANY_TARGET\" --allow-empty", workflow)
        self.assertIn("run_weekly_public_lens_expansion.py", workflow)
        self.assertIn("verify-reserve --min-unused 8", workflow)
        self.assertIn("automation/public-lens-source-agent", workflow)
        self.assertIn("gh pr create", workflow)

    def test_openclaw_runner_enforces_substantive_daily_output(self):
        runner = (
            public_lens_operations.ROOT
            / "ops"
            / "openclaw"
            / "daily-source-agent.sh"
        ).read_text(encoding="utf-8")
        self.assertIn('if [ "$PACKET_COUNT" -lt 2 ]', runner)
        self.assertIn('if [ "$LENS_COUNT" -lt 1 ]', runner)
        self.assertIn("git push --force-with-lease", runner)
        self.assertIn("public-lens-gap-resolution-history.csv", runner)


if __name__ == "__main__":
    unittest.main()
