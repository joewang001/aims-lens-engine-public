# Experiment 4 — Adversarial Mathematical Alignment

**Protocol version:** v0.1-corrective-prespecified
**Status:** pre-specified on the v1.4 corrective branch before committing result-bearing outputs

## Purpose

Experiment 4 converts corrective findings F1–F4 into deterministic adversarial regression
fixtures. Each case records both:

- the behavior of the frozen v1.3 semantics; and
- the corrected v1.4 behavior.

The historical v1.3 artifact remains immutable. The experiment does not rewrite that release.
Instead, the runner contains small `legacy_*` reference helpers that mirror the relevant frozen
v1.3 logic for the four identified counterexamples.

Historical frozen reference:

```text
tag:    v0.9.2-paper-v1.3
commit: f7fcb6a3129cb58fe20c414f1abe519376def8e1
```

This experiment tests internal mathematical–implementation alignment only. It does not establish
real-employer validity, population fairness, external calibration, candidate learning effects,
or employment outcomes.

## Case E4-01 — Eq. 15 parameter-information-gain counterexample

Input:

```text
Dirichlet alpha = (1, 1)
```

Frozen v1.3 behavior:

- the function exposed as Eq. 15 computed one-step posterior-predictive category-entropy
  reduction;
- expected value: approximately `0.0566330122651325`.

Corrected v1.4 behavior:

- Eq. 15 computes parameter-posterior information gain
  `I(Theta; Y)`;
- expected value:
  `ln(2) - 1/2 = 0.1931471805599453`.

Acceptance criteria:

1. corrected value matches `ln(2)-1/2` within the declared tolerance;
2. legacy predictive reduction matches its declared value within tolerance;
3. the two quantities are materially distinct.

## Case E4-02 — High-confidence calibration cancellation

Input:

```text
prediction 1 = [0.9, 0.1], outcome = class 1
prediction 2 = [0.1, 0.9], outcome = class 0
```

Both predictions are wrong with top-label confidence 0.9.

Frozen v1.3 behavior:

- vector-bin ECE averages the two prediction vectors and the two one-hot outcome vectors;
- opposing class errors cancel;
- vector ECE = 0.

Corrected v1.4 behavior:

- manuscript-facing top-label ECE compares confidence with empirical top-label accuracy;
- bin confidence = 0.9;
- bin accuracy = 0;
- top-label ECE = 0.9.

Complementary Brier score and multiclass log loss are also recorded and must both be positive.

Acceptance criteria:

1. the legacy vector diagnostic reproduces the cancellation counterexample;
2. corrected top-label ECE is `0.9` within tolerance;
3. Brier score > 0;
4. log loss > 0.

## Case E4-03 — Compatibility-masked evidence support inflation

The existing deterministic paper request is used as the structural baseline. `collaboration` is
present in the category universe but absent from `permitted_categories`.

### Below-threshold attack

Replace evidence with one fresh quality-1 authorized `ownership` record, then append 100 fresh
quality-1 authorized `collaboration` records.

Use:

```text
abstention threshold = 0.20
support tau = existing paper value
```

Frozen v1.3 behavior:

- all-category effective evidence mass enters the support score;
- masked `collaboration` records inflate support;
- the request crosses the release threshold.

Corrected v1.4 behavior:

- support mass is summed only over permitted categories;
- masked-only records do not increase released support;
- the request remains below threshold and abstains.

### Above-threshold invariance

Start from the supported paper baseline and append 50 fresh quality-1 authorized
`collaboration` records.

Corrected v1.4 behavior must leave:

- permitted effective evidence mass unchanged;
- released data support unchanged;
- released diagnostic distribution unchanged;
- priority order unchanged.

Acceptance criteria:

1. the below-threshold legacy mirror releases while current v1.4 abstains for insufficient support;
2. masked-only evidence changes legacy support but not corrected permitted support;
3. the above-threshold corrected output is invariant to the masked-evidence flood.

## Case E4-04 — Zero-permitted-mass routing

### Mixed supported + unsupported components

Use permitted category `a`.

- L0 has distribution `{a: 1, b: 0}`;
- L5 has distribution `{a: 0, b: 1}`.

Frozen v1.3 behavior:

- L5 is normalized over the permitted set;
- zero permitted mass is converted to the uniform distribution over `{a}`;
- L5 receives non-zero routing weight.

Corrected v1.4 behavior:

- L5 is excluded because it retains no positive permitted mass;
- only L0 remains in routing provenance.

### All supported mass removed

A service-level fixture retains a declared L0 with zero coverage and supplies only broader
authorized/applicable routing distributions whose mass lies on a masked category.

Frozen v1.3 behavior:

- zero-permitted-mass broader levels become uniform;
- the runtime can release a practice priority.

Corrected v1.4 behavior:

- all such components are excluded;
- the runtime abstains with `reason = no_supported_routing_mass`.

Acceptance criteria:

1. a zero-permitted-mass component never receives current routing weight;
2. the mixed current route has one provenance component while the legacy mirror has two;
3. the all-massless current service abstains with `no_supported_routing_mass`;
4. the frozen v1.3 mirror reproduces the legacy release behavior.

## Numerical tolerance

Unless an assertion is exact by structure, the declared absolute tolerance is:

```text
1e-12
```

Reported floating-point values are canonicalized to 12 decimal places.

## Outputs

The runner writes:

```text
examples/paper/experiments/exp4/results/exp4_results.json
examples/paper/experiments/exp4/results/exp4_case_matrix.csv
```

The JSON contains full structured observations for all four cases. The CSV contains one summary
row per corrective finding.

## Reproducibility

The experiment is deterministic and dependency-free.

After protocol, fixtures, and runner are committed, the result-bearing run is executed and the
generated outputs are committed separately. Later CI must rerun Experiment 4 and require a zero
diff across committed experiment outputs.

This commit sequence is a repository pre-specification record for a corrective software/research
workflow. It is not an externally registered clinical or statistical preregistration.

## Claim boundary

Experiment 4 may support statements that the four identified v1.3 adversarial cases are
reproduced and that the v1.4 reference code satisfies the declared corrective invariants.

It must not be used to claim:

- named-employer behavioral validity;
- real-participant calibration;
- fairness across demographic groups;
- interview-performance improvement;
- employment-outcome improvement.
