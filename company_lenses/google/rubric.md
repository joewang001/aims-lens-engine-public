# Google Rubric

Status: v0.1 synthesis draft. Static validation completed; production use not approved.

This rubric explains how the Google public lens should adjust AIMS scoring. It is inferred from public sources and project-owner-authorized private material distillation, not from an official Google hiring standard.

## Scoring Posture

Google weighting should emphasize structured problem solving, role-related depth, clear communication while reasoning, collaboration, humility, and responsible innovation. A technically correct answer is not enough if the candidate cannot explain assumptions, trade-offs, tests, user impact, and risks.

Current weights in `profile.json`:

| Dimension | Weight | Google interpretation |
|---|---:|---|
| Structured Thinking | 0.18 | Clarifies ambiguous prompts, decomposes problems, names assumptions, compares approaches, and tests edge cases. |
| Analytical Problem-Solving | 0.27 | Strong algorithmic, systems, data, AI/ML, or role-specific reasoning with explicit trade-offs. |
| Ownership & Execution | 0.13 | Moves from analysis to practical action, but with less ownership-heavy weighting than Amazon. |
| Impact & Results | 0.17 | Connects work to helpful, inclusive, safe, and measurable user/product outcomes. |
| Collaboration & Communication | 0.13 | Thinks aloud, handles disagreement, influences without authority, and explains complex ideas clearly. |
| Growth Mindset | 0.12 | Shows humility, learning, resilience, and adaptation under uncertainty. |

## Dimension Rules

### Structured Thinking

High score:

- Clarifies inputs, constraints, assumptions, and success criteria before solving.
- Explains alternative approaches and why one is chosen.
- Uses tests, edge cases, and failure modes to validate reasoning.

Low score:

- Jumps directly to code or solution.
- Gives a memorized pattern without explaining applicability.
- Ignores ambiguity or hidden constraints.

### Analytical Problem-Solving

High score:

- Solves from first principles or clearly maps a known pattern to the problem.
- Names complexity, scalability, data quality, reliability, or model evaluation trade-offs.
- Adapts reasoning by role: SWE, SRE, Data, UI, Android, AI/ML.

Low score:

- Produces a correct-looking answer with weak explanation.
- Cannot reason about complexity, tests, or failure modes.
- Overfits to one prep pattern.

### Ownership & Execution

High score:

- Turns analysis into a practical next step, experiment, mitigation, or implementation plan.
- Shows initiative without inflating personal scope.
- Handles process ambiguity constructively.

Low score:

- Stays abstract and never makes a decision.
- Blames process uncertainty instead of using available evidence to improve.

### Impact & Results

High score:

- Connects work to helpful user outcomes, product quality, reliability, accessibility, fairness, or responsible AI.
- Uses metrics carefully and names limitations.

Low score:

- Optimizes only an internal metric or offline model score.
- Ignores user trust, safety, privacy, fairness, or broad usefulness.

### Collaboration & Communication

High score:

- Thinks aloud and keeps the interviewer or stakeholder oriented.
- Handles disagreement with evidence and humility.
- Makes technical trade-offs understandable to non-identical audiences.

Low score:

- Treats collaboration as agreement.
- Cannot explain reasoning while solving.
- Uses personality polish instead of evidence.

### Growth Mindset

High score:

- Shows intellectual humility, changed thinking, recovery from mistakes, and learning loops.
- Uses limited feedback or ambiguous outcomes constructively.

Low score:

- Overstates certainty.
- Treats rejection or limited feedback only as external unfairness.

## Role Overlays

| Role family | Strong evidence to seek | Do not over-credit |
|---|---|---|
| SWE | Clarification, DSA reasoning, complexity, code quality, tests, edge cases, narration. | Silent coding or memorized solutions without explanation. |
| SRE | Reliability triage, debugging, automation, escalation judgment, user impact, post-incident learning. | Tool names without incident reasoning or communication. |
| Data / Analytics | Metric definition, segmentation, data quality, experiment logic, uncertainty communication. | Dashboard/query mechanics without product interpretation. |
| UI / Frontend | Accessibility, performance, user usefulness, collaboration with design/product. | Visual preference without measurable user or technical trade-off. |
| AI/ML | Evaluation design, error analysis, offline-online gaps, fairness/safety/privacy, monitoring. | Better offline metric with no deployment-risk reasoning. |
| All roles | Googleyness through collaboration, humility, ambiguity handling, and influence. | Generic claims of being "Googley" without evidence. |

## Private Material Distillation Rule

Private materials can strengthen a lens only when converted into aggregate signals. Public repo files may include role-level patterns, confidence levels, original generated questions, evidence IDs, and limitations. They must not include copied article bodies, copied interview question lists, private URLs, or unnecessary author-specific details.

## Production Rule

This rubric can be used for internal v0.1 testing and validation-case generation. It should not be used for production candidate screening until:

- private-material provenance is reviewed or kept lower-confidence;
- live transcript tests are run;
- same-answer cross-lens comparison against Amazon and later lenses is completed;
- human reviewer approves `profile.json`, `rubric.md`, and `validation_report.md`.
