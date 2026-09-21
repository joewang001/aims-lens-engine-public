# Experiment 3 — Candidate-Answer Semantic Regression

**Protocol version:** v0.1 pre-registered public contract

## Purpose

Experiment 3 preserves and independently audits six public-safe candidate-answer regression cases originally maintained for the JobACE Aha Moment. It separates a historical semantic baseline from a deterministic public semantic oracle.

This is **not** a rerun of the production language model. The public artifact does not contain the full proprietary generation prompt or historical model responses. It therefore does not claim current-model accuracy, fairness validation, employer-side screening validity, or employment-outcome efficacy.

## Two evidence layers

1. **Historical semantic baseline.** The source regression record states AHA-001 through AHA-006 passed their semantic release gate.
2. **Deterministic public semantic oracle.** Frozen candidate transcripts and explicitly recorded evidence markers are re-evaluated for target-role clarity, measurable impact, technical reasoning, ownership, collaboration, mentoring, senior scope, unsupported self-claims, role-fit connection, Strong Answer Gate eligibility, and Diagnostic-vs-Validation Probe mode.

## Canonical-case integrity

Each transcript carries a SHA-256. A case fails if the transcript changes without an explicit fixture-version change. AHA-001 is special: the source record provides a canonical base transcript and separately identifies four evidence markers for a stronger production regression variant (50,000+ users, cross-functional coordination, code review, and approximately 30% reduction in regression bugs). Because the full stronger transcript was not retrieved, the public fixture preserves the base transcript verbatim and records only those source-supported markers; it does not reconstruct missing wording.

## Strong Answer Gate

For this public reference oracle, Validation Probe eligibility requires a clearly stated Senior Software Developer target, measurable impact, technical problem/solution evidence, project ownership, collaboration, senior-scope evidence, and a role-fit connection. The language-surface flag is not used in this gate.

Expected Validation Probe cases are AHA-005 and AHA-006. AHA-006 is a controlled fixture showing that the declared gate does not use its non-native-English surface flag. This is **not** group-level or population-level fairness validation.

## Expected diagnostic cases

- AHA-001: measurable impact is credited; ownership/senior scope remains unresolved.
- AHA-002: unsupported claims require evidence/ownership clarification.
- AHA-003: measurable technical impact is credited; ownership/senior positioning remains unresolved.
- AHA-004: target role remains `Not clearly stated`; current professional identity is not substituted for target role.

## Historical-only generation rules

The historical source also records response-level requirements: no more than two follow-up questions, one or two relevant AIMS signals, no Quick Score, no complete replacement answer, voice-friendly under 180 words, and no company-style rewrite. These require generated text. Because historical response text was not retrieved and this public experiment does not invoke a current language model, they remain historical baseline contract items and are marked **not re-executed**.

## Pass criteria

Experiment 3 passes only if exactly six canonical IDs are present; transcript hashes match; all historical baseline statuses remain PASS; target-role, mode, Strong Answer Gate, primary-gap class, and must-credit features match expectations; AHA-006 remains Validation Probe eligible while language-surface variation is excluded from the gate; and no current-model rerun is falsely recorded.

## Reproducibility

The runner is dependency-free and deterministic. It emits `exp3_results.json` and `exp3_case_matrix.csv`. CI reruns Experiment 3 and the repository-wide committed-output diff gate.

## Safe manuscript claim

> In six controlled candidate-answer regression fixtures derived from a previously passing Aha baseline, a transparent deterministic semantic oracle reproduced the expected target-role, evidence-crediting, diagnostic-mode, and Strong-Answer-Gate classifications for all six cases.

For AHA-006 only:

> In the controlled regression fixture, surface-level non-native English variation did not override the declared evidence-based gate.

The experiment must not be described as fairness validation, model calibration, current production-model validation, real-user outcome validation, or employer-side screening evidence.
