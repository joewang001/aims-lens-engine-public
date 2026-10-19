"""Regression guards for hiring-signal provenance and the required disclosure.

These checks exist because the gap audit only counts items. A lens can pass every
threshold while its signals claim a stronger provenance than their sources support,
or while it omits the disclosure that governance/evidence-standard.md requires.
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LENSES = ROOT / "company_lenses"

BASIS_VALUES = {"stated_by_company", "derived_public_inference", "generic_public_default"}

# Source types that mean the company itself published the claim.
COMPANY_SOURCE_PREFIXES = ("official_", "executive_primary", "recruiting_material", "job_description")

DISCLOSURE_MARKERS = ("does not represent an official", "is not an official")


def lens_dirs() -> list[Path]:
    return sorted(p for p in LENSES.iterdir() if p.is_dir() and not p.name.startswith("_"))


def evidence_types(path: Path) -> dict[str, str]:
    rows: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 3:
            continue
        first = cells[0]
        if "-" not in first or not first.split("-")[0].isupper():
            continue
        rows[first] = cells[1]
    return rows


class HiringSignalBasisTests(unittest.TestCase):
    def test_every_signal_declares_a_known_basis(self):
        for path in lens_dirs():
            profile = json.loads((path / "profile.json").read_text(encoding="utf-8"))
            for signal in profile.get("hiring_signals", []):
                with self.subTest(company=path.name, signal=signal.get("signal", "")[:60]):
                    self.assertIn(signal.get("basis"), BASIS_VALUES)

    def test_stated_by_company_signals_cite_a_company_issued_source(self):
        for path in lens_dirs():
            profile = json.loads((path / "profile.json").read_text(encoding="utf-8"))
            types = evidence_types(path / "evidence.md")
            for signal in profile.get("hiring_signals", []):
                if signal.get("basis") != "stated_by_company":
                    continue
                cited = [types.get(item, "") for item in signal.get("evidence_ids", [])]
                with self.subTest(company=path.name, signal=signal.get("signal", "")[:60]):
                    self.assertTrue(
                        any(kind.startswith(COMPANY_SOURCE_PREFIXES) for kind in cited),
                        f"{path.name} claims a company-stated signal with no company-issued source: {cited}",
                    )


class PublicInferredDisclosureTests(unittest.TestCase):
    def test_every_public_lens_discloses_it_is_not_official(self):
        for path in lens_dirs():
            profile = json.loads((path / "profile.json").read_text(encoding="utf-8"))
            if profile.get("visibility") != "PUBLIC_COMPANY_LENS":
                continue
            text = (path / "limits.md").read_text(encoding="utf-8").lower()
            with self.subTest(company=path.name):
                self.assertTrue(
                    any(marker in text for marker in DISCLOSURE_MARKERS),
                    f"{path.name} limits.md is missing the required public-inferred disclosure",
                )

    def test_generator_template_emits_the_disclosure(self):
        source = (ROOT / "tools" / "generate_public_lens_patch.py").read_text(encoding="utf-8")
        self.assertIn("does not represent an official", source)


if __name__ == "__main__":
    unittest.main()
