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

## Run the manuscript v1.3 controlled verification bundle

```bash
python tools/run_exp1a_core_verification.py
python tools/run_exp1b_lens_differentiation.py
python tools/run_exp2_sensitivity_ablation.py
python tools/run_exp3_semantic_regression.py
```

Experiments 1A, 1B, 2, and 3 use synthetic or public-safe fixtures. CI reruns all four and requires a zero git diff across `examples/paper/experiments`, providing committed-output reproducibility across the declared reference environment.

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

This branch is a **manuscript v1.3 release candidate**, not yet a frozen archival release.

The manifest has two explicit states:

- `release_status: candidate` permits `frozen_artifact_ref: pending_until_release_freeze`;
- `release_status: frozen` requires an immutable-looking tag or 40-character commit SHA.

Final archival sequence:

1. complete manuscript/repository cross-audit and release-metadata alignment;
2. run the full paper CI with all four experiments and zero committed-output diff;
3. create the freeze-metadata commit by setting `release_status: frozen`, a final immutable tag name in `frozen_artifact_ref`, and `date-released` in `CITATION.cff`;
4. rerun CI;
5. create the immutable Git tag on that exact green commit;
6. verify the tag resolves to that commit;
7. cite the frozen tag/commit in the manuscript rather than the moving branch.
