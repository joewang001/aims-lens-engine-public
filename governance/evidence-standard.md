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

## Support Strength Rule

`basis` records provenance: who said it. It does not record how strongly the cited source
supports the claim. Both facts matter, so judge them separately.

Direct support — the company-issued source states the behaviour or criterion being claimed:
careers and hiring-process pages, published interview guidance, job postings, official
engineering or culture posts.

Weak support — the company-issued source establishes business positioning, mission, values,
products, or customers, and the claimed evaluation criterion is a reasonable reading of that
positioning rather than a statement the company made. Homepages, investor relations pages,
annual reports, and general about-us material usually sit here.

A signal whose only company-issued source is positioning material may still be recorded as
`basis: stated_by_company`, because the company did publish the material it rests on, but its
evidence row must name the support as weak so a reviewer can see the difference without
re-deriving it. A candidate-reported account, private aggregate, third-party case book, or
criticism is not company-issued at any strength and stays `derived_public_inference`.

Revisit a weak-support signal when a direct source appears, or when the claim would carry
weight in a hiring decision. Weak support is not a licence to overstate: if the claim needs a
direct source to be defensible and none exists, drop the signal instead of leaning on
positioning.

### Weak-Support Register

Reviewed against their cited evidence on 2026-10-20. These signals rest on positioning
material rather than a stated criterion, and are retained as `stated_by_company` under the
Support Strength Rule. Record additions here when a review finds the same pattern.

| Company | Signal | Company-issued source | Why it is weak |
| --- | --- | --- | --- |
| BMO | Uses concrete behavioral evidence rather than generic banking or brand interest | BMO purpose and values | Values page describes conduct; it does not state an interview evidence standard |
| CIBC | Uses concrete behavioral evidence rather than generic banking or brand interest | CIBC Careers | Careers page describes culture; no stated evaluation criterion |
| JPMorgan Chase | Uses concrete behavioral evidence rather than generic banking or brand interest | Interview preparation page | Preparation guidance, not a stated bar for behavioural specificity |
| RBC | Uses concrete behavioral evidence rather than generic banking or brand interest | RBC Purpose, Vision and Values | Values page; no stated interview evidence standard |
| Scotiabank | Uses concrete behavioral evidence rather than generic banking or brand interest | Scotiabank Careers / Why Scotiabank | Careers positioning; no stated evaluation criterion |
| Accenture | Explains technology choices through client outcomes, delivery constraints, and measurable business value | Homepage, software engineering careers, investor relations | Business positioning implies client-outcome focus; no stated interview criterion |
| Adobe | Connects product or craft decisions to customer workflows and business outcomes | Homepage, investor relations, about page | Customer-outcome positioning, not a stated evaluation standard |
| Amazon | For BIE and analytics roles, defines metrics clearly, validates data, communicates uncertainty, and converts analysis into decisions | Product Manager interview prep (with candidate-reported and private sources) | Role-adjacent preparation guidance; the specific analytical bar is inferred |

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
