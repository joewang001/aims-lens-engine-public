<!-- doc-parity: id=wiki-core; version=1.2; language=en; companion=AIMS_LENS_ENGINE_WIKI.zh-CN.md -->
# AIMS Lens Engine Wiki — Canonical Source

[English](AIMS_LENS_ENGINE_WIKI.md) | [中文](AIMS_LENS_ENGINE_WIKI.zh-CN.md)

This file is the repository source for the public Wiki. It is written for readers who want to understand the system before reading the manuscript or code.

## 1. What is AIMS Lens Engine?

AIMS Lens Engine is an evidence-governed reasoning layer for target-specific **candidate-side** interview practice.

Its job is not primarily to write interview questions. A general-purpose LLM can already do that.

Its harder job is to determine:

- which contextual assumptions are justified;
- which evidence is allowed to influence the decision;
- how sparse evidence should borrow from broader contexts;
- when a follow-up category is structurally incompatible;
- when specificity should be reduced;
- when the system should abstain;
- how the decision can be reconstructed later.

A Lens is a **versioned, evidence-bounded practice hypothesis**.

## 2. The problem it addresses

Targeted interview preparation creates a temptation to overclaim specificity.

If a system sees “Amazon,” “RBC,” or “McKinsey,” it can easily generate company-flavored questions. Fluent output can make the result feel authoritative even when the underlying evidence is thin.

AIMS Lens Engine treats that as a governance problem.

It asks whether the company-specific assumption is supported at all, and if not, routes toward broader industry/archetype/general practice context.

## 3. Core objects

### Lens

A Lens contains a bounded representation of:

- target context;
- follow-up categories;
- AIMS capability mappings;
- evidence references;
- constraints;
- uncertainty settings;
- maturity;
- limitations.

### Evidence packet

An evidence packet records not only “what the source said,” but whether it is authorized for the current purpose, how reliable/current it is, what scope it supports, and how it was transformed.

### Candidate state

Candidate-side data such as answer evidence or practice history is a different epistemic object from organization evidence. Candidate state must not silently rewrite a company Lens.

### Practice decision

The output is an ordered practice priority with support, uncertainty, routing provenance, and a disclaimer. It is not a hiring recommendation or employer-behavior probability.

## 4. AIMS capability model

The reference material uses six capability dimensions:

1. structured thinking;
2. analytical problem solving;
3. ownership and execution;
4. impact and results;
5. collaboration and communication;
6. growth mindset.

A Lens can change which dimensions deserve attention in a given context, but it should not manufacture candidate evidence that is not present in the candidate's real experience.

## 5. How evidence becomes a Lens

The distillation pipeline is:

```text
define scope
   ↓
collect independent evidence
   ↓
normalize and authorize evidence
   ↓
map supported signals to AIMS / follow-up taxonomy
   ↓
record uncertainty, contradictions, and limits
   ↓
validate Lens structure and maturity
   ↓
version and maintain
```

See `docs/aims-lens-distillation-strategy.md` for the full process.

## 6. Evidence governance

A simple conceptual rule is:

```text
effective contribution
= authorization gate
× quality
× recency
```

Authorization is binary eligibility, not “low confidence.” Unauthorized evidence contributes zero.

Quality and recency only affect evidence after it is eligible.

This prevents a strong-looking but impermissible source from being rescued by a high confidence score.

## 7. Hierarchical partial pooling

Company-specific evidence is often sparse. The reference model therefore borrows from broader levels.

```text
generic
  ↓
archetype
  ↓
industry
  ↓
company / target context
```

This is partial pooling: broader knowledge stabilizes sparse narrower estimates, while real narrower evidence can still move the result.

## 8. Compatibility masking

Not every follow-up category makes sense in every context.

Compatibility rules can remove categories that are structurally invalid for the declared stage or context before routing and prioritization.

The absence of a category after masking should not be interpreted as “the employer never asks this.” It means the current model contract does not permit that category in the present practice decision.

## 9. Routing and backoff

The reference routing sequence is:

| Level | Meaning |
| --- | --- |
| L0 | full eligible parent context |
| L1 | drop one parent/context component |
| L2 | drop two |
| L3 | industry context |
| L4 | role/company archetype |
| L5 | generic practice |

L0 is most specific. L5 is generic.

Routing combines eligible levels using authorization, applicability, coverage, and a distance discount. Sparse evidence therefore does not automatically receive maximum specificity.

## 10. Uncertainty, data support, and abstention

The engine exposes uncertainty rather than hiding it behind fluent text.

`data_support` summarizes effective evidence mass. It is not a probability of employer behavior or interview success.

`abstention` is triggered when the engine does not have enough justified support or no valid route/category remains.

A system that sometimes says “I do not have enough evidence to make this more specific” is behaving more honestly than one that always generates a confident company-specific answer.

## 11. Maturity

The research-facing maturity sequence is:

- `exploratory`
- `reviewed_practice`
- `evaluation_ready`
- `empirically_supported`

These states describe review/evidence status. `empirically_supported` must be earned through actual empirical evaluation for the declared use; it is not synonymous with “approved internally.”

## 12. Relationship to JobACE

JobACE is the first deep reference integration.

AIMS Lens Engine can decide and explain a practice priority. JobACE can turn that decision into a candidate learning loop:

```text
practice
  → receive evidence-linked feedback
  → revise
  → answer again
  → track improvement
```

The Lens Engine is therefore the reasoning/governance layer; JobACE is a reference client that can provide interaction, coaching, history, and progress tracking.

JobACE is not required for the Lens Engine architecture.

## 13. What the research core does not do

The manuscript research core does not:

- rank candidates for employers;
- recommend hire/reject;
- infer protected traits;
- claim confidential employer access;
- promise employment outcomes;
- assert that a company Lens is the organization's official rubric.

Broader historical concepts are documented separately and are not paper claims.

## 14. Reproducibility

A reviewer can run:

```bash
python tools/validate_paper_artifact.py
python -m unittest discover -s tests -v
python tools/run_paper_artifact_demo.py
```

The reference implementation is intentionally small and dependency-free.

It demonstrates executable correspondence to the mathematical specification; it does not substitute for empirical validation.

## 15. Public vs protected information

Public-safe material can include schemas, protocols, synthetic examples, public Lens assets, evidence standards, and reference code.

Protected material includes real candidate data, tenant-private configuration, confidential company evidence, production credentials, and proprietary production calibration state.

## 16. Frequently confused terms

**Priority vs probability**

A high practice priority does not mean a high probability that an employer will ask the question.

**Company Lens vs company truth**

A company Lens is an evidence-bounded hypothesis, not an official employer description.

**Support vs confidence**

Data support summarizes effective evidence mass; it should not be casually called “confidence” when no calibration supports that interpretation.

**Backoff vs failure**

Backoff is an intended behavior. It allows the system to remain useful while reducing unsupported specificity.

**Abstention vs missing feature**

Abstention is a governance feature that prevents fabricated certainty.

## 17. Where to go next

- `README.md` — project overview
- `RESEARCH_BOUNDARY.md` — manuscript scope
- `docs/aims-lens-distillation-strategy.md` — Lens construction
- `docs/PAPER_TO_CODE_MAP.md` — equation/code traceability
- `REPRODUCIBILITY.md` — reviewer execution path
- `docs/DOCUMENTATION_GOVERNANCE.md` — bilingual consistency
