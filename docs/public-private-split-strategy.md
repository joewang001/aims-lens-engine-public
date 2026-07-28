# Public / Private Split Strategy

Status: approved direction for public-release preparation.

## Purpose

AIMS Lens Engine should support two goals at the same time:

- Build an open, credible lens standard that outside contributors can inspect, use, and extend.
- Preserve JobACE's private evaluation advantage, production data, and proprietary interview coaching logic.

The split should not be a simple repository cleanup exercise. It is a product and governance boundary. Public assets should make the lens ecosystem stronger. Private assets should protect JobACE's data, tenant workflows, scoring calibration, and production integration.

## Strategic Positioning

The public project should be positioned as:

> An open framework for evidence-backed company, role, industry, and thinker lenses used in interview preparation, candidate evaluation support, and strategic career decisioning.

The private JobACE layer should be positioned as:

> A proprietary evaluation and coaching layer that combines public lens standards, private evidence, JobACE-specific scoring calibration, and production interview workflows.

## Target Architecture

```text
Public Open Source Core
  schemas
  governance standards
  public distillation playbooks
  public company lens examples
  validation tools
  contribution workflow

Private JobACE Intelligence Layer
  private materials
  tenant uploads
  workspace database
  audit and review logs
  JobACE scoring adapters
  production deployment configs
  private calibration data

Commercial / Enterprise Extension Layer
  API contracts may be public
  reference service may be limited public
  production workspace and tenant operations stay private
  enterprise private lenses stay tenant-private
```

## Public Release Scope

The following areas are candidates for public release after audit.

### Public Schemas

Release:

- `schemas/company_lens.schema.json`
- `schemas/evidence.schema.json`
- `schemas/question_bank.schema.json`
- `schemas/derived_lens.schema.json`
- `schemas/role_lens.schema.json`
- `schemas/interview_prep_plan.schema.json`

Purpose:

- Define the portable lens artifact format.
- Let contributors validate company lens submissions.
- Make the project usable without JobACE.

Public schemas must not contain JobACE tenant IDs, production endpoint secrets, private scoring weights, or candidate examples derived from real users.

### Public Governance

Release:

- `governance/evidence-standard.md`
- `governance/privacy-and-fairness.md`
- public lens status and confidence rules

Purpose:

- Explain evidence requirements.
- Prevent public lenses from pretending to be official company standards.
- Require confidence states such as `FULLY_DISTILLED`, `DERIVED_LENS`, `LIGHTWEIGHT_SCAN`, and `GENERIC_AIMS`.

### Public Documentation

Release public-safe versions of:

- system design
- distillation playbook
- implementation roadmap
- role routing principles
- validation checklist
- contributor guide

Remove or rewrite:

- JobACE production URLs unless intentionally public.
- internal deployment notes.
- private material workflows.
- tenant-specific API key instructions.
- operational details that expose production behavior.

### Public Company Lenses

Release lens content that is based on public sources, public community aggregates, or public-safe distilled summaries of higher-value private sources.

The public repository publishes structured, verifiable insight. It does not publish raw source archives. Private or paid materials can be strategically valuable and may support public lenses after transformation, but the raw text, full source structure, copied question sets, user-submitted job postings, and candidate data must remain private.

Initial public release target:

- `company_lenses/amazon`
- `company_lenses/google`
- `company_lenses/mckinsey`
- `company_lenses/microsoft`
- `company_lenses/apple`
- `company_lenses/jpmorgan`
- `company_lenses/rbc`
- `company_lenses/td`
- `company_lenses/bmo`
- `company_lenses/cibc`
- `company_lenses/scotiabank`
- `company_lenses/shopify`

This first public set should include at least 12 companies so the project demonstrates cross-industry coverage, repeatable structure, and broader external verifiability. If audit results block one candidate, replace it with another public-safe lens rather than shrinking the release below 10 companies.

Before release, each lens must pass a public-safety audit:

- no private Medium article text copied into public files
- no user-submitted job posting text copied into public files
- no candidate answer or resume content
- no raw scraped interview posts copied verbatim
- no `private_only` evidence IDs in the public export
- no claim that the lens represents official company hiring policy

