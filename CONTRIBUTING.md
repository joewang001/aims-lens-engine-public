# Contributing to AIMS Lens Engine

AIMS Lens Engine accepts public-safe improvements to company lenses, schemas,
validation cases, governance documents, and tooling.

## Contribution Boundary

Good contributions:

- Use public sources, properly cited summaries, and clear confidence levels.
- Improve schemas, validation tools, routing rules, or public examples.
- Add public company lens material that is non-verbatim and independently useful.
- Mark uncertainty, source limitations, and role or geography constraints.
- Preserve the distinction between public lens content and private JobACE data.

Do not contribute:

- Raw copyrighted articles, copied job postings, paywalled materials, or private
  employer documents.
- Candidate resumes, candidate answers, tenant uploads, user-submitted job
  bodies, review logs, API keys, tokens, database paths, or production configs.
- Any material marked `private_only`, `tenant_upload`, `candidate_answer`,
  `candidate_resume`, `internal_review_record`, or `private_scoring_calibration`.
- Claims that a public lens is an official company hiring standard.
- Company logos, trademarks, or brand assets unless their usage rights are clear.

## Evidence Classes

Use these public evidence classes:

- `public_source`: official or openly available company materials.
- `public_community_aggregate`: aggregated public community patterns with lower
  confidence and clear limitations.
- `private_distillation_public_safe`: non-verbatim, public-safe signal distilled
  from private or paid material, with no raw text, no user-specific details, and
  no tenant or candidate data.

Never use `private_only` evidence in public lens files.

## Pull Request Checklist

Before opening a pull request:

1. Keep edits scoped to public-safe files.
2. Cite sources in `evidence.md` or the relevant documentation.
3. Do not include raw source text beyond short fair-use snippets.
4. Run the public export and scanner:

   ```bash
   python tools/export_public_release.py --execute --clean
   python tools/scan_public_export.py --allowlist
   python tools/generate_public_release_audit_report.py --allowlist
   ```

5. Confirm the generated audit report has no blockers and no unresolved review
   findings.

## Review Standard

Maintainers may reject or rewrite contributions that are useful but not
public-safe. The default rule is simple: when in doubt, keep the public lens
non-verbatim, evidence-aware, and privacy-preserving.
