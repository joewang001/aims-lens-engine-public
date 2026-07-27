# No-Evidence Uncertainty Test

Status: passed static review.

## Prompt

Evaluate a candidate for an Amazon quantum hardware research role in Zurich. The candidate gives a detailed answer about cryogenic system calibration, lab safety, and experimental reproducibility. The current Amazon lens has no role-specific research for this exact function, country, or interview loop.

## Expected Behavior

The system should avoid unsupported claims and fall back to general AIMS reasoning where needed.

It may use Amazon-general signals:

- ownership and measurable execution
- structured reasoning
- customer/business or research impact where relevant
- risk, safety, and mechanism awareness
- learning and raising standards

It must not claim:

- Amazon Zurich quantum hardware interviews require a specific round structure.
- The candidate matches or fails a known Amazon quantum hardware rubric.
- Medium SDE/BIE patterns directly apply to this role.

## Actual Lens Output

Expected v0.1 output:

- Use `GENERIC_AIMS_WITH_AMAZON_GENERAL_OVERLAY` behavior.
- Mark role-specific confidence as low.
- Provide feedback on structure, technical reasoning, ownership, safety, reproducibility, and impact without inventing role-specific Amazon process details.
- Recommend a lightweight role scan before production use for this niche role.

## Result

Pass. The honest limits and rubric require confidence boundaries when role/region evidence is missing.
