# Paper Release Readiness — v1.5 Routing-Ablation Research Release

Target branch: `paper-routing-ablation-v1.5`
Previous frozen tag: `v0.10.0-paper-v1.4`
Previous frozen commit: `a0d89f33aaa7303404a9b26cc7bec5a331a6e82f`
v1.5 result-bearing Experiment 6 baseline: `3f2a4d3b8ebfdf2535233e76ac6cc4debd0a1a75`
Release-candidate Commit E: `79ccb9ea039e6320101b58e732da0a182bb7b973`
Release-candidate CI: Paper Artifact CI #32 / run `36465884041` — PASS
Release artifact version: **`0.11.0-paper-v1.5`**
Target immutable tag: **`v0.11.0-paper-v1.5`**
Current release status: **frozen metadata** — tag creation remains gated on this exact commit passing the complete remote Paper Artifact CI.

## Objective

Record the final v1.5 freeze metadata without modifying the scientific runtime, experiment protocols, runners, committed experiment results, or manuscript scientific content, then gate immutable tag creation on the exact freeze commit passing remote CI.

The v1.5 release preserves the candidate-side interview-practice research boundary and integrates the pre-specified K=5 Experiment 6 routing–shrinkage overlap ablation. Experiment 6 is controlled architecture evidence with regime-dependent results; it does not establish external calibration, employer-behavior prediction, population fairness, interview-improvement efficacy, or employment-outcome efficacy.

## v1.5 scientific scope

The v1.5 release retains Experiments 1A–5 and adds:

- **Experiment 6 — routing–shrinkage overlap ablation:** K=5, 81 factorial conditions, 40,500 paired L0-only versus routed realizations, and 8.1 million synthetic held-out observations;
- explicit reporting that routing can help in sparse/aligned regimes and can worsen scores under strong broader-context mismatch;
- cross-environment byte-for-byte Experiment 6 output reproducibility on Windows/Python 3.11 and GitHub Actions Ubuntu/Python 3.11;
- narrower claim language separating policy-constrained routing distributions from automatically calibrated posterior-predictive claims;
- explicit limitations for Experiment 5 as a synthetic binary latent-parameter hierarchy-approximation benchmark.

## Freeze-metadata state

This freeze-metadata commit records the final release identity while keeping tag creation as a post-CI action:

- `VERSION`: `0.11.0-paper-v1.5`;
- `CITATION.cff`: version `0.11.0-paper-v1.5`, `date-released: 2026-09-28`;
- `paper_artifact_manifest.yaml`: `paper_version: v1.5`, `release_status: frozen`;
- `frozen_artifact_ref: v0.11.0-paper-v1.5`;
- `target_release_tag: v0.11.0-paper-v1.5`;
- README files state the immutable archival ref and the rule that the tag is created only after this exact freeze-metadata commit passes remote CI.

The previous frozen v1.4 tag and commit remain immutable historical references.

## Release-candidate verification baseline

Commit E `79ccb9ea039e6320101b58e732da0a182bb7b973` was verified before freeze:

- Paper Artifact CI #32 / run `36465884041`: PASS;
- paper artifact validator: PASS;
- documentation alignment validator: PASS;
- unit tests: 33/33 PASS;
- deterministic demo: PASS;
- Experiments 1A–6: PASS;
- committed experiment outputs: zero diff;
- local worktree was clean and local/remote ahead/behind was 0/0 before this freeze edit.

The Experiment 6 committed result hashes remain those recorded in `docs/manuscript/v1.5/INTEGRATION.md`; this freeze commit must not change those files.

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
python tools/run_exp6_routing_overlap_ablation.py
git diff --exit-code -- examples/paper/experiments
git diff --check
```

Expected gate state:

- Exp1A / Exp1B / Exp2 / Exp3 / Exp4 / Exp5 / Exp6: PASS;
- unit tests: 33/33 PASS;
- paper artifact validator: PASS;
- documentation alignment: PASS;
- committed experiment outputs: zero diff;
- remote Paper Artifact CI: GREEN.

## Tag finalization sequence

The release-candidate Commit E `79ccb9ea039e6320101b58e732da0a182bb7b973` passed Paper Artifact CI #32. The remaining archival sequence is:

1. create this **separate freeze-metadata commit**;
2. rerun the complete local freeze validation suite;
3. push the freeze-metadata commit and require remote Paper Artifact CI to pass;
4. create immutable tag `v0.11.0-paper-v1.5` on that exact green freeze commit;
5. verify remotely that the tag resolves to the exact freeze commit;
6. synchronize the anonymous reviewer snapshot and manuscript artifact citation;
7. keep the v1.5 frozen branch/tag history immutable.

Do not create or advertise `v0.11.0-paper-v1.5` as existing before this exact freeze commit is green.

## Historical immutability

The following frozen artifacts must not be rewritten, retagged, force-moved, or otherwise altered:

- v1.4 tag: `v0.10.0-paper-v1.4`;
- v1.4 commit: `a0d89f33aaa7303404a9b26cc7bec5a331a6e82f`.

PR #6 and PR #7 remain outside this release procedure unless explicitly requested.
