# Average Answer Validation Case

Status: passed static review.

## Interview Question

AMZ-Q-003: A team wants to launch a feature quickly because it may improve a key business metric, but the customer problem is not clearly proven. How would you decide whether to launch, delay, or redesign the plan?

## Candidate Answer

I would first ask why the team believes the feature will improve the metric and look at the data behind that assumption. If the data is strong, I would probably launch an MVP to a small group. If the data is weak, I would delay and do more discovery.

I would talk to product, engineering, and maybe customer support to understand the problem. I would also define success metrics before launch. If we launch, I would monitor the metric and roll back if it performs badly.

## Expected Lens Behavior

- Score moderate on analytical problem-solving because the answer mentions data, MVP, success metrics, and rollback.
- Score moderate on structured thinking because it gives a basic launch/delay framework.
- Do not score high because the customer problem remains underdeveloped, decision reversibility is only implicit, and risks are not concrete.
- Follow-up should ask for customer evidence, what minimum data is enough, what harms could occur, and how reversibility changes speed.

## Actual Lens Output

Expected v0.1 output:

- Average Amazon fit signal.
- Primary dimensions: `analytical_problem_solving`, `structured_thinking`.
- Feedback should say the answer is directionally sound but too generic for a strong Amazon-style decision case.
- Follow-up should ask the candidate to define the customer problem, decision type, risk boundaries, and exact metrics.

## Result

Pass. The rubric avoids over-crediting generic product judgment and requires sharper customer-backwards reasoning, risk definition, and decision mechanism.
