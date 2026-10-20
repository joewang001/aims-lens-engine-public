# Evidence Standard

## Source Types

Use these source type labels:

- `official_company`
- `executive_primary`
- `job_description`
- `recruiting_material`
- `public_interview_experience`
- `employee_review`
- `news_or_case`
- `external_criticism`
- `company_provided_private`

## Confidence Rules

High confidence:

- official company material
- executive primary sources
- repeated signals across independent source types
- enterprise-provided private materials approved by tenant owner

Medium confidence:

- multiple public interview experiences
- repeated employee reviews
- reputable business reporting

Low confidence:

- single anonymous post
- undated interview memory
- isolated opinion
- unverifiable repost

## Cross-Validation Rule

A key lens claim should not be promoted to company-level principle unless at least two independent source categories support it, or one authoritative enterprise-private source supports it.

## Copyright Rule

Do not store large copied interview question banks from copyrighted sources. Store:

- short summary
- source reference
- role family
- skill tags
- AIMS dimensions
- generated variants

Summarizing is not derivation. When a company discloses its own interview questions,
process, or evaluation guidance, the resulting de-identified summary still traces to that
company-issued source and is recorded as `basis: stated_by_company`. The Copyright Rule
governs how much text is stored, not who the source is.

Use `basis: derived_public_inference` only when no company-issued source supports the claim,
for example when it is synthesized from public business positioning, candidate-reported
interview accounts, third-party case material, or external criticism. Use
`basis: generic_public_default` for generator boilerplate that is not specific to the company.

Every signal in `hiring_signals` must declare one of these three `basis` values; the field is
required for lenses published after this standard was amended, and a signal whose provenance
cannot be established must be left out rather than labelled by guess.

## Disclosure Rule

Public inferred lenses must include:

`This lens is inferred from public sources and does not represent an official company hiring standard.`

Private enterprise lenses must include:

`This lens is based on company-provided materials and is available only within the authorized tenant scope.`
