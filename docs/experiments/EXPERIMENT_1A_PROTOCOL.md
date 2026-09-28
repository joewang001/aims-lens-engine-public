# Experiment 1A — Core Synthetic End-to-End Verification

**Protocol version:** v0.1.1 reproducibility amendment


## Reproducibility amendment v0.1.1

A later repository-wide regeneration gate exposed cross-Python-version differences only in the
unrounded floating-point values stored in `exp1a_baseline_trace.json`. The Experiment 1A
pass/fail result file, all seven invariant outcomes, and the research-core behavior were stable.

Before freezing the combined experiment artifact, v0.1.1 canonicalizes floating-point values in
the explanatory baseline trace to 12 decimal places. This is a serialization-only change. The
input fixtures, invariant definitions, authorization test, abstention thresholds, routing logic,
and final result assertions are unchanged.

## Purpose

Experiment 1A verifies that the candidate-side paper core obeys its declared algorithmic
invariants under controlled synthetic inputs. It tests authorization, temporal recency,
hierarchical borrowing, compatibility masking, routing eligibility, data support, and abstention.

This experiment evaluates internal behavioral consistency. It does not establish ecological
validity, candidate learning benefit, employer behavior, hiring outcomes, or employment outcomes.

## Baseline

E1A-01 uses the existing paper example request as the baseline. The runner emits a complete
numeric trace containing:

1. authorized evidence records;
2. effective weighted counts;
3. effective evidence mass;
4. parent distribution;
5. local posterior;
6. compatibility-masked posterior;
7. routing provenance and normalized routing weights;
8. final diagnostic distribution;
9. normalized entropy;
10. data support;
11. final mode and priority order.

## Pre-registered cases

### E1A-01 — Supported baseline

Expected:
- ordered_practice_priority;
- data_support >= declared abstention threshold;
- all released categories belong to permitted_categories;
- routing provenance is non-empty.

### E1A-02 — Authorization hard gate

Start from E1A-01 and append 100 fresh, quality=1.0 `tradeoff` records with
`authorized=false`.

Expected:
- effective evidence mass exactly unchanged;
- weighted counts exactly unchanged;
- local posterior exactly unchanged;
- final result object exactly unchanged;
- total-variation distance from baseline = 0.

This verifies that strong-looking but unauthorized evidence contributes zero mass.

### E1A-03 — Temporal aging

Use the same authorized records and quality values as the baseline, but add 730 days to every
authorized record's age.

Expected:
- effective evidence mass decreases;
- data support decreases;
- no old record gains weight relative to its corresponding baseline record.

No claim is made about an optimal decay rate.

### E1A-04 — Zero local evidence

Remove all evidence.

Expected:
- weighted counts are all zero;
- effective evidence mass = 0;
- local posterior equals the normalized parent distribution;
- final mode = abstain;
- abstention reason = insufficient_data_support.

This verifies the no-local-data partial-pooling limit.

### E1A-05 — All categories masked

Set permitted_categories to an empty list while retaining otherwise valid baseline inputs.

Expected:
- final mode = abstain;
- reason = all_categories_masked.

### E1A-06 — No eligible route

Keep exactly one valid L0 declaration, but make every routing level unauthorized or
inapplicable.

Expected:
- final mode = abstain;
- reason = no_eligible_routing_level;
- no routed diagnostic distribution is released.

### E1A-07 — Low support

Retain a single authorized record with quality=0.10 and age=365 days while keeping the
baseline abstention threshold.

Expected:
- data_support < abstention_threshold;
- final mode = abstain;
- reason = insufficient_data_support.

## Metrics

For each case:
- effective evidence mass;
- data support;
- mode / abstention reason;
- top category when released;
- normalized entropy when released;
- diagnostic distribution;
- routing provenance;
- canonical SHA-256.

For invariant comparisons:
- exact equality flags;
- total-variation distance;
- monotonic support/effective-mass checks.

## Determinism

The runner is executed twice on the same commit. JSON and CSV output hashes must match exactly.

## Research boundary

The experiment uses synthetic data only and produces candidate-side practice priorities.
It does not rank candidates, recommend hiring/rejection, infer protected traits, or claim that
a named employer will behave according to the synthetic routing distributions.
