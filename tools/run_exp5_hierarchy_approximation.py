#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from research_core.inference import hierarchical_partial_pooling, posterior_alpha

FIXTURE_PATH = ROOT / "examples/paper/experiments/exp5/fixtures.json"
OUT_DIR = ROOT / "examples/paper/experiments/exp5/results"


def log_beta(a: float, b: float) -> float:
    if a <= 0 or b <= 0:
        raise ValueError("Beta parameters must be positive")
    return math.lgamma(a) + math.lgamma(b) - math.lgamma(a + b)


def beta_continued_fraction(
    a: float,
    b: float,
    x: float,
    max_iter: int = 200,
    epsilon: float = 3e-14,
) -> float:
    qab = a + b
    qap = a + 1.0
    qam = a - 1.0
    tiny = 1e-300

    c = 1.0
    d = 1.0 - qab * x / qap
    if abs(d) < tiny:
        d = tiny
    d = 1.0 / d
    h = d

    for m in range(1, max_iter + 1):
        m2 = 2 * m

        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        if abs(d) < tiny:
            d = tiny
        c = 1.0 + aa / c
        if abs(c) < tiny:
            c = tiny
        d = 1.0 / d
        h *= d * c

        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        if abs(d) < tiny:
            d = tiny
        c = 1.0 + aa / c
        if abs(c) < tiny:
            c = tiny
        d = 1.0 / d
        delta = d * c
        h *= delta

        if abs(delta - 1.0) < epsilon:
            return h

    raise RuntimeError("incomplete-beta continued fraction did not converge")


def regularized_beta(x: float, a: float, b: float) -> float:
    if a <= 0 or b <= 0:
        raise ValueError("Beta parameters must be positive")
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0

    log_bt = (
        math.lgamma(a + b)
        - math.lgamma(a)
        - math.lgamma(b)
        + a * math.log(x)
        + b * math.log1p(-x)
    )
    bt = math.exp(log_bt)

    if x < (a + 1.0) / (a + b + 2.0):
        return bt * beta_continued_fraction(a, b, x) / a

    return 1.0 - bt * beta_continued_fraction(b, a, 1.0 - x) / b


def beta_ppf(q: float, a: float, b: float, iterations: int) -> float:
    if not 0.0 < q < 1.0:
        raise ValueError("quantile must be in (0,1)")
    lo, hi = 0.0, 1.0
    for _ in range(iterations):
        mid = (lo + hi) / 2.0
        if regularized_beta(mid, a, b) < q:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2.0


def logsumexp(values: list[float]) -> float:
    if not values:
        raise ValueError("logsumexp requires values")
    maximum = max(values)
    return maximum + math.log(
        math.fsum(math.exp(value - maximum) for value in values)
    )


def midpoint_grid(points: int) -> list[float]:
    if points <= 0:
        raise ValueError("grid points must be positive")
    return [(index + 0.5) / points for index in range(points)]


def plugin_stats(
    base_probability: float,
    kappa_archetype: float,
    kappa_industry: float,
    kappa_company: float,
    archetype_counts: tuple[int, int],
    industry_counts: tuple[int, int],
    company_counts: tuple[int, int],
    credible_level: float,
    quantile_iterations: int,
) -> dict:
    categories = ["success", "failure"]
    generic = {
        "success": base_probability,
        "failure": 1.0 - base_probability,
    }
    archetype = {
        "success": float(archetype_counts[0]),
        "failure": float(archetype_counts[1]),
    }
    industry = {
        "success": float(industry_counts[0]),
        "failure": float(industry_counts[1]),
    }
    company = {
        "success": float(company_counts[0]),
        "failure": float(company_counts[1]),
    }

    levels = hierarchical_partial_pooling(
        generic,
        archetype,
        industry,
        company,
        categories,
        kappa_archetype,
        kappa_industry,
        kappa_company,
    )

    industry_mean = levels["industry"]
    company_alpha = posterior_alpha(
        industry_mean,
        company,
        categories,
        kappa_company,
    )

    a = float(company_alpha["success"])
    b = float(company_alpha["failure"])
    mean = a / (a + b)

    tail = (1.0 - credible_level) / 2.0
    lower = beta_ppf(tail, a, b, quantile_iterations)
    upper = beta_ppf(1.0 - tail, a, b, quantile_iterations)

    return {
        "posterior_mean": mean,
        "interval_lower": lower,
        "interval_upper": upper,
        "interval_width": upper - lower,
        "plug_in_industry_mean": float(industry_mean["success"]),
    }


