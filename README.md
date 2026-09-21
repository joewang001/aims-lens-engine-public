<!-- doc-parity: id=readme-overview; version=1.2; language=en; companion=README.zh-CN.md -->
# AIMS Lens Engine

[English](README.md) | [中文](README.zh-CN.md)

AIMS Lens Engine is an independently deployable, institution-agnostic **evidence-governed interview reasoning and practice-decision engine**. It turns heterogeneous, differently authorized evidence into versioned practice hypotheses, then uses explicit uncertainty, routing, backoff, and abstention rules to decide what interview-practice follow-up deserves attention next.

**Freeze-metadata artifact:** `0.10.0-paper-v1.4`

**Aligned manuscript:** `v1.4`

**Corrective experimental baseline:** `c18899b469e1d579391306872d5834ebf6e3caf3`

**Immutable archival ref:** `v0.10.0-paper-v1.4`

**Release status:** `frozen`

**Tag creation gate:** the immutable tag is created only after this exact freeze-metadata commit passes remote Paper Artifact CI.

**Release date:** `2026-09-21`

**Previous frozen paper artifact:** `v0.9.2-paper-v1.3` at `f7fcb6a3129cb58fe20c414f1abe519376def8e1`

**Public repository:** https://github.com/joewang001/aims-lens-engine-public

> A Lens is a **versioned, evidence-bounded hypothesis for practice**. It is not an employer's official hiring rubric, not privileged knowledge of a company's interview process, and not a hiring-outcome prediction.

## Understand AIMS Lens Engine in five minutes

### Why this exists

Generic LLMs can generate plausible interview questions, follow-ups, and polished coaching from a résumé and job description. Question-bank sites can provide company-labelled examples. Both are useful, but neither automatically answers a harder governance question:

**What evidence justifies using a company-, role-, or industry-specific assumption, how strong is that evidence, and when should the system stop pretending that it knows more than it does?**

AIMS Lens Engine makes those questions explicit. It separates:

- **evidence eligibility** from evidence strength;
- **practice hypotheses** from employer ground truth;
- **candidate state** from organization evidence;
- **specificity** from unsupported confidence;
- **probabilistic priority** from language-generation fluency.

When the evidence does not support a specific Lens, the engine backs off from L0 toward L5 or abstains.

## A simple mental model

```text
Public / authorized evidence
        │
        ▼
 Evidence packets
 authorization • provenance • quality • recency
        │
        ▼
 Versioned Lens hypothesis
 company • role • industry • archetype • general
        │
        ▼
 Evidence-governed inference
 partial pooling • compatibility mask • uncertainty
        │
        ▼
 Routing / backoff
 L0 ──► L1 ──► L2 ──► L3 ──► L4 ──► L5
        │
        ▼
 Candidate-side practice decision
 ordered follow-up priority • support • explanation • abstention
```

The final output is a **practice priority**, not a probability that a named employer will ask a question or hire a candidate.

## What a Lens contains

A Lens is a machine-readable, reviewable representation of a bounded interview context. Depending on scope, it can describe:

- the target role, level, interview stage, and competency context;
- a follow-up taxonomy linked to AIMS dimensions;
- evidence packets with source, authorization, quality, recency, and provenance;
- constraints and compatibility rules;
- uncertainty settings and routing/backoff behavior;
- maturity and review state;
- explicit limitations and anti-claims.

Named-company Lens assets are therefore best read as **contestable practice hypotheses inferred from permitted evidence**.

## How a Lens is built

The canonical distillation process is documented in:

- [Distillation Strategy — English](docs/aims-lens-distillation-strategy.md)
- [蒸馏策略 — 中文](docs/aims-lens-distillation-strategy-zh.md)

At a high level:

1. **Define the practice context.** Identify target company/role/industry, region, level, interview stage, and intended candidate-side practice use.
2. **Collect evidence independently.** Separate official material, hiring signals, executive language, community experience, decision cases, and critic/risk evidence.
3. **Normalize evidence.** Convert material into evidence packets with authorization, provenance, quality, recency, scope, and expiry.
4. **Synthesize a Lens.** Map supported signals to the AIMS capability model and a follow-up taxonomy without promoting community anecdotes into employer truth.
5. **Apply probabilistic inference.** Use recursive plug-in hierarchical Dirichlet shrinkage, compatibility masking, and explicit uncertainty.
6. **Route honestly.** Use the declared L0–L5 backoff sequence; unsupported specificity is discounted, backed off, or rejected through abstention.
7. **Validate and maintain.** Track maturity, drift, contradictory evidence, expiry, and review history.

