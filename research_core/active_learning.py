from __future__ import annotations
import math
from typing import Mapping


def _entropy(probabilities):
    return -sum(p*math.log(p) for p in probabilities if p>0)


def expected_information_gain(alpha: Mapping[str,float]) -> float:
    """One-record Dirichlet reference operationalization of manuscript Eq. 15.

    H is predictive categorical entropy. The expectation is taken over the
    current posterior-predictive outcome for the next *already-authorized* record.
    This is a reference acquisition score, not authorization to collect data.
    """
    keys=list(alpha); total=sum(alpha.values())
    if total<=0: raise ValueError("alpha mass must be positive")
    current=[alpha[k]/total for k in keys]; h0=_entropy(current); expected_h=0.0
    for i,k in enumerate(keys):
        outcome_prob=current[i]
        updated=dict(alpha); updated[k]+=1.0; z=sum(updated.values())
        h1=_entropy([updated[j]/z for j in keys])
        expected_h += outcome_prob*h1
    return h0-expected_h
