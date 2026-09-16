# Privacy, Fairness, and Candidate-Side Use Boundary

## Intended use

The paper research core is an interview-practice aid. It helps a candidate decide what evidence or competency to practice next. It is not an employer-side selection system.

## Prohibited paper-core uses

The frozen research artifact must not:

- rank candidates for employers;
- recommend that an employer advance, hold, or reject a candidate;
- infer protected or sensitive characteristics;
- tell a candidate that a specific employer is likely to reject them;
- encourage fabrication of experience, metrics, ownership, or credentials;
- claim that practice performance guarantees a hiring outcome.

## Data separation

Public Lens evidence, private enterprise evidence, and candidate data are separate classes with separate update paths.

Candidate-side production systems should implement:

- tenant isolation where applicable;
- purpose limitation;
- access logging;
- retention schedules;
- deletion workflows;
- export controls;
- consent for candidate-state adaptation;
- separation of raw candidate content from organization-level Lens updates.

The paper artifact itself uses synthetic examples and requires no private candidate data.

## Fairness and accessibility

Fairness review applies to both model outputs and interaction design. Evaluation should test whether errors, abstentions, routing depth, and practice benefit differ across relevant participant groups.

Design considerations include:

- language variation and multilingual support;
- plain-language explanations;
- screen-reader compatibility;
- adjustable pacing and alternative formats;
- configurable follow-up style where culturally appropriate;
- avoidance of protected-trait inference or proxy use.

## Authenticity-preserving coaching

The system may help a candidate surface, organize, substantiate, and reflect on genuine experience. It must not optimize deceptive impression management or manufacture evidence the candidate did not provide.

## Explainability without false precision

The preferred explanation names:

- Lens type and version;
- evidence maturity;
- major context factors;
- routing/backoff level;
- evidence-support limitations;
- why a broader fallback was used when applicable.

A numerical score must not be described as the probability of employer behavior unless the paper's empirical calibration conditions are actually satisfied for that claim.

## Organizational stereotyping and contestability

A company Lens is a bounded hypothesis, not an ontological description of an organization. Team, role, region, interviewer, and time may differ. Public-source selection bias and stale evidence can distort a Lens. The design therefore requires versioning, expiry/review, provenance, fallback, and a way for authorized reviewers to contest or withdraw unsupported claims.

## Fail-closed governance

The system should narrow its claim, route more broadly, or abstain when evidence rights are missing, evidence is stale, an audit cannot reproduce an output, a required calibration check fails, or a fairness review threshold is triggered.
