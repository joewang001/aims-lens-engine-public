from __future__ import annotations
from collections import defaultdict

class CandidateStateModel:
    """Candidate-side adaptation that never updates organization/industry Lens evidence."""
    def __init__(self, candidate_id: str):
        self.candidate_id=candidate_id; self.evidence_gaps=defaultdict(int); self.practice_history=[]; self.adaptation_consent=False
    def set_consent(self, allowed: bool): self.adaptation_consent=bool(allowed)
    def update_from_practice(self, practice_record: dict) -> None:
        if not self.adaptation_consent: return
        self.practice_history.append(practice_record)
        for gap in practice_record.get("evidence_gaps",[]): self.evidence_gaps[gap]+=1
    def get_practice_priority(self):
        return sorted(self.evidence_gaps,key=lambda k:(-self.evidence_gaps[k],k))
