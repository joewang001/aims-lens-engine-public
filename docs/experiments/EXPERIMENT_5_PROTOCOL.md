# Experiment 5 — Hierarchy Approximation Benchmark

**Protocol version:** v0.1-corrective-prespecified
**Status:** pre-specified on the v1.4 corrective branch before committing result-bearing outputs

## Purpose

Experiment 5 quantifies the approximation introduced by the dependency-free recursive plug-in
hierarchical Dirichlet implementation used by the public reference artifact.

The current reference path propagates posterior means from one hierarchy level into the next.
That is a recursive plug-in approximation: it does not integrate over parent-level posterior
uncertainty when constructing the child posterior.

This experiment compares that implementation with a deterministic uncertainty-propagating
reference in a binary Beta hierarchy under synthetic data.

This is an internal approximation benchmark. It does not establish employer validity, candidate
learning benefit, population fairness, calibration on real participants, or employment outcomes.

## Model

The binary hierarchy is:

```text
psi   ~ Beta(kappa_a * pi,       kappa_a * (1-pi))
phi   ~ Beta(kappa_i * psi,      kappa_i * (1-psi))
theta ~ Beta(kappa_c * phi,      kappa_c * (1-phi))
```

with independent binomial observations at the archetype, industry, and company levels.

The declared constants are:

- base probability `pi = 0.5`;
- `kappa_a = 8`;
- `kappa_i = 8`;
- `kappa_c = 8`;
- 95% posterior interval.

The fixture file is:

```text
examples/paper/experiments/exp5/fixtures.json
```

## Compared estimators

### A. Recursive plug-in reference implementation

The public implementation recursively uses the posterior mean of each parent as the fixed prior
mean for the next level.

For the company-level interval, Experiment 5 treats the plug-in industry posterior mean as fixed
and forms the conditional Beta posterior:

```text
theta | phi_hat, D_company
```

This is therefore a **conditional interval given the plug-in parent distribution**.

### B. Uncertainty-propagating hierarchical reference

For the same declared binary hierarchy, the benchmark numerically integrates over the joint
posterior of `psi` and `phi`.

The company observations contribute to upper-level posterior weights through the exact
Beta-binomial marginal likelihood obtained by integrating out `theta`. Conditional on each `phi`,
the company posterior for `theta` is Beta and is mixed over the integrated posterior of `phi`.

The reference therefore propagates uncertainty across hierarchy levels for this declared binary
model. It is a numerical reference for the synthetic benchmark, not a claim that the production
system implements a full general-purpose hierarchical Bayesian engine.

## Deterministic numerical integration

The reference uses midpoint quadrature on `(0,1)` for both `psi` and `phi`.

Primary grid:

- 240 midpoint nodes per dimension.

Convergence grid:

- 480 midpoint nodes per dimension.

The 480-grid calculation is not reported as a competing estimator. It is used only to verify that
the 240-grid result is numerically stable.

Posterior interval endpoints are computed from the mixture CDF using deterministic bisection and a
dependency-free regularized incomplete-beta implementation.

No random sampling, external package, network access, or API call is used.

## Synthetic regimes

Three fixed count regimes are declared before result-bearing outputs are committed.

Counts are represented as `[success, failure]`.

### Sparse

- archetype: `[1, 0]`
- industry: `[1, 0]`
- company: `[1, 0]`

### Intermediate

- archetype: `[6, 4]`
- industry: `[5, 3]`
- company: `[4, 2]`

### Dense

- archetype: `[30, 20]`
- industry: `[25, 15]`
- company: `[20, 10]`

These regimes are illustrative synthetic conditions, not estimates of real interview evidence
volumes.

## Reported quantities

For each regime, report:

- plug-in posterior mean;
- plug-in 95% interval;
- uncertainty-propagating reference posterior mean;
- reference 95% interval;
- absolute posterior-mean difference;
- plug-in interval width;
- reference interval width;
- reference-to-plug-in interval-width ratio;
- 240-vs-480 grid convergence deltas for mean, lower endpoint, and upper endpoint.

## Acceptance criteria

Experiment 5 passes only if the numerical reference converges.

Declared tolerances:

- absolute posterior-mean difference between 240- and 480-grid references: `<= 5e-5`;
- absolute lower-endpoint difference: `<= 5e-5`;
- absolute upper-endpoint difference: `<= 5e-5`.

No pass/fail criterion requires either estimator to have a larger interval, a smaller error, or a
specific directional relationship across sparse, intermediate, and dense regimes. Those
differences are descriptive outputs.

This prevents the experiment from turning a methodological comparison into a constructed
"winner" claim.

## Reproducibility contract

Reported floating-point values are canonicalized to 12 decimal places.

The runner writes:

```text
examples/paper/experiments/exp5/results/exp5_results.json
examples/paper/experiments/exp5/results/exp5_case_matrix.csv
```

After the protocol, fixtures, and runner are committed, the result-bearing run is executed and the
two generated outputs are committed separately. Subsequent CI must regenerate the files
byte-for-byte and require a zero diff across the experiment directory.

This repository commit sequence is a pre-specification record for the corrective workflow; it is
not an externally registered clinical or statistical preregistration.

## Claim boundary

Experiment 5 may support statements about:

- the semantics of the recursive plug-in approximation;
- the magnitude of approximation differences under the declared synthetic regimes;
- the numerical stability of the uncertainty-propagating reference.

It must not be used to claim:

- real-employer validity;
- real-world calibration;
- fairness across populations;
- candidate interview improvement;
- employment-outcome improvement;
- optimal hierarchy depth or concentration parameters.
