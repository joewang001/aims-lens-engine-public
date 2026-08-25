# Public Lens Operations Plan

AIMS Lens Engine is intended to operate as a continuously refreshed open-source
lens library. The public repository should not wait for ad hoc manual projects
before it improves existing company lenses or expands into new industries.

This plan defines the recurring operating model for public-safe lens updates,
new company additions, automation, and exception handling.

## Operating Goal

Maintain a public lens system that:

- refreshes existing company lenses on a predictable rotation;
- updates all seven independent lens dimensions when evidence supports it;
- adds new leading-company lenses in undercovered industries at a fixed cadence;
- uses automation for normal public-safe updates;
- escalates only high-risk or boundary-changing updates to human maintainers.

## Source Baseline

Expansion and refresh priorities should combine multiple public signals instead
of relying on one ranking:

- Large-company scale and economic relevance, such as Fortune Global 500.
- Public-company scale across sales, profit, assets, and market value, such as
  Forbes Global 2000.
- Hiring and career-growth relevance, such as LinkedIn Top Companies.
- Public evidence quality: official company pages, careers pages, investor
  relations, engineering blogs, public leadership letters, and public interview
  pattern summaries.

These rankings help select candidate companies. They do not define hiring
standards and must not be treated as company endorsement.

## Cadence And Quantity

### Weekly Existing-Lens Refresh

Every week, automation should select three existing company lenses for refresh
candidate updates.

Selection priority:

1. stale `source_cutoff`;
2. `LIGHTWEIGHT_SCAN` status;
3. missing or thin role overlays;
4. industries with high user demand or weak coverage;
5. companies with recent public source changes.

Weekly target:

- 3 existing companies reviewed;
- at least 1 dimension updated when public evidence supports a change;
- 0 private-source bodies imported;
- scanner and seven-dimension coverage pass before PR.

### Monthly New-Company Expansion

Every month, automation should add two new public company lens candidates from
the approved expansion backlog.

Monthly target:

- 2 new `LIGHTWEIGHT_SCAN` company lenses;
- each new lens includes `README.md`, `profile.json`, `evidence.md`,
  `question_bank.json`, `rubric.md`, `rewrite_rules.md`, `limits.md`, and
  `validation_report.md`;
- each new lens includes at least one initial role overlay when official public
  sources are strong enough;
- at least 3 public source entries per company, preferably including official
  homepage, careers, and investor or engineering source;
- every generated question remains original and non-verbatim.

### Quarterly Coverage Expansion

Every quarter, automation should propose a coverage expansion batch.

Quarterly target:

- add or refresh at least 6 companies across at least 3 undercovered industries;
- identify 2 new industries or role families to add to the backlog;
- review whether any `LIGHTWEIGHT_SCAN` lens can be deepened, but do not promote
  status automatically unless promotion gates are explicitly satisfied.

## Seven-Dimension Update Requirement

Existing and new company lenses must preserve the seven dimensions separately:

| Dimension | Required update path |
| --- | --- |
| Company says | official-source summary in `evidence.md`; culture principle in `profile.json` |
| Company judges | hiring signals in `profile.json`; criteria in `rubric.md` |
| Company asks | original questions in `question_bank.json`; follow-up logic |
| Evidence valued | `aims_weighting`, source confidence, and scoring emphasis |
| Risk warnings | `anti_signals`, `limits.md`, fallback and human-review notes |
| Role variation | `role_overlays/` by role family, or explicit lightweight limitation |
| Honest unknowns | `honest_limits`, `limits.md`, and `validation_report.md` |

Automation may update one or several dimensions in a PR, but it must not merge a
change that blends them into one generic summary.

## Automation Architecture

The long-term automation should have four stages.

### Stage 1: Candidate Planning

Current implementation:

```bash
python tools/prepare_public_lens_refresh.py
```

Output:

```text
docs/refresh-candidates/public-lens-refresh-candidate.md
```

This stage ranks existing lenses and proposes expansion candidates from repo
metadata. It can run weekly and open a planning PR.

### Stage 2: Public Source Collection

Next sourcing agent responsibility:

- read only approved public source types;
- extract short source metadata and public-safe signals;
- never copy raw job posting bodies, paywalled text, private employer material,
  candidate material, tenant uploads, or secrets;
- store only source URL, date accessed, source type, confidence, and distilled
  non-verbatim signal.

Approved source types:

- official company homepage;
- careers page;
- investor relations page;
- official engineering or product blog;
- official leadership letter or public values page;
- public community aggregate when clearly labeled lower confidence.

### Stage 3: Lens Patch Generation

The agent may patch public lens files when all conditions are true:

- target company is in the approved backlog or already exists;
- source class is `public_source` or clearly labeled
  `public_community_aggregate`;
