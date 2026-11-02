"""Contract: incomplete public research is advisory, missing evidence is not."""

import json
import tempfile
import unittest
from pathlib import Path

from tools.validate_public_lens_coverage import validate_company


class CoveragePolicyTests(unittest.TestCase):
    def test_lightweight_depth_gaps_are_warnings(self):
        with tempfile.TemporaryDirectory() as folder:
            company = Path(folder)
            (company / "profile.json").write_text(json.dumps({
                "lens_id": "sample", "company": "Sample", "lens_status": "LIGHTWEIGHT_SCAN",
                "version": "0.1", "source_cutoff": "2026-10-01",
            }), encoding="utf-8")
            (company / "evidence.md").write_text("Official public careers source: https://example.org/careers", encoding="utf-8")
            findings = validate_company(company, max_stale_days=180)
            self.assertFalse([f for f in findings if f.severity == "blocker"])
            self.assertTrue([f for f in findings if f.severity == "warning"])

    def test_lightweight_without_evidence_is_blocked(self):
        with tempfile.TemporaryDirectory() as folder:
            company = Path(folder)
            (company / "profile.json").write_text(json.dumps({
                "lens_id": "sample", "company": "Sample", "lens_status": "LIGHTWEIGHT_SCAN",
                "version": "0.1", "source_cutoff": "2026-10-01",
            }), encoding="utf-8")
            findings = validate_company(company, max_stale_days=180)
            self.assertIn("missing_evidence", [f.code for f in findings if f.severity == "blocker"])


if __name__ == "__main__":
    unittest.main()
