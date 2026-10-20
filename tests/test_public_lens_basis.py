"""Regression guards for hiring-signal provenance and the required disclosure.

These checks exist because the gap audit only counts items. A lens can pass every
threshold while its signals claim a stronger provenance than their sources support,
or while it omits the disclosure that governance/evidence-standard.md requires.
"""

from __future__ import annotations

import json
import unittest
import tempfile
from unittest.mock import patch
from tools import generate_public_lens_patch as generator
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
        packet = {
            "company_slug": "fixture", "company": "Fixture Company",
            "lens_updates": {},
            "sources": [{
                "evidence_id": "FIX-001", "source_type": "official_careers",
                "title": "Fixture careers", "date_accessed": "2026-10-19",
                "confidence": 0.8, "public_safe_signal": "Public fixture for generation testing.",
                "url": "https://example.com/careers",
            }],
        }
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with patch.object(generator, "COMPANY_LENSES", root), patch.object(
                generator, "update_manifest_for_company"
            ):
                generator.create_company_lens(packet)
            text = (root / "fixture" / "limits.md").read_text(encoding="utf-8")
            self.assertIn("does not represent an official Fixture Company hiring standard", text)
            profile = json.loads((root / "fixture" / "profile.json").read_text(encoding="utf-8"))
            self.assertEqual(len(profile["hiring_signals"]), 2)
            for signal in profile["hiring_signals"]:
                self.assertEqual(signal["basis"], "generic_public_default")


class WeakSupportRegisterTests(unittest.TestCase):
    """The register in governance/evidence-standard.md must describe real lenses.

    Weak support is legitimate, but a register that drifts out of sync with the
    lenses silently becomes decoration, so each row is checked against the data.
    """

    def register_rows(self) -> list[tuple[str, str]]:
        text = (ROOT / "governance" / "evidence-standard.md").read_text(encoding="utf-8")
        marker = "### Weak-Support Register"
        self.assertIn(marker, text)
        section = text.split(marker, 1)[1]
        rows: list[tuple[str, str]] = []
        for line in section.splitlines():
            if not line.startswith("|"):
                continue
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            if len(cells) < 2 or cells[0] in ("Company", "---") or set(cells[0]) == {"-"}:
                continue
            rows.append((cells[0], cells[1]))
        self.assertTrue(rows)
        return rows

    def test_register_rows_match_a_lens_signal(self):
        by_company = {}
        for path in lens_dirs():
            profile = json.loads((path / "profile.json").read_text(encoding="utf-8"))
            by_company[profile.get("company")] = profile

        for company, signal in self.register_rows():
            with self.subTest(company=company, signal=signal[:60]):
                self.assertIn(company, by_company, f"{company} has no lens")
                signals = by_company[company].get("hiring_signals", [])
                match = [item for item in signals if item.get("signal", "").startswith(signal[:40])]
                self.assertTrue(match, f"{company} has no signal starting with {signal[:40]!r}")
                self.assertEqual(match[0].get("basis"), "stated_by_company")



if __name__ == "__main__":
    unittest.main()
