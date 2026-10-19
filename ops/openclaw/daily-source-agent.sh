#!/bin/sh
set -eu

REPO_URL=${AIMS_REPO_WRITE_URL:-git@github.com:joewang001/aims-lens-engine-public.git}
WORK_ROOT=${AIMS_OPS_ROOT:-/home/node/.openclaw/workspace/aims-lens-public-ops}
REPO_DIR=${WORK_ROOT}/source-agent-repo
KEY=${AIMS_DEPLOY_KEY:-${WORK_ROOT}/credentials/aims-lens-deploy-key}
KNOWN_HOSTS=${AIMS_KNOWN_HOSTS:-${WORK_ROOT}/credentials/github-known-hosts}
BRANCH=${AIMS_SOURCE_BRANCH:-automation/public-lens-source-agent}
PYTHONPATH_VALUE=${AIMS_PYTHONPATH:-/home/node/.openclaw/workspace/.pylib}
PROMPT_TEMPLATE=${AIMS_SOURCE_PROMPT:-${REPO_DIR}/ops/openclaw/daily-source-agent-prompt.md}
PROMPT=${WORK_ROOT}/daily-source-agent-prompt.rendered.md
AGENT_RESULT=${WORK_ROOT}/last-daily-source-agent-result.json

if [ ! -f "$KEY" ]; then
  echo "missing repo-scoped deploy key: $KEY" >&2
  exit 2
fi
if [ ! -f "$KNOWN_HOSTS" ]; then
  echo "missing GitHub known-hosts file: $KNOWN_HOSTS" >&2
  exit 2
fi

export GIT_SSH_COMMAND="ssh -i $KEY -o IdentitiesOnly=yes -o UserKnownHostsFile=$KNOWN_HOSTS -o StrictHostKeyChecking=yes"
mkdir -p "$WORK_ROOT"

if [ ! -d "$REPO_DIR/.git" ]; then
  git clone "$REPO_URL" "$REPO_DIR"
fi
cd "$REPO_DIR"
git remote set-url origin "$REPO_URL"
git fetch --prune origin
if git show-ref --verify --quiet "refs/remotes/origin/$BRANCH" && \
  ! git merge-base --is-ancestor "origin/$BRANCH" origin/main; then
  echo "prior sourcing branch is not merged; refusing to overwrite it" >&2
  exit 4
fi
git checkout -B "$BRANCH" origin/main
git reset --hard origin/main
git clean -fd

PYTHONPATH="$PYTHONPATH_VALUE" python3 tools/public_lens_operations.py audit-gaps --catalog-reserve-target 8
PYTHONPATH="$PYTHONPATH_VALUE" python3 tools/public_lens_operations.py plan-daily \
  --weekday auto --weekly-cohort-limit 2 --historical-limit 2 --catalog-reserve-target 8

RUN_DATE=$(TZ=America/Toronto date +%F)
WEEKDAY=$(TZ=America/Toronto date +%A)
sed \
  -e "s|{{REPO_DIR}}|$REPO_DIR|g" \
  -e "s|{{RUN_DATE}}|$RUN_DATE|g" \
  -e "s|{{WEEKDAY}}|$WEEKDAY|g" \
  "$PROMPT_TEMPLATE" > "$PROMPT"

openclaw agent \
  --agent main \
  --session-key agent:main:aims-lens-daily-source \
  --message-file "$PROMPT" \
  --thinking high \
  --timeout 1200 \
  --json > "$AGENT_RESULT"

PYTHONPATH="$PYTHONPATH_VALUE" python3 tools/generate_public_lens_patch.py \
  --existing-limit 1000 --execute --allow-empty
PYTHONPATH="$PYTHONPATH_VALUE" python3 tools/public_lens_operations.py audit-gaps --catalog-reserve-target 8
PYTHONPATH="$PYTHONPATH_VALUE" python3 tools/public_lens_operations.py plan-daily \
  --weekday auto --weekly-cohort-limit 2 --historical-limit 2 --catalog-reserve-target 8
PYTHONPATH="$PYTHONPATH_VALUE" python3 tools/prepare_public_lens_refresh.py
PYTHONPATH="$PYTHONPATH_VALUE" python3 tools/scan_public_export.py --allowlist
PYTHONPATH="$PYTHONPATH_VALUE" python3 tools/validate_public_lens_coverage.py --min-companies 12

PACKET_COUNT=$(git diff --name-only -- docs/refresh-candidates/source-packets \
  | awk '/\.source-packet\.json$/ {count++} END {print count+0}')
LENS_COUNT=$(git diff --name-only -- company_lenses \
  | awk -F/ '/^company_lenses\/[a-z0-9-]+\// {seen[$2]=1} END {print length(seen)+0}')

if [ "$PACKET_COUNT" -lt 2 ]; then
  echo "daily sourcing hard gate failed: changed source packets=$PACKET_COUNT, minimum=2" >&2
  exit 3
fi
if [ "$LENS_COUNT" -lt 1 ]; then
  echo "daily sourcing hard gate failed: changed company lenses=$LENS_COUNT, minimum=1" >&2
  exit 3
fi

git config user.name "AIMS Lens Sourcing Agent"
git config user.email "aims-lens-automation@users.noreply.github.com"
git add \
  company_lenses \
  docs/refresh-candidates/public-lens-daily-plan.json \
  docs/refresh-candidates/public-lens-daily-plan.md \
  docs/refresh-candidates/public-lens-information-gaps.csv \
  docs/refresh-candidates/public-lens-information-gaps.md \
  docs/refresh-candidates/public-lens-gap-resolution-history.csv \
  docs/refresh-candidates/public-lens-gap-resolution-history.md \
  docs/refresh-candidates/public-lens-refresh-candidate.md \
  docs/refresh-candidates/source-packets \
  public_manifest.yaml
git diff --cached --quiet && {
  echo "daily sourcing hard gate failed: no staged changes" >&2
  exit 3
}
git commit -m "Advance daily public lens sourcing ($RUN_DATE)"
git push --force-with-lease origin "HEAD:refs/heads/$BRANCH"

printf '{"status":"ok","job":"daily-source-agent","run_date":"%s","branch":"%s","source_packets_changed":%s,"company_lenses_changed":%s,"head":"%s"}\n' \
  "$RUN_DATE" "$BRANCH" "$PACKET_COUNT" "$LENS_COUNT" "$(git rev-parse --short HEAD)"
