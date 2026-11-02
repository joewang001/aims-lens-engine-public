import json
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import patch
from tools import collect_public_lens_sources as sources
from tools import run_weekly_public_lens_expansion as weekly

class WeeklyExpansionTests(unittest.TestCase):
    def test_five_company_batch_prefers_five_sectors(self):
        catalog = {slug: {'industries': [sector]} for slug, sector in [
            ('a', 'tech'), ('b', 'tech'), ('c', 'health'), ('d', 'retail'),
            ('e', 'energy'), ('f', 'transport')]}
        with tempfile.TemporaryDirectory() as tmp, patch.object(sources, 'CATALOG', catalog), patch.object(sources, 'COMPANY_LENSES', Path(tmp)):
            chosen = sources.choose_expansion(5)
            self.assertEqual(len({catalog[s]['industries'][0] for s in chosen}), 5)

    def test_idempotent_and_partial_weekly_target(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            profiles = []
            for slug in ['a', 'b']:
                directory = root / slug
                directory.mkdir()
                (directory / 'profile.json').write_text(json.dumps({'introduced_at': '2026-10-19'}))
                profiles.append(directory)
            with patch.object(weekly.ops, 'company_dirs', return_value=profiles), patch.object(weekly.sources, 'choose_expansion', return_value=list('cdefghijklmnop')):
                self.assertEqual(weekly.plan(2, 8, date(2026, 10, 19))['needed'], 0)
                self.assertEqual(weekly.plan(5, 8, date(2026, 10, 19))['selected'], ['c', 'd', 'e'])

    def test_reserve_is_advisory_when_two_valid_candidates_exist(self):
        with patch.object(weekly.ops, 'company_dirs', return_value=[]), patch.object(weekly.sources, 'choose_expansion', return_value=list('abcdefghijkl')):
            result = weekly.plan(5, 8, date(2026, 10, 19))
            self.assertEqual(result['needed'], 5)
            self.assertEqual(result['unused_after'], 7)

    def test_insufficient_candidates_remains_blocking(self):
        with patch.object(weekly.ops, 'company_dirs', return_value=[]), patch.object(weekly.sources, 'choose_expansion', return_value=['a']):
            with self.assertRaisesRegex(ValueError, 'insufficient public candidates'):
                weekly.plan(2, 8, date(2026, 10, 19))
