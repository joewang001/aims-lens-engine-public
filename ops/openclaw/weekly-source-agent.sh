#!/bin/sh
# Deterministic public-catalog expansion; no LLM or private source access.
set -eu
export TZ=America/Toronto
ROOT=${AIMS_OPS_ROOT:-/home/node/.openclaw/workspace/aims-lens-public-ops}
KEY=${AIMS_DEPLOY_KEY:-${ROOT}/credentials/aims-lens-deploy-key}
KNOWN_HOSTS=${AIMS_KNOWN_HOSTS:-${ROOT}/credentials/github-known-hosts}
REPO=${ROOT}/weekly-source-repo
BRANCH=automation/public-lens-source-agent
URL=git@github.com:joewang001/aims-lens-engine-public.git
export PYTHONPATH=${AIMS_PYTHONPATH:-/home/node/.openclaw/workspace/.pylib}
mkdir -p "$ROOT"
# An atomic lock prevents overlapping NAS retries; never overwrite an open branch.
if ! mkdir "$ROOT/weekly-source.lock"; then
  echo "weekly sourcing already running; refusing concurrent execution" >&2
  exit 4
fi
trap 'rmdir "$ROOT/weekly-source.lock"' EXIT
export GIT_SSH_COMMAND="ssh -i $KEY -o IdentitiesOnly=yes -o UserKnownHostsFile=$KNOWN_HOSTS -o StrictHostKeyChecking=yes"
if [ ! -d "$REPO/.git" ]; then git clone "$URL" "$REPO"; fi
cd "$REPO"
if [ -n "$(git status --porcelain)" ]; then
  echo "weekly checkout contains uncommitted work; preserving it" >&2
  exit 4
fi
git fetch --prune origin
if git show-ref --verify --quiet "refs/remotes/origin/$BRANCH" &&   ! git merge-base --is-ancestor "origin/$BRANCH" origin/main; then
  echo "automation branch pending; refusing to overwrite it" >&2
  exit 4
fi
git checkout -B weekly-source origin/main
TARGET=$(python3 -c 'import json; print(json.load(open("config/public_lens_expansion_catalog.json"))["weekly_new_company_target"])')
python3 tools/run_weekly_public_lens_expansion.py --target "$TARGET" --reserve 8 --dry-run
if [ "${1:-}" = "--dry-run" ]; then exit 0; fi
# The no-op path checks main and does not create a report-only PR.
if python3 tools/public_lens_operations.py verify-weekly-cohort --min-new-companies "$TARGET"; then
  echo "weekly sourcing complete: main already meets the target"
  exit 0
fi
python3 tools/run_weekly_public_lens_expansion.py --target "$TARGET" --reserve 8
python3 tools/prepare_public_lens_refresh.py
python3 tools/public_lens_operations.py audit-gaps --catalog-reserve-target 8
python3 tools/scan_public_export.py --allowlist
python3 tools/validate_public_lens_coverage.py --min-companies 12
git config user.name "AIMS Lens Sourcing Agent"
git config user.email "aims-lens-automation@users.noreply.github.com"
git add company_lenses docs/refresh-candidates public_manifest.yaml
git commit -m "Complete weekly public lens cohort ($(date +%F))"
git push origin "HEAD:$BRANCH"
echo "weekly sourcing submitted: awaiting PR validation and merge; monitor verifies main"
