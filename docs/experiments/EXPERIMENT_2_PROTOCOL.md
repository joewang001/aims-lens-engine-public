# Experiment 2 — Parameter Sensitivity and Controlled Ablations

## Purpose

Experiment 2 evaluates how declared research parameters affect the reference implementation and
what changes when selected structural components are removed under controlled synthetic
conditions.

It contains three one-factor sensitivity studies and four controlled ablations.

This is a synthetic verification and sensitivity study. It does not establish ecological
validity, employer behavior, candidate learning benefit, or employment outcomes.

## Why no 45-cell lambda × gamma × delta factorial is used

The three parameters do not occupy the same implementation layer.

- `gamma` is a routing/backoff parameter in the service path.
- `delta` is a temporal evidence-decay parameter.
- `lambda_0` is treated here as a lower-level prior concentration in
  `alpha_0 = lambda_0 * pi_base`; it is not a `PracticeRequest` field and is not equated with
  `kappa_company`.

A forced full factorial would conflate distinct hierarchy levels. The study therefore uses
pre-registered one-factor perturbations while holding the other inputs fixed.

# Part A — Sensitivity

## S1 — Routing discount gamma

Values:

- 0.5
- 0.7
- 0.9

The existing paper request is used with the abstention threshold disabled so routing behavior can
be observed at every value.

Pre-registered expectations:

1. normalized L0 routing weight decreases monotonically as gamma increases;
2. total fallback weight (L3 + L5) increases monotonically;
3. L5/L3 routing-weight ratio increases monotonically;
4. effective evidence mass and data support remain unchanged;
5. adjacent final diagnostic distributions have non-zero total-variation distance.

This tests the declared specificity-discount mechanism, not which gamma is optimal.

## S2 — Temporal decay delta

Monthly values:

- 0.01
- 0.02
- 0.05

Runtime conversion:

`delta_day = delta_month / 30.44`

One quality-1 authorized synthetic record is placed in each of four categories at ages:

- ownership: 7 days
- evidence: 30 days
- tradeoff: 180 days
- reflection: 365 days

The parent distribution is uniform and the service route contains L0 only so the test isolates
recency-weighted local inference.

Pre-registered expectations:

1. every record's effective weight decreases as delta increases;
2. total effective evidence mass decreases monotonically;
3. data support decreases monotonically;
4. the recent/old weight ratio increases monotonically.

No optimal temporal decay is claimed.

## S3 — Prior concentration lambda_0

Values:

- 1
- 5
- 10
- 20
- 50

This is a lower-level posterior experiment using:

`alpha_0 = lambda_0 * pi_base + counts`

with a uniform `pi_base` and fixed synthetic counts that differ strongly from the prior.

Pre-registered expectations:

1. TV(posterior, prior) decreases monotonically with lambda_0;
2. TV(posterior, empirical distribution) increases monotonically with lambda_0.

This verifies prior-strength behavior only.

# Part B — Controlled ablations

The Monte Carlo master seed is `1729`. Unless otherwise stated, each stochastic condition uses
200 deterministic replicates and only the Python standard library.

## A2 — Remove industry prior

Synthetic hierarchy:

generic -> archetype -> industry -> company

The industry generating distribution is intentionally informative for the company truth.
Company sample sizes:

- 1
- 3
- 5
- 10
- 20

Full model:
generic -> archetype -> industry -> company

A2 ablation:
generic -> archetype -> company

Primary metric:
TV distance from the known synthetic company truth.

Pre-registered expectation:
mean TV error for the full model is lower than the no-industry ablation at every declared company
sample size.

Variance and top-category accuracy are reported descriptively.

## A3 — Remove compatibility mask

Four deterministic scenarios assign the highest raw probability mass to a category declared
invalid in that context.

Full model:
apply compatibility mask and renormalize.

A3 ablation:
release the unmasked distribution.

Pre-registered expectations:

- full invalid probability mass = 0 in every scenario;
- full invalid-top1 rate = 0;
- ablated invalid probability mass > 0 in every scenario;
- ablated invalid-top1 rate = 1 across the four constructed scenarios.

This verifies invalid-category suppression, not empirical correctness of any real compatibility
rule.

## A4 — Remove hierarchical partial pooling

Uses the same synthetic hierarchy and paired draws as A2.

Full model:
hierarchical company posterior.

A4 ablation:
company-local empirical distribution only.

Pre-registered expectation:
mean TV error for the full hierarchy is lower than the local-only estimator at every declared
company sample size.

Variance and top-category accuracy are reported descriptively.

## A6 — Remove temporal decay

Synthetic temporal drift:

- 60 older observations generated from `P_old`;
- 20 recent observations generated from `P_current`;
- old age = 1095 days;
- recent age = 7 days;
- full-model delta = 0.02/month;
- ablation delta = 0.

Both conditions use the same observations in each paired replicate.

Pre-registered expectations:

- mean TV error to `P_current` is lower with declared temporal decay;
- paired win rate of the decay model is greater than 0.5.

The conclusion is restricted to this declared synthetic drift process.

## Ablations not executed

A1 (similar-company retrieval) is not executed because retrieval relevance requires an external
corpus and relevance ground truth.

A5 (evidence lineage / explainability) is not executed as a human-explainability ablation because
human-perceived explanation quality requires external labels or human evaluation.

They remain part of the later empirical protocol rather than being converted into artificial
synthetic wins.

# Outputs

The runner emits:

- `exp2_results.json`
- `exp2_sensitivity.csv`
- `exp2_ablation_summary.csv`
- `exp2_ablation_replicates.csv`

The JSON contains the pre-registered pass/fail assertions and the exact synthetic truths.

# Determinism and reproducibility

The runner is executed twice on the same commit and all output SHA-256 hashes must match.

CI reruns Experiments 1A, 1B, and 2 and then requires:

`git diff --exit-code -- examples/paper/experiments`

so regenerated experiment outputs must be byte-identical to the committed artifacts.

# Research boundary

Experiment 2 uses synthetic data only. It does not rank candidates, recommend hiring/rejection,
infer protected traits, predict named-employer behavior, or demonstrate real-world interview or
employment efficacy.
