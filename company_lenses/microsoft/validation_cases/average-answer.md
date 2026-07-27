# Average Answer Validation Case

Status: passed static review.

## Interview Question

MSFT-Q-002: You inherit a service where a recent change caused intermittent failures that are hard to reproduce. Walk me through how you would clarify the problem, investigate the data, fix it, and test confidence.

## Candidate Answer

I would look at logs and try to reproduce the issue. Then I would check recent commits and roll back if needed. After fixing it, I would add a test so it does not happen again.

## Expected Lens Behavior

- Moderate technical signal.
- Needs stronger clarification, hypothesis-driven debugging, monitoring, and customer impact analysis.

## Result

Pass.
