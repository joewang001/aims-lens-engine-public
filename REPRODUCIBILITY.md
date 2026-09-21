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
python tools/validate_documentation_alignment.py
python -m unittest discover -s tests -v
```

The validator checks required research-core files, the paper-manifest policy declarations and concrete include paths, required paper-core exclusions, excluded employer-side API terms, the synthetic request's runtime constraints, deterministic expected output, and an explicit abstention-gate probe.

The JSON Schema files remain the normative exchange contracts. The dependency-free validator intentionally performs targeted runtime checks rather than claiming to be a complete general-purpose JSON Schema or OpenAPI validator.

## Run the v1.4 controlled and corrective verification bundle

```bash
python tools/run_exp1a_core_verification.py
python tools/run_exp1b_lens_differentiation.py
python tools/run_exp2_sensitivity_ablation.py
python tools/run_exp3_semantic_regression.py
python tools/run_exp4_adversarial_alignment.py
python tools/run_exp5_hierarchy_approximation.py
```

Experiments 1A, 1B, 2, and 3 retain the controlled synthetic/public-safe verification, sensitivity, ablation, and semantic-regression coverage inherited from the v1.3 research artifact.

Experiment 4 is **internal mathematical–implementation correction evidence** for the four identified v1.3 counterexamples: Eq. 15 parameter information gain, calibration cancellation, masked-evidence support inflation, and zero-permitted-mass routing. The historical v1.3 artifact remains immutable; the runner uses explicit legacy reference helpers for comparison.

Experiment 5 is a **synthetic approximation benchmark** of the **recursive plug-in hierarchical Dirichlet shrinkage** path against a deterministic uncertainty-propagating binary reference. The plug-in credible intervals are **conditional Dirichlet intervals given the plug-in parent distribution**. Its pass/fail criterion is numerical convergence of the reference calculation; estimator differences are descriptive.

These experiments concern internal mathematical–implementation behavior under declared controlled inputs. They do not establish real-employer validity, population fairness, employer-behavior prediction, interview-improvement efficacy, or employment-outcome efficacy.

On the v1.4 corrective branch, CI reruns Experiments 1A, 1B, 2, 3, 4, and 5 and requires a zero git diff across `examples/paper/experiments`, providing committed-output reproducibility for the complete controlled and corrective bundle.
## What the demo establishes

The demo is a **reference implementation**, not empirical validation. It demonstrates that the manuscript's core operations can be expressed reproducibly:

1. authorization gating;
2. quality and temporal evidence weighting;
3. company-level use of recursive plug-in hierarchical Dirichlet shrinkage against a supplied parent distribution; the complete four-level helper remains a standalone research path benchmarked separately in Experiment 5, with conditional Dirichlet intervals given the plug-in parent distribution;
4. compatibility masking;
5. backoff-aware routing mixture;
6. uncertainty and data-support summaries;
7. provenance-aware practice-priority output;
8. fail-closed abstention when declared support is inadequate.

It does not establish that a company follows the modeled pattern, that the output predicts employer behavior, or that interview outcomes improve. Those claims require the empirical evaluation protocol described in the paper.

## Equation-level traceability

See `docs/PAPER_TO_CODE_MAP.md` for the section/equation-to-function index, `docs/MATH_TO_CODE_COMPLETENESS_AUDIT.md` for executable-counterpart completeness, and `docs/IMPLEMENTATION_INTEGRATION_COVERAGE_MATRIX.md` for the separate runtime-integration / evaluation / experiment / external-validation status.

## Freeze step before submission

This freeze-metadata state declares artifact `0.10.0-paper-v1.4` and immutable archival ref **`v0.10.0-paper-v1.4`**. The Git tag is created only after this exact freeze-metadata commit passes the full remote Paper Artifact CI. Once the tag resolves to that green commit, the artifact is the frozen manuscript v1.4 release.

The v1.4 corrective experimental baseline remains `c18899b469e1d579391306872d5834ebf6e3caf3`. The previous frozen v1.3 artifact remains `v0.9.2-paper-v1.3` at `f7fcb6a3129cb58fe20c414f1abe519376def8e1`.

The manifest records:

- `release_status: frozen`;
- `frozen_artifact_ref: v0.10.0-paper-v1.4`;
- `target_release_tag: v0.10.0-paper-v1.4`.

Final archival sequence:

1. the release-candidate metadata commit `2543a310accacf8ecf69bba3e50b5ecb351383ab` passed remote Paper Artifact CI run #29;
2. this separate freeze-metadata commit records the frozen status, archival ref, and `date-released`;
3. rerun the full local validation / unit-test / Exp1A–5 suite and require zero committed-output diff;
4. push the freeze-metadata commit and require remote Paper Artifact CI to be green;
5. create immutable Git tag `v0.10.0-paper-v1.4` on that exact green commit;
6. verify remotely that the tag resolves to the exact freeze commit;
7. cite the frozen tag / commit in the manuscript rather than the moving branch.
