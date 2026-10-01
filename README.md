# AIMS Lens Engine

[中文说明](README_ZH.md) | [Quick Start](#quick-start) | [Contributing](CONTRIBUTING.md)

AIMS Lens Engine turns evidence about companies, roles, and industries into structured, auditable **lenses** for interview preparation and human-reviewed decision support. A lens records contextual priorities, sources, and limitations; it is not an official employer hiring standard.

This public repository is for developers, researchers, and partner institutions who want to inspect lens examples, validate public-safe content, or build integrations using the published schemas and API contracts. It is not a turnkey JobACE deployment or a hosted API service.

- **Software release:** `v0.8.1-public-core` — the public core version recorded in [VERSION](VERSION) and [CHANGELOG.md](CHANGELOG.md).
- **Research manuscript:** `v1.5` — a separate manuscript version, not a software release number. The manuscript and frozen research baseline are not included on this public `main` branch.
- **Public release status:** `public_released`.

Start with [company lens examples](company_lenses/), the [repository map](#repository-map), or the checks below. JobACE is a reference integration; it is not required to inspect or validate this public core.

## Quick Start

Use Python 3.11 or newer. Clone the public repository and create a virtual environment:

```bash
git clone https://github.com/joewang001/aims-lens-engine-public.git
cd aims-lens-engine-public
python -m venv .venv
```

Activate it with `source .venv/bin/activate` on macOS/Linux or `.venv\Scripts\Activate.ps1` in Windows PowerShell. If your system uses `python3`, substitute it for `python` when creating the environment.

```bash
python -m pip install PyYAML
python tools/scan_public_export.py --allowlist
python tools/validate_public_lens_coverage.py --min-companies 12
```

Successful checks report `public_scan_status=ok` and `public_lens_coverage_status=ok`. They run locally without API keys or private services. [api/openapi.yaml](api/openapi.yaml) describes integration contracts; it does not start an API server.

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
.github/              Public-lens maintenance workflow
api/                  API contracts and OpenAPI draft
architecture/         System design and routing model
agents/               Multi-agent research templates
company_lenses/       Lens files and company profile folders
docs/                 Project charter and implementation plan
governance/           privacy, fairness, evidence, and version rules
routing/              Role-routing configuration
schemas/              JSON schemas for structured lens artifacts
examples/             sample requests, reports, and validation cases
tools/                Public export, validation, and maintenance tools
```

Only directories present in this public checkout are listed. Private services and excluded assets are not part of this repository map.

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

## Interview Prep Integration Boundary

The public tree includes [interview-prep request examples](examples/b2c-mckinsey-improvement-plan-request.json) and `tools/interview_prep_planner.py`, but its `interview_prep_templates/` assets are not included. Do not treat the planner as a self-contained public Quick Start.

API endpoint descriptions are integration contracts, not services shipped by this public release. For public validation, use the [Quick Start](#quick-start) above.

## Contribution

Contributions are welcome when they improve the public core without importing private or copyrighted source bodies. See `CONTRIBUTING.md` for source, privacy, evidence, and pull request rules.

## Continuous Updates

AIMS Lens Engine is intended to keep refreshing and expanding. Existing company lenses should receive new public-safe evidence across the seven independent dimensions, and new leading companies should be added in undercovered industries. The maintenance workflow validates every PR and scheduled run, then opens automated refresh-candidate PRs. See `docs/public-lens-refresh-and-expansion.md` for the mechanism and `docs/public-lens-operations-plan.md` for cadence, quantity targets, approved expansion waves, and normal auto-merge rules.

## License

Code, schemas, and tools are licensed under Apache-2.0. Public lens content and documentation are licensed under CC BY 4.0. See `LICENSE`, `NOTICE`, and `CONTENT_LICENSE.md`.
