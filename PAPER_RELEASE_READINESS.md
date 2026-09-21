# Paper Release Readiness — v1.4 Corrective Research Release

Target branch: `paper-math-alignment-v1.4`
Previous frozen tag: `v0.9.2-paper-v1.3`
Previous frozen commit: `f7fcb6a3129cb58fe20c414f1abe519376def8e1`
v1.4 corrective experimental baseline: `c18899b469e1d579391306872d5834ebf6e3caf3`
Release artifact version: **`0.10.0-paper-v1.4`**
Target immutable tag: **`v0.10.0-paper-v1.4`**
Current release status: **frozen metadata** — tag creation remains gated on this exact commit passing remote CI.

## Objective

Record the final v1.4 freeze metadata without modifying or moving the frozen v1.3 history, then gate immutable tag creation on the exact freeze commit passing remote CI.

The v1.4 release preserves the candidate-side interview-practice research boundary. It records the completed internal mathematical–implementation corrections while keeping external-validity claims explicitly out of scope.

## Corrective scope

The v1.4 release candidate includes:

- **F1 — Eq. 15:** parameter-information-gain alignment;
- **F2 — calibration:** top-label ECE correction;
- **F3 — support:** permitted-category evidence support;
- **F4 — routing:** zero-permitted-mass fail-closed behavior;
- **F5 — hierarchy:** synthetic benchmark of the **recursive plug-in hierarchical Dirichlet shrinkage** approximation;
- **F6 — coverage:** explicit implementation / runtime integration / evaluation / experiment / external-validation matrix.

For the recursive plug-in hierarchy, reported credible intervals are **conditional Dirichlet intervals given the plug-in parent distribution**. They are not presented as full hierarchical posterior uncertainty propagation.

## Experiment interpretation boundary

- **Experiments 1A/1B/2/3** remain controlled verification / sensitivity / ablation / semantic-regression evidence.
- **Experiment 4** is internal mathematical–implementation correction evidence.
- **Experiment 5** is a synthetic approximation benchmark.
- None of these experiments establish real-employer validity, population fairness, employer-behavior prediction, interview-improvement efficacy, or employment-outcome efficacy.

## Freeze-metadata state

The freeze-metadata commit records the final release identity while keeping tag creation as a post-CI action:

- `VERSION`: `0.10.0-paper-v1.4`;
- `CITATION.cff`: version `0.10.0-paper-v1.4`, `date-released: 2026-09-21`;
- `paper_artifact_manifest.yaml`: `paper_version: v1.4`, `release_status: frozen`;
- `frozen_artifact_ref: v0.10.0-paper-v1.4`;
- `target_release_tag: v0.10.0-paper-v1.4`;
- README files state the immutable archival ref and the rule that the tag is created only after this exact freeze commit passes remote CI.

The previous frozen v1.3 tag and commit remain immutable historical references.

## v1.4 paper-artifact coverage

The paper allowlist includes the existing v1.3 research core plus the v1.4 corrective assets, including:

- `docs/experiments/EXPERIMENT_4_PROTOCOL.md`;
- `docs/experiments/EXPERIMENT_5_PROTOCOL.md`;
- `examples/paper/experiments/exp4/`;
- `examples/paper/experiments/exp5/`;
- `tools/run_exp4_adversarial_alignment.py`;
- `tools/run_exp5_hierarchy_approximation.py`;
- `docs/IMPLEMENTATION_INTEGRATION_COVERAGE_MATRIX.md`;
- `tools/validate_documentation_alignment.py`;
- bilingual root README metadata needed by documentation alignment.

## Freeze validation gates

For the freeze-metadata commit, all of the following must pass locally before push and remotely before tag creation:

```bash
python tools/validate_paper_artifact.py
python tools/validate_documentation_alignment.py
python -m unittest discover -s tests -v
python tools/run_paper_artifact_demo.py
python tools/run_exp1a_core_verification.py
python tools/run_exp1b_lens_differentiation.py
python tools/run_exp2_sensitivity_ablation.py
python tools/run_exp3_semantic_regression.py
python tools/run_exp4_adversarial_alignment.py
python tools/run_exp5_hierarchy_approximation.py
git diff --exit-code -- examples/paper/experiments
```

Expected gate state:

- Exp1A / Exp1B / Exp2 / Exp3 / Exp4 / Exp5: PASS;
- unit tests: PASS;
- paper artifact validator: PASS;
- documentation alignment: PASS;
- committed experiment outputs: zero diff;
- remote Paper Artifact CI: GREEN.

## Tag finalization sequence

The release-candidate commit `2543a310accacf8ecf69bba3e50b5ecb351383ab` passed remote Paper Artifact CI run #29. The remaining archival sequence is:

1. commit this **separate freeze-metadata change**;
2. rerun the full local validation suite;
3. push the freeze-metadata commit and require remote Paper Artifact CI to pass;
4. create immutable tag `v0.10.0-paper-v1.4` on that exact green freeze commit;
5. verify remotely that the tag resolves to that exact commit;
6. update manuscript Code and Artifact Availability wording to cite the frozen tag / commit.

Do not create or advertise the v1.4 tag as existing before this exact freeze commit is green.

## Historical immutability

The following historical artifact must not be rewritten, retagged, force-moved, or otherwise altered:

- tag: `v0.9.2-paper-v1.3`;
- commit: `f7fcb6a3129cb58fe20c414f1abe519376def8e1`.

PR #6 and PR #7 remain outside this release procedure unless explicitly requested.
