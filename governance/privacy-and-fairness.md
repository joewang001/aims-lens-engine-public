# Privacy and Fairness

## Data Separation

Public lenses, private enterprise lenses, and candidate evaluation data must be separated by tenant and visibility.

Private enterprise data must not be used to improve public lenses unless explicitly authorized.

## Candidate Data

Candidate answers, resumes, scores, and screening reports are sensitive data.

Required controls:

- tenant isolation
- access logs
- retention policy
- deletion workflow
- export controls
- human review for adverse decisions

## Fairness Constraints

The system must not score candidates based on protected or sensitive traits.

Disallowed scoring factors include:

- age
- race
- ethnicity
- gender
- religion
- disability
- marital status
- pregnancy
- national origin
- citizenship status unless legally required for the role

## Screening Recommendation

The system provides decision support, not automatic final hiring decisions.

For low-confidence results, conflicting evidence, or borderline recommendations, return:

`human_review_required`

## Explanation Requirement

Every screening report should explain:

- assessed role requirements
- AIMS scores
- company lens adjustments
- evidence limitations
- recommended human follow-up questions
