# Paper-to-Code Map

This map is the reviewer-oriented index for manuscript v1.3. It links paper claims to the smallest public artifact that makes the claim inspectable. Executable traceability is distinct from runtime integration; see `docs/IMPLEMENTATION_INTEGRATION_COVERAGE_MATRIX.md` for that separation.

| Paper location | Claim / object | Primary repo path |
|---|---|---|
| §3.2 | Structured Interview DNA | `schemas/interview_dna.schema.json`, `examples/paper/interview_dna.example.json` |
| §3.3 | Evidence packet / authorization boundary | `research_core/evidence.py`, `schemas/evidence_packet.schema.json` |
| §4.1 | Highest-specificity eligible Lens routing | `research_core/routing.py::select_highest_specificity` |
| §4.2 | Follow-up category selection before wording | `research_core/service.py` |
| §4.3 | Candidate-state isolation | `research_core/candidate_state.py` |
| §5.1 | Declared DAG / parent caps | `research_core/dag.py` |
| §5.2 Eq. 1 | DAG factorization | `research_core/dag.py::joint_factorization` |
| §5.2 Eq. 2 | Stopping logistic model | `research_core/stopping.py` |
| §5.2 Eq. 3 | Compatibility mask | `research_core/compatibility.py` |
| §5.3 Eq. 4 | Hierarchical pooling | `research_core/inference.py::hierarchical_partial_pooling` |
| §5.3 Eq. 5 | Weighted sufficient statistics | `research_core/evidence.py::weighted_counts` |
| §5.3 Eq. 6–7 | Dirichlet posterior / mean | `research_core/inference.py` |
| §5.4 Eq. 8–9 | Six-level mixture / provenance | `research_core/routing.py` |
| §5.5 Eq. 10–11 | Entropy / evidential support | `research_core/uncertainty.py` |
| §5.5 Eq. 12–13 | Brier / ECE | `research_core/evaluation.py` |
| §5.5 Eq. 14 | KL drift | `research_core/evaluation.py::kl_divergence` |
| §5.5 Eq. 15 | Annotation information gain | `research_core/active_learning.py` |
| §7.2 | De-identification protocol | `research_core/privacy.py` |
| §7.7 | Core controlled verification (Experiment 1A) | `docs/experiments/EXPERIMENT_1A_PROTOCOL.md`, `tools/run_exp1a_core_verification.py`, `examples/paper/experiments/exp1a/` |
| §7.7 | Lens/role-prior controls (Experiment 1B) | `docs/experiments/EXPERIMENT_1B_PROTOCOL.md`, `tools/run_exp1b_lens_differentiation.py`, `examples/paper/experiments/exp1b/` |
| §7.8 | Sensitivity and controlled ablations (Experiment 2) | `docs/experiments/EXPERIMENT_2_PROTOCOL.md`, `tools/run_exp2_sensitivity_ablation.py`, `examples/paper/experiments/exp2/` |
| §7.9 | Candidate-answer semantic regression (Experiment 3) | `docs/experiments/EXPERIMENT_3_PROTOCOL.md`, `tools/run_exp3_semantic_regression.py`, `examples/paper/experiments/exp3/` |
| §7.10 | End-to-end numeric trace and committed-output reproducibility | `examples/paper/experiments/exp1a/results/exp1a_baseline_trace.json`, `.github/workflows/paper-artifact-ci.yml` |
| v1.4 corrective | Hierarchy plug-in approximation benchmark (Experiment 5) | `docs/experiments/EXPERIMENT_5_PROTOCOL.md`, `tools/run_exp5_hierarchy_approximation.py`, `examples/paper/experiments/exp5/` |
| §8.2 | Minimized context boundary | `research_core/privacy.py::MinimizedContextPackage`, schema |
| §9.4 | Plain-language explanation | `research_core/explanation.py` |
| §9.5 | Auditable reconstruction | `research_core/audit.py` |
| Appendix B | Initial research parameters | `config/paper_defaults.json` |
| Appendix C | Candidate runtime plus standalone research utilities | `research_core/`, `tools/run_paper_artifact_demo.py`, `docs/IMPLEMENTATION_INTEGRATION_COVERAGE_MATRIX.md` |

Before freezing a manuscript v1.3 release, run the validator, unit tests, deterministic demo, Experiments 1A/1B/2/3, and the committed-output reproducibility gate defined in `.github/workflows/paper-artifact-ci.yml`.
