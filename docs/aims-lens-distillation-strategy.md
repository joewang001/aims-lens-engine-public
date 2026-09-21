<!-- doc-parity: id=distillation-strategy; version=1.2; language=en; companion=aims-lens-distillation-strategy-zh.md -->
# AIMS Lens Engine — Evidence Distillation Strategy

[English](aims-lens-distillation-strategy.md) | [中文](aims-lens-distillation-strategy-zh.md)

> Distill only what the permitted evidence can support, and encode uncertainty where the evidence ends.

## 1. Purpose and boundary

Distillation converts heterogeneous evidence into a **versioned, evidence-bounded practice hypothesis** that the AIMS Lens Engine can inspect, validate, route, update, and explain.

The paper-facing use is **candidate-side interview practice**. Distillation is not a process for discovering an employer's secret hiring rubric. It does not turn public anecdotes into company truth, and it does not make a Lens authoritative merely because a company name appears in the file.

A distilled Lens should answer five questions:

1. **Scope:** what interview context is this Lens trying to represent?
2. **Evidence:** what material is authorized and attributable to support it?
3. **Interpretation:** which AIMS dimensions and follow-up categories are reasonably supported?
4. **Uncertainty:** where is the evidence sparse, contradictory, stale, or indirect?
5. **Behavior under uncertainty:** when must the system mix broader context, back off from L0 toward L5, or abstain?

## 2. Core epistemic rule

The object being distilled is not “how this organization truly judges candidates.”

The safer and more precise object is:

**the interview-practice patterns that can be reasonably hypothesized from permitted evidence, within a declared scope and maturity state.**

This distinction is essential. Official company material, job descriptions, public interviews, candidate reports, and third-party commentary have different evidential roles. They cannot be merged into one undifferentiated “company standard.”

## 3. Phase 0 — Define the target context

Before research begins, write an intake record covering:

- Lens type: company, role, industry, archetype, derived, or general practice;
- target organization if any;
- region;
- role family and level;
- interview stage;
- competency focus;
- candidate-side intended use;
- source cutoff date;
- whether any authorized private material exists;
- known limitations.

A request such as “build an Amazon Lens” is incomplete until scope is declared. A global corporate narrative, a Canadian SDE role, and an executive product interview are not interchangeable contexts.

### Default interpretation

If the input names a company but gives no additional scope, the public-safe default is:

- public evidence only;
- candidate-side practice;
- explicit limitations;
- no claim of official endorsement;
- no claim that a modeled pattern is the employer's current internal rubric.

## 4. Phase 0.5 — Create an auditable workspace

A company Lens workspace may use:

```text
company_lenses/<company>/
├── README.md
├── intake.md
├── collection_log.md
├── profile.json
├── evidence.json
├── evidence.md
├── rubric.md
├── question_bank.json
├── limits.md
├── validation_report.md
├── evidence_audit.md
└── research/
    ├── 01-official-culture.md
    ├── 02-executive-thought.md
    ├── 03-hiring-signals.md
    ├── 04-interview-questions.md
    ├── 05-employee-voice.md
    ├── 06-decision-cases.md
    └── 07-critic-risk.md
```

Not every public Lens currently has every file. The structure is a target contract for auditable distillation, not a claim that every existing asset is complete.

Private or tenant-scoped source bodies must not be copied into the public Lens directory.

## 5. Phase 1 — Independent evidence collection

A robust Lens should avoid allowing one source class to define the conclusion. The original multi-agent design uses seven independent evidence dimensions.

| Evidence dimension | Typical public sources | What it can support | What it cannot establish alone |
| --- | --- | --- | --- |
| Official culture | career pages, values, annual reports | declared principles and language | actual interviewer behavior |
| Executive thought | public letters, interviews, speeches | decision language and strategic emphasis | universal hiring criteria |
| Hiring signals | job postings, career guidance | role expectations and recurring capability language | hidden scoring weights |
| Interview experience | public candidate reports, videos, community posts | possible question/follow-up patterns | official or current process |
| Employee voice | interviews, community discussion | cultural tensions and lived experience hypotheses | verified organization-wide truth |
| Decision cases | public product/business decisions | observable trade-off patterns | causal explanation of hiring |
| Critic & risk | regulatory actions, criticism, failures | counter-evidence and anti-romanticization | direct interview policy |

### Source discipline

Every material signal should preserve:

- source URL or stable reference;
- source type;
- access/collection date;
- declared scope;
- transformation history;
- evidence quality;
- authorization/permitted use;
- expiry or refresh condition where applicable.

Contradictory evidence is preserved rather than silently averaged away.

## 6. Phase 2 — Evidence normalization and authorization

Raw materials become evidence packets before they influence inference.

The conceptual gate is:

```text
eligible evidence
= authorization
× quality
× recency
```

Authorization is not a confidence score. It is a hard gate. If evidence is not authorized for the intended use, it contributes zero effective mass regardless of how persuasive it appears.

For eligible evidence, quality and recency can weight contribution. Recency must use units consistent with the declared decay rate.

Community reports should normally carry narrower scope and lower evidential authority than direct official or authorized sources. Repetition can increase support for a pattern, but repetition does not magically convert a community report into an official company rule.

## 7. Phase 3 — Synthesis into AIMS and follow-up hypotheses

Evidence is synthesized into structures that the practice engine can use:

