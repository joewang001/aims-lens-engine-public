# System Design

## High-Level Flow

```text
User or partner request
        |
        v
Target context parser
        |
        v
Lens router
        |
        +--> FULLY_DISTILLED
        +--> DERIVED_LENS
        +--> LIGHTWEIGHT_SCAN
        +--> GENERIC_AIMS
        |
        v
AIMS base evaluator
        |
        v
Lens overlay
        |
        v
Response generator
        |
        v
Score, feedback, rewrite, follow-up, screening recommendation, evidence, confidence
```

## Core Services

### Lens Router

Inputs:

- target company
- target role
- job description
- country or region
- industry
- requested use case
- tenant id

Output:

- selected lens id
- lens status
- confidence
- fallback explanation

Routing order:

1. Exact private enterprise lens.
2. Exact public company lens.
3. Derived lens from similar companies and industry archetypes.
4. Lightweight scan from supplied JD and public profile.
5. Generic AIMS.

### Distillation Orchestrator

Runs independent agents and stores their outputs.

Agent types:

- official culture
- executive thought
- hiring signal
- interview question
- employee voice
- decision case
- critic and risk

### Evidence Store

Stores:

- source URL or document reference
- source title
- source date
- source type
- extracted signal
- confidence
- related AIMS dimensions
- related company principles

### Evaluation Engine

Combines:

- AIMS base score
- company lens rubric
- role lens rubric
- evidence-aware explanation
- screening recommendation

### Runtime Decision Layer

The promoted v1.5 runtime core exposes a local, pre-routing decision layer for
practice prioritization. Its inputs are a declared category taxonomy, a parent
distribution, authorized evidence, compatibility-permitted categories, and
caller-supplied hyperparameters.

The local flow is:

    authorized evidence
            |
            v
    quality + recency weighting
            |
            v
    company-level hierarchical shrinkage
            |
            v
    compatibility mask
            |
            v
    permitted-category evidence support
            |
            +--> abstain
            |
            +--> ordered practice priority

The internal DecisionEnvelope reports the decision mode, abstention reason when
applicable, ordered priority, compatibility-masked diagnostic distribution, data
support, and effective permitted evidence mass.

This layer intentionally stops before cross-level routing mixtures, support-aware
backoff, divergence guards, JobACE adapter translation, provenance/explanation
assembly, or natural-language generation. It prioritizes practice; it is not a
prediction of a specific employer's interview process or hiring decision.

### Shadow Routing Policy

The next promotion stage evaluates a proposed support-aware backoff policy in
shadow mode only. It does not replace the local decision service or alter any
public API response.

For each L0-L5 candidate, the shadow policy requires:

- authorization and applicability;
- freshness and maturity eligibility;
- a compatibility-valid distribution;
- caller-supplied effective permitted evidence mass; and
- a caller-supplied support threshold.

The selector considers levels from most specific to least specific and chooses the
first level whose permitted distribution retains positive mass and whose data
support meets the declared threshold. If no level qualifies, it fails closed with
no selected backoff level.

The shadow Context Divergence Guard separately measures total-variation distance
between the local reference distribution and the selected shadow distribution.
Its threshold is caller-supplied and its enforcement mode is fixed to shadow:
triggering the observation does not block, replace, or otherwise change the live
decision.

This policy is a production proposal motivated by the regime-dependent routing
results in the v1.5 synthetic routing-shrinkage experiment. That experiment did
not establish an optimal fallback rule or validated production divergence
threshold, so no experiment fixture or mismatch value is embedded as a runtime
constant.

### Reference Adapter Layer

JobACE integration is represented in the public repository by a reference
adapter only. The existing external JobACE adapter contract remains unchanged.
Adapter v2 normalizes that contract into an institution-agnostic practice
context while preserving the accepted external identifiers and optional
context fields.

Candidate-side AIMS scores may be carried as an unbound signal packet using the
existing six public AIMS dimensions:

- structured_thinking
- analytical_problem_solving
- ownership_execution
- impact_results
- collaboration_communication
- growth_mindset

The reference adapter does not infer a mapping from those six dimensions to the
v1.5 follow-up taxonomy or to runtime evidence categories. It also does not
derive practice gaps, scoring calibration, routing weights, or screening
recommendations from the scores. Any such binding requires a separately
reviewed downstream policy.

The public reference layer performs no persistence, production prompt routing,
tenant configuration, private calibration, or live decision invocation.
Production JobACE mappings and proprietary scoring logic remain outside the
public core.

### Production Promotion Layer

The promoted runtime is gated through three internal artifacts:

1. a stable local DecisionEnvelope;
2. a public-safe provenance and explanation envelope; and
3. a fail-closed runtime switch with explicit promotion attestations.

The production-candidate envelope may expose only decision-level information:

- decision mode and abstention reason;
- ordered practice priority and diagnostic distribution from the local
  decision;
- data support and effective permitted evidence mass;
- runtime path (legacy, shadow, or promoted_local);
- shadow routing level, backoff distance, support, and total-variation
  divergence summary when a PR-C observation is present; and
- deterministic explanation text with the practice-not-prediction disclaimer.

The public provenance layer intentionally excludes operational audit records and
identifying or reconstructive fields, including audit IDs, timestamps, context
hashes, parent configuration, evidence packet IDs, tenant/user/conversation
identifiers, and raw routing distributions.

The runtime switch does not treat repository state as proof of production
readiness. A caller requesting promoted_local must explicitly attest that all
of the following gates are satisfied:

- runtime regression suite;
- public-safety scan;
- external contract compatibility;
- provenance review;
- private production controls;
- human-review calibration; and
- owner approval.

If any gate is absent or false, the requested promoted-local path fails closed
to shadow. legacy remains available as a non-promoted path.

Importantly, this switch promotes only the local decision path. The PR-C
support-aware backoff selector and Context Divergence Guard remain
enforcement_mode="shadow" even when the local decision path is promoted.
Turning either PR-C mechanism into live enforcement requires a separate
validation and review decision; PR-E does not make that scientific or product
claim.

### Enterprise Lens Manager

Handles:

- tenant ownership
- private lens permissions
- company-provided documents
- HR approval state
- versioning
- audit history

## Lens Status

`FULLY_DISTILLED`

Multi-agent research and validation complete.

`DERIVED_LENS`

Generated from anchor companies, industry archetypes, role requirements, region, and target JD.

`LIGHTWEIGHT_SCAN`

Generated from limited public or user-provided material. Must disclose lower confidence.

`GENERIC_AIMS`

No useful company-specific context available.

## Data Boundaries

Public inferred lenses and private enterprise lenses must remain separate.

Private enterprise materials cannot be used in public lenses or other tenants unless explicitly authorized.