Allowed public evidence visibility classes:

- `public_source`: official pages, public reports, public blogs, public job descriptions, and public documentation that can be cited safely.
- `public_community_aggregate`: aggregated public interview or employee signals, with lower confidence and no copied personal posts.
- `private_distillation_public_safe`: distilled non-verbatim signals derived from private, paid, or owner-authorized materials; raw source bodies remain private.

Blocked public evidence visibility class:

- `private_only`: tenant uploads, raw paid material, user-submitted job postings, candidate data, internal review records, private scoring calibration, and enterprise-specific content.

Public company lenses should include:

- `profile.json`
- `evidence.md` with public-safe references
- `rubric.md`
- `question_bank.json` if questions are generated or public-safe
- `rewrite_rules.md`
- `limits.md`
- `validation_report.md`

### Public Tools

Release:

- schema validators
- lens structure checkers
- public-safe lint tools
- export audit tools

Do not release:

- production tenant admin tools
- JobACE API adapters with real contracts
- scripts that access private local paths
- tools that assume private databases or private materials

## Private Scope

The following areas must remain private unless explicitly approved.

### Private Materials

Keep private:

- `private_materials/`
- private Medium distillations
- manually copied job postings
- tenant uploads
- enterprise-provided material
- any copyrighted source bodies not licensed for redistribution

Rule:

Private evidence can inform private JobACE or tenant-specific lenses, but it must not be copied into public lenses unless transformed into a public-safe, non-verbatim, permission-compatible summary.

### Workspace And Production Data

Keep private:

- `workspace_data/`
- `audit_logs/`
- `review_logs/`
- production SQLite or Postgres data
- tenant API keys
- review decisions
- raw material paths

Rule:

These artifacts are operational records. They are not open source content.

### JobACE Integration

Keep private:

- real JobACE scoring adapters
- production request / response mappings
- prompt routing tied to JobACE interview flows
- candidate evaluation calibration
- improvement plan personalization logic derived from JobACE data
- deployment configs for `lens.jobace.ca` and `lens-api.jobace.ca`

Public version:

- expose a mock adapter or interface contract only.
- include examples with synthetic candidate data only.

### Private Calibration

Keep private:

- candidate personas derived from real users
- historical scoring outputs
- reviewer calibration decisions
- false positive / false negative analysis from JobACE users
- any enterprise screening outcomes

Public version:

- use synthetic fixtures that are clearly marked as synthetic.

## Commercial / Enterprise Boundary

Some enterprise-facing functionality can have public interfaces without public implementation.

May be public:

- OpenAPI contract for source material submission.
- sample tenant flow using fake data.
- schema for review decisions.
- high-level workspace architecture.

Should remain private:

- production authentication implementation details.
- tenant key rotation operations.
- internal review queue data.
- enterprise-specific lens content.
- deployment and scaling configuration.

This keeps the project credible for B2B partners without exposing JobACE's operating system.

## Repository Strategy

Use a staged split instead of a sudden hard fork.

### Stage 1: Define Release Manifests

Create:

```text
public_manifest.yaml
private_manifest.yaml
```

`public_manifest.yaml` should list files and directories eligible for export.

`private_manifest.yaml` should list files and patterns that must never be exported.

The private manifest should include at minimum:

```text
private_materials/
workspace_data/
audit_logs/
review_logs/
.env
.env.*
.venv-lens-workspace/
tenant_uploads/
candidate_data/
```

### Stage 2: Build Public Export

Create an export script that copies only manifest-approved files into a clean release directory:

```text
dist/public/aims-lens-engine/
```

The export script should fail if:

- a private path appears in the export.
- a file contains known private markers.
- a lens references private-only evidence IDs without public-safe explanation.
- generated files include API keys, local database paths, or production secrets.

### Stage 3: Public Safety Audit

Before the first public repository push:

- run schema validation on exported lenses.
- run private marker scan.
- manually inspect each public company lens.
- verify license compatibility for every public artifact.
- confirm no copied raw interview posts or copyrighted article bodies are present.

### Stage 4: Create Public Repository

Create a separate public repository after the export is clean.

Recommended public repository name:

```text
aims-lens-engine
```

Recommended private repository name:

```text
aims-lens-engine-private
```

If the current repository remains private, treat it as the source repository and export public releases from it.

### Stage 5: Contribution Workflow

Public contributions should enter through:

- company lens proposals
- evidence additions
- schema improvements
- validation rules
- public documentation fixes

Contribution rules:

- contributors must cite sources.
- no copyrighted raw article bodies.
- no confidential employer documents.
- no personal candidate data.
- no claims that inferred lenses are official company standards.
- maintainers can downgrade evidence confidence or reject unsupported claims.

## License Strategy

Use a split license model.

Approved public license direction:

- Apache-2.0 for schemas, tools, and framework code.
- CC BY 4.0 for documentation and public lens text.

Approved private license direction:

- proprietary JobACE internal license.
- enterprise private lens terms handled by contract.

The first public release should include a clear license split instead of treating code and lens text as the same artifact class.

## Public Lens Status Rules

Every public lens must include:

- lens status
- version
- evidence date
- evidence confidence
- limitations
- public / private visibility marker
- evidence visibility class

Recommended visibility field:

```json
{
  "visibility": "public"
}
```

Private and tenant lenses should use:

```json
{
  "visibility": "private",
  "tenant_scope": "tenant_id_or_internal_scope"
}
```

Public release tooling should reject any public export that contains `visibility: private`.

Public release tooling should also reject any exported evidence entry marked:

```json
{
  "evidence_visibility": "private_only"
}
```

Public release tooling may allow:

```json
{
  "evidence_visibility": "private_distillation_public_safe"
}
```

only when the entry is a non-verbatim distilled signal and does not include raw private text, copied paid content, user-submitted job posting bodies, candidate records, or tenant-specific details.

## JobACE Usage Rule

JobACE may consume:

- public lenses
- private JobACE lenses
- tenant-authorized private lenses
- derived lenses generated from a user's target role and job description

JobACE must disclose lens confidence in user-facing outputs when the system relies on `DERIVED_LENS`, `LIGHTWEIGHT_SCAN`, or sparse evidence.

JobACE must not present public inferred lenses as official company hiring standards.

## Immediate Next Steps

1. Add `public_manifest.yaml` and `private_manifest.yaml`.
2. Add a public export script.
3. Add a private marker scanner.
4. Audit current `company_lenses/` for public safety.
5. Decide which initial lenses are public release candidates.
6. Draft `CONTRIBUTING.md`.
7. Draft public `LICENSE` and documentation license decision.
8. Create a clean public export and review it before pushing.

## Approved Decisions

Approved direction for the first public release:

- Public code license: Apache-2.0.
- Public content license: CC BY 4.0.
- First public lens set: 12+ companies, starting with Amazon, Google, McKinsey, Microsoft, Apple, JPMorgan, RBC, TD, BMO, CIBC, Scotiabank, and Shopify.
- Private-derived signals: allowed only as `private_distillation_public_safe` summaries.
- Raw private materials: never exported.
- Workspace API: publish API contracts, schemas, examples, and optional mock/reference adapter first; keep production tenant operations private.
- JobACE mention: allowed as a commercial reference implementation, not as proof that JobACE's private evaluation layer is open source.
- Private-to-public promotion: owner-approved and checklist-gated; never automatic.

Post-release maintenance decisions:

- Keep public content license wording synchronized across README, manifest, and content-license files.
- Decide whether to include a limited mock `services/lens_workspace_api/` implementation in the first public export or defer it to a later release.
- Assign named maintainers who can approve private-to-public lens promotion.

## Current Recommendation

Keep the current private repository as the source of truth for now.

Build a manifest-based public export pipeline first. Only after the exported tree passes automated and manual safety checks should it become a public GitHub repository.

The first public release should be large enough to be persuasive: at least 12 company lenses across technology, consulting, global finance, Canadian banking, and Canadian growth companies. The release should preserve high-value private-derived insight through public-safe synthesis while still preventing leakage of private materials, tenant data, JobACE scoring logic, or production configuration.
