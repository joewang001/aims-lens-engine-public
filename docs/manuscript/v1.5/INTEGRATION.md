# Manuscript v1.5 integration

Status: manuscript integration candidate; not a frozen release or submission-ready package.

Base: `5b5cd3cc1e332f7b57f7d62cc62676467a91c8a3` (Commit D).
Result-bearing baseline: `3f2a4d3b8ebfdf2535233e76ac6cc4debd0a1a75` (Commit C).
Branch: `paper-routing-ablation-v1.5`.
Frozen v1.4 remains `v0.10.0-paper-v1.4` at `a0d89f33aaa7303404a9b26cc7bec5a331a6e82f`.

## Revision coverage

| Item | Integration |
|---|---|
| M1 | Title and abstract narrowed to evidence governance; Contributions 4–6 distinguish mechanisms, routing policy weights, calibration protocol, and claims gates. Title page and cover letter synchronized. |
| M2 | Section 7.12 and Table 6 identify Experiment 5 as a synthetic binary latent-parameter hierarchy-approximation benchmark; fixed K=2, root π=0.5 and concentrations 8; observations at three levels; quadrature and conditional Beta mixture; numerical-convergence-only PASS; no SBC, coverage, or general K-category validation. |
| M3 | Section 5.2 describes Eq.3 as deterministic policy masking, not a posterior update or calibration-preserving operation; zero permitted mass fails closed. |
| M4 | Section 5.4 uses routing decision distribution notation; raw scores and positive-score/positive-permitted-mass active set precede normalization; binary gates and declared coverage are distinguished from posterior probabilities and data support. |
| M5 | Section 5.5, Table 5 and Supplementary Table S5 distinguish model-internal, masked, and released routed distributions; final released output is the primary external calibration target. Synthetic held-out diagnostics do not establish external calibration. |
| M6 | Section 7.5 separates executable runtime abstention from empirical claim gating; calibration failure alone need not trigger runtime abstention. τ=8 and threshold 0.3 remain illustrative fixture inputs. |
| S2 | Section 9.5 and Supplementary Listing S9 distinguish full runtime routing provenance from the minimal AuditRecord; the minimal record alone cannot reconstruct weights. |
| S3 | Contribution 11 and Sections 7.10/10.3 label controlled verification and explicitly retain unexecuted A1/A5. |
| S4 | Section 5.4 and Supplementary Tables S11/S13 identify 0.78/0.92/1.00 as fixture coverage constants; no automatic EvidencePacket-to-coverage estimator exists. |
| Experiment 6 | Section 7.13, Table 6, limitations, conclusion and Supplementary Section S5 integrate design, positive and negative results, reporting conventions, cross-environment reproducibility, and claim limits. |

## Result checks

All numerical summaries were checked against the committed 81-row condition matrix, without rerunning the result-bearing experiment.

- Mean log loss improves in 71/81 conditions; Brier in 71/81; TV in 70/81.
- All ten worsened mean-log-loss conditions have ρ=0.8.
- Equal-condition mean deltas: log loss −0.03146, Brier −0.01116, TV −0.02853.
- Largest mean log-loss degradation: n=50, ρ=0.8, κ=20, γ=0.9; ΔLL +0.03783, ΔBrier +0.01517, ΔTV +0.05976, routing shift 0.11576; 2.8% of paired replicates improve log loss.
- Largest mean log-loss improvement: n=2, ρ=0.1, κ=2, γ=0.9; ΔLL −0.17141.
- Supplementary S5 reports held-out scores for both extreme conditions and identifies 5th/95th percentiles as replicate-distribution percentiles, not confidence intervals.

Result hashes remain:

| File | SHA-256 |
|---|---|
| exp6_results.json | 4adaf9d5a67bfd1ea9bd591462f0459551e73382d9733c56bfd39cc902646140 |
| exp6_condition_matrix.csv | b2513cfdefbb78d72e49ad2ea88d1d706f6e0fedbd8dd45becf92ff3f54d0058 |
| exp6_paired_deltas.csv | 43c8558ff7a38405209645b554428aa59bec584e2b96701f99d9615d0e3f7c68 |

## Validation and remaining gates

- Paper artifact validator: PASS.
- Documentation alignment validator: PASS.
- Unit tests: 33/33 PASS.
- DOCX ZIP/XML integrity and native mathematical-object check: PASS; all 14 main-manuscript math objects remain editable. Equation 8 and 9 OMML structures were rebuilt to correct subscript/superscript attachment exposed by rendering; the other 12 math objects are unchanged.
- Reviewer-facing XML/relationships identity scan: PASS for author name, reference-integration identity, public repository identity, contact address, and full commit SHA.
- Highlights: four items, each within 85 characters.
- Visual QA: PASS. Native Word 16 SaveAs2 with PDF format 17 succeeded in the logged-on Windows user environment. All 47 pages were inspected: main manuscript 27, supplement 15, and five ancillary documents with one page each. Equation 8/9 script positioning and Table 6/S5/S11/S13 widths and typography were corrected and re-rendered. Source DOCX hashes were verified unchanged by export. The packaged renderer lacked LibreOffice; earlier Runner export calls timed out, and their precise failure cause remains undetermined. PDF/page-image files are local QA artifacts, outside the repository.
- Local Commit E scope: two blinded manuscript DOCX files, this integration record, and v1.5 candidate documentation/metadata/validator alignment. Publication and release remain pending.
- Final v1.5 freeze/tag, anonymous reviewer snapshot synchronization and submission remain separate outstanding gates.

The earlier v1.5 draft contained copied v1.4 README/QA status files; those historical claims must not be treated as validation of these revised documents.
No protocol, fixtures, scientific runtime, experiment runner, or committed result files were changed for this manuscript integration. No PR merge, push, release tag, or submission is part of this local integration step.
