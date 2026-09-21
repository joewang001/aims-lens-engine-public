# Paper-Release Readiness Refactor Plan

Target branch: `paper-release-readiness-v1.1`  
Base: `main` at `cf2586e5649feb05fd19faefa479e765055c76d4`  
Original branch target: AIMS Lens Engine v1.1 journal-preparation manuscript
Current aligned manuscript: **v1.3**
Release-candidate artifact: **v0.9.2-paper-v1.3**
Frozen experimental bundle: `84c0afc5f928989237832d625002aba17ae8ac4f`

## Objective

Make the public repository internally consistent with manuscript v1.3 before journal submission, while preserving repository history and leaving `main` unchanged until review/merge. The v1.3 release layer additionally aligns the frozen controlled-verification bundle, reviewer documentation, citation metadata, and archival freeze semantics.

The frozen manuscript artifact must present AIMS Lens Engine as an independent, institution-agnostic, candidate-side interview-practice reasoning engine. JobACE remains a reference client. Historical employer-side screening experiments remain visible in repository history or wider project files but are not part of the paper research core.

## Classification rules

Every file on the base commit is classified by the precedence below. A more specific path overrides a directory rule.

### A. MODIFY — paper-facing files

| File | Action | Reason |
|---|---|---|
| `README.md` | replace | Lead with independent research-core positioning; add reviewer quick start and explicit legacy boundary. |
| `VERSION` | replace on branch | Mark branch artifact as `v0.9.0-paper-readiness`; do not change `main` until accepted. |
| `CHANGELOG.md` | prepend | Record the paper-readiness boundary and artifact changes. |
| `api/openapi.yaml` | replace | Remove employer-side screening / advance / reject semantics from the paper-facing API; expose Lens validation, routing, practice priority and explanation. |
| `architecture/system-design.md` | replace | Make Versioned Lens API the system boundary; JobACE becomes one client; split public research assets from protected production assets. |
| `architecture/lens-router.md` | replace | Align routing with L0-L5 paper backoff and practice-only scope. |
| `governance/evidence-standard.md` | replace | Separate authorization gate from quality/recency weight; define Lens as evidence-bounded hypothesis. |
| `governance/privacy-and-fairness.md` | replace | Remove employer adverse-decision framing from paper governance; add authenticity, stereotyping, contestability, fail-closed rules. |

### B. ADD — manuscript research core

| New file | Purpose |
|---|---|
| `CITATION.cff` | Machine-readable citation metadata. |
| `RESEARCH_BOUNDARY.md` | Normative definition of paper scope and exclusions. |
| `REPRODUCIBILITY.md` | Reviewer runbook requiring no network/private data. |
| `PAPER_RELEASE_READINESS.md` | This file-level refactor record. |
| `paper_artifact_manifest.yaml` | Frozen manuscript allowlist/exclusion policy, narrower than `public_manifest.yaml`. |
| `research_core/__init__.py` | Public reference package surface. |
| `research_core/models.py` | Institution-agnostic evidence, routing and practice request models. |
| `research_core/inference.py` | Authorization gating, recency/quality weighting, partial pooling, compatibility mask, routing mixture, entropy/support. |
| `research_core/service.py` | Ordered candidate-side practice-priority service. |
| `schemas/followup_priority_request.schema.json` | Research-core request contract. |
| `schemas/followup_priority_response.schema.json` | Research-core response contract. |
| `examples/paper/followup_priority_request.json` | Synthetic deterministic example. |
| `examples/paper/expected_followup_priority_response.json` | Expected deterministic output. |
| `tools/run_paper_artifact_demo.py` | One-command reviewer demo. |
| `tools/validate_paper_artifact.py` | Boundary and deterministic-output validation. |
| `tests/test_research_core.py` | Reference implementation unit tests. |
| `.github/workflows/paper-artifact-ci.yml` | CI for paper artifact. |
| `legacy/employer_decision_support/README.md` | Scope marker for historical employer-side semantics; points to git history rather than duplicating old API. |

### C. KEEP — legal, contribution and broad public-release infrastructure

These files remain unchanged and are valid repository-level assets. They are not rewritten merely for the paper:

- `LICENSE`
- `NOTICE`
- `CONTENT_LICENSE.md`
- `CONTRIBUTING.md`
- `README_ZH.md` — retain as broader project documentation; update separately if a Chinese paper-artifact mirror is desired.
- `public_manifest.yaml` — remains the broad public-export allowlist; the paper uses the stricter `paper_artifact_manifest.yaml`.
- `private_manifest.yaml` — remains the hard denylist for private data and production assets.
- `.github/workflows/public-lens-maintenance.yml` — remains the wider public-Lens maintenance workflow, outside frozen paper reproducibility.

### D. KEEP AS SUPPORTING PUBLIC ASSETS — not required to reproduce the paper model

All files under these paths remain in the repository, but are outside the minimal frozen paper artifact unless explicitly allowlisted:

