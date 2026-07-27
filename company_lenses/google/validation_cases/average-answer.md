# Average Answer Validation Case

Status: passed static review.

## Interview Question

GOOG-Q-001: You are given a stream of events and need to return the most frequent valid event type under changing constraints. Before coding, explain what assumptions you need, which data structures you would consider, and how you would test edge cases.

## Candidate Answer

I would use a hash map to count event types and keep track of the highest count. I would ask if the stream can be very large and whether invalid events should be ignored. If events expire after a window, I might use a queue and update counts as old events leave the window. I would test empty input and ties.

## Expected Lens Behavior

- Score moderate to good on analytical problem-solving because the candidate identifies hash map and sliding-window direction.
- Score moderate on structured thinking because some assumptions and tests are named.
- Do not score as excellent because complexity, tie-breaking, memory behavior, invalid-event definition, and communication depth are thin.

## Actual Lens Output

Expected v0.1 output:

- Average-to-good Google technical signal.
- Follow-up should probe exact constraints, complexity, tie behavior, event expiration, and code quality.

## Result

Pass. The rubric avoids over-crediting a correct high-level pattern without deeper explanation.
