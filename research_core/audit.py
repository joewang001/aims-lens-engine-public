from __future__ import annotations
from dataclasses import dataclass
from typing import List

@dataclass(frozen=True)
class AuditRecord:
    audit_id: str; timestamp: str; lens_id: str; lens_version: str; lens_type: str; maturity: str
    context_hash: str; parent_config: dict; primary_category: str; alternatives: List[str]
    diagnostic_weight: float; explanation: str; evidence_packet_ids: List[str]
    routing_level: str; backoff_distance: int
    def reconstruct(self) -> dict:
        return {"lens":self.lens_id,"version":self.lens_version,"context_hash":self.context_hash,"parent_config":self.parent_config,"decision":self.primary_category,"diagnostic_weight":self.diagnostic_weight,"evidence":self.evidence_packet_ids,"routing":self.routing_level,"backoff":self.backoff_distance}
