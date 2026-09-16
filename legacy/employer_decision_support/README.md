# Historical Employer-Side Decision-Support Materials

This directory marks a **scope boundary**, not a claim that prior experiments never existed.

Earlier AIMS Lens Engine development explored employer-side screening, human-review queues, and advance/hold/reject decision-support semantics. Those concepts are outside the manuscript **AIMS Lens Engine: An Evidence-Governed Probabilistic Framework for Interview Follow-Up Simulation and Practice Prioritization** and outside the frozen `paper_artifact_manifest.yaml`.

The paper research core is candidate-side interview practice. In particular, it must not:

- rank candidates for employers;
- recommend rejection or advancement;
- predict hiring outcomes;
- infer protected characteristics;
- treat candidate practice data as employer evidence.

Historical files that remain elsewhere in the wider repository are retained for development provenance and backward compatibility, but they must not be interpreted as part of the paper artifact. The paper-facing `api/openapi.yaml`, governance documents, reference implementation, examples, and CI intentionally exclude these semantics.

For an archival paper release, a maintainer may choose either to leave historical files in the repository but exclude them through `paper_artifact_manifest.yaml`, or to publish a release asset containing only the allowlisted paper artifact.
