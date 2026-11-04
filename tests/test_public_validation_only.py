from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
class PublicValidationOnlyTests(unittest.TestCase):
    def test_no_scheduled_public_growth_or_public_mutation(self):
        content=(ROOT/'.github/workflows/public-lens-maintenance.yml').read_text(encoding='utf-8')
        self.assertNotIn('  schedule:',content)
        self.assertIn('contents: read',content)
        self.assertNotIn('gh pr merge',content)
        self.assertNotIn('gh pr create',content)
        self.assertIn('tools/validate_public_lens_coverage.py',content)
    def test_public_execution_tools_removed(self):
        removed=['collect_public_lens_sources.py','generate_public_lens_patch.py',
                 'public_lens_operations.py','run_weekly_public_lens_expansion.py',
                 'prepare_public_lens_refresh.py','publish_public_lens.py']
        for name in removed:
            with self.subTest(name=name):
                self.assertFalse((ROOT/'tools'/name).exists())
    def test_public_validator_preserved(self):
        self.assertTrue((ROOT/'tools/scan_public_export.py').is_file())
        self.assertTrue((ROOT/'tools/validate_public_lens_coverage.py').is_file())

if __name__=='__main__':unittest.main()
