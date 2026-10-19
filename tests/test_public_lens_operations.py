import argparse
import json
import tempfile
import unittest
from pathlib import Path

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
    def test_tuesday_through_sunday_cover_all_seven_dimensions(self):
        covered = {
            dimension
            for weekday in range(1, 7)
            for dimension in public_lens_operations.DAILY_FOCUS[weekday]
        }
        self.assertEqual(covered, set(public_lens_operations.SEVEN_DIMENSIONS))

    def test_gap_audit_records_reason_and_downstream_action(self):
        rows = public_lens_operations.build_gap_rows(reserve_target=8)
        self.assertTrue(rows)
        for row in rows:
            self.assertTrue(row["reason"])
            self.assertTrue(row["next_action"])
            self.assertTrue(row["owner_queue"])
            self.assertEqual(row["resolution_status"], "open")

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
        self.assertIn("verify-growth", workflow)
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


if __name__ == "__main__":
    unittest.main()
