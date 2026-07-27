# Project Charter

## Project Name

AIMS Lens Engine Independent Platform Project

## Approval Scope

The approved scope is:

1. Build the system independently from JobACE in the early stage.
2. Store the project locally and on GitHub.
3. Support B2B API usage by partners.
4. Support enterprise self-service distillation of their own company lens.
5. Allow enterprises to use JobACE for first-round or second-round screening after integration.
6. Later connect the mature lens engine to JobACE AIMS for upgraded interview coaching and evaluation.

## Strategic Goal

Build a proprietary knowledge and evaluation infrastructure that turns company culture, hiring standards, public interview signals, and role expectations into structured, evidence-backed lenses.

The long-term product should serve:

- Job seekers preparing for target-company interviews.
- Enterprises screening candidates.
- Recruiting platforms and career-service partners using API access.
- Companies that want to create and govern their own private lens.

## Non-Goals For MVP

- Do not modify the existing JobACE production flow.
- Do not build a full enterprise portal before the lens quality is proven.
- Do not represent public inferred lenses as official company hiring standards.
- Do not use private enterprise data to improve public lenses without explicit authorization.

## Success Criteria

MVP success requires:

1. Amazon, Google, and McKinsey have complete draft lenses.
2. Each lens has archived multi-source evidence.
3. The same candidate answer receives clearly different feedback under each lens.
4. The API draft can evaluate, rewrite, generate follow-ups, and screen a candidate.
5. Every output includes lens status and confidence.
6. The system can fall back from direct lens to derived lens to lightweight scan.

## Decision Principle

AIMS remains the common scoring language. Company lenses provide context, weighting, rubric interpretation, question style, and evidence-backed hiring signals.
