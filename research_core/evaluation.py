from __future__ import annotations
import math
from typing import Iterable, List, Sequence


def multiclass_brier(predictions: Sequence[Sequence[float]], outcomes: Sequence[int]) -> float:
    """Manuscript Eq. 12."""
    if len(predictions)!=len(outcomes) or not predictions: raise ValueError("shape mismatch or empty input")
    total=0.0
    for p,y in zip(predictions,outcomes):
        if not 0<=y<len(p): raise ValueError("outcome index out of range")
        total+=sum((pk-(1.0 if k==y else 0.0))**2 for k,pk in enumerate(p))
    return total/len(predictions)


def top_label_ece(
    predictions: Sequence[Sequence[float]],
    outcomes: Sequence[int],
    bins: int = 10,
) -> float:
    """Top-label expected calibration error for manuscript Eq. 13.

    Records are binned by the confidence of the predicted top class. Within
    each bin, compare mean top-label confidence with empirical top-label
    accuracy. This avoids cancellation between opposing class-vector errors
    that can occur in the legacy vector diagnostic.
    """
    if len(predictions) != len(outcomes) or not predictions:
        raise ValueError("shape mismatch or empty input")
    if bins <= 0:
        raise ValueError("bins must be positive")

    buckets = [[] for _ in range(bins)]
    for p, y in zip(predictions, outcomes):
        if not p or not 0 <= y < len(p):
            raise ValueError("outcome index out of range or empty prediction")
        predicted = max(range(len(p)), key=lambda j: p[j])
        confidence = float(p[predicted])
        if not 0.0 <= confidence <= 1.0:
            raise ValueError("top-label confidence must be in [0,1]")
        idx = min(bins - 1, int(confidence * bins))
        buckets[idx].append((confidence, 1.0 if predicted == y else 0.0))

    n = len(predictions)
    ece = 0.0
    for bucket in buckets:
        if not bucket:
            continue
        avg_confidence = sum(conf for conf, _ in bucket) / len(bucket)
        avg_accuracy = sum(correct for _, correct in bucket) / len(bucket)
        ece += (len(bucket) / n) * abs(avg_accuracy - avg_confidence)
    return ece


def vector_ece(
    predictions: Sequence[Sequence[float]],
    outcomes: Sequence[int],
    bins: int = 10,
) -> float:
    """Legacy supplementary vector-bin calibration diagnostic.

    Records are binned by maximum predicted probability and bin-level mean
    one-hot outcomes are compared with bin-level mean prediction vectors using
    L1 distance. Opposing class errors can cancel within a bin, so this metric
    is retained only for supplementary diagnostics and is not manuscript Eq. 13.
    """
    if len(predictions)!=len(outcomes) or not predictions:
        raise ValueError("shape mismatch or empty input")
    if bins <= 0:
        raise ValueError("bins must be positive")
    k=len(predictions[0]); buckets=[[] for _ in range(bins)]
    for p,y in zip(predictions,outcomes):
        if len(p) != k or not 0 <= y < len(p):
            raise ValueError("shape mismatch or outcome index out of range")
        conf=max(p); idx=min(bins-1,int(conf*bins)); buckets[idx].append((p,y))
    n=len(predictions); ece=0.0
    for bucket in buckets:
        if not bucket: continue
        avg_p=[sum(p[j] for p,_ in bucket)/len(bucket) for j in range(k)]
        avg_y=[sum(1.0 if y==j else 0.0 for _,y in bucket)/len(bucket) for j in range(k)]
        l1=sum(abs(a-b) for a,b in zip(avg_y,avg_p))
        ece += (len(bucket)/n)*l1
    return ece


def multiclass_log_loss(predictions: Sequence[Sequence[float]], outcomes: Sequence[int], epsilon: float=1e-15) -> float:
    if len(predictions)!=len(outcomes) or not predictions: raise ValueError("shape mismatch or empty input")
    return -sum(math.log(max(epsilon,min(1-epsilon,p[y]))) for p,y in zip(predictions,outcomes))/len(predictions)


def kl_divergence(p_new: Sequence[float], p_ref: Sequence[float], epsilon: float=1e-15) -> float:
    """Manuscript Eq. 14."""
    if len(p_new)!=len(p_ref): raise ValueError("shape mismatch")
    total=0.0
    for p,q in zip(p_new,p_ref):
        if p>0: total += p*math.log(p/max(q,epsilon))
    return total
