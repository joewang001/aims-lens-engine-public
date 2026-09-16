# AIMS Lens Engine

AIMS Lens Engine is an independently deployable, institution-agnostic **evidence-governed interview reasoning and practice-decision engine**. It is designed to select and explain interview-practice follow-up priorities under incomplete, heterogeneous, and differently authorized evidence.

**Paper-readiness artifact version:** `v0.9.1-paper-math-complete`

**Public repository:** https://github.com/joewang001/aims-lens-engine-public

## Relationship to JobACE

JobACE is the first deep reference integration of AIMS Lens Engine, not an architectural prerequisite. The Lens Engine owns versioned Lens representation, evidence lineage, routing/backoff, constrained dependency assumptions, hierarchical borrowing, compatibility constraints, uncertainty, abstention, and explanation provenance. A client such as JobACE may own candidate-facing interaction, coaching, learning history, and progress tracking.

Client systems should integrate through versioned APIs rather than copy the Lens inference algorithm.

## Paper research boundary

The manuscript-associated research core is **candidate-side interview practice**. It does not rank candidates for employers, recommend hiring/rejection decisions, infer protected characteristics, or claim to predict a named employer's real interview behavior.

A Lens is a **versioned, evidence-bounded hypothesis for practice**, not an official or complete description of an organization.

Read:

- `RESEARCH_BOUNDARY.md`
- `REPRODUCIBILITY.md`
- `PAPER_RELEASE_READINESS.md`
- `docs/MATH_TO_CODE_COMPLETENESS_AUDIT.md`
- `docs/PAPER_TO_CODE_MAP.md`
- `paper_artifact_manifest.yaml`

## Reviewer quick start

The paper reference implementation is dependency-free and uses synthetic data.

```bash
python tools/validate_paper_artifact.py
python -m unittest discover -s tests -v
python tools/run_paper_artifact_demo.py
```

The demo covers:

- evidence authorization as a hard gate;
- quality and recency weighting of eligible evidence;
- hierarchical Dirichlet-style partial pooling;
- compatibility masking;
- declared backoff and routing mixture;
- uncertainty and data-support summaries;
- provenance-aware ordered practice priorities;
- all fifteen Section 5 mathematical expressions through inspectable reference functions;
- calibration metrics, KL drift monitoring, and reference information-gain scoring.

It is a reference implementation, not empirical proof that the framework predicts employer behavior or improves employment outcomes.

## Research-core map

```text
api/                         candidate-side research API
architecture/                system boundary and routing specification
governance/                  evidence, privacy, fairness, authenticity, abstention
research_core/               paper reference inference implementation
schemas/                     research and supporting public schemas
examples/paper/              synthetic deterministic paper examples
tools/                       reproducibility and public-release tooling
tests/                       paper reference tests
company_lenses/              supporting public Lens assets; not employer ground truth
docs/                        wider project and public-Lens operations documentation
legacy/                      historical/non-paper capabilities explicitly outside research core
```

## Open / protected boundary

The public project may contain:

- protocol and schemas;
- validators;
- reference implementation;
- public-safe Lens assets;
- synthetic examples;
- public evidence standards and governance documentation.

It must not expose:

- JobACE user data;
- candidate records, resumes, or real transcripts;
- tenant-private configuration;
- confidential organization evidence;
- production credentials or databases;
- proprietary production policy/calibration state.

The existing `public_manifest.yaml` and `private_manifest.yaml` govern the broader public export. The narrower `paper_artifact_manifest.yaml` defines the frozen manuscript artifact.

## Broader repository history

Earlier development explored additional product and pilot workflows, including employer-side decision-support concepts. Those historical artifacts are **not part of the manuscript research core**. The paper-readiness branch preserves history but separates these semantics from the candidate-side API and frozen artifact manifest. See `legacy/employer_decision_support/README.md`.

## Public company Lens assets

Named company Lens folders are supporting public artifacts. Their presence does not mean AIMS claims official access to employer hiring criteria. Public inferred Lenses must expose provenance, limitations, review state, and the disclosure that they are practice hypotheses inferred from permitted evidence.

## Licenses

- Code, schemas, and tools: Apache-2.0
- Public Lens content and documentation: CC BY 4.0

See `LICENSE`, `NOTICE`, and `CONTENT_LICENSE.md`.

## Citation

See `CITATION.cff`. For a manuscript submission or archival release, cite a frozen tag or commit rather than a moving `main` branch.
