# Limited Pilot Policy

Status: approved_for_limited_pilot.

## Approved Use

- Internal evaluation of company lens routing and scoring reports.
- Controlled partner pilot through API or review workflow.
- Candidate coaching, interview preparation, and reviewer-assist use cases.
- Company lens feedback with clear evidence notices and confidence states.

## Required Controls

- Human review is required for weak, risky, generic, or low-confidence cases.
- Public community evidence must remain aggregate and lower-confidence unless corroborated.
- Screening reports must preserve `schemas/screening_report.schema.json`.
- Reports must include evidence notices and fairness review flags.
- Generic company fallback must not imply a company-specific lens.

## Blocked Use

- Automated rejection.
- Fully unsupervised hiring decisions.
- Treating community evidence as official company policy.
- Copying raw interview posts, long article bodies, or verbatim question banks.
- Bypassing login, paywall, or access controls.

## Exit Criteria For Full Production

- Real LLM scorer integration passes the Phase 2C gate suite.
- Additional human reviewer calibration confirms acceptable false-positive and false-negative behavior.
- API audit logging and tenant-level controls are implemented.
- Role/company coverage is refreshed on a scheduled evidence-review cadence.
