# Role Routing And Live Transcript Validation

Status: v0.1 routing and validation draft. Production approval pending.

## Purpose

Role routing selects the best company lens and role overlay from company name, role title, job description, and transcript context. It must preserve confidence boundaries and fall back to general AIMS when evidence is missing.

## Routing Logic

1. Normalize company aliases.
2. Detect role family from title and job description.
3. Select company-specific role overlay when available.
4. If role overlay is missing, use company lens plus generic role overlay.
5. If company is missing, use role overlay plus generic AIMS.
6. If both are missing, use `GENERIC_AIMS`.

## Public Community Source Policy

Public sources such as Reddit, Glassdoor public pages, Indeed public interview pages, public forums, and public blogs can be used as additional evidence. They must be handled as lower-confidence public interview or community evidence unless corroborated.

Allowed:

- summarize recurring interview patterns
- record source category and confidence
- generate original variants
- flag contradictions and source limitations

Blocked:

- bypassing login, paywall, robots, or access controls
- copying full posts or long article bodies
- copying raw question banks verbatim
- exposing author-specific details that are not needed for lens behavior

## Validation Standard

Each routed test case must record:

- selected company lens
- selected role overlay
- confidence state
- expected AIMS dimensions
- expected company-specific feedback
- expected role-specific feedback
- unsupported claim checks
- whether human review is required

## Production Blockers

- At least 20 transcript cases per high-priority company.
- At least 15 cases per high-priority role overlay.
- Same-answer cross-lens validation.
- Same-answer cross-role validation.
- Human reviewer sign-off.
