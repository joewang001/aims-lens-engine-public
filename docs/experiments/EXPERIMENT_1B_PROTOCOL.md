# Experiment 1B — Controlled Lens and Role-Prior Differentiation

## Purpose
Test whether the paper-core output changes only when the declared Lens/role prior changes while candidate-side state, evidence mass, hyperparameters, routing coverage, and generic fallback are held fixed. This is structural verification, not employer-behavior validation.

## Categories
The six AIMS dimensions are used directly as declared practice-priority categories: structured_thinking, analytical_problem_solving, ownership_execution, impact_results, collaboration_communication, and growth_mindset. No hand-authored mapping to the five-category demo is introduced.

## Fixed controls
Every case uses one authorized synthetic observation per category (quality 0.5, age 0), kappa_company=10, routing_gamma=0.7, support_tau=8, abstention_threshold=0, all categories permitted, and coverage=1.0. Symmetric evidence ensures between-case differences come from declared priors/routing distributions.

## Study 1 — Company-prior positive control
Hold a common SWE role-archetype prior fixed and vary only company-profile AIMS priors for Amazon, Google, and JPMorgan Chase. Every pair must have non-zero total-variation distance. Expected top categories: Amazon=ownership_execution; Google=analytical_problem_solving; JPMorgan Chase=analytical_problem_solving.

## Study 2 — Company-label negative control
RBC, CIBC, and BMO use the same retail-banking role prior. At the audited source versions, the selected company profiles share the same AIMS weighting and selected retail-banking overlays share the same role weighting. Complete paper-core result objects must therefore be identical. TV=0 is required. If company labels alone change output, the experiment fails.

## Study 3 — Role-prior positive control
Historical shared-answer text is retained as provenance only and is not passed to paper core. Vary role priors across SWE, Data Analytics, Retail Banking, Risk/Compliance, and Consulting Case/PEI. Expected tops: analytical_problem_solving, analytical_problem_solving, impact_results, analytical_problem_solving, structured_thinking respectively. Five distinct distributions and at least two distinct top categories are required.

## Metrics and determinism
Record mode, top_category, priority_order, diagnostic_distribution, entropy, data support, effective evidence mass, routing provenance, pairwise TV distance, exact-equality flags, and canonical SHA-256. Run twice on the same experiment-base commit; JSON/CSV hashes must match exactly.

## Boundary
Historical advance/hold/reject semantics are excluded. This experiment does not validate named-employer behavior, candidate learning outcomes, hiring outcomes, or employment decisions.
