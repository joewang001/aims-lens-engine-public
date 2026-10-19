# NAS public-lens publication channel

Routine public-lens work can be submitted from a dedicated checkout of this
repository using an existing repository-scoped write deploy key. Configure the
key only for this checkout, keep it outside the checkout, and pin GitHub host
keys with strict host verification. Do not change backup-repository remotes or
global SSH/Git identity settings.

## Publish

1. Fetch main and create a named work branch from current `origin/main`.
2. Apply supported, public-safe lens or source-packet improvements.
3. Run:

   ```sh
   python3 tools/publish_public_lens.py --message "Describe the public lens improvement"
   ```

The helper audits the gaps, runs unit tests, checks the public boundary and
coverage, and pushes only `automation/public-lens-source-agent`. GitHub then
validates that exact commit, opens/updates its PR and requests merge. A local
`submitted` result is not proof of merge: verify the PR, main and a fresh audit.

An advanced main branch, an unmerged automation branch, non-public changes or
failed checks stop publication without overwriting previous work. The helper
does not force push, push main, or handle credentials. Infrastructure, workflow,
schema and runtime changes require a separate maintainer PR.

Completed gap history remains append-only. After merge, audit can backfill the
actual main commit and PR; publish generated provenance updates through the
same checked channel if needed. No private sources, candidate/tenant data,
copied job bodies, paywalled text, credentials or production configuration may
be included.

## Live channel verification

A documentation-only update on 2026-10-19 exercises the NAS-origin push and
automation PR path. Its push-run and PR records are the acceptance evidence.
The verification does not generate or modify company lens content.

A second clean submission verifies the normal path with repository auto-merge
already enabled. The validation job must finish before the PR job can request
merge, and the request matches the exact validated head commit.
