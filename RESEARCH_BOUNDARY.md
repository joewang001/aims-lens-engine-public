# Research Artifact Boundary

This document defines the boundary of the research artifact associated with the manuscript **AIMS Lens Engine: An Evidence-Governed Probabilistic Framework for Interview Follow-Up Simulation and Practice Prioritization**.

## Research-core purpose

The paper artifact is a candidate-side interview-practice reasoning engine. It selects and explains practice follow-up priorities under incomplete, heterogeneous, and differently authorized evidence. It is **not** an employer-side candidate ranking, screening, rejection, or hiring-decision system.

The core abstractions are institution-agnostic:

- `tenant`
- `role_context`
- `candidate_state_features`
- `evidence_lineage`
- versioned `lens`
- compatibility constraints
- hierarchical borrowing and backoff
- uncertainty and abstention
- explanation provenance

JobACE is the first deep reference integration. It is not an architectural prerequisite.

## Included in the paper research core

The frozen paper artifact should include only the following classes of material:

1. Public protocol and API contracts for Lens validation, routing, practice follow-up prioritization, and explanation.
2. Versioned schemas required to exchange research-core inputs and outputs.
3. A dependency-free Python reference implementation of the paper's core inference operations.
4. Synthetic or public-safe example inputs and expected outputs.
5. Governance rules that define evidence authorization, quality, recency, provenance, privacy, fairness, and abstention.
6. Reproducibility scripts and tests.
7. Citation and artifact metadata.

## Explicitly outside the paper research core

The following may remain in the wider repository for historical or product-development reasons, but are not evidence for the paper's candidate-side claims and must not be included in the frozen paper artifact:

- employer-side candidate screening or ranking workflows;
- advance / hold / reject decision APIs or schemas;
- human-review queues for adverse employment decisions;
- JobACE tenant configuration or production adapter state;
- candidate records, resumes, transcripts, scores, or practice histories from real users;
- private company or enterprise evidence;
- production calibration parameters;
- production credentials, service hosts, databases, audit logs, or deployment configuration;
- real private conversations or proprietary production policies.

## Evidence is not employer truth

A Lens is a **versioned, evidence-bounded hypothesis for practice**. It must not be described as an authoritative representation of how a named employer actually interviews or decides. Company-specific specificity must be earned by permitted, attributable, current, reviewed evidence and must fall back to broader contexts when support is inadequate.

## Authorization and evidential weight are separate

Evidence permission is a hard gate. An unauthorized record contributes zero model mass regardless of its apparent quality. For authorized records, quality and recency may influence evidential weight. In notation used by the reference implementation:

`effective_weight = authorization_gate × quality_weight × recency_weight`

where `authorization_gate ∈ {0,1}`.

## Candidate data separation

Candidate-side state may personalize the candidate's next practice step when consent allows it, but candidate records must not automatically update company, industry, archetype, or public Lenses. This prevents a feedback loop in which system-generated practice becomes its own evidence about employers.

## JobACE boundary

JobACE may provide interaction, coaching, longitudinal learning history, progress tracking, and client-facing workflow. The Lens Engine provides the institution-agnostic reasoning service. Client applications should integrate through versioned APIs rather than copy or fork the inference algorithm.