- `company_lenses/**`
- `agents/templates/**`
- `routing/role_router.json`
- `docs/aims-lens-distillation-strategy-zh.md`
- `docs/candidate-persona-fixtures.md`
- `docs/distillation-playbook.md`
- `docs/implementation-plan.md`
- `docs/project-charter.md`
- `docs/public-lens-operations-plan.md`
- `docs/public-lens-refresh-and-expansion.md`
- `docs/public-lens-sourcing-agent-contract.md`
- `docs/public-private-split-strategy.md`
- `docs/public-private-split-strategy-zh.md`
- `docs/refresh-candidates/**`
- `docs/role-routing-and-validation.md`
- `docs/validation-checklist.md`

Interpretation rule for `company_lenses/**`: named-company assets are public practice hypotheses inferred from permitted evidence; they are not official employer standards and are not required by the deterministic paper demo.

### E. KEEP AS SUPPORTING SCHEMAS — outside minimal paper core

The following existing schema files remain in place because they support the wider open project, but the manuscript does not rely on them as its reproducibility contract:

- `schemas/agent_artifact.schema.json`
- `schemas/candidate_persona_fixture.schema.json`
- `schemas/company_lens.schema.json`
- `schemas/derived_lens.schema.json`
- `schemas/dual_layer_evaluation.schema.json`
- `schemas/evidence.schema.json`
- `schemas/interview_prep_plan.schema.json`
- `schemas/public_lens_source_packet.schema.json`
- `schemas/question_bank.schema.json`
- `schemas/role_lens.schema.json`

### F. RETAIN BUT SEPARATE FROM RESEARCH CORE — employer/product-specific semantics

These files remain in repository history/wider development scope, but must not be included in the frozen paper artifact or cited as implementation evidence for the manuscript's candidate-side claims:

- `schemas/jobace_adapter_contract.schema.json`
- `schemas/review_decision.schema.json`
- `schemas/screening_report.schema.json`
- `examples/human-review-decision-request.json`
- `examples/internal-pilot-screening-request.json`
- `examples/jobace-amazon-marketing-request.json`
- `examples/jobace-review-decision-request.json`
- `examples/jobace-staging-screening-request.json`
- `examples/jobace-staging-validation-suite.json`
- `examples/lens-workspace-create-api-key-request.json`
- `examples/lens-workspace-create-tenant-request.json`
- `examples/lens-workspace-source-material-request.json`
- `docs/limited-pilot-policy.md`
- `tools/llm_scorer.py`
- `tools/run_scoring_harness.py`

The legacy boundary also covers any future path matching:

- `services/**`
- `integrations/jobace/**`
- employer ranking / screening / advance / reject decision workflows.

### G. KEEP AS BROADER PUBLIC TOOLING — outside paper core

The following existing tools remain useful for public Lens operations and validation but are not needed to reproduce the manuscript reference path:

- `tools/collect_public_lens_sources.py`
- `tools/export_public_release.py`
- `tools/generate_phase2c_validation_cases.py`
- `tools/generate_public_lens_patch.py`
- `tools/generate_public_release_audit_report.py`
- `tools/interview_prep_planner.py`
- `tools/prepare_public_lens_refresh.py`
- `tools/scan_public_export.py`
- `tools/validate_b2c2_improvement_plan.py`
- `tools/validate_candidate_personas.py`
- `tools/validate_cross_company_fit_matrix.py`
- `tools/validate_dual_layer_evaluation.py`
- `tools/validate_public_lens_coverage.py`
- `tools/validate_role_routing.py`

### H. KEEP AS EXISTING NON-PAPER EXAMPLES

Unless listed in section F, current `examples/*.json` remain wider-project examples. They are not included in the paper artifact. The paper's reproducibility examples live only under `examples/paper/**`.

## Why no destructive deletion is required

The manuscript problem is not that historical employer-side experiments exist; the problem is ambiguity over which files constitute the research artifact. The refactor therefore uses four boundaries:

1. paper-facing API and governance contain candidate-side semantics only;
2. `paper_artifact_manifest.yaml` is a strict manuscript allowlist;
3. historical employer decision-support semantics are explicitly labelled non-paper;
4. git history preserves provenance without forcing those semantics into the current paper core.

## Release gates before journal submission

The branch is ready for a frozen paper release only when all gates pass:

- `python tools/validate_paper_artifact.py` -> `PAPER_ARTIFACT_VALIDATION_PASS`;
- `python -m unittest tests.test_research_core` -> pass;
- `python tools/run_paper_artifact_demo.py` -> matches expected JSON;
- no paper-core API contains screening/advance/reject endpoints;
- no private/candidate production data is present in the paper artifact;
- manuscript Code and Artifact Availability points to a frozen tag/commit, not moving `main`;
- a release tag such as `v0.9.2-paper-v1.3` is created after review;
- optional but recommended: archive the tag with Zenodo and add the resulting DOI to `CITATION.cff` and the manuscript.

## Branch strategy

1. Use the existing `paper-release-readiness-v1.1` branch, preserving the recorded branch-base commit.
2. Apply only this overlay; do not delete broader project assets.
3. Run paper CI and review the compare against `main`.
4. Do **not** merge before manuscript/artifact consistency review.
5. Once accepted for submission, create a frozen release tag from this branch (or a clean follow-up branch) and cite that immutable ref in the manuscript.
