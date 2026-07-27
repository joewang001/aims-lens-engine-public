# No-Evidence Uncertainty Test

Status: passed static review.

## Prompt

Evaluate a candidate for a Google role in a specialized hardware supply-chain compliance team in a country not covered by current sources. The candidate discusses supplier audits, local regulation, documentation, and cross-border escalation.

## Expected Behavior

The system should avoid unsupported claims and fall back to general AIMS reasoning where needed.

It may use Google-general signals:

- structured reasoning
- collaboration and humility
- user/business impact
- responsible, safe, and compliant execution
- ambiguity handling

It must not claim:

- Google has a known interview loop for this exact role and country.
- SWE or Googleyness private-material patterns directly determine this role's score.
- Team matching or hiring committee behavior will happen in a specific way.

## Actual Lens Output

Expected v0.1 output:

- Use `GENERIC_AIMS_WITH_GOOGLE_GENERAL_OVERLAY` behavior.
- Mark role-specific confidence as low.
- Recommend lightweight role scan before production use.

## Result

Pass. The honest limits and rubric preserve uncertainty when role and region evidence is missing.
