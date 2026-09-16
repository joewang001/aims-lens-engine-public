from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Iterable, List, Tuple
from .inference import normalize

BACKOFF_SEQUENCE = [
    ("L0_full_parent_context",0),
    ("L1_drop_one_parent",1),
    ("L2_drop_two_parents",2),
    ("L3_industry_context",3),
    ("L4_archetype_context",4),
    ("L5_generic_context",5),
]


def route_mixture(levels, categories: Iterable[str], gamma: float) -> Tuple[Dict[str,float],List[dict]]:
    """Implements manuscript Eq. 8–9."""
    if not 0 < gamma <= 1: raise ValueError("gamma must be in (0,1]")
    cats=list(categories); components=[]
    for level in levels:
        level.validate()
        a=1.0 if level.authorized else 0.0
        s=1.0 if level.applicable else 0.0
        raw=a*s*level.coverage*(gamma**level.backoff_distance)
        if raw>0:
            components.append((level,raw,normalize(level.distribution,cats)))
    if not components: return {},[]
    z=sum(w for _,w,_ in components); mix={k:0.0 for k in cats}; provenance=[]
    for level,raw,dist in components:
        omega=raw/z
        for k in cats: mix[k]+=omega*dist[k]
        provenance.append({"level":level.name,"backoff_distance":level.backoff_distance,"authorization":level.authorized,"applicability":level.applicable,"coverage":round(level.coverage,6),"routing_weight":round(omega,6)})
    return normalize(mix,cats),provenance


@dataclass(frozen=True)
class LensCandidate:
    lens_id: str
    specificity_rank: int
    authorized: bool
    fresh: bool
    maturity_allows_output: bool
    applicable: bool


def select_highest_specificity(candidates: Iterable[LensCandidate]) -> LensCandidate | None:
    eligible=[c for c in candidates if c.authorized and c.fresh and c.maturity_allows_output and c.applicable]
    return max(eligible,key=lambda c:c.specificity_rank) if eligible else None
