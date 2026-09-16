# Changelog

## v0.9.1-paper-math-complete

- Added equation-level paper-to-code traceability for all 15 mathematical expressions in manuscript Section 5.
- Added executable DAG validation/factorization, stopping logistic form, exact compatibility masking, hierarchical posterior utilities, credible intervals, Brier/ECE/log-loss metrics, KL drift, and reference information-gain scoring.
- Corrected the paper artifact data-support implementation to `1 - exp(-n_eff/tau)` and normalized entropy to use the declared permitted-category count.
- Aligned synthetic temporal decay with the manuscript's exponential-decay form and isolated ambiguous manuscript parameters rather than inventing semantics.
- Added Structured Interview DNA, Evidence Packet, and minimized-context schemas plus a safe synthetic DNA example.
- Added candidate-state, privacy-boundary, explanation, audit, policy, and Lens validation reference modules.
- Added `docs/MATH_TO_CODE_COMPLETENESS_AUDIT.md` and `docs/PAPER_TO_CODE_MAP.md`.

## v0.9.0-paper-readiness

- Added a manuscript-specific research boundary and frozen paper artifact manifest.
- Reframed the paper research core as candidate-side interview-practice reasoning, not employer-side selection decision support.
- Added an institution-agnostic research API for Lens validation, routing, follow-up-priority selection, and explanation.
- Added a dependency-free reference implementation for authorization gating, quality/recency weighting, hierarchical Dirichlet-style partial pooling, compatibility masking, backoff routing mixture, uncertainty, and data-support summaries.
- Added synthetic deterministic paper examples, validation tooling, unit tests, and CI.
- Added `CITATION.cff` and reproducibility documentation.
- Separated historical employer-side screening/decision semantics from the manuscript research core without rewriting repository history.
- Preserved JobACE as the first deep reference integration while removing JobACE-specific assumptions from the research-core interface.

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
