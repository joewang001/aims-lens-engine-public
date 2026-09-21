# Changelog

## 0.10.0-paper-v1.4 (release candidate)

- Aligned release-candidate metadata with manuscript v1.4 without claiming a frozen v1.4 tag.
- Recorded frozen v1.3 commit `f7fcb6a3129cb58fe20c414f1abe519376def8e1` as the v1.4 branch base and `c18899b469e1d579391306872d5834ebf6e3caf3` as the corrective experimental baseline.
- Added Experiment 4 / Experiment 5 protocols and runners, the implementation–integration coverage matrix, and documentation-alignment validation to the paper artifact allowlist.
- Aligned README / reproducibility wording with top-label ECE, recursive plug-in hierarchical Dirichlet shrinkage, and conditional Dirichlet intervals given the plug-in parent distribution.
- Preserved Experiment 4 as internal mathematical–implementation correction evidence and Experiment 5 as a synthetic approximation benchmark, with no external-validity, fairness, employer-behavior, or employment-outcome claim.
## v0.9.2-paper-v1.3

- Aligned reviewer-facing artifact metadata and documentation with manuscript v1.3.
- Recorded the frozen experimental bundle commit `84c0afc5f928989237832d625002aba17ae8ac4f`.
- Added Experiment 1A/1B/2/3 paths to the paper-to-code and reproducibility documentation.
- Documented controlled synthetic verification, sensitivity, ablations, and semantic regression while preserving external-validity boundaries.
- Split branch-base, experimental-bundle, and final archival-reference semantics in the paper manifest.
- Updated the paper validator to support explicit release-candidate and frozen archival states without changing experiment logic or outputs.

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
