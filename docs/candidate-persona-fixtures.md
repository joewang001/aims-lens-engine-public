# Candidate Persona Fixtures

## Purpose

Candidate persona fixtures make mock interview practice more realistic. Instead of testing only ideal candidates, they simulate candidates with uneven strengths:

- strong for McKinsey but weaker for Amazon ownership depth
- strong for Amazon operations but weaker for McKinsey case structure
- strong for Google analytics but weaker for client synthesis
- strong for Microsoft or Google product marketing but weaker for quantitative case work
- strong for Microsoft product marketing or program operations but weaker for technical PM loops
- strong for RBC operational risk or risk analytics but weaker for broad strategy, client advisory, or compliance-heavy roles

These fixtures help test whether AIMS scoring, company lens routing, B2C improvement plans, and final assessment UI react differently to different candidate profiles.

## Current Pack

```text
candidate_personas/mckinsey_case/
  README.md
  personas.json
  prompt_pack.md
candidate_personas/amazon_behavioral/
  README.md
  personas.json
  prompt_pack.md
candidate_personas/google_product_analytics/
  README.md
  personas.json
  prompt_pack.md
candidate_personas/microsoft_behavioral_product/
  README.md
  personas.json
  prompt_pack.md
candidate_personas/rbc_banking_risk/
  README.md
  personas.json
  prompt_pack.md
candidate_personas/cross_company_fit_matrix.json
candidate_personas/cross_company_fit_matrix.md
```

The first pack includes five synthetic McKinsey case interview candidates:

- strategy generalist
- operator owner
- quant researcher
- product storyteller
- raw high-potential early-career candidate

The Amazon behavioral pack reuses the same five underlying candidate profiles to test cross-company fit transfer under Amazon Leadership Principles.

The Google product and analytics pack reuses the same five profiles to test technical depth, product sense, analytics rigor, user focus, collaboration, and ambiguity handling.

The Microsoft behavioral and product pack reuses the same five profiles to test collaboration, growth mindset, customer-partner focus, enterprise product judgment, technical partnership, inclusive leadership, and product/program fit.

The RBC banking risk pack reuses the same five profiles to test risk and compliance judgment, client trust, process control, regulatory awareness, stakeholder escalation, analytical review, and banking communication.

The cross-company fit matrix provides the automated QA baseline for expected recommendation, score band, must-show evidence, and risk flags across all company packs.

## How To Use In Mock QA

1. Select a persona from `personas.json`.
2. Use `mock_prompt` as hidden candidate context.
3. Run a realistic mock interview.
4. Score the answer with AIMS.
5. Compare expected company fit and generated improvement plan.
6. Confirm final assessment displays persona-specific Priority Improvement Points.
7. Validate recommendation and risk calibration against `candidate_personas/cross_company_fit_matrix.json`.

## Expansion Order

Recommended next packs:

```text
candidate_personas/jpmorgan_finance_technology/
```

The same candidate can be reused across companies to test fit transfer. For example, the operator persona should score better in Amazon behavioral practice than in McKinsey strategy case practice.
