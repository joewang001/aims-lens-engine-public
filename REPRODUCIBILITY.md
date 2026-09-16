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

The validator checks the paper manifest, required files, exclusion rules, synthetic example shape, and the reference inference path.

## What the demo establishes

The demo is a **reference implementation**, not empirical validation. It demonstrates that the manuscript's core operations can be expressed reproducibly:

1. authorization gating;
2. quality and temporal evidence weighting;
3. hierarchical Dirichlet-style partial pooling;
4. compatibility masking;
5. backoff-aware routing mixture;
6. uncertainty and data-support summaries;
7. provenance-aware practice-priority output.

It does not establish that a company follows the modeled pattern, that the output predicts employer behavior, or that interview outcomes improve. Those claims require the empirical evaluation protocol described in the paper.

## Equation-level traceability

See `docs/PAPER_TO_CODE_MAP.md` for the section/equation-to-function index and `docs/MATH_TO_CODE_COMPLETENESS_AUDIT.md` for completeness status, deliberate boundaries, and manuscript issues found by the audit.
