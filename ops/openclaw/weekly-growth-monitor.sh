#!/bin/sh
set -eu

REPO_URL=${AIMS_REPO_READ_URL:-https://github.com/joewang001/aims-lens-engine-public.git}
REPO_REF=${AIMS_REPO_READ_REF:-main}
WORK_ROOT=${AIMS_OPS_ROOT:-/home/node/.openclaw/workspace/aims-lens-public-ops}
WORK=${WORK_ROOT}/weekly-monitor-repo
OUT=${WORK_ROOT}/last-weekly-growth-monitor.json
PYTHONPATH_VALUE=${AIMS_PYTHONPATH:-/home/node/.openclaw/workspace/.pylib}

rm -rf "$WORK"
git clone --depth 1 --branch "$REPO_REF" "$REPO_URL" "$WORK"
cd "$WORK"

COHORT=$(PYTHONPATH="$PYTHONPATH_VALUE" python3 tools/public_lens_operations.py \
  verify-weekly-cohort --min-new-companies 2)
RESERVE=$(PYTHONPATH="$PYTHONPATH_VALUE" python3 tools/public_lens_operations.py \
  verify-reserve --min-unused 8)
SCAN=$(PYTHONPATH="$PYTHONPATH_VALUE" python3 tools/scan_public_export.py --allowlist)
COVERAGE=$(PYTHONPATH="$PYTHONPATH_VALUE" python3 tools/validate_public_lens_coverage.py --min-companies 12)
HEAD=$(git rev-parse --short HEAD)

python3 - "$OUT" "$HEAD" "$COHORT" "$RESERVE" "$SCAN" "$COVERAGE" <<'PY'
import json
import sys
from datetime import datetime, timezone

path, head, cohort, reserve, scan, coverage = sys.argv[1:]
payload = {
    "status": "ok",
    "job": "weekly-growth-monitor",
    "head": head,
    "cohort": cohort,
    "reserve": reserve,
    "scan": scan,
    "coverage": coverage,
    "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
}
with open(path, "w", encoding="utf-8") as handle:
    json.dump(payload, handle, ensure_ascii=True)
    handle.write("\n")
print(json.dumps(payload, ensure_ascii=True))
PY
