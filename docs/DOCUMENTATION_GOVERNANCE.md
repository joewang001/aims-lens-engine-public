<!-- doc-parity: id=documentation-governance; version=1.2; language=en; companion=DOCUMENTATION_GOVERNANCE.zh-CN.md -->
# Documentation Governance

[English](DOCUMENTATION_GOVERNANCE.md) | [中文](DOCUMENTATION_GOVERNANCE.zh-CN.md)

## Policy

English is the canonical public research language for AIMS Lens Engine. Chinese companion documents are maintained at **semantic parity**.

Semantic parity means the two languages must agree on facts, research boundaries, definitions, mathematical meaning, version state, API behavior, governance requirements, limitations, and empirical status. It does **not** require sentence-by-sentence translation or equal length.

## What must remain identical in meaning

The following are normative and must not diverge across languages:

- the definition of a Lens as a **versioned, evidence-bounded practice hypothesis**;
- the candidate-side research boundary;
- the statement that named-company Lenses are not employer ground truth;
- evidence authorization as a hard gate;
- the L0–L5 routing/backoff interpretation;
- the meaning of uncertainty, data support, and abstention;
- maturity states: `exploratory`, `reviewed_practice`, `evaluation_ready`, `empirically_supported`;
- JobACE as the first deep reference integration, not an architectural prerequisite;
- empirical-status statements and limitations;
- privacy, fairness, protected-data, and public/private boundaries;
- version numbers, frozen release references, API names, schema names, license terms, and citation instructions.

## What may differ

The languages may differ in:

- sentence structure and idiom;
- explanatory examples;
- introductory metaphors;
- paragraph length;
- ordering of non-normative examples;
- additional clarification aimed at a specific language community.

A Chinese explanation may be more conversational and an English explanation more technical, provided they do not create different claims.

## Pair metadata

Maintained pairs begin with a hidden marker:

```text
<!-- doc-parity: id=<stable-id>; version=<semantic-version>; language=<en|zh-CN>; companion=<path> -->
```

Both members of a pair must share the same `id` and semantic `version`.

## Update workflow

For a normative documentation change:

1. edit the English canonical document;
2. update the Chinese companion in the same change set;
3. bump the pair semantic version if meaning changes;
4. run `python tools/validate_documentation_alignment.py`;
5. run paper validation if the English README or any paper-facing research document changed;
6. describe material terminology changes in the pull request.

Pure typo/formatting corrections do not require a semantic-version bump if meaning is unchanged.

## Wiki rule

The canonical source for Wiki text lives in `docs/wiki/`. The rendered GitHub Wiki may be copied from those files, but the repository source is the auditable version.

Do not edit the live Wiki in a way that creates a new normative definition without updating `docs/wiki/` and its bilingual companion.

## Broader product and historical documentation

Employer-side or other broader product concepts may be preserved for provenance in `docs/broader-product/` or `legacy/`. Those documents must carry an explicit statement that they are outside the manuscript research core and are not evidence for paper claims.

## Conflict resolution

When two documents appear inconsistent, use this priority for manuscript interpretation:

1. frozen manuscript and `RESEARCH_BOUNDARY.md`;
2. paper artifact manifest and paper-facing API/schema;
3. `README.md` and research implementation maps;
4. canonical distillation / Wiki documentation;
5. broader product, operations, and historical documents.

The correct response to a conflict is to repair the documentation, not to exploit the hierarchy to leave contradictory statements in place.
