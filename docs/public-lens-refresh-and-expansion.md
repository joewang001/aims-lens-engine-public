# Public Lens Refresh And Expansion Model

AIMS Lens Engine should behave like a living open-source knowledge system, not a
one-time content dump. The public project needs two recurring motions:

- Refresh existing company lenses with new public-safe evidence.
- Expand coverage into additional leading companies and industries.

The normal path should be automated. Human review is reserved for exceptions,
not for every routine update.

## Operating Principles

1. Public-safe by default.
   Automated updates may use public sources, public community aggregates, and
   non-verbatim public-safe distillation. They must not import private materials,
   tenant uploads, candidate data, copied job postings, paywalled source text,
   secrets, production configuration, or company brand assets.

2. Seven dimensions stay independent.
   A company lens is only useful if it preserves separate evidence for how the
   company speaks, how it judges, what it asks, what evidence it values, what it
   treats as risk, how roles vary, and what the system does not know.

3. Automation creates candidate updates.
   Bot-generated changes should open pull requests with source notes, confidence
   labels, changed files, and validation output. Low-risk maintenance PRs can be
   auto-merged after gates pass. Risky PRs are escalated.

4. Expansion follows coverage gaps.
   New company candidates should be chosen from undercovered industries first,
   then by public evidence quality, hiring relevance, and contribution demand.

5. Public lenses are not official hiring standards.
   Every update must preserve the project boundary: the lens is an evidence-based
   preparation and evaluation aid, not an official statement from the company.

## Seven-Dimension Refresh Checklist

Each company lens should preserve these dimensions:

| Dimension | Public artifact signals |
| --- | --- |
| Company says | `profile.json` culture principles, `evidence.md` official source summaries |
| Company judges | `profile.json` hiring signals, `rubric.md` scoring priorities |
| Company asks | `question_bank.json` original questions and follow-up logic |
| Evidence valued | `aims_weighting`, `rubric.md`, source confidence notes |
| Risk warnings | `anti_signals`, `limits.md`, human review or fallback guidance |
| Role variation | `role_overlays/` when mature, or explicit limits when lightweight |
| Honest unknowns | `honest_limits`, `limits.md`, `validation_report.md` |

Refresh work should not collapse these into a single generic summary. If new
evidence only strengthens one dimension, update that dimension and leave the
others unchanged.

## Recurring Update Cadence

Recommended schedule:

- Weekly: scan for stale lens metadata, broken structure, and undercovered
  industries.
- Monthly: refresh public evidence for existing high-demand companies.
- Monthly: add one to three new leading companies when evidence quality is high.
- Quarterly: review industry coverage and promote mature lightweight lenses.

## Automated Low-Risk Path

A routine bot PR can be auto-merged when all conditions are true:

- Only allowlisted public files are changed.
- No scanner blockers or review findings are present.
- The seven-dimension coverage check passes.
- Added source notes are public, non-verbatim, and attributed.
- No new brand assets, raw job posting bodies, candidate data, tenant data, or
  production configuration are included.
- The PR changes existing lens summaries, validation cases, or documentation
  without introducing a new evidence class.

## Automated PR Flow

The public repository includes a scheduled GitHub Actions workflow:

```text
.github/workflows/public-lens-maintenance.yml
```

On every pull request and push, it validates the public boundary and
seven-dimension coverage. On the weekly schedule or manual dispatch, it also
runs:

```bash
python tools/prepare_public_lens_refresh.py
```

That script writes a refresh candidate report under
`docs/refresh-candidates/`. The workflow then opens or updates an automated PR
with the generated report. This upgrades automation from passive validation to
an active maintenance loop while keeping actual lens-content changes behind the
same scanner and coverage gates.

The generated PR is allowed to merge automatically only when it remains a
planning/report PR. If a future sourcing agent adds real lens content, the
escalation rules below apply.

## Escalation Path

Require maintainer review when any condition is true:

- A new company lens is introduced.
- A new industry category is introduced.
- A private-derived signal is used, even if public-safe.
- The update relies on paid, gated, or community material.
- The scanner reports any blocker or review finding.
- A lens status is promoted, for example from `LIGHTWEIGHT_SCAN` to
  `FULLY_DISTILLED`.
- The change affects schemas, scoring behavior, routing behavior, or licensing.

## Expansion Priority

New companies should be selected by a simple score:

```text
priority = industry_gap + hiring_relevance + public_evidence_quality + contributor_demand - legal_or_privacy_risk
```

Suggested expansion order after the initial public release:

- Consulting and professional services beyond McKinsey.
- AI infrastructure and semiconductor leaders.
- Enterprise software and cloud leaders.
- Healthcare and pharma leaders.
- Energy and utilities leaders.
- Retail, logistics, and consumer platform leaders.
- Canadian employers with strong public hiring demand.

## Required Validation

Before merge or release, run:

```bash
python tools/scan_public_export.py --allowlist
python tools/validate_public_lens_coverage.py --min-companies 12
python tools/prepare_public_lens_refresh.py
```

For source-repo exports, also run:

```bash
python tools/export_public_release.py --execute --clean
python tools/generate_public_release_audit_report.py --allowlist
```

The goal is a public system that updates itself routinely, while preserving hard
boundaries around privacy, copyright, source quality, and JobACE private
implementation details.
