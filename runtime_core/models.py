from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class EvidenceRecord:
    """Minimal evidence record used by the production runtime primitives."""

    category: str
    authorized: bool
    quality: float
    age_days: float

    def validate(self) -> None:
        if not self.category:
            raise ValueError("evidence category must not be empty")
        if not math.isfinite(self.quality) or not 0.0 <= self.quality <= 1.0:
            raise ValueError("quality must be in [0,1]")
        if not math.isfinite(self.age_days) or self.age_days < 0.0:
            raise ValueError("age_days must be non-negative")
