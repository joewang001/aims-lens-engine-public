# Amazon Rubric

Status: v0.1 synthesis draft. Static validation completed; production use not approved.

This rubric explains how the Amazon public lens should adjust AIMS scoring. It is inferred from public sources and candidate voice summaries, not from an official Amazon hiring standard.

## Scoring Posture

Amazon weighting should be stricter than a generic AIMS lens on evidence quality. A strong answer needs concrete personal action, customer or business relevance, measurable result, and decision logic. Vague culture-fit language should not score well.

Current weights in `profile.json`:

| Dimension | Weight | Amazon interpretation |
|---|---:|---|
| Structured Thinking | 0.15 | Clear STAR/narrative structure, decision framing, assumptions, trade-offs, and risk boundaries. |
| Analytical Problem-Solving | 0.17 | Customer-backwards diagnosis, metric quality, technical depth, decision reversibility, and judgment under constraints. |
| Ownership & Execution | 0.24 | Personal ownership, initiative, follow-through, mechanism creation, and production/operational responsibility. |
| Impact & Results | 0.22 | Quantified customer, business, technical, or operational result, with trust and safety treated as part of impact. |
| Collaboration & Communication | 0.09 | Clear stakeholder communication, narrative reasoning, escalation, and ability to invite challenge. |
| Growth Mindset | 0.13 | Learning from failure, raising standards, iteration, and improved later behavior. |

## Dimension Rules

### Structured Thinking

High score:

- Uses situation, task/problem, action, result, and learning without sounding scripted.
- Names constraints, assumptions, alternatives, and trade-offs.
- Distinguishes reversible from hard-to-reverse decisions where relevant.
- For writing/narrative prompts, separates facts, assumptions, risks, and recommendation.

Low score:

- Tells a story with no sequence or decision logic.
- Uses Leadership Principle labels without evidence.
- Jumps to implementation before defining the customer or business problem.

Evidence: `AMZ-OFFICIAL-003`, `AMZ-HIRE-001`, `AMZ-HIRE-002`, `AMZ-CASE-001`, `AMZ-CASE-003`.

### Analytical Problem-Solving

High score:

- Starts with customer problem, root cause, metric definition, or technical constraint.
- Explains why an option was chosen and what alternatives were rejected.
- For technical roles, covers complexity, scale, failure modes, maintainability, and operational consequences.
- For BIE/data roles, validates metric definitions, data quality, segmentation, and decision usefulness.

Low score:

- Gives only a final answer, query, design, or opinion without reasoning.
- Uses metrics without defining them.
- Treats scale or ambiguity as an afterthought for senior roles.

Evidence: `AMZ-CASE-001`, `AMZ-CASE-002`, `AMZ-MED-002`, `AMZ-MED-003`, `AMZ-MED-004`.

### Ownership & Execution

High score:

- Clearly states "I did" actions, not only team activities.
- Shows initiative beyond assigned scope when appropriate.
- Creates a mechanism, process, dashboard, operational practice, or follow-through loop.
- For senior roles, owns post-launch outcomes, incidents, iteration, and quality.

Low score:

- Hides behind "we" when personal contribution is unclear.
- Describes effort without outcome.
- Escalates every ambiguity instead of exercising judgment.

Evidence: `AMZ-OFFICIAL-003`, `AMZ-HIRE-002`, `AMZ-CASE-002`, `AMZ-MED-004`.

### Impact & Results

High score:

- Quantifies result or gives a credible observable outcome.
- Connects result to customer, business, technical reliability, operations, or team standard.
- Includes negative side effects or risk trade-offs when relevant.
- Treats customer trust, worker safety, consent, and transparency as impact boundaries.

Low score:

- Claims success with no metric, customer signal, or decision result.
- Optimizes for growth or productivity while ignoring trust, safety, consent, or quality.
- Overstates impact from a small or unproven action.

Evidence: `AMZ-HIRE-001`, `AMZ-HIRE-002`, `AMZ-HIRE-003`, `AMZ-RISK-001`, `AMZ-RISK-002`.

### Collaboration & Communication

High score:

- Communicates decision logic clearly to stakeholders.
- Invites challenge and makes assumptions explicit.
- Explains how disagreement, escalation, or alignment was handled.
- For narrative prompts, shows concise written reasoning rather than persuasion alone.

