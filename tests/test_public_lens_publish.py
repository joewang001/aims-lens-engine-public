import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from tools import publish_public_lens as publisher


class PublicationScopeTests(unittest.TestCase):
    def test_only_routine_public_content_is_eligible(self):
        publisher.validate_paths([
            "company_lenses/example/profile.json",
            "docs/refresh-candidates/source-packets/example.source-packet.json",
            "public_manifest.yaml", "tests/test_public_lens_operations.py",
        ])

    def test_private_paths_and_workflow_changes_cannot_use_routine_channel(self):
        for path in [".env", "credentials/id_ed25519", "runtime_core/config.json",
                     ".github/workflows/public-lens-maintenance.yml", "../private.json", "/tmp/key"]:
            with self.subTest(path=path), self.assertRaises(ValueError):
                publisher.validate_paths([path])

    def test_symlinks_cannot_be_published_as_public_sources(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            link = root / "company_lenses/example/profile.json"
            link.parent.mkdir(parents=True)
            link.symlink_to(root / "outside.json")
            with patch.object(publisher, "ROOT", root), self.assertRaises(ValueError):
                publisher.validate_paths([str(link.relative_to(root))])

    def test_automation_waits_for_unit_tests_and_matches_the_tested_head(self):
        workflow = (publisher.ROOT / ".github/workflows/public-lens-maintenance.yml").read_text()
        validation = workflow.split("  weekly-company-expansion:")[0]
        self.assertIn("python -m unittest discover -s tests -v", validation)
        publication = workflow.split("  open-sourcing-agent-pull-request:")[1].split("  daily-seven-dimension-enrichment:")[0]
        self.assertIn("needs: validate-public-lens", publication)
        self.assertIn('--match-head-commit "$GITHUB_SHA"', publication)
        self.assertIn("MERGEABLE) ready=true", publication)
        self.assertNotIn("--auto", publication)
