# Reproducibility Guide

The paper reference implementation is intentionally small and dependency-free so a reviewer can inspect and run the core inference path without production services or private data.

## Requirements

- Python 3.11 or newer
- No network access
- No API keys
- No JobACE account
- No private Lens assets

## Run the deterministic paper demo

```bash
python tools/run_paper_artifact_demo.py
```

The script loads:

```text
examples/paper/followup_priority_request.json
```

and writes a deterministic JSON result to stdout. The result should be structurally consistent with:

```text
examples/paper/expected_followup_priority_response.json
```

Minor floating-point formatting differences are acceptable.

## Run validation and unit tests

```bash
python tools/validate_paper_artifact.py
python -m unittest discover -s tests -v
```

The validator checks required research-core files, the paper-manifest policy declarations and concrete include paths, required paper-core exclusions, excluded employer-side API terms, the synthetic request's runtime constraints, deterministic expected output, and an explicit abstention-gate probe.

The JSON Schema files remain the normative exchange contracts. The dependency-free validator intentionally performs targeted runtime checks rather than claiming to be a complete general-purpose JSON Schema or OpenAPI validator.

## What the demo establishes

The demo is a **reference implementation**, not empirical validation. It demonstrates that the manuscript's core operations can be expressed reproducibly:

1. authorization gating;
2. quality and temporal evidence weighting;
3. hierarchical Dirichlet-style partial pooling;
4. compatibility masking;
5. backoff-aware routing mixture;
6. uncertainty and data-support summaries;
7. provenance-aware practice-priority output;
8. fail-closed abstention when declared support is inadequate.

It does not establish that a company follows the modeled pattern, that the output predicts employer behavior, or that interview outcomes improve. Those claims require the empirical evaluation protocol described in the paper.

## Equation-level traceability

See `docs/PAPER_TO_CODE_MAP.md` for the section/equation-to-function index and `docs/MATH_TO_CODE_COMPLETENESS_AUDIT.md` for completeness status, deliberate boundaries, and manuscript issues found by the audit.

## Freeze step before submission

This branch is a release candidate, not yet a frozen archival release. Before journal submission:

1. select the final reviewed commit;
2. replace `frozen_artifact_ref: pending_until_release_freeze` in `paper_artifact_manifest.yaml` with the final tag or commit;
3. add `date-released` to `CITATION.cff`;
4. cite that frozen tag/commit in the manuscript rather than the moving branch.
