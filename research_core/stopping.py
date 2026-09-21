from __future__ import annotations
import math
from typing import Mapping


def sigmoid(x: float) -> float:
    if x >= 0:
        z=math.exp(-x)
        return 1.0/(1.0+z)
    z=math.exp(x)
    return z/(1.0+z)


def stopping_probability(intercept: float, coefficients: Mapping[str,float], features: Mapping[str,float]) -> float:
    """Regularized-logistic model form from manuscript Eq. 2.

    Regularization is a fitting-time concern; this function evaluates a fitted
    coefficient vector without claiming that coefficients have been empirically estimated.
    """
    linear=intercept + sum(coefficients.get(k,0.0)*float(v) for k,v in features.items())
    return sigmoid(linear)
