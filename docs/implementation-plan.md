# Implementation Plan

## Phase 1: Foundation

Estimated duration: 2 weeks.

Deliverables:

- Company Lens schema
- Agent research templates
- Evidence standard
- Lens status model
- API draft
- Validation checklist
- Initial repository structure

Engineering approach:

- Use file-based lens artifacts first.
- Keep artifacts human-readable.
- Require source links, source dates, source type, confidence, and extracted signals.
- Avoid database migrations until the workflow stabilizes.

## Phase 2: MVP Distillation

Estimated duration: 4 to 6 weeks.

Companies:

- Amazon
- Google
- McKinsey

For each company:

- Run independent multi-agent research.
- Archive all research notes.
- Build `profile.json`.
- Build `rubric.md`.
- Build `question_bank.json`.
- Build `rewrite_rules.md`.
- Build `evidence.md`.
- Build `limits.md`.
- Build `validation_report.md`.

Validation tests:

- Same answer across three lenses.
- Strong, medium, and weak answer tests.
- No-evidence uncertainty test.
- AIMS weighting and explanation test.

## Phase 3: Standalone API Prototype

Estimated duration: 3 to 4 weeks.

Endpoints:

- `POST /v1/evaluate-answer`
- `POST /v1/rewrite-answer`
- `POST /v1/generate-questions`
- `POST /v1/screen-candidate`
- `POST /v1/lenses/derive`
- `GET /v1/lenses/{lens_id}`

API requirements:

- tenant-aware
- versioned
- evidence-aware
- confidence-aware
- privacy boundaries for private enterprise lenses

## Phase 4: Enterprise Self-Service Prototype

Estimated duration: 4 to 6 weeks after API prototype.

Enterprise flow:

1. Company creates tenant.
2. Company uploads public/private materials.
3. System runs distillation agents.
4. HR reviews generated lens.
5. System publishes private lens v1.0.
6. Enterprise uses lens for screening campaigns.
7. Hiring outcomes calibrate future lens versions.

## Phase 5: JobACE Integration

Estimated duration: 3 to 5 weeks after standalone API is stable.

Integration points:

- Aha Moment
- Mock Interview
- Evaluation
- Final Report
- Company-specific interview preparation
- Enterprise first-round and second-round screening

JobACE should call AIMS Lens Engine as an external service first.

## Phase 6: Expansion

Global anchor expansion:

- Apple
- Microsoft
- Netflix
- Goldman Sachs
- Toyota

Canada library:

- banks
- insurance
- technology
- telecom
- retail
- energy
- manufacturing

Long-term automation:

- agent orchestration
- source refresh
- human review queue
- lens versioning
- evaluation calibration
- enterprise dashboard
