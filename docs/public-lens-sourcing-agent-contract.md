# Public Lens Sourcing Agent Contract

This contract defines how an external sourcing agent can turn public web
research into AIMS Lens Engine updates without importing private, candidate,
tenant, paid, or copyrighted source bodies.

The sourcing agent may be a local script, a scheduled CI job, or an external AI
worker. The public repository only accepts the resulting source packet and lens
patch after validation.

## Agent Responsibilities

The sourcing agent must:

- collect only approved public source types;
- write source metadata and non-verbatim distilled signals;
- map every signal to one or more seven-dimension labels;
- attach source IDs to every proposed lens update;
- avoid raw source bodies, copied job descriptions, paywalled text, private
  employer material, candidate material, tenant uploads, secrets, and production
  configuration;
- mark community or social material as lower confidence and review-required when
  it affects scoring.

## Approved Source Types

- `official_company`
- `official_careers`
- `official_investor_relations`
- `official_engineering_blog`
- `official_product_blog`
- `official_leadership_letter`
- `public_community_aggregate`

## Seven-Dimension Labels

- `company_says`
- `company_judges`
- `company_asks`
- `evidence_valued`
- `risk_warnings`
- `role_variation`
- `honest_unknowns`

## Source Packet

The source packet is a JSON document validated by
`schemas/public_lens_source_packet.schema.json`.

Minimum packet shape:

```json
{
  "company_slug": "nvidia",
  "company": "NVIDIA",
  "collected_at": "2026-08-25T13:00:00Z",
  "source_policy": {
    "public_safe": true,
    "contains_private_material": false,
    "contains_candidate_data": false,
    "contains_raw_job_posting_body": false,
    "contains_paywalled_text": false
  },
  "sources": [],
  "lens_updates": {
    "culture_principles": [],
    "hiring_signals": [],
    "anti_signals": [],
    "questions": [],
    "role_overlays": []
  }
}
```

## Normal Automation Path

1. Select existing lens refresh targets or approved-backlog expansion targets.
2. Collect public source metadata.
3. Produce one source packet per company.
4. Validate packet structure and public-safety flags.
5. Generate lens patches.
6. Run:

   ```bash
   python tools/scan_public_export.py --allowlist
   python tools/validate_public_lens_coverage.py --min-companies 12
   ```

7. Open a PR with source packet summary, changed files, validation output, and
   auto-merge eligibility.

## Auto-Merge Eligibility

An automated content PR may be auto-merged only when:

- all packet source-policy flags are public-safe;
- evidence classes are only public source or public community aggregate;
- no scanner blocker or review finding appears;
- coverage validation passes;
- the PR changes at most three existing lenses or adds at most two approved
  `LIGHTWEIGHT_SCAN` backlog companies;
- no schema, routing, scoring, license, workflow-permission, or boundary policy
  change is included;
- no lens is promoted to `FULLY_DISTILLED`.

Anything outside this boundary requires maintainer review.