def full_hierarchical_reference(
    base_probability: float,
    kappa_archetype: float,
    kappa_industry: float,
    kappa_company: float,
    archetype_counts: tuple[int, int],
    industry_counts: tuple[int, int],
    company_counts: tuple[int, int],
    credible_level: float,
    quantile_iterations: int,
    grid_points: int,
) -> dict:
    psi_grid = midpoint_grid(grid_points)
    phi_grid = midpoint_grid(grid_points)

    archetype_success, archetype_failure = archetype_counts
    industry_success, industry_failure = industry_counts
    company_success, company_failure = company_counts

    psi_prior_a = kappa_archetype * base_probability
    psi_prior_b = kappa_archetype * (1.0 - base_probability)

    log_psi_terms = []
    for psi in psi_grid:
        log_psi_terms.append(
            (psi_prior_a - 1.0 + archetype_success) * math.log(psi)
            + (psi_prior_b - 1.0 + archetype_failure) * math.log1p(-psi)
            - log_beta(psi_prior_a, psi_prior_b)
        )

    log_phi_marginal = []
    for phi in phi_grid:
        company_log_marginal = (
            log_beta(
                kappa_company * phi + company_success,
                kappa_company * (1.0 - phi) + company_failure,
            )
            - log_beta(
                kappa_company * phi,
                kappa_company * (1.0 - phi),
            )
        )

        terms = []
        for psi, log_psi in zip(psi_grid, log_psi_terms):
            phi_prior_a = kappa_industry * psi
            phi_prior_b = kappa_industry * (1.0 - psi)
            terms.append(
                log_psi
                + (phi_prior_a - 1.0 + industry_success) * math.log(phi)
                + (phi_prior_b - 1.0 + industry_failure) * math.log1p(-phi)
                - log_beta(phi_prior_a, phi_prior_b)
                + company_log_marginal
            )
        log_phi_marginal.append(logsumexp(terms))

    log_normalizer = logsumexp(log_phi_marginal)
    weights = [
        math.exp(value - log_normalizer)
        for value in log_phi_marginal
    ]
    weight_total = math.fsum(weights)
    weights = [weight / weight_total for weight in weights]

    conditional_a = [
        kappa_company * phi + company_success
        for phi in phi_grid
    ]
    conditional_b = [
        kappa_company * (1.0 - phi) + company_failure
        for phi in phi_grid
    ]
    conditional_means = [
        a / (a + b)
        for a, b in zip(conditional_a, conditional_b)
    ]

    posterior_mean = math.fsum(
        weight * mean
        for weight, mean in zip(weights, conditional_means)
    )

    def mixture_cdf(x: float) -> float:
        return math.fsum(
            weight * regularized_beta(x, a, b)
            for weight, a, b in zip(weights, conditional_a, conditional_b)
        )

    def mixture_ppf(q: float) -> float:
        lo, hi = 0.0, 1.0
        for _ in range(quantile_iterations):
            mid = (lo + hi) / 2.0
            if mixture_cdf(mid) < q:
                lo = mid
            else:
                hi = mid
        return (lo + hi) / 2.0

    tail = (1.0 - credible_level) / 2.0
    lower = mixture_ppf(tail)
    upper = mixture_ppf(1.0 - tail)

    return {
        "posterior_mean": posterior_mean,
        "interval_lower": lower,
        "interval_upper": upper,
        "interval_width": upper - lower,
        "grid_points": grid_points,
    }


