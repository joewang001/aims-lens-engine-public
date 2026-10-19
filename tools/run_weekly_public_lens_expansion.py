#!/usr/bin/env python3
"""Idempotent weekly expansion shared by GitHub Actions and the NAS producer."""
import argparse
import json
import subprocess
import sys
import tempfile
from datetime import date
from pathlib import Path

try:
    from tools import collect_public_lens_sources as sources
    from tools import public_lens_operations as ops
except ModuleNotFoundError:
    import collect_public_lens_sources as sources
    import public_lens_operations as ops

ROOT = Path(__file__).resolve().parents[1]

def plan(target, reserve, run_date):
    if target < 1 or reserve < 0:
        raise ValueError("target must be positive and reserve nonnegative")
    start = ops.week_start(run_date)
    cohort = [p.name for p in ops.company_dirs()
              if ops.introduced_this_week(ops.load_json(p / 'profile.json'), start=start)]
    needed = max(0, target - len(cohort))
    unused = sources.choose_expansion(len(sources.CATALOG))
    if needed and len(unused) - needed < reserve:
        raise ValueError(f"candidate reserve would fall below {reserve}: unused={len(unused)} needed={needed}")
    selected = unused[:needed]
    return {'week_start': start.isoformat(), 'target': target, 'existing_cohort': sorted(cohort),
            'needed': needed, 'selected': selected, 'unused_after': len(unused) - needed}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--target', type=int, default=2)
    parser.add_argument('--reserve', type=int, default=8)
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    payload = plan(args.target, args.reserve, date.today())
    print(json.dumps(payload), flush=True)
    if args.dry_run or not payload['needed']:
        return 0
    def run(*arguments):
        subprocess.run([sys.executable, *arguments], cwd=ROOT, check=True)
    with tempfile.TemporaryDirectory(prefix='aims-weekly-') as temporary:
        baseline = str(Path(temporary) / 'baseline.json')
        run('tools/public_lens_operations.py', 'snapshot', '--output', baseline)
        packets = []
        for slug in payload['selected']:
            run('tools/collect_public_lens_sources.py', '--company', slug)
            packets += ['--packet', str(sources.DEFAULT_OUTPUT_DIR / f'{slug}.source-packet.json')]
        run('tools/generate_public_lens_patch.py', '--packet-dir', temporary, *packets, '--execute')
        run('tools/public_lens_operations.py', 'verify-growth', '--baseline', baseline,
            '--min-new-companies', str(payload['needed']))
    run('tools/public_lens_operations.py', 'verify-weekly-cohort', '--min-new-companies', str(args.target))
    run('tools/public_lens_operations.py', 'verify-reserve', '--min-unused', str(args.reserve))
    return 0

if __name__ == '__main__':
    sys.exit(main())
