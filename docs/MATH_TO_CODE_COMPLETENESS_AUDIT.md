# Math-to-Code Completeness Audit — Manuscript v1.3

**Scope.** This audit maps every mathematical expression in manuscript Section 5, every algorithm/listing that defines public research behavior, and every stated operational threshold to the paper-release reference artifact. It distinguishes reproducible reference logic from empirical quantities that have not yet been fitted or validated.

## A. Equations 1–15

| Eq. | Manuscript construct | Reference artifact | Status | Boundary / note |
|---|---|---|---|---|
| 1 | DAG joint factorization | `research_core/dag.py::joint_factorization`, `validate_dag` | Complete reference logic | Caller supplies declared local conditionals; no undeclared edges are inferred. |
| 2 | Logistic stopping model | `research_core/stopping.py::stopping_probability` | Complete functional form | Coefficients are not claimed to be empirically fitted. |
| 3 | Compatibility masking and renormalization | `research_core/compatibility.py::masked_and_renormalized` | Complete | Returns no distribution when every category is masked, enabling abstention. |
| 4 | Generic → archetype → industry → company Dirichlet hierarchy | `research_core/inference.py::hierarchical_partial_pooling` | Reference-complete for inference logic | Hyperparameter learning is not implemented because the manuscript does not claim fitted hyperparameters. |
| 5 | Authorization-gated, quality- and recency-weighted counts | `research_core/evidence.py::weighted_counts`, `exponential_recency_weight` | Complete and equation-aligned | Authorization is binary; recency is exactly `exp(-delta * age)`. |
| 6 | Company posterior Dirichlet parameters | `research_core/inference.py::posterior_alpha` | Complete | Works with fractional effective counts. |
| 7 | Posterior mean | `research_core/inference.py::posterior_mean` | Complete | Direct normalized posterior-alpha calculation. |
| 8 | Routed predictive mixture | `research_core/routing.py::route_mixture` | Complete | Exposes component provenance. |
| 9 | Routing weights | `research_core/routing.py::route_mixture` | Complete | Implements authorization × applicability × coverage × gamma^distance and normalization. |
| 10 | Normalized entropy | `research_core/uncertainty.py::normalized_entropy` | Complete and corrected | Denominator uses permitted category count `K_L`, not only non-zero entries. |
| 11 | Data-support score `1-exp(-n_eff/tau)` | `research_core/uncertainty.py::data_support`, `research_core/service.py::prioritize_followups` | Corrected v1.4 reference logic | `n_eff` used for release/abstention is the sum of authorization-, quality-, and recency-weighted counts over the current permitted categories only. Compatibility-masked categories contribute zero released support. Explicitly not a correctness probability. |
| 12 | Multiclass Brier score | `research_core/evaluation.py::multiclass_brier` | Complete | Evaluation only; does not assert calibration. |
| 13 | Vector-form ECE | `research_core/evaluation.py::vector_ece` | Complete reference operationalization | Binning is by maximum predicted probability; bin vector mismatch uses L1 distance as written. |
| 14 | KL drift statistic | `research_core/evaluation.py::kl_divergence` | Complete | Threshold remains an empirical policy setting. |
| 15 | Expected parameter information gain | `research_core/active_learning.py::expected_information_gain` | Corrected reference operationalization | Computes one-record Dirichlet-parameter posterior information gain (equivalently `I(Theta;Y)`) for already-authorized records. The former predictive category-entropy reduction is retained separately as `predictive_entropy_reduction` and is not Eq. 15. |

### Posterior uncertainty

The manuscript also states that Dirichlet posteriors provide credible intervals. `research_core/inference.py::credible_intervals` supplies deterministic-seed Monte Carlo marginal intervals using only the Python standard library. This reproduces the inference concept without implying empirical coverage has been validated.

## B. Manuscript listings / algorithms

| Listing | Construct | Artifact | Status |
|---|---|---|---|
| 1 | Structured Interview DNA | `schemas/interview_dna.schema.json`, `examples/paper/interview_dna.example.json` | Complete public schema/example |
| 2 | EvidencePacket | `research_core/evidence.py::EvidencePacket`, `schemas/evidence_packet.schema.json` | Complete reference structure |
| 3 | Lens routing | `research_core/routing.py::select_highest_specificity`, `BACKOFF_SEQUENCE`, `architecture/lens-router.md` | Complete public decision rules |
| 4 | Follow-up category selection | `research_core/service.py::prioritize_followups` | Complete reference pipeline |
| 5 | Candidate-state adaptation | `research_core/candidate_state.py::CandidateStateModel` | Complete reference separation/consent logic |
| 6 | Transcript de-identification | `research_core/privacy.py::deidentify_transcript` | Partial by design | Contact/date handling is executable; person/company/location NER is a pluggable reviewed dependency. The repository does **not** claim production-grade de-identification accuracy. |
| 7 | Minimized Context Package | `research_core/privacy.py::MinimizedContextPackage`, `schemas/minimized_context.schema.json` | Complete |
| 8 | Plain-language explanation | `research_core/explanation.py::generate_explanation` | Complete reference logic |
| 9 | Audit record | `research_core/audit.py::AuditRecord` | Complete reference structure |
| 10 | Lens load/validation | `research_core/lens.py::load_lens`, `validate_interview_dna` | Complete lightweight validator | JSON Schema files remain the normative contract. |
| 11 | Hierarchical inference | `research_core/inference.py` | Complete reference logic |
| 12 | Compatibility masking | `research_core/compatibility.py` | Complete |
| 13 | Routing class / backoff | `research_core/routing.py` | Complete |
| 14 | Full AIMS pipeline | `research_core/service.py` | Complete reference path |

