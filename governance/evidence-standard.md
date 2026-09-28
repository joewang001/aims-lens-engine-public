# Evidence Standard — Paper Research Core

## Principle

A Lens is a versioned, evidence-bounded practice hypothesis. It is not an authoritative description of an employer's internal hiring process.

## Evidence fields

Every research-core evidence record should expose or derive:

- source reference or stable identifier;
- source type;
- source date and ingestion date where available;
- declared use purpose;
- authorization / rights state;
- quality or reliability assessment;
- Lens claims or categories supported;
- transformation lineage;
- reviewer state;
- expiry or review date where policy requires one.

## Authorization is a hard gate

Authorization and quality are not the same variable.

- `authorization = 0` means the record contributes no model mass.
- `authorization = 1` means the record is eligible to be considered.
- quality and recency may weight an eligible record after authorization.

Reference implementation:

```text
effective_weight = authorization_gate × quality_weight × recency_weight
```

This prevents a high-quality but unauthorized record from entering the model through a fractional score.

## Public source types

Recommended labels include:

- `official_company`
- `executive_primary`
- `job_description_public`
- `recruiting_material_public`
- `public_interview_experience`
- `employee_review_aggregate`
- `news_or_case`
- `external_criticism`
- `research_literature`
- `synthetic_example`

Private enterprise evidence may exist in production systems, but it is outside the frozen paper artifact unless it is transformed into an explicitly approved public-safe artifact with no confidential text or tenant-specific detail.

## Quality guidance

Quality is an auditable implementation input, not a universal theoretical constant.

Higher-quality evidence may include:

- attributable primary material relevant to the declared claim;
- repeated signals across independent source types;
- recent evidence for time-sensitive interview practices;
- reviewed structured annotations with documented disagreement handling.

Lower-quality evidence may include:

- isolated anonymous reports;
- undated recollections;
- unverifiable reposts;
- evidence whose relation to the modeled claim is indirect.

The paper artifact does not claim that any particular numeric quality mapping is universally valid; such mappings require validation and sensitivity analysis.

## Cross-validation and specificity rule

Company-specific specificity must be earned. A named-company practice claim should not be promoted merely because one source mentions it. Release policy should require independent corroboration or an appropriately authorized and reviewed source class, and must expose limitations.

## Copyright and quotation rule

Do not reproduce proprietary interview banks or large copyrighted source bodies. Store structured metadata, short permissible excerpts where needed, source references, distilled signals, and generated research-safe examples.

## Mandatory disclosure for public inferred Lenses

A public company Lens should include a statement equivalent to:

> This Lens is inferred from permitted public evidence for interview practice. It is not an official company hiring standard and does not predict a specific employer's interview or hiring decision.

## Candidate evidence is separate

Candidate answers, resumes, practice history, and progress records are not organization-level Lens evidence. Candidate-state features may be used for the same candidate's practice adaptation with consent, but must not automatically update company or industry Lenses.
