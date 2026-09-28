from __future__ import annotations
import re
from dataclasses import asdict, dataclass
from typing import Callable, Optional

@dataclass(frozen=True)
class MinimizedContextPackage:
    role_level: str
    stage: str
    competency: str
    evidence_gap_signal: str
    prior_followup: Optional[str]
    time_remaining: str
    requested_lens_id: Optional[str]
    def to_dict(self): return asdict(self)


def deidentify_transcript(raw_transcript: str, named_entity_replacer: Callable[[str],str] | None=None) -> str:
    """Reference de-identification pipeline corresponding to Listing 6.

    Contact and date patterns are handled locally. Names/companies/locations require
    a reviewed environment-specific NER/replacement function; this reference code
    intentionally does not claim production-grade de-identification accuracy.
    """
    text=raw_transcript
    text=re.sub(r'\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b','[CONTACT]',text)
    text=re.sub(r'(?<!\w)(?:\+?\d[\d ()-]{7,}\d)(?!\w)','[CONTACT]',text)
    text=re.sub(r'\b\d{4}-\d{2}-\d{2}\b','[DATE]',text)
    if named_entity_replacer is not None: text=named_entity_replacer(text)
    return text
