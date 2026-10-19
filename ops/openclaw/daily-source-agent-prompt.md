# AIMS Lens Daily Public Sourcing Task

Run date: `{{RUN_DATE}}` (`{{WEEKDAY}}`, America/Toronto)
Repository: `{{REPO_DIR}}`

Work only inside the repository above. This is a public open-source dataset.

## Required inputs

1. Read `docs/refresh-candidates/public-lens-daily-plan.json`.
2. Read `docs/refresh-candidates/public-lens-information-gaps.csv`.
3. Read `docs/public-lens-sourcing-agent-contract.md`.
4. Inspect the existing source packet and lens files for every target company.

## Required work

- Research every company in `weekly_new_company_targets` and every company in
  `historical_company_targets`, prioritizing today's `focus_dimensions`.
- Use `web_search` and `web_fetch`. Prefer official company, careers, investor,
  engineering, product, leadership, or public policy pages.
- Update at least two distinct files under
  `docs/refresh-candidates/source-packets/` with genuinely new or newly
  verified public evidence. Do not make date-only or formatting-only updates.
- Use non-verbatim source summaries. Do not copy page bodies or long quotes.
- Add only claims that the cited source supports. Mark uncertainty explicitly.
- Expand supported culture principles, hiring signals, anti-signals, original
  questions, and role overlays when the evidence supports them.
- Keep unsupported dimensions unresolved; the subsequent audit will retain
  them in the information-gap register with reasons and next actions.

## Public boundary

Never add private material, candidate or tenant data, copied job-posting
bodies, paywalled text, credentials, production configuration, or claims that
a company officially uses AIMS Lens. Do not contact people or publish content.

## File contract

- Edit source packets only under
  `docs/refresh-candidates/source-packets/*.source-packet.json`.
- Follow `schemas/public_lens_source_packet.schema.json`.
- Keep `source_policy` public-safe flags unchanged.
- Use ISO dates and stable evidence IDs.
- Do not directly edit generated company lens files or operational reports;
  the runner generates those after your research.

Finish with a concise list of companies researched, sources added, dimensions
strengthened, and unresolved source limitations. Do not commit or push; the
runner owns validation and Git operations.
