# Changelog

## Unreleased

- Began production promotion of selected manuscript v1.5 reasoning mechanisms into a
  standalone `runtime_core` package without changing the existing JobACE adapter
  contract or public API.
- Added fail-closed evidence weighting, compatibility masking, permitted-category
  support accounting, and company-level hierarchical shrinkage primitives.
- Added focused runtime-core unit tests and an independent CI gate.
- Added an internal Decision Envelope and local decision service that compose the
  promoted primitives into abstention or ordered practice-priority outputs while
  stopping before routing, backoff, adapter translation, or LLM generation.
- Added a shadow-only proposed support-aware L0-L5 backoff policy and an
  observe-only Context Divergence Guard using caller-supplied thresholds. These
  mechanisms do not change the live decision path.
- Added a public-safe JobACE Adapter v2 reference layer that preserves the
  existing external contract while normalizing it into an institution-agnostic
  practice context, plus an unbound candidate-signal adapter for the existing
  six-dimension AIMS score taxonomy. No live decision binding or API change is
  introduced.
- Added a public-safe production-candidate envelope, deterministic explanation
  layer, decision regression comparator, and fail-closed runtime promotion
  switch. Promoted-local release requires explicit gate attestations; the PR-C
  support-aware backoff and Context Divergence Guard remain shadow-only.

## v0.8.1-public-core

- Published the public-safe AIMS Lens Engine core.
- Released code, schemas, and tools under Apache-2.0.
- Released public lens content and documentation under CC BY 4.0.
- Included the public manifest, private denylist, export scanner, audit tooling,
  contribution rules, and the initial public company-lens set.

## v0.7.0-jobace-contract-ready

- Added Phase 3C.1 Jobace staging integration contract.
- Added Jobace adapter reference client.
- Added Jobace staging request and review-decision examples.
- Added adapter contract schema and validator.
- Recorded full 230-case live LLM regression pass.

## v0.6.0-limited-pilot-llm-ready

- Added optional OpenAI-backed LLM scorer behind the existing limited-pilot API.
- Preserved deterministic scorer as the default fallback.
- Added Phase 3B regression harness for fallback and live LLM scoring.
- Added API audit logging under gitignored `audit_logs/`.
- Kept Phase 2C production gates, human review workflow, and automated-rejection block intact.

## v0.5.0-internal-pilot

- Added internal pilot API.
- Added candidate-level human review queue and reviewer decision workflow.
- Entered `approved_for_limited_pilot`.

## v0.4.0-production-gates

- Completed Phase 2C production gate coverage.
- Added 230 transcript fixtures, cross-company validation, cross-role validation, and human reviewer sign-off.
