# Validation Checklist

## Fully Distilled Lens Gate

A company lens cannot be marked `FULLY_DISTILLED` until all checks pass.

### 1. Source Coverage

Required:

- official company sources
- hiring or recruiting signals
- interview question patterns
- at least one external or critical source

Preferred:

- executive primary sources
- employee voice sources
- decision case sources

### 2. Evidence Quality

Check:

- source type is recorded
- access date is recorded
- publish date is recorded when available
- confidence is assigned
- signal maps to AIMS dimensions
- major claims have evidence ids

### 3. Cross-Source Support

Promote a signal to company-level principle only if:

- two independent source categories support it, or
- one authoritative company-provided private source supports it

Otherwise downgrade it to a lower-confidence note.

### 4. Copyright and Use

Check:

- no large copied interview question bank
- public question patterns are summarized
- generated questions are original variants
- source references are retained

### 5. AIMS Mapping

Check:

- all six AIMS dimensions are represented
- weights are justified
- company-specific interpretations are concrete
- generic traits are not repeated as company-specific insights

### 6. Same-Answer Cross-Lens Test

Run the same answer through at least three lenses.

Pass condition:

- feedback differs in value lens, not only wording
- score explanation reflects company priorities
- follow-up questions differ by company

### 7. Strong, Average, Weak Answer Test

Each lens must evaluate:

- strong answer
- average answer
- weak answer

Pass condition:

- score separation is visible
- weak answers are not discarded as non-answers
- improvement advice is company-specific

### 8. No-Evidence Uncertainty Test

Ask a question outside the evidence base.

Pass condition:

- system avoids unsupported claims
- output states uncertainty
- system falls back to general AIMS or derived reasoning

### 9. B2B Screening Safety

Check:

- screening report explains reasoning
- low confidence returns `human_review_required`
- protected characteristics are not used
- adverse decisions are framed as decision support

### 10. Version and Limits

Check:

- `source_cutoff` exists
- version exists
- honest limits are present
- public/private visibility is correct