- AIMS dimension signals;
- follow-up taxonomy;
- stage/role compatibility constraints;
- supported anti-signals;
- known contradictions;
- explicit limits;
- uncertainty settings;
- evidence lineage.

The six AIMS capability dimensions are:

- structured thinking;
- analytical problem solving;
- ownership and execution;
- impact and results;
- collaboration and communication;
- growth mindset.

A company or role Lens may emphasize dimensions differently, but evidence should be traceable to why a dimension or follow-up category receives attention.

Synthesis should avoid “one company, one personality.” Large organizations contain business-unit, role, geography, interviewer, and time variation.

## 8. Phase 4 — Hierarchical inference and partial pooling

Sparse company-level evidence should not be treated as certain. The reference framework therefore supports hierarchical borrowing across broader contexts.

A simplified hierarchy is:

```text
generic practice
      ↓
archetype
      ↓
industry
      ↓
company / target context
```

The Dirichlet-style reference implementation uses the broader distribution as a prior center and adds eligible effective evidence at the narrower level.

This has two benefits:

1. a sparse company Lens does not collapse into arbitrary zero/one judgments;
2. broader patterns can inform practice while still allowing company-specific evidence to move the distribution when enough support exists.

The hierarchy is a transparent baseline, not a claim that Dirichlet-multinomial modeling is universally optimal.

## 9. Phase 5 — Compatibility, routing, backoff, and abstention

A high raw score is not enough. The category must also be structurally permitted.

Compatibility masking removes follow-up categories that are invalid for the current interview stage or declared context.

Routing then considers eligible levels:

| Level | Interpretation | Backoff distance |
| --- | --- | ---: |
| L0 | full eligible parent context | 0 |
| L1 | drop one parent/context component | 1 |
| L2 | drop two | 2 |
| L3 | industry context | 3 |
| L4 | role/company archetype | 4 |
| L5 | generic practice | 5 |

L0 is the most specific. L5 is the generic fallback.

Routing weight depends on authorization, applicability, evidence coverage, and a backoff discount. The exact output is a practice mixture, not an assertion that one level is “the employer truth.”

### Abstention

The engine should fail closed when:

- no compatible category remains;
- no eligible routing level remains;
- declared support falls below an abstention threshold;
- required evidence is unauthorized or expired;
- the requested specificity exceeds the Lens maturity.

Abstention is a useful output. It prevents fluent generation from manufacturing specificity.

## 10. Phase 6 — Maturity and validation

The research-facing maturity states are:

1. `exploratory`
2. `reviewed_practice`
3. `evaluation_ready`
4. `empirically_supported`

A maturity label describes what has been reviewed or validated. It must not be used as marketing shorthand for “accurate.”

Recommended validation layers include:

- schema validation;
- source/provenance review;
- authorization review;
- contradiction review;
- cross-Lens differentiation tests;
- strong/average/weak synthetic cases;
- no-evidence and low-support abstention cases;
- fairness review of masks and exclusions;
- calibration evaluation when labeled data are available;
- drift review over time.

`empirically_supported` should require actual empirical evidence for the declared use and population, not simply internal approval.

## 11. Phase 7 — Refresh and drift

A Lens is versioned because evidence changes.

Refresh can be triggered by:

- evidence expiry;
- major organizational change;
- substantial new official material;
- repeated new public interview reports;
- material KL drift or calibration degradation;
- reviewer-documented contradiction;
- schema/model version change.

Updates should preserve the previous version, evidence lineage, and change rationale.

## 12. Public and protected evidence

The public repository may demonstrate:

- schemas;
- evidence standards;
- public-safe Lens assets;
- synthetic examples;
- reference inference code;
- validation tooling.

It must not expose candidate data, real JobACE conversations, tenant-private evidence, confidential company documents, production credentials, or proprietary production calibration state.

Authorized private evidence may exist in a protected deployment, but it is outside the public paper artifact.

## 13. What distillation must never imply

A public company Lens must not imply:

- “this is the company's official rubric” without explicit authoritative evidence;
- “this company will ask this next” as a calibrated employer-behavior probability;
- “this candidate should be hired/rejected”;
- hidden access to confidential interview material;
- protected-trait inference;
- fabricated candidate experience;
- empirical effectiveness that has not been measured.

## 14. Relationship to broader product history

Earlier development explored employer-side and reviewer-assist concepts. Those concepts are preserved outside the manuscript research core for provenance.

They are not part of this canonical distillation strategy and are not evidence for the paper's candidate-side claims.

See:

- `docs/broader-product/README.md`
- `legacy/employer_decision_support/`
- `RESEARCH_BOUNDARY.md`

## 15. Operational checklist

Before marking a public practice Lens ready for use, confirm:

- scope is explicit;
- evidence sources are attributable;
- permitted use is known;
- unauthorized evidence contributes zero mass;
- source types are not silently conflated;
- contradictions are documented;
- AIMS/follow-up mappings are traceable;
- compatibility rules are reviewable;
- maturity is declared;
- limitations are visible;
- routing/backoff behavior is defined;
- low-support conditions can abstain;
- named-company language does not imply employer truth;
- the Lens can be reproduced from its public-safe evidence record or clearly states what protected evidence is unavailable.

This is the core distillation discipline: **specificity must be earned by evidence, not manufactured by language.**
