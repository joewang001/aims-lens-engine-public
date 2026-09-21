<!-- doc-parity: id=broader-product-boundary; version=1.2; language=en; companion=README.zh-CN.md -->
# Broader Product and Historical Extensions

[English](README.md) | [中文](README.zh-CN.md)

This directory documents the boundary between the **manuscript research core** and broader ideas explored during AIMS Lens Engine / JobACE product development.

## Manuscript core

The paper-facing core is candidate-side interview practice:

- evidence-governed Lens representation;
- probabilistic practice-priority inference;
- compatibility constraints;
- L0–L5 routing/backoff;
- uncertainty and abstention;
- provenance, explanation, and auditability.

## Outside the manuscript core

Repository history includes experiments or concepts related to employer-side screening, reviewer assistance, enterprise decision workflows, and broader product use.

Those materials:

- are not part of the paper artifact;
- are not validated by the manuscript's empirical claims;
- should not be cited as evidence that AIMS Lens Engine is an employer hiring-decision system;
- may require materially different legal, fairness, validation, and human-oversight analysis if pursued as future products.

Historical code or schemas may remain under `legacy/` so development provenance is not erased.

## Why preserve the boundary instead of deleting history

Deleting every earlier product concept would make the repository look cleaner but would reduce transparency about how the system evolved.

The preferred approach is:

1. preserve historical artifacts;
2. label them clearly;
3. exclude them from the paper artifact;
4. keep the public research API candidate-side;
5. evaluate any future extension under its own governance and evidence requirements.

The existence of a historical extension is not a current product claim.