## Core concepts

| Concept | Meaning |
| --- | --- |
| **Lens** | A versioned, evidence-bounded practice hypothesis. |
| **Evidence authorization** | A hard eligibility gate. Unauthorized evidence contributes zero mass. |
| **Evidence quality** | A weight applied only after authorization. |
| **Recency** | Time decay applied in units consistent with the declared decay rate. |
| **Compatibility mask** | Removes categories that are structurally impermissible in the current context. |
| **Partial pooling** | Shares statistical strength across generic → archetype → industry → company levels without treating sparse cells as certain. |
| **Routing / backoff** | Combines eligible context levels and discounts weaker specificity by backoff distance. |
| **L0–L5** | L0 is the most specific eligible context; L5 is generic practice context. |
| **Data support** | A bounded summary of effective evidence mass; it is not an employer-behavior probability. |
| **Abstention** | A fail-closed outcome when support, compatibility, authorization, or routing is inadequate. |
| **Maturity** | `exploratory` → `reviewed_practice` → `evaluation_ready` → `empirically_supported`. |

## Research model

The public reference implementation exposes the manuscript's core mathematical path:

- constrained probabilistic DAG specification;
- logistic stopping model;
- compatibility masking;
- recursive plug-in hierarchical Dirichlet shrinkage;
- authorization × quality × recency effective evidence;
- posterior means and conditional Dirichlet intervals given the plug-in parent distribution;
- six-level routing and backoff mixture;
- normalized entropy and data support;
- Brier score, top-label ECE, and log loss helpers;
- KL drift;
- reference information-gain scoring.

See:

- [`docs/PAPER_TO_CODE_MAP.md`](docs/PAPER_TO_CODE_MAP.md)
- [`docs/MATH_TO_CODE_COMPLETENESS_AUDIT.md`](docs/MATH_TO_CODE_COMPLETENESS_AUDIT.md)

The executable reference functions show that the mathematical specification is implementable and inspectable. They do **not** by themselves establish empirical validity, employer-behavior prediction, or employment-outcome improvement.

## Example: candidate-side use

Suppose a candidate is preparing for a senior product role at a named company.

The client may provide a job description, résumé, interview stage, and the candidate's previous answer. A Lens may contribute eligible company/role/industry context derived from public or otherwise authorized evidence.

The engine then asks:

- Which evidence is authorized for this use?
- Which signals are compatible with this stage and competency?
- How much effective evidence supports the more specific context?
- Should the system use L0, mix with broader levels, back off, or abstain?
- Which follow-up category deserves the highest **practice priority**?
- What evidence and routing path justify that decision?

A language model can then phrase a natural question or explanation, but the LLM is downstream of the governance and inference decision.

## How this differs from a generic LLM or question bank

| Generic approach | AIMS Lens Engine |
| --- | --- |
| Generates plausible questions from prompt context | Requires an explicit evidence and routing basis for target-specific practice |
| Often blends source types implicitly | Separates authorization, quality, recency, provenance, and scope |
| May sound equally confident under sparse evidence | Backs off or abstains when specificity is unsupported |
| Usually treats context as prompt text | Represents context as versioned Lens data with maturity and limits |
| Feedback can be difficult to audit | Exposes decision provenance and evidence references |
| Company-labelled questions may imply specificity | Named-company Lenses must disclose that they are evidence-bounded hypotheses |

This does not make AIMS Lens Engine a universal replacement for general-purpose AI. It defines a narrower, inspectable reasoning and governance layer that a client system can use when target-specific interview practice requires evidence discipline.

## Relationship to JobACE

JobACE is the first deep reference integration of AIMS Lens Engine, **not an architectural prerequisite**.

AIMS Lens Engine owns the research-facing reasoning layer:

- Lens representation and validation;
- evidence lineage and authorization;
- routing/backoff;
- probabilistic inference;
- compatibility constraints;
- uncertainty and abstention;
- explanation and audit provenance.

A client such as JobACE may own:

- candidate-facing interaction;
- voice and text practice flows;
- coaching;
- practice history;
- progress tracking;
- institution-facing delivery.