def canonicalize(obj, decimals: int):
    if isinstance(obj, dict):
        return {key: canonicalize(value, decimals) for key, value in obj.items()}
    if isinstance(obj, list):
        return [canonicalize(value, decimals) for value in obj]
    if isinstance(obj, float):
        return round(obj, decimals)
    return obj


def validate_fixture(raw: dict) -> None:
    required = [
        "base_probability",
        "kappa_archetype",
        "kappa_industry",
        "kappa_company",
        "credible_level",
        "primary_grid_points",
        "convergence_grid_points",
        "quantile_bisection_iterations",
        "report_decimal_places",
        "convergence_tolerance",
        "regimes",
    ]
    missing = [key for key in required if key not in raw]
    if missing:
        raise ValueError(f"fixture missing keys: {missing}")

    if not 0.0 < float(raw["base_probability"]) < 1.0:
        raise ValueError("base_probability must be in (0,1)")
    if not 0.0 < float(raw["credible_level"]) < 1.0:
        raise ValueError("credible_level must be in (0,1)")
    if int(raw["convergence_grid_points"]) <= int(raw["primary_grid_points"]):
        raise ValueError("convergence grid must be finer than primary grid")

    names = [item["name"] for item in raw["regimes"]]
    if names != ["sparse", "intermediate", "dense"]:
        raise ValueError("regimes must be sparse, intermediate, dense in that order")

    for regime in raw["regimes"]:
        for key in ["archetype_counts", "industry_counts", "company_counts"]:
            counts = regime[key]
            if len(counts) != 2 or any(int(value) < 0 for value in counts):
                raise ValueError(f"invalid binary counts for {regime['name']}:{key}")

    if abs(regularized_beta(0.3, 1.0, 1.0) - 0.3) > 1e-12:
        raise ValueError("regularized-beta sanity check failed")


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise ValueError("cannot write empty CSV")
    fieldnames = list(rows[0])
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=fieldnames,
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    raw = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    validate_fixture(raw)

    base_probability = float(raw["base_probability"])
    kappa_archetype = float(raw["kappa_archetype"])
    kappa_industry = float(raw["kappa_industry"])
    kappa_company = float(raw["kappa_company"])
    credible_level = float(raw["credible_level"])
    primary_grid = int(raw["primary_grid_points"])
    convergence_grid = int(raw["convergence_grid_points"])
    quantile_iterations = int(raw["quantile_bisection_iterations"])
    decimals = int(raw["report_decimal_places"])
    tolerance = raw["convergence_tolerance"]

    failures = []
    cases = []

    for regime in raw["regimes"]:
        archetype_counts = tuple(int(x) for x in regime["archetype_counts"])
        industry_counts = tuple(int(x) for x in regime["industry_counts"])
        company_counts = tuple(int(x) for x in regime["company_counts"])

        plugin = plugin_stats(
            base_probability,
            kappa_archetype,
            kappa_industry,
            kappa_company,
            archetype_counts,
            industry_counts,
            company_counts,
            credible_level,
            quantile_iterations,
        )

        primary = full_hierarchical_reference(
            base_probability,
            kappa_archetype,
            kappa_industry,
            kappa_company,
            archetype_counts,
            industry_counts,
            company_counts,
            credible_level,
            quantile_iterations,
            primary_grid,
        )

        convergence = full_hierarchical_reference(
            base_probability,
            kappa_archetype,
            kappa_industry,
            kappa_company,
            archetype_counts,
            industry_counts,
            company_counts,
            credible_level,
            quantile_iterations,
            convergence_grid,
        )

        convergence_delta = {
            "posterior_mean": abs(
                primary["posterior_mean"] - convergence["posterior_mean"]
            ),
            "interval_lower": abs(
                primary["interval_lower"] - convergence["interval_lower"]
            ),
            "interval_upper": abs(
                primary["interval_upper"] - convergence["interval_upper"]
            ),
        }

        convergence_pass = (
            convergence_delta["posterior_mean"]
            <= float(tolerance["posterior_mean"])
            and convergence_delta["interval_lower"]
            <= float(tolerance["interval_lower"])
            and convergence_delta["interval_upper"]
            <= float(tolerance["interval_upper"])
        )

        if not convergence_pass:
            failures.append(
                f"{regime['name']}: 240-vs-480 numerical convergence tolerance exceeded"
            )

        case = {
            "regime": regime["name"],
            "counts": {
                "archetype": list(archetype_counts),
                "industry": list(industry_counts),
                "company": list(company_counts),
            },
            "plugin": plugin,
            "uncertainty_propagating_reference": primary,
            "convergence_reference": convergence,
            "comparison": {
                "absolute_mean_difference": abs(
                    primary["posterior_mean"] - plugin["posterior_mean"]
                ),
                "plugin_interval_width": plugin["interval_width"],
                "reference_interval_width": primary["interval_width"],
                "reference_to_plugin_width_ratio": (
                    primary["interval_width"] / plugin["interval_width"]
                ),
            },
            "convergence_delta": convergence_delta,
            "convergence_pass": convergence_pass,
        }
        cases.append(case)

    result = {
        "protocol_version": raw["protocol_version"],
        "reference_model": "binary_full_hierarchical_posterior_midpoint_quadrature",
        "primary_grid_points": primary_grid,
        "convergence_grid_points": convergence_grid,
        "credible_level": credible_level,
        "declared_kappa": {
            "archetype": kappa_archetype,
            "industry": kappa_industry,
            "company": kappa_company,
        },
        "cases": cases,
        "acceptance_scope": (
            "Pass/fail is numerical-convergence only. Estimator differences are descriptive."
        ),
        "failures": failures,
        "passed": not failures,
    }

    result = canonicalize(result, decimals)

    matrix = []
    for case in result["cases"]:
        matrix.append(
            {
                "regime": case["regime"],
                "plugin_mean": case["plugin"]["posterior_mean"],
                "plugin_lower": case["plugin"]["interval_lower"],
                "plugin_upper": case["plugin"]["interval_upper"],
                "plugin_width": case["plugin"]["interval_width"],
                "reference_mean": case["uncertainty_propagating_reference"]["posterior_mean"],
                "reference_lower": case["uncertainty_propagating_reference"]["interval_lower"],
                "reference_upper": case["uncertainty_propagating_reference"]["interval_upper"],
                "reference_width": case["uncertainty_propagating_reference"]["interval_width"],
                "absolute_mean_difference": case["comparison"]["absolute_mean_difference"],
                "reference_to_plugin_width_ratio": case["comparison"]["reference_to_plugin_width_ratio"],
                "convergence_mean_delta": case["convergence_delta"]["posterior_mean"],
                "convergence_lower_delta": case["convergence_delta"]["interval_lower"],
                "convergence_upper_delta": case["convergence_delta"]["interval_upper"],
                "convergence_pass": case["convergence_pass"],
            }
        )

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    json_path = OUT_DIR / "exp5_results.json"
    csv_path = OUT_DIR / "exp5_case_matrix.csv"

    json_path.write_text(
        json.dumps(result, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    write_csv(csv_path, matrix)

    print(f"exp5_failures={len(failures)}")
    print(f"case_count={len(cases)}")
    print(f"exp5_results_sha256={hashlib.sha256(json_path.read_bytes()).hexdigest()}")
    print(f"exp5_case_matrix_sha256={hashlib.sha256(csv_path.read_bytes()).hexdigest()}")

    if failures:
        for failure in failures:
            print("FAIL:", failure)
        return 1

    print("EXPERIMENT_5_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
