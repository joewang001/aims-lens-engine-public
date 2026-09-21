# Documentation System v1.2

Documentation System v1.2 rebases the bilingual documentation architecture introduced in v1.1 onto the current frozen research baseline.

## Fact baseline

- Repository branch baseline: paper-release-readiness-v1.1
- Baseline commit before this documentation change: f7fcb6a3129cb58fe20c414f1abe519376def8e1
- Frozen paper artifact: v0.9.2-paper-v1.3
- Aligned manuscript: v1.3
- Experimental bundle: 84c0afc5f928989237832d625002aba17ae8ac4f
- Release date: 2026-09-20

## Documentation rules

- README.md is the canonical English landing page.
- README.zh-CN.md is its semantic-equivalent Chinese companion.
- Semantic parity covers facts, definitions, research boundaries, version state, empirical status, APIs, governance, limitations, licenses, and citation guidance.
- Literal sentence-by-sentence translation and equal byte length are not required.
- Employer-side screening, reviewer-assist, and enterprise concepts are preserved as broader-product or historical provenance, not manuscript claims.

## Legacy preservation

Before canonical paths were replaced, the existing repository documents were preserved as:

- docs/archive/README_ZH-legacy-pre-v1.2.md
- docs/archive/aims-lens-distillation-strategy-zh-legacy-pre-v1.1.md
- docs/archive/distillation-playbook-legacy-pre-v1.2.md

README_ZH.md is now a compatibility notice pointing to README.zh-CN.md.

## Validation

Run the documentation-alignment validator, paper-artifact validator, unit tests, deterministic paper demo, and git diff --check before commit.