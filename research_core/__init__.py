"""AIMS Lens Engine manuscript reference implementation.

This package reproduces the paper's public mathematical and decision logic. It is
not the complete JobACE or any tenant's production implementation.
"""
from .models import EvidenceRecord, PracticeRequest, RoutingLevel
from .service import prioritize_followups
__all__=["EvidenceRecord","PracticeRequest","RoutingLevel","prioritize_followups"]
