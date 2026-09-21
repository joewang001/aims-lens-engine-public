from __future__ import annotations
import math
from typing import Mapping


def _entropy(probabilities):
    return -sum(p * math.log(p) for p in probabilities if p > 0)


def _digamma(x: float) -> float:
    """Dependency-free digamma for positive x.

    Uses recurrence to x >= 8 followed by the standard asymptotic expansion.
    This is sufficient for deterministic reference calculations in the paper
    artifact and avoids adding a SciPy dependency.
    """
    if x <= 0:
        raise ValueError("digamma requires x > 0")

    result = 0.0
    while x < 8.0:
        result -= 1.0 / x
        x += 1.0

    inv = 1.0 / x
    inv2 = inv * inv
    result += (
        math.log(x)
        - 0.5 * inv
        - inv2
        * (
            1.0 / 12.0
            - inv2
            * (
                1.0 / 120.0
                - inv2
                * (
                    1.0 / 252.0
                    - inv2 * (1.0 / 240.0 - inv2 * (1.0 / 132.0))
                )
            )
        )
    )
    return result


def predictive_entropy_reduction(alpha: Mapping[str, float]) -> float:
    """Expected one-record reduction in posterior-predictive category entropy.

    This was the v1.3 implementation previously exposed as Eq. 15. It remains
    available as a separate diagnostic, but it is NOT parameter-posterior
    information gain.
    """
    keys = list(alpha)
    if not keys or any(float(alpha[k]) <= 0 for k in keys):
        raise ValueError("Dirichlet alpha values must all be positive")

    total = sum(float(alpha[k]) for k in keys)
    current = [float(alpha[k]) / total for k in keys]
    h0 = _entropy(current)
    expected_h = 0.0

    for i, key in enumerate(keys):
        outcome_prob = current[i]
        updated = {k: float(alpha[k]) for k in keys}
        updated[key] += 1.0
        z = sum(updated.values())
        h1 = _entropy([updated[k] / z for k in keys])
        expected_h += outcome_prob * h1

    return max(0.0, h0 - expected_h)


def expected_information_gain(alpha: Mapping[str, float]) -> float:
    """One-record parameter-posterior information gain for manuscript Eq. 15.

    Let Theta ~ Dirichlet(alpha) and the next already-authorized categorical
    record Y ~ Categorical(Theta). The expected reduction in posterior
    differential entropy,

        H[p(Theta | D)] - E_Y[H[p(Theta | D, Y)]],

    equals the mutual information I(Theta; Y). For a Dirichlet-categorical
    model this can be evaluated without explicitly computing Dirichlet
    differential entropies:

        I(Theta;Y)
          = H(E[Theta])
            + sum_k p_k * (psi(alpha_k + 1) - psi(alpha_0 + 1))

    where p_k = alpha_k / alpha_0 and psi is the digamma function.

    This score ranks the information expected from one *already-authorized*
    annotation. It does not authorize data collection and is distinct from
    predictive category-entropy reduction.
    """
    keys = list(alpha)
    if not keys or any(float(alpha[k]) <= 0 for k in keys):
        raise ValueError("Dirichlet alpha values must all be positive")

    values = [float(alpha[k]) for k in keys]
    total = sum(values)
    probabilities = [value / total for value in values]

    predictive_entropy = _entropy(probabilities)
    expected_conditional_entropy = -sum(
        p * (_digamma(a + 1.0) - _digamma(total + 1.0))
        for p, a in zip(probabilities, values)
    )
    information_gain = predictive_entropy - expected_conditional_entropy

    return max(0.0, information_gain)