## C. Thresholds and initialization parameters

All initial values are centralized in `config/paper_defaults.json` so a reviewer can distinguish declared initial settings from learned parameters.

| Manuscript item | Repo representation | Status / caution |
|---|---|---|
| prior strength `lambda_0 = 10` | `prior_strength_lambda0` | Documented; relationship to manuscript `alpha_0` should be clarified in v1.3 before treating it as an executable prior vector. |
| `kappa = 20` “half-life in observations” | `half_life_observations_kappa` | **Manuscript ambiguity.** `kappa` is also used for hierarchical concentration parameters. No hidden implementation is invented. Rename/define in v1.3. |
| backoff `gamma = 0.7` | `backoff_discount_gamma`; `route_mixture` | Executable |
| temporal `delta = 0.02/month` | `temporal_decay_delta_per_month`; `exponential_recency_weight` | Executable when evidence age is supplied in months; demo uses the mathematically equivalent half-life-to-rate conversion in days. |
| KL review threshold `0.3` | `kl_drift_review_threshold`; `kl_divergence` | Metric executable; threshold not claimed validated |
| ECE secondary target `0.10` | `ece_secondary_target`; `vector_ece` | Metric executable; target remains secondary/empirical |
| support ceiling example `0.85` | `support_ceiling_example`; `research_core/policy.py::apply_support_ceiling` | Executable policy cap; not probability |
| abstention threshold example `0.3` | `abstention_threshold_example`; `should_abstain` | Executable configurable policy |
| minimum sample size `30` | `minimum_sample_size_example` | Documented only; v1.3 should clarify what operation is gated because hierarchical shrinkage is already continuous below and above 30. |
| maximum parents `6` | `maximum_declared_parents`; `PARENT_CARDINALITY_CAPS` | Executable; test verifies 22,050 configurations |

## D. Manuscript issues exposed by the audit

These should be corrected in manuscript v1.3 rather than hidden in code:

1. **`primary_probability` in Listing 4** should be renamed `primary_priority_weight` (or similar) unless the Lens is Evaluation-Ready and held-out calibration has been established.
2. **`confidence` in Listing 9 AuditRecord** should become `diagnostic_weight`, `support`, or a typed field that distinguishes support from calibrated probability.
3. **Symbol collision for `kappa`.** Section 5 uses `kappa_c`, `kappa_i`, `kappa_a` as Dirichlet concentration parameters, while Appendix B/Table 19 uses `kappa` for a “half-life.” Rename the latter (for example `h_n`) or define a separate prior-decay quantity.
4. **`lambda_0` versus `alpha_0`.** The appendix says prior strength `lambda_0 = 10`, while the hierarchy writes `pi_u ~ Dirichlet(alpha_0)`. v1.3 should explicitly define whether `alpha_0 = lambda_0 * pi_base` or use one notation consistently.
5. **Minimum sample size = 30.** The manuscript should say exactly which release/fitting operation this gates. The Bayesian hierarchy itself does not suddenly switch methods at 30 observations.
6. **“Prediction” wording in limitations.** Candidate-side ordered practice priorities should not be casually called employer predictions.
7. **De-identification claim boundary.** Listing 6 is a procedure/interface, not evidence that PII removal has been empirically validated. The text should state that production de-identification requires validated entity detection and review.

## E. Current completeness assessment

- Core Section 5 equations with executable counterpart: **15/15**.
- Public decision algorithms/listings with counterpart: **14/14**, with Listing 6 intentionally partial at the NER layer and explicitly disclosed.
- Declared thresholds centralized: **10/10**, but three (`lambda_0`, observation half-life `kappa`, min sample 30) require manuscript clarification before stronger executable semantics are justified.
- Controlled verification claims: **present and artifact-backed** for Experiments 1A, 1B, 2, and 3. External participant, named-employer, calibration, fairness, current-production-LLM, and employment-outcome validation remain future empirical work.

The target is conceptual reproducibility and reference-algorithm reproducibility, not disclosure of tenant configuration, JobACE production policy, user data, proprietary operational thresholds, or complete production code.

## F. Manuscript v1.3 controlled-verification alignment

The v1.3 manuscript adds controlled results without changing the Section 5 mathematical definitions:

- **Experiment 1A:** seven candidate-side end-to-end invariant cases, including authorization hard-gating, aging, masking, routing eligibility, support, and fail-closed abstention.
- **Experiment 1B:** eleven controlled Lens/role-prior fixtures with positive and company-name negative controls.
- **Experiment 2:** one-factor sensitivity for `gamma`, `delta`, and `lambda_0`, plus controlled A2/A3/A4/A6 synthetic ablations.
- **Experiment 3:** six public-safe candidate-answer semantic regression fixtures; the current production language model is explicitly **not** rerun.

These experiments verify internal mechanism behavior, contract preservation, and reproducibility under controlled inputs. They do not establish the external empirical claims reserved by manuscript Sections 7.1–7.6.
