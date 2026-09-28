# System Design — Paper Research Core

## Architectural boundary

AIMS Lens Engine is an independently deployable, institution-agnostic reasoning service. JobACE is the first deep reference integration, not an architectural prerequisite.

```text
CLIENT / APPLICATION LAYER

JobACE     University     Career Service     Training Provider     Enterprise L&D
   \           |               |                    |                    /
    \__________|_______________|____________________|___________________/
                                |
                         Versioned Lens API
                                |
                                v
+-----------------------------------------------------------------------+
|                         AIMS LENS ENGINE CORE                         |
|                                                                       |
| Lens Registry      Evidence Lineage      Routing / Backoff            |
| Structured DNA     Compatibility Rules   Constrained DAG              |
| Hierarchical Inference / Borrowing       Uncertainty / Abstention     |
| Explanation / Provenance                 Audit Reconstruction         |
+-----------------------------------------------------------------------+
                                |
                 +--------------+---------------+
                 |                              |
                 v                              v
         Public research assets          Protected production assets
         schemas / validators            tenant configuration
         safe Lens examples              candidate records
         synthetic examples              private evidence
         reference implementation        credentials / deployment policy
```

## Research-core responsibilities

The paper research core owns:

- versioned Lens representation;
- evidence authorization and lineage;
- structured interview DNA;
- compatibility rules;
- constrained dependency assumptions;
- hierarchical borrowing and partial pooling;
- declared L0-L5 backoff;
- uncertainty and data-support summaries;
- abstention and broad-routing rules;
- explanation provenance;
- reproducible candidate-side practice decisions.

## Client responsibilities

Client systems such as JobACE own interaction and workflow concerns, for example:

- identity and account management;
- candidate-facing interview UI;
- coaching workflow;
- longitudinal practice history;
- progress tracking;
- institution-specific presentation and permissions.

Clients should call versioned Lens APIs instead of duplicating the Lens inference algorithm.

## Candidate-state boundary

Candidate-state features may personalize the candidate's next practice step when consent allows it. Candidate practice records must not automatically update company, industry, archetype, or public Lenses. Only deliberately authorized evidence pipelines may update those assets.

## Paper API surface

The frozen paper artifact exposes four conceptual operations:

1. `validate Lens` — verify schema, provenance, rights, maturity, and declared constraints;
2. `route` — choose the highest-specificity eligible practice Lens or fallback;
3. `follow-up priority` — select an ordered practice category under compatibility and uncertainty constraints;
4. `explain` — return provenance and a plain-language practice-only explanation.

## Explicitly out of scope

Employer-side candidate ranking, automated screening, rejection recommendations, hiring-decision APIs, and protected-trait inference are outside the paper research core. Historical experiments related to those functions may remain elsewhere in the repository but are excluded from `paper_artifact_manifest.yaml`.

## Open / protected split

### Public research artifact

- protocol and schemas;
- validators;
- candidate-side research API;
- reference inference implementation;
- synthetic examples and expected outputs;
- public-safe Lens templates/assets;
- governance rules and reproducibility tests.

### Protected production assets

- real candidate records or transcripts;
- tenant-specific configuration;
- private organizational evidence;
- production credentials and deployment configuration;
- proprietary production routing/calibration policies;
- JobACE private workflow data.