The client should integrate through versioned APIs rather than copy the inference algorithm.

## Research boundary

The manuscript-associated research core is **candidate-side interview practice**.

It does not:

- rank candidates for employers;
- recommend hiring or rejection decisions;
- infer protected characteristics;
- claim access to confidential employer rubrics;
- claim that a named company necessarily follows a modeled pattern;
- promise interview or hiring success;
- treat a practice priority as an employer-behavior probability.

Historical or exploratory employer-side concepts remain outside the manuscript research core. See [Broader Product and Historical Extensions](docs/broader-product/README.md).

## Reviewer quick start

The paper reference implementation is dependency-free and uses synthetic data.

```bash
python tools/validate_paper_artifact.py
python -m unittest discover -s tests -v
python tools/run_paper_artifact_demo.py
python tools/run_exp1a_core_verification.py
python tools/run_exp1b_lens_differentiation.py
python tools/run_exp2_sensitivity_ablation.py
python tools/run_exp3_semantic_regression.py
python tools/run_exp4_adversarial_alignment.py
python tools/run_exp5_hierarchy_approximation.py
```

Manuscript v1.4 retains Experiments 1A/1B/2/3 and adds Experiment 4 as internal mathematical–implementation correction evidence plus Experiment 5 as a synthetic approximation benchmark. These results verify declared mechanism behavior, corrective alignment, approximation behavior, and reproducibility under controlled inputs; they do not establish real-employer validity, population fairness, current production-LLM accuracy, interview improvement, or employment-outcome efficacy.

Documentation alignment can be checked separately:

```bash
python tools/validate_documentation_alignment.py
```

## Repository map

```text
api/                         candidate-side research API
architecture/                system boundary and routing specification
governance/                  evidence, privacy, fairness, authenticity, abstention
research_core/               paper reference implementation
schemas/                     research and supporting public schemas
examples/paper/              synthetic deterministic paper examples
company_lenses/              supporting public Lens assets
docs/                        research, operations, bilingual documentation
docs/wiki/                   canonical source for bilingual Wiki content
docs/broader-product/        explicitly non-paper product/history boundary
legacy/                      historical/non-paper capabilities
tools/                       validators, demo, public-release tooling
tests/                       reference tests
```

## Documentation

Start with the [Documentation Hub](docs/README.md).

Key documents:

- [Research Boundary](RESEARCH_BOUNDARY.md)
- [Reproducibility Guide](REPRODUCIBILITY.md)
- [Paper Release Readiness](PAPER_RELEASE_READINESS.md)
- [Distillation Strategy](docs/aims-lens-distillation-strategy.md)
- [Documentation Governance](docs/DOCUMENTATION_GOVERNANCE.md)
- [Wiki Source — English](docs/wiki/AIMS_LENS_ENGINE_WIKI.md)
- [Wiki Source — 中文](docs/wiki/AIMS_LENS_ENGINE_WIKI.zh-CN.md)

English is the canonical public research language. Chinese companion documents maintain **semantic parity**, not literal sentence-by-sentence translation.

## Open / protected boundary

The public project may contain protocols, schemas, validators, reference code, synthetic examples, public-safe Lens assets, and public governance documentation.

It must not expose JobACE user data, candidate records, real transcripts, tenant-private configuration, confidential organization evidence, production credentials/databases, or proprietary production policy/calibration state.

The broader public export is governed by `public_manifest.yaml` and `private_manifest.yaml`. The narrower manuscript artifact is governed by `paper_artifact_manifest.yaml`.

## Public company Lens assets

Company Lens folders are supporting public artifacts, not employer ground truth. Public inferred Lenses should expose provenance, limitations, review state, and evidence maturity. Community sources can inform a practice hypothesis but cannot be silently upgraded into official employer criteria.

## Contributions

Contributions are welcome when they improve the public core without importing private data or copyrighted source bodies. See `CONTRIBUTING.md`.

For bilingual documentation, changes to normative meaning should update the English canonical document and its Chinese companion in the same pull request.

## Licenses

- Code, schemas, and tools: Apache-2.0
- Public Lens content and documentation: CC BY 4.0

See `LICENSE`, `NOTICE`, and `CONTENT_LICENSE.md`.

## Citation

See `CITATION.cff`. For manuscript submission or archival use, cite a frozen tag or commit rather than a moving branch.
