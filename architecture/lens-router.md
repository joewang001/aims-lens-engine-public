# Lens Router

## Purpose

The Lens Router chooses the best available lens for a request.

It must prioritize accuracy and disclosure over forced company-specific output.

## Inputs

- `tenant_id`
- `company`
- `role`
- `job_description`
- `region`
- `industry`
- `lens_id`
- `use_case`

Use cases:

- job seeker interview prep
- answer evaluation
- answer rewrite
- question generation
- candidate screening
- enterprise lens creation

## Routing Order

1. Explicit `lens_id`, if authorized.
2. Private enterprise lens for tenant and company.
3. Public fully distilled company lens.
4. Derived lens from similar companies, industry, region, role, and JD.
5. Lightweight scan from supplied materials.
6. Generic AIMS.

## Output

```json
{
  "selected_lens_id": "amazon_public_v0_1",
  "lens_status": "FULLY_DISTILLED",
  "confidence": 0.91,
  "routing_reason": "Exact public company lens found.",
  "fallbacks_considered": [],
  "evidence_notice": "This lens is inferred from public sources and does not represent an official company hiring standard."
}
```

## Derived Lens Construction

When no exact lens exists:

1. Identify industry archetype.
2. Identify regional anchor.
3. Identify similar public lenses.
4. Apply role lens.
5. Extract target JD requirements.
6. Produce temporary lens with confidence and limitations.

## Safety Rules

- Do not expose private tenant lenses across tenants.
- Do not use private data in public derived lenses.
- Do not claim official company authority for public inferred lenses.
- Use `GENERIC_AIMS` when evidence is too weak.
