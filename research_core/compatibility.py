from __future__ import annotations
from typing import Dict, Iterable


def masked_and_renormalized(distribution: Dict[str,float], categories: Iterable[str], permitted_categories: Iterable[str]) -> Dict[str,float]:
    """Implements manuscript Eq. 3: q_k ∝ M_k p_k."""
    cats=list(categories); permitted=set(permitted_categories)
    masked={k:(max(0.0,distribution.get(k,0.0)) if k in permitted else 0.0) for k in cats}
    total=sum(masked.values())
    if total <= 0:
        return {}
    return {k:v/total for k,v in masked.items() if k in permitted}
