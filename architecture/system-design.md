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
