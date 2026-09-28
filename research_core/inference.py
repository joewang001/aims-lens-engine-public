from __future__ import annotations

import random
from typing import Dict, Iterable, List, Mapping, Tuple


def normalize(values: Mapping[str,float], categories: Iterable[str]) -> Dict[str,float]:
    cats=list(categories)
    total=sum(max(0.0,float(values.get(k,0.0))) for k in cats)
    if total <= 0:
        if not cats: return {}
        return {k:1.0/len(cats) for k in cats}
    return {k:max(0.0,float(values.get(k,0.0)))/total for k in cats}


def posterior_alpha(parent_distribution: Mapping[str,float], counts: Mapping[str,float], categories: Iterable[str], kappa: float) -> Dict[str,float]:
    """Dirichlet posterior parameters, manuscript Eq. 6."""
    if kappa <= 0: raise ValueError("kappa must be positive")
    cats=list(categories); parent=normalize(parent_distribution,cats)
    return {k:kappa*parent[k] + max(0.0,float(counts.get(k,0.0))) for k in cats}


def posterior_mean(alpha: Mapping[str,float]) -> Dict[str,float]:
    """Dirichlet posterior mean, manuscript Eq. 7."""
    total=sum(alpha.values())
    if total <= 0: raise ValueError("alpha mass must be positive")
    return {k:v/total for k,v in alpha.items()}


def hierarchical_dirichlet_mean(parent_distribution, counts, categories, kappa):
    return posterior_mean(posterior_alpha(parent_distribution, counts, categories, kappa))


def hierarchical_partial_pooling(
    generic_distribution: Mapping[str,float],
    archetype_counts: Mapping[str,float],
    industry_counts: Mapping[str,float],
    company_counts: Mapping[str,float],
    categories: Iterable[str],
    kappa_archetype: float,
    kappa_industry: float,
    kappa_company: float,
) -> Dict[str,Dict[str,float]]:
    """Reference implementation of manuscript Eq. 4–7 hierarchy.

    Generic pi -> archetype psi -> industry phi -> company theta. The return value
    exposes every level so borrowing is inspectable rather than hidden.
    """
    cats=list(categories)
    generic=normalize(generic_distribution,cats)
    archetype=hierarchical_dirichlet_mean(generic, archetype_counts,cats,kappa_archetype)
    industry=hierarchical_dirichlet_mean(archetype,industry_counts,cats,kappa_industry)
    company=hierarchical_dirichlet_mean(industry,company_counts,cats,kappa_company)
    return {"generic":generic,"archetype":archetype,"industry":industry,"company":company}


def sample_dirichlet(alpha: Mapping[str,float], draws: int=4000, seed: int=17) -> List[Dict[str,float]]:
    if draws <= 0: raise ValueError("draws must be positive")
    rng=random.Random(seed); keys=list(alpha)
    out=[]
    for _ in range(draws):
        vals=[rng.gammavariate(alpha[k],1.0) for k in keys]
        total=sum(vals)
        out.append({k:v/total for k,v in zip(keys,vals)})
    return out


def credible_intervals(alpha: Mapping[str,float], level: float=0.95, draws: int=4000, seed: int=17) -> Dict[str,Tuple[float,float]]:
    """Monte-Carlo marginal credible intervals for a Dirichlet posterior."""
    if not 0 < level < 1: raise ValueError("level must be in (0,1)")
    samples=sample_dirichlet(alpha,draws,seed); lo=(1-level)/2; hi=1-lo
    def q(xs,p):
        xs=sorted(xs); pos=p*(len(xs)-1); a=int(pos); b=min(a+1,len(xs)-1); f=pos-a
        return xs[a]*(1-f)+xs[b]*f
    return {k:(q([s[k] for s in samples],lo),q([s[k] for s in samples],hi)) for k in alpha}
