"""Public-safe reference adapters for external integrations.

These adapters demonstrate contract-compatible normalization only. They do not
contain production JobACE scoring logic, tenant configuration, calibration, or
decision-policy bindings.
"""

from .candidate_signals import (
    AIMS_DIMENSIONS,
    CandidateSignal,
    CandidateSignalPacket,
    adapt_current_aims_scores,
)
from .jobace_v2 import (
    AdapterV2Envelope,
    ExternalIdentifiers,
    PracticeContext,
    adapt_jobace_payload_v2,
)

__all__ = [
    "AIMS_DIMENSIONS",
    "AdapterV2Envelope",
    "CandidateSignal",
    "CandidateSignalPacket",
    "ExternalIdentifiers",
    "PracticeContext",
    "adapt_current_aims_scores",
    "adapt_jobace_payload_v2",
]
