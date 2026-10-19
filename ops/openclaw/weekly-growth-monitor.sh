#!/bin/sh
set -eu
export REPO_URL=${AIMS_REPO_READ_URL:-https://github.com/joewang001/aims-lens-engine-public.git}
export REPO_REF=${AIMS_REPO_READ_REF:-main}
export WORK_ROOT=${AIMS_OPS_ROOT:-/home/node/.openclaw/workspace/aims-lens-public-ops}
export PYTHONPATH=${AIMS_PYTHONPATH:-/home/node/.openclaw/workspace/.pylib}
python3 - <<'PY'
import json
import os
from pathlib import Path
import subprocess
import sys
from datetime import datetime, timezone
root = Path(os.environ['WORK_ROOT'])
root.mkdir(parents=True, exist_ok=True)
work = root / 'weekly-monitor-repo'
result = {'status': 'error', 'job': 'weekly-growth-monitor', 'checks': {}}
def run(stage, args, cwd=None):
    proc = subprocess.run(args, cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output = proc.stdout.strip()
    result['checks'][stage] = {'exit_code': proc.returncode, 'output': output}
    print(f'{stage}: {output}', flush=True)
    if proc.returncode:
        result['failed_stage'] = stage
        raise RuntimeError(f'{stage} exited with code {proc.returncode}')
    return output
try:
    # Keep the checkout for diagnosis; refresh it without deleting the directory.
    if not (work / '.git').is_dir():
        run('clone', ['git', 'clone', '--depth', '1', '--branch', os.environ['REPO_REF'], os.environ['REPO_URL'], str(work)])
    else:
        run('fetch', ['git', 'fetch', '--depth', '1', os.environ['REPO_URL'], os.environ['REPO_REF']], work)
        run('checkout', ['git', 'checkout', '--detach', 'FETCH_HEAD'], work)
    result['head'] = run('head', ['git', 'rev-parse', '--short', 'HEAD'], work)
    for name, args in [
        ('cohort', ['tools/public_lens_operations.py', 'verify-weekly-cohort', '--min-new-companies', '2']),
        ('reserve', ['tools/public_lens_operations.py', 'verify-reserve', '--min-unused', '8']),
        ('scan', ['tools/scan_public_export.py', '--allowlist']),
        ('coverage', ['tools/validate_public_lens_coverage.py', '--min-companies', '12']),
    ]:
        result[name] = run(name, ['python3'] + args, work)
    result['status'] = 'ok'
except Exception as exc:
    result['error'] = str(exc)
finally:
    result['generated_at'] = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    target = root / 'last-weekly-growth-monitor.json'
    temp = target.with_suffix('.json.tmp')
    temp.write_text(json.dumps(result, ensure_ascii=True) + '\n')
    temp.replace(target)
    print(json.dumps(result, ensure_ascii=True), flush=True)
sys.exit(0 if result['status'] == 'ok' else 1)
PY
