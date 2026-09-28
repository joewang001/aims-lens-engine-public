# Lens Router — Research-Core Specification

## Purpose

The Lens Router selects the most specific **authorized, applicable, sufficiently supported** practice context. It prefers an honest broader fallback over unsupported company specificity.

A routing result is a practice-context decision, not a claim that a named employer will ask a particular question or make a particular hiring decision.

## Institution-agnostic inputs

- `tenant` — optional namespace for the integrating institution;
- `role_context` — role, level, interview stage, competency and region as available;
- `candidate_state_features` — short-lived, consented practice features when needed;
- `requested_lens_id` — optional explicit Lens;
- `use_case` — interview-practice operation only;
- evidence authorization, freshness, maturity and applicability metadata.

## Eligible paper use cases

- interview practice;
- practice-answer review;
- follow-up-priority selection;
- research simulation;
- career-service or training-program practice support.

Employer-side candidate ranking, screening, rejection, or hiring decisions are not paper-core use cases.

## Declared backoff sequence

The paper defines an auditable six-level backoff sequence:

| Level | Description | Backoff distance |
|---|---|---:|
| L0 | Full eligible parent context | 0 |
| L1 | Drop one declared parent | 1 |
| L2 | Drop two declared parents | 2 |
| L3 | Industry context | 3 |
| L4 | Role/company archetype context | 4 |
| L5 | Generic interview-practice context | 5 |

A named-company Lens may be considered only when its evidence is permitted, attributable, current enough for the declared policy, reviewed, and mature enough for the requested output.

## Routing weight

For an eligible level `ell`, the reference artifact uses an auditable routing weight of the form:

```text
raw_weight_ell = authorization_ell
                 × applicability_ell
                 × evidence_coverage_ell
                 × gamma^(backoff_distance_ell)
```

Weights are normalized across eligible levels. Authorization and applicability are gates; evidence coverage and backoff discount influence relative contribution.

## Output

A routing result should expose at least:

```json
{
  "selected_lens_type": "industry",
  "routing_level": "L3",
  "backoff_distance": 3,
  "evidence_maturity": "reviewed_practice",
  "explanation": "Company-specific evidence did not meet the release gate; industry context was used.",
  "disclaimer": "Routing selects a practice context and does not predict a specific employer's behavior."
}
```

## Candidate-state separation

Candidate-state features may affect the candidate's next exercise but must not silently become evidence about an employer. Candidate data and organizational Lens evidence are separate stores and separate update paths.

## Fail-closed rules

Route more broadly or abstain when:

- rights or authorization are absent;
- Lens freshness is outside policy;
- evidence maturity is insufficient;
- a required audit cannot reproduce the released result;
- compatibility rules leave no valid follow-up category;
- subgroup or fairness review triggers a hold;
- a calibration gate required by the requested output has failed.