Low score:

- Equates collaboration with consensus only.
- Avoids conflict or risk communication.
- Uses vague stakeholder language without actual communication choices.

Evidence: `AMZ-CASE-001`, `AMZ-CASE-003`, `AMZ-HIRE-003`, `AMZ-MED-002`.

### Growth Mindset

High score:

- Owns a failure or weak result with a specific diagnosis.
- Explains the mechanism or behavior changed afterward.
- Shows raising standards for self or team.
- Uses learning to improve later customer, business, or technical outcomes.

Low score:

- Gives a harmless fake failure.
- Blames others without personal correction.
- Says "I learned to communicate better" without proof of later changed behavior.

Evidence: `AMZ-HIRE-002`, `AMZ-MED-001`, `AMZ-MED-004`.

## Role Overlays

| Role family | Strong evidence to seek | Do not over-credit |
|---|---|---|
| All roles | STAR detail, personal ownership, customer/business impact, quantified result. | Generic LP keywords or memorized culture language. |
| SDE | Correct reasoning, trade-offs, maintainability, production impact, debugging and improvement. | Coding correctness without explanation, scale, or ownership. |
| Senior SDE | System design depth, failure modes, operational metrics, post-launch ownership, customer experience under load. | Architecture buzzwords without trade-offs or operating model. |
| BIE / Data | Metric definition, SQL/analysis reasoning, data validation, dashboard usefulness, stakeholder decision impact. | Query mechanics without business interpretation or metric trust. |
| Product / Program / Business | Working backwards, decision reversibility, narrative reasoning, customer and metric clarity. | Opinions or roadmap claims without customer proof and trade-offs. |
| Operations | Safe execution, process mechanisms, throughput/quality balance, escalation judgment. | Productivity stories that ignore safety, quality, or worker impact. |

## Risk Boundary Rules

- Do not reward "Bias for Action" if the answer ignores safety, consent, compliance, transparency, or customer trust.
- Do not reward "Customer Obsession" if the answer manipulates choice, hides trade-offs, or optimizes a metric while harming trust.
- Treat regulatory and legal sources as risk context. They should shape anti-pattern detection but should not be used to claim that any individual candidate must discuss those cases.
- For B2B screening outputs, phrase risk feedback as an interview evaluation concern, not as a legal conclusion.

## Follow-Up Generator Rules

For weak or incomplete answers, ask follow-ups in this order:

1. What was your exact personal role?
2. What customer, business, technical, or operational problem were you solving?
3. What data, constraint, or trade-off shaped your decision?
4. What did you do, and why that option?
5. What changed because of your action?
6. What risk or downside did you manage?
7. What did you learn or make durable afterward?

For technical and data roles, insert role probes before final scoring:

- SDE: complexity, failure modes, tests, trade-offs, maintainability, production impact.
- Senior SDE: scale, reliability, degradation, observability, ownership after launch.
- BIE: metric definition, data quality, SQL/analysis approach, stakeholder decision.
- Applied Science: problem formulation, model choice, experimental design, evaluation metric, error analysis, research-to-product impact.
- Data Center: safe troubleshooting, escalation threshold, root cause analysis, operational reliability, documentation, and shift handoff.

## Private Material Distillation Rule

Private materials can strengthen a lens only when converted into aggregate signals. Product-facing prompts and public repo files may include:

- role-level patterns
- confidence levels
- original generated questions
- evidence IDs such as `AMZ-PRIV-001`
- limitations and provenance notes

Product-facing prompts and public repo files must not include:

- copied Medium article bodies
- copied interview question lists
- private URLs unless explicitly approved
- author-specific personal details that are not needed for the lens

Private-material-derived evidence should remain lower confidence than official Amazon sources unless independently confirmed by public or official sources.

## Production Rule

This rubric can be used for internal v0.1 testing and validation-case generation. It should not be used for production candidate screening until:

- Medium URL/provenance review is completed or the Medium-derived signals remain clearly lower-confidence.
- At least one strong, average, weak, and no-evidence case is reviewed by a human.
- Same-answer cross-lens tests show Amazon-specific feedback differs from generic AIMS and from other company lenses.
- `validation_report.md` is marked approved.
