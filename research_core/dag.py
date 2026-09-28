from __future__ import annotations

from collections import deque
from typing import Dict, Iterable, Mapping, Sequence

PARENT_CARDINALITY_CAPS = {
    "stage": 5,
    "role_level": 5,
    "competency": 6,
    "evidence_gap": 7,
    "prior_followup": 7,
    "time_remaining": 3,
}


def validate_dag(parents: Mapping[str, Sequence[str]]) -> None:
    """Validate that declared dependencies are acyclic and parent references exist."""
    nodes=set(parents)
    for ps in parents.values():
        nodes.update(ps)
    indegree={n:0 for n in nodes}
    children={n:[] for n in nodes}
    for child, ps in parents.items():
        for parent in ps:
            children[parent].append(child)
            indegree[child]+=1
    q=deque(n for n,d in indegree.items() if d==0)
    visited=0
    while q:
        n=q.popleft(); visited+=1
        for c in children[n]:
            indegree[c]-=1
            if indegree[c]==0:
                q.append(c)
    if visited != len(nodes):
        raise ValueError("declared dependency graph contains a cycle")


def joint_factorization(local_conditionals: Mapping[str, float]) -> float:
    """Product of declared local conditionals, manuscript Eq. 1.

    The caller is responsible for computing each p(z_j | Pa(j), L). This function
    deliberately does not infer undeclared edges.
    """
    product=1.0
    for node,p in local_conditionals.items():
        if not 0.0 <= p <= 1.0:
            raise ValueError(f"conditional probability for {node} must be in [0,1]")
        product*=p
    return product


def parent_configuration_count(cardinalities: Iterable[int]) -> int:
    total=1
    for c in cardinalities:
        if c <= 0:
            raise ValueError("cardinalities must be positive")
        total*=c
    return total