- changed content is non-verbatim and cites source IDs;
- no schema, license, scoring, or private-boundary rule changes are included;
- generated questions are original;
- lens remains clearly non-official.

### Stage 4: Validation, PR, And Merge

Required checks:

```bash
python tools/scan_public_export.py --allowlist
python tools/validate_public_lens_coverage.py --min-companies 12
python tools/prepare_public_lens_refresh.py
```

Normal low-risk PRs can be auto-merged when:

- only allowlisted public files changed;
- scanner blockers = 0;
- scanner review findings = 0;
- coverage blockers = 0;
- no new evidence class introduced;
- no private-derived signal introduced;
- no lens status promotion;
- no schema, routing, scoring, workflow-permission, or license change;
- PR touches at most 3 existing lenses or adds at most 2 approved-backlog
  `LIGHTWEIGHT_SCAN` company lenses.

## Human Review Exceptions

Require maintainer review for:

- private-derived public-safe signals;
- paywalled, gated, or community evidence that affects scoring;
- new industry not already in the approved backlog;
- more than 2 new companies in one PR;
- any lens status promotion;
- changes to schemas, scorer behavior, routing, CI permissions, licenses, or
  private/public boundary rules;
- any scanner blocker or review finding;
- any claim that a lens represents an official company hiring standard.

This keeps normal refresh and approved-backlog expansion automated while
preserving a hard boundary for privacy, copyright, governance, and reputation
risk.

## Approved Expansion Backlog

The first expansion backlog should prioritize industries where the current
public library is thin.

| Wave | Industry | Target companies | Monthly quantity | Automation default |
| --- | --- | --- | ---: | --- |
| 1 | AI infrastructure and semiconductors | NVIDIA, AMD, Intel, TSMC | 2 | auto PR if official-source only |
| 2 | Consulting and professional services | Accenture, Deloitte, BCG, Bain | 2 | auto PR if official-source only |
| 3 | Enterprise software and cloud | Salesforce, Oracle, ServiceNow, Adobe | 2 | auto PR if official-source only |
| 4 | Healthcare and pharma | Johnson & Johnson, Pfizer, Roche, Novartis | 2 | auto PR if official-source only |
| 5 | Energy and utilities | Enbridge, Shell, BP, NextEra Energy | 2 | auto PR if official-source only |
| 6 | Retail, logistics, and consumer platforms | Walmart, Costco, UPS, Airbnb | 2 | auto PR if official-source only |
| 7 | Aerospace, defense, and industrial systems | Boeing, Lockheed Martin, Siemens, GE Aerospace | 2 | auto PR if official-source only |
| 8 | Canadian anchor employers | Manulife, Sun Life, Bell, Telus | 2 | auto PR if official-source only |

The backlog is pre-approved for automation at `LIGHTWEIGHT_SCAN` status only.
Promotion to `FULLY_DISTILLED` still requires explicit validation gates.

## Output Targets

Monthly operating targets:

- Existing lens refresh: 12 company checks per month.
- New company expansion: 2 new company lenses per month.
- Role overlay expansion: at least 2 new role overlays per month.
- Validation cases: at least 4 new validation cases per month.
- Public scanner outcome: 0 blockers and 0 review findings.

Quarterly operating targets:

- 6 to 8 new company lenses.
- 3 or more industries improved.
- 1 public release note summarizing source, coverage, and validation changes.
- backlog re-ranked using public evidence quality and contributor demand.

## Success Metrics

Track:

- company lens count;
- industry count;
- role overlay count;
- average source age;
- number of lenses by status;
- scanner blocker and review count;
- percentage of lenses with complete seven-dimension coverage;
- number of community PRs accepted;
- number of auto-generated PRs merged without manual intervention.

## First 90 Days

### Month 1

- Refresh Shopify, Amazon, Google, RBC, BMO, and McKinsey.
- Add NVIDIA and Accenture.
- Add or deepen Shopify product, sales, and merchant-success overlays.

### Month 2

- Refresh Microsoft, Apple, JPMorgan, TD, CIBC, and Scotiabank.
- Add Salesforce and Johnson & Johnson.
- Add validation cases for technology, banking, consulting, and healthcare.

### Month 3

- Refresh all 12 initial lenses for source freshness and role-overlay gaps.
- Add Enbridge and Walmart.
- Produce quarterly coverage report and re-rank the expansion backlog.

## Implementation Next Step

The next engineering step is to extend the scheduled workflow from planning PRs
to content PRs by adding a source collector and lens patch generator:

```text
tools/collect_public_lens_sources.py
tools/generate_public_lens_patch.py
```

Those tools should create real lens updates only from approved public sources,
then rely on the existing scanner, coverage validator, and PR rules before
merge.
