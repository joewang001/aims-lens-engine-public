# Distillation Playbook

## Purpose

This playbook defines how AIMS Lens Engine turns company evidence into a structured company lens.

The process is intentionally multi-agent and evidence-first. A company lens is not a general essay about company culture. It is an operational artifact used for evaluation, answer rewriting, question generation, and candidate screening.

## Lens Development Stages

### Stage 1: Intake

Required inputs:

- target company
- target region or global scope
- priority role families
- intended use case
- visibility: public, private, or hybrid
- source cutoff date

Output:

- company workspace
- agent assignments
- intake note

### Stage 2: Independent Research

Each agent works independently and writes only to its assigned file.

Required agents:

1. Official Culture Agent
2. Executive Thought Agent
3. Hiring Signal Agent
4. Interview Question Agent
5. Employee Voice Agent
6. Decision Case Agent
7. Critic and Risk Agent

Each agent must produce:

- source log
- extracted signals
- hiring implications
- anti-signals
- contradictions
- open questions

No agent may finalize company-level conclusions alone.

### Stage 3: Evidence Normalization

Research notes are converted into evidence records.

Normalization requirements:

- each evidence record has a stable id
- each signal maps to one or more AIMS dimensions
- each signal has confidence
- each source has source type and access date
- copyrighted interview material is summarized, not copied in bulk

### Stage 4: Synthesis

Synthesis combines agent outputs into:

- culture principles
- hiring signals
- anti-signals
- AIMS weighting
- interview patterns
- rewrite lens
- screening rubric
- honest limits

Synthesis must preserve disagreements and uncertainty.

### Stage 5: Validation

Validation must run before a lens can be marked `FULLY_DISTILLED`.

Required validation:

- source coverage check
- cross-source support check
- AIMS mapping check
- same-answer cross-lens test
- strong, average, weak answer test
- no-evidence uncertainty test
- privacy and copyright check

### Stage 6: Approval

Approval states:

- `draft`
- `ready_for_review`
- `approved_v1`
- `needs_revision`

Only approved lenses may be used for B2B screening.

## File Contract

Each company folder should use this structure:

```text
company_lenses/<company>/
  README.md
  intake.md
  profile.json
  rubric.md
  question_bank.json
  rewrite_rules.md
  evidence.md
  limits.md
  validation_report.md
  research/
    01-official-culture.md
    02-executive-thought.md
    03-hiring-signals.md
    04-interview-questions.md
    05-employee-voice.md
    06-decision-cases.md
    07-critic-risk.md
  validation_cases/
    strong-answer.md
    average-answer.md
    weak-answer.md
    no-evidence-test.md
```

## AIMS Mapping Rule

Every company signal must map to at least one of:

- `structured_thinking`
- `analytical_problem_solving`
- `ownership_execution`
- `impact_results`
- `collaboration_communication`
- `growth_mindset`

A company lens may weight these dimensions differently, but the scoring language must remain AIMS-compatible.

## Confidence Rule

Use these bands:

- `0.85-1.00`: strong evidence from official or repeated independent sources
- `0.65-0.84`: credible but not exhaustive support
- `0.40-0.64`: plausible pattern with limited support
- `0.00-0.39`: weak evidence, use only as a caveat

## Derived Lens Rule

If a company has no fully distilled lens, use:

1. exact industry archetype
2. region anchor
3. similar company lenses
4. role lens
5. job description

Always disclose:

- derived status
- reference lenses
- confidence
- limitations

## Public vs Private Boundary

Public lens:

- based on public sources
- can be used for job seeker preparation
- cannot claim official company endorsement

Private lens:

- based on company-provided materials
- tenant-scoped
- can be used for enterprise screening
- cannot leak into public library without written authorization
