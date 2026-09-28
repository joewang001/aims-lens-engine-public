from __future__ import annotations

import importlib.util
import json
import math
import random
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from research_core.inference import hierarchical_dirichlet_mean
from research_core.models import RoutingLevel
from research_core.routing import route_mixture

RUNNER_PATH = ROOT / "tools/run_exp6_routing_overlap_ablation.py"
FIXTURE_PATH = ROOT / "examples/paper/experiments/exp6/fixtures.json"

_spec = importlib.util.spec_from_file_location("run_exp6_routing_overlap_ablation", RUNNER_PATH)
if _spec is None or _spec.loader is None:
    raise RuntimeError("could not load Experiment 6 runner")
exp6 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(exp6)


class Experiment6CommitBTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))

    def test_fixture_contract_validates_without_writing_results(self):
        exp6.validate_only(self.raw)
        self.assertEqual(self.raw["replication"]["primary_factorial_conditions"], 81)
        self.assertEqual(self.raw["replication"]["total_paired_training_realizations"], 40500)
        self.assertEqual(self.raw["replication"]["total_heldout_observations"], 8100000)

    def test_seed_contract_uses_fixed_sha256_prefix(self):
        seed = exp6.deterministic_seed(
            "0.1.0-pre-specified",
            0,
            2,
            0.1,
            2.0,
            0.4,
            0,
        )
        self.assertEqual(seed, 2307452519820928386)
        self.assertEqual(
            seed,
            exp6.deterministic_seed(
                "0.1.0-pre-specified",
                0,
                2,
                0.1,
                2.0,
                0.4,
                0,
            ),
        )
        self.assertNotEqual(
            seed,
            exp6.deterministic_seed(
                "0.1.0-pre-specified",
                0,
                2,
                0.1,
                2.0,
                0.4,
                1,
            ),
        )

    def test_declared_routing_weights_match_frozen_formula(self):
        expected = self.raw["routing"]["expected_weights"]
        for gamma in self.raw["routing"]["gamma"]:
            calculated = exp6.routing_weights(self.raw["routing"]["levels"], float(gamma))
            declared = expected[exp6.canonical_float(float(gamma))]
            for name, value in declared.items():
                self.assertAlmostEqual(calculated[name], float(value), places=9)

    def test_path_a_calls_public_shrinkage_semantics_and_path_b_public_routing(self):
        categories = list(self.raw["categories"])
        truth = exp6.truth_distribution(self.raw, 0)
        l3, l5 = exp6.broader_context_distributions(truth, 0.4, categories)
        counts = {
            "ownership": 1.0,
            "evidence": 1.0,
            "tradeoff": 0.0,
            "collaboration": 0.0,
            "reflection": 0.0,
        }
        kappa = 6.0
        gamma = 0.7

        path_a, path_b, provenance = exp6.path_distributions(
            categories,
            l3,
            l5,
            counts,
            kappa,
            gamma,
            self.raw["routing"]["levels"],
        )

        expected_a = hierarchical_dirichlet_mean(
            l3,
            counts,
            categories,
            kappa,
        )
        for category in categories:
            self.assertAlmostEqual(path_a[category], expected_a[category], places=12)

        level_specs = {level["name"]: level for level in self.raw["routing"]["levels"]}
        public_levels = [
            RoutingLevel(
                "L0_full_context",
                0,
                True,
                True,
                float(level_specs["L0_full_context"]["coverage"]),
                expected_a,
            ),
            RoutingLevel(
                "L3_industry_context",
                3,
                True,
                True,
                float(level_specs["L3_industry_context"]["coverage"]),
                l3,
            ),
            RoutingLevel(
                "L5_generic_context",
                5,
                True,
                True,
                float(level_specs["L5_generic_context"]["coverage"]),
                l5,
            ),
        ]
        expected_b, expected_provenance = route_mixture(public_levels, categories, gamma)
        for category in categories:
            self.assertAlmostEqual(path_b[category], expected_b[category], places=12)
        self.assertEqual(provenance, expected_provenance)

    def test_population_metric_formulas_match_direct_calculation(self):
        categories = ["a", "b", "c"]
        truth = {"a": 0.5, "b": 0.3, "c": 0.2}
        prediction = {"a": 0.4, "b": 0.35, "c": 0.25}

        ll = -sum(truth[k] * math.log(prediction[k]) for k in categories)
        brier = 1.0 + sum(prediction[k] ** 2 for k in categories) - 2.0 * sum(
            truth[k] * prediction[k] for k in categories
        )
        tv = 0.5 * sum(abs(prediction[k] - truth[k]) for k in categories)

        self.assertAlmostEqual(
            exp6.exact_expected_log_loss(prediction, truth, categories),
            ll,
            places=12,
        )
        self.assertAlmostEqual(
            exp6.exact_expected_brier(prediction, truth, categories),
            brier,
            places=12,
        )
        self.assertAlmostEqual(
            exp6.total_variation(prediction, truth, categories),
            tv,
            places=12,
        )

    def test_replicate_sampling_is_paired_and_deterministic(self):
        categories = list(self.raw["categories"])
        truth = exp6.truth_distribution(self.raw, 2)
        seed = exp6.deterministic_seed(
            self.raw["protocol_version"],
            2,
            10,
            0.4,
            6.0,
            0.7,
            17,
        )

        rng_a = random.Random(seed)
        counts_a = exp6.sample_company_counts(rng_a, truth, categories, 10)
        outcomes_a = exp6.sample_outcomes(rng_a, truth, categories, 200)

        rng_b = random.Random(seed)
        counts_b = exp6.sample_company_counts(rng_b, truth, categories, 10)
        outcomes_b = exp6.sample_outcomes(rng_b, truth, categories, 200)

        self.assertEqual(counts_a, counts_b)
        self.assertEqual(outcomes_a, outcomes_b)
        self.assertEqual(sum(counts_a.values()), 10.0)
        self.assertEqual(len(outcomes_a), 200)

    def test_pass_semantics_do_not_require_routing_to_win(self):
        values = [0.2, -0.1, 0.0, 0.3]
        summary = exp6.summarize(values, lower_is_better=True)
        self.assertAlmostEqual(summary["proportion_routing_improves"], 0.25)
        self.assertGreater(summary["mean"], 0.0)
        self.assertFalse(self.raw["execution_pass"]["routing_performance_direction_required"])


if __name__ == "__main__":
    unittest.main()
