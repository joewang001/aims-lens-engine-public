<!-- doc-parity: id=documentation-hub; version=1.2; language=en; companion=README.zh-CN.md -->
# AIMS Lens Engine Documentation Hub

[English](README.md) | [中文](README.zh-CN.md)

This directory contains several kinds of documentation with different authority. They should not be read as interchangeable.

## Documentation layers

| Layer | Purpose | Canonical examples |
| --- | --- | --- |
| **Research boundary** | Defines what the manuscript does and does not claim | `../RESEARCH_BOUNDARY.md`, `../REPRODUCIBILITY.md` |
| **Research implementation** | Maps equations, algorithms, schemas, tests, and demos | `PAPER_TO_CODE_MAP.md`, `MATH_TO_CODE_COMPLETENESS_AUDIT.md` |
| **Lens distillation** | Explains how evidence becomes a governed practice Lens | `aims-lens-distillation-strategy.md` |
| **Public Lens operations** | Maintains public-safe supporting Lens assets | `public-lens-operations-plan.md`, `public-lens-refresh-and-expansion.md` |
| **Product/history boundary** | Preserves broader or historical concepts without turning them into paper claims | `broader-product/README.md`, `../legacy/` |
| **Wiki source** | Human-oriented explanation for GitHub Wiki / onboarding | `wiki/AIMS_LENS_ENGINE_WIKI.md` |

## Canonical bilingual pairs

The English document is canonical for public research wording. Chinese is a semantic-equivalent companion.

| English | 中文 |
| --- | --- |
| `../README.md` | `../README.zh-CN.md` |
| `README.md` | `README.zh-CN.md` |
| `DOCUMENTATION_GOVERNANCE.md` | `DOCUMENTATION_GOVERNANCE.zh-CN.md` |
| `aims-lens-distillation-strategy.md` | `aims-lens-distillation-strategy-zh.md` |
| `wiki/AIMS_LENS_ENGINE_WIKI.md` | `wiki/AIMS_LENS_ENGINE_WIKI.zh-CN.md` |
| `broader-product/README.md` | `broader-product/README.zh-CN.md` |

Run:

```bash
python tools/validate_documentation_alignment.py
```

from the repository root to verify pair metadata and shared machine-readable terminology.

## Reading order for a new reviewer

1. `../README.md`
2. `../RESEARCH_BOUNDARY.md`
3. `aims-lens-distillation-strategy.md`
4. `PAPER_TO_CODE_MAP.md`
5. `../REPRODUCIBILITY.md`
6. `wiki/AIMS_LENS_ENGINE_WIKI.md`

## Authority rule

If a broader product or historical document conflicts with the manuscript research boundary, **the paper-facing research documents control interpretation of manuscript claims**.

If English and Chinese companions conflict on a normative point, fix both documents in the same pull request; do not silently choose one as a convenient interpretation.
