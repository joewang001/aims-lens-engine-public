# AIMS Lens Engine

Independent company, role, industry, and thinker lens distillation platform for interview evaluation, candidate screening, interview preparation, and decision support.

Current version: `v0.8.1-public-core`

Current status: `public_released`

## Positioning

AIMS Lens Engine is built as an independent system first. This public repository contains the open, public-safe core: schemas, company lens structures, evidence standards, validation tools, and public company lens examples.

JobACE uses AIMS Lens Engine as a commercial reference implementation, but the production workspace service, tenant data, candidate data, review logs, private calibration, deployment configuration, and enterprise-specific lenses remain private.

The system distills public and private evidence into structured lenses:

- Company Lens
- Role Lens
- Industry Lens
- Thinker Lens
- Interview Question Bank
- Evidence and Validation Layer

## Product Modes

- `FULLY_DISTILLED`: multi-agent research, archived evidence, validation complete.
- `DERIVED_LENS`: generated from similar companies, industry archetypes, role requirements, and target JD.
- `LIGHTWEIGHT_SCAN`: generated from limited public/company-provided material with explicit lower confidence.
- `GENERIC_AIMS`: fallback when no meaningful target lens exists.

## Public Release Scope

The first public release is designed to be large enough for external review and contribution. It includes at least 12 public company lenses:

- Amazon
- Google
- McKinsey
- Microsoft
- Apple
- JPMorgan
- RBC
- TD
- BMO
- CIBC
- Scotiabank
- Shopify

Additional company lenses should be added only when they meet the public contribution and evidence rules in `CONTRIBUTING.md`.

## Repository Map

```text
api/                  API contracts and OpenAPI draft
architecture/         System design and routing model
agents/               Multi-agent research templates
company_lenses/       Lens files and company profile folders
docs/                 Project charter and implementation plan
governance/           privacy, fairness, evidence, and version rules
schemas/              JSON schemas for structured lens artifacts
examples/             sample requests, reports, and validation cases
services/             private production services, excluded from public export by default
interview_prep_templates/ B2C improvement plan templates for structured interview practice
candidate_personas/     Synthetic candidate fixtures for mock interview QA and calibration
```

## Implementation Principle

Start file-first and auditable. Move to database, queue, and review portal only after the MVP proves that the lens outputs are differentiated, useful, and evidence-backed.

## Public And Private Boundary

The public release is produced through an allowlist and denylist pair:

```text
public_manifest.yaml
private_manifest.yaml
tools/export_public_release.py
tools/scan_public_export.py
tools/generate_public_release_audit_report.py
```

The export tooling copies only allowlisted public paths, then applies the private manifest as a hard denylist. Public releases must not include raw private materials, tenant uploads, candidate data, production service code, API keys, local databases, deployment configuration, or private review records.

To create and audit a public export:

```bash
python tools/export_public_release.py --execute --clean
python tools/scan_public_export.py --allowlist
python tools/generate_public_release_audit_report.py --allowlist
```

## Interview Prep Templates

Phase B2C-1 adds the first B2C improvement plan template:

```text
interview_prep_templates/mckinsey_case/
docs/phase-b2c1-mckinsey-case-improvement-plan.md
docs/phase-b2c2-improvement-plan-adapter.md
docs/candidate-persona-fixtures.md
```

It converts McKinsey-style case interview preparation into a reusable AIMS-linked training plan for interview prep users.
B2C-2 adds `tools/interview_prep_planner.py` and `POST /v1/interview-prep/improvement-plan` so product flows can turn AIMS scores into Priority Improvement Points, drills, reflection routing, and next mock instructions.

## Contribution

Contributions are welcome when they improve the public core without importing private or copyrighted source bodies. See `CONTRIBUTING.md` for source, privacy, evidence, and pull request rules.

## Continuous Updates

AIMS Lens Engine is intended to keep refreshing and expanding. Existing company lenses should receive new public-safe evidence across the seven independent dimensions, and new leading companies should be added in undercovered industries. The maintenance workflow validates every PR and scheduled run, then opens automated refresh-candidate PRs. See `docs/public-lens-refresh-and-expansion.md` for the mechanism and `docs/public-lens-operations-plan.md` for cadence, quantity targets, approved expansion waves, and normal auto-merge rules.

## License

Code, schemas, and tools are licensed under Apache-2.0. Public lens content and documentation are licensed under CC BY 4.0. See `LICENSE`, `NOTICE`, and `CONTENT_LICENSE.md`.
