# Implementation–Integration Coverage Matrix — v1.4 Corrective Branch

## Purpose

This matrix separates five questions that must not be collapsed into a single claim:

1. **Executable counterpart** — does public code exist for the mathematical construct?
2. **Candidate-runtime integration** — is that construct exercised by
   `research_core.service::prioritize_followups`?
3. **Evaluation / monitoring use** — is it an offline diagnostic rather than a runtime decision step?
4. **Controlled experimental coverage** — is it exercised by a declared synthetic/public-safe experiment?
5. **External empirical validation** — has it been validated on an external population or real outcome?

The frozen v1.3 artifact correctly exposed executable counterparts for all Section 5 equations.
That statement does **not** mean all fifteen equations are composed into one end-to-end runtime.

## Status vocabulary

| Status | Meaning |
|---|---|
| **Integrated** | Reached directly or indirectly from `prioritize_followups`. |
| **Partial** | A related lower-level operation is in runtime, but the complete manuscript construct is not. |
| **Standalone** | Executable public utility exists, but it is not called by the candidate runtime. |
| **Evaluation** | Intended for offline evaluation / monitoring rather than runtime prioritization. |
| **Experimental** | Exercised in a controlled experiment or corrective benchmark. |
| **Not externally validated** | No real-population / employment-outcome validation is claimed. |

## Equation coverage

| Eq. | Construct | Executable counterpart | Candidate runtime | Evaluation / monitoring | Controlled experimental coverage | External empirical validation |
|---|---|---|---|---|---|---|
| 1 | DAG joint factorization | `research_core/dag.py::joint_factorization`, `validate_dag` | Standalone | No | Unit-level structural test | Not externally validated |
| 2 | Logistic stopping model | `research_core/stopping.py::stopping_probability` | Standalone | No | Unit-level functional test | Not externally validated; coefficients are not claimed fitted |
| 3 | Compatibility masking | `research_core/compatibility.py::masked_and_renormalized` | **Integrated** | No | Exp1A; Exp2 A3 | Not externally validated |
| 4 | Generic → archetype → industry → company hierarchy | `research_core/inference.py::hierarchical_partial_pooling` | **Partial** — runtime uses company-level shrinkage against a supplied parent distribution, not the complete four-level helper | No | Exp2 A2/A4; Exp5 hierarchy approximation benchmark | Not externally validated |
| 5 | Authorization × quality × recency weighted counts | `research_core/evidence.py::weighted_counts` | **Integrated** | No | Exp1A; Exp2 temporal sensitivity/ablation | Not externally validated |
| 6 | Dirichlet posterior parameters | `research_core/inference.py::posterior_alpha` | **Integrated indirectly** through `hierarchical_dirichlet_mean` | No | Exp2; Exp5 plug-in comparator | Not externally validated |
| 7 | Posterior mean | `research_core/inference.py::posterior_mean` | **Integrated indirectly** through `hierarchical_dirichlet_mean` | No | Exp2; Exp5 plug-in comparator | Not externally validated |
| 8 | Routed predictive mixture | `research_core/routing.py::route_mixture` | **Integrated** | No | Exp1A; Exp2 gamma sensitivity; Exp4 E4-04 | Not externally validated |
| 9 | Routing weights | `research_core/routing.py::route_mixture` | **Integrated** | No | Exp1A; Exp2 gamma sensitivity | Not externally validated |
| 10 | Normalized entropy | `research_core/uncertainty.py::normalized_entropy` | **Integrated** | Runtime diagnostic summary | Exp1A baseline trace | Not externally validated |
| 11 | Data-support score | `research_core/uncertainty.py::data_support`, `research_core/service.py` | **Integrated** | Runtime release / abstention support summary | Exp1A; Exp4 E4-03 | Not externally validated |
| 12 | Multiclass Brier score | `research_core/evaluation.py::multiclass_brier` | Standalone | **Evaluation** | Unit-level metric test | No external calibration claim |
| 13 | Top-label ECE | `research_core/evaluation.py::top_label_ece` | Standalone | **Evaluation** | Exp4 E4-02 | No external calibration claim |
| 14 | KL drift statistic | `research_core/evaluation.py::kl_divergence` | Standalone | **Evaluation / monitoring** | Unit-level metric test | Threshold not externally validated |
| 15 | Expected parameter information gain | `research_core/active_learning.py::expected_information_gain` | Standalone | Acquisition-scoring utility | Exp4 E4-01 | Not externally validated |

## Runtime call-graph boundary

The public candidate-side runtime can be summarized as:

```text
PracticeRequest.validate
    ↓
weighted_counts                                  Eq.5
    ↓
hierarchical_dirichlet_mean
    ├─ posterior_alpha                           Eq.6
    └─ posterior_mean                            Eq.7
    ↓
compatibility mask                              Eq.3
    ↓
route_mixture                                   Eq.8–9
    ↓
data_support / abstention                       Eq.11
    ↓
normalized_entropy                              Eq.10
    ↓
ordered candidate-side practice priority
```

The following Section 5 constructs are **not** called by this runtime path:

```text
Eq.1  DAG joint factorization
Eq.2  logistic stopping
Eq.12 Brier
Eq.13 top-label ECE
Eq.14 KL drift
Eq.15 information gain
```

Eq.4 is **partially represented**: runtime performs company-level Dirichlet shrinkage using a
supplied parent distribution, while the complete generic → archetype → industry → company helper
is a standalone research implementation and is benchmarked in Experiment 5.

## Posterior-uncertainty boundary

`research_core.inference::credible_intervals(alpha)` computes marginal intervals conditional on
the supplied Dirichlet parameter vector. In the recursive plug-in hierarchy, that parameter vector
uses plug-in parent distributions; therefore those intervals do not propagate upper-level
posterior uncertainty.

Experiment 5 quantifies this approximation under a declared synthetic binary hierarchy by
comparing the plug-in result with a deterministic uncertainty-propagating numerical reference.

This benchmark is an internal approximation study. It does not establish real-employer validity,
population calibration, fairness, candidate learning effects, or employment outcomes.

## Claim discipline

Safe repository / manuscript language:

- “All Section 5 equations have an executable public counterpart.”
- “The candidate-side runtime integrates the subset needed for evidence weighting, local
  shrinkage, compatibility, routing, support, uncertainty summary, and abstention.”
- “Other mathematical components are standalone evaluation, monitoring, stopping, DAG, or
  acquisition utilities.”
- “Controlled experiments verify declared mechanism behavior under synthetic/public-safe inputs.”

Avoid using the following as shorthand:

- “All equations are integrated into the runtime.”
- “The full mathematical model runs end to end.”
- “15/15 implemented” when the reader could reasonably interpret “implemented” as runtime
  integration or empirical validation.
- “Full Bayesian uncertainty propagation” for the recursive plug-in hierarchy.
- “Validated” without specifying whether the evidence is unit-level, controlled synthetic,
  public-safe semantic regression, or external empirical validation.
