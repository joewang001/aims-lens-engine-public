from __future__ import annotations

import json
import math
import sys
import unittest
from dataclasses import replace
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from research_core import EvidenceRecord, PracticeRequest, RoutingLevel, prioritize_followups
from research_core.active_learning import expected_information_gain
from research_core.compatibility import masked_and_renormalized
from research_core.dag import PARENT_CARDINALITY_CAPS, joint_factorization, parent_configuration_count, validate_dag
from research_core.evaluation import kl_divergence, multiclass_brier, multiclass_log_loss, vector_ece
from research_core.evidence import decay_rate_from_half_life, weighted_counts
from research_core.inference import credible_intervals, hierarchical_partial_pooling, posterior_alpha, posterior_mean
from research_core.lens import load_lens
from research_core.routing import BACKOFF_SEQUENCE, LensCandidate, route_mixture, select_highest_specificity
from research_core.stopping import stopping_probability
from research_core.uncertainty import data_support, normalized_entropy


class ResearchCoreTests(unittest.TestCase):
    def _request(self):
        raw = json.loads((ROOT / "examples/paper/followup_priority_request.json").read_text())
        return PracticeRequest(
            categories=raw["categories"],
            parent_distribution=raw["parent_distribution"],
            evidence=[EvidenceRecord(**x) for x in raw["evidence"]],
            permitted_categories=raw["permitted_categories"],
            kappa_company=raw["kappa_company"],
            temporal_decay_rate_per_day=raw["temporal_decay_rate_per_day"],
            routing_levels=[RoutingLevel(**x) for x in raw["routing_levels"]],
            routing_gamma=raw["routing_gamma"],
            support_tau=raw["support_tau"],
            abstention_threshold=raw.get("abstention_threshold", 0.0),
        )

    def test_eq1_dag_factorization_and_declared_cardinality(self):
        validate_dag({"followup": ["stage", "competency"], "stop": ["time_remaining", "followup"]})
        self.assertAlmostEqual(joint_factorization({"stage": 0.5, "competency": 0.5, "followup": 0.8}), 0.2)
        self.assertEqual(parent_configuration_count(PARENT_CARDINALITY_CAPS.values()), 22050)

    def test_eq2_logistic_stopping(self):
        self.assertAlmostEqual(stopping_probability(0.0, {"time": 1.0}, {"time": 0.0}), 0.5)

    def test_eq3_mask_excludes_invalidity_not_rarity(self):
        out = masked_and_renormalized({"a": 0.1, "b": 0.9}, ["a", "b"], ["a"])
        self.assertEqual(out, {"a": 1.0})

    def test_eq5_unauthorized_evidence_contributes_zero_mass(self):
        counts, mass = weighted_counts(
            [EvidenceRecord("ownership", False, 1.0, 0)],
            ["ownership", "evidence"],
            decay_rate_from_half_life(90),
        )
        self.assertEqual(counts["ownership"], 0.0)
        self.assertEqual(mass, 0.0)

    def test_eq6_7_dirichlet_posterior(self):
        alpha = posterior_alpha({"a": 0.6, "b": 0.4}, {"a": 2, "b": 0}, ["a", "b"], 10)
        self.assertEqual(alpha, {"a": 8.0, "b": 4.0})
        self.assertAlmostEqual(posterior_mean(alpha)["a"], 2 / 3)
        ci = credible_intervals(alpha, draws=500, seed=1)
        self.assertTrue(ci["a"][0] < 2 / 3 < ci["a"][1])

    def test_eq4_hierarchical_borrowing_is_exposed(self):
        levels = hierarchical_partial_pooling(
            {"a": 0.5, "b": 0.5}, {"a": 1}, {"b": 1}, {"a": 2}, ["a", "b"], 5, 5, 5
        )
        self.assertEqual(set(levels), {"generic", "archetype", "industry", "company"})
        self.assertGreater(levels["company"]["a"], 0.5)

    def test_eq8_9_backoff_sequence_and_routing(self):
        self.assertEqual([d for _, d in BACKOFF_SEQUENCE], list(range(6)))
        levels = [
            RoutingLevel("L0", 0, True, True, 0.5, {"a": 1, "b": 0}),
            RoutingLevel("L5", 5, True, True, 1.0, {"a": 0, "b": 1}),
        ]
        mix, provenance = route_mixture(levels, ["a", "b"], 0.7)
        self.assertAlmostEqual(sum(mix.values()), 1.0)
        self.assertEqual(len(provenance), 2)

    def test_routing_name_must_match_declared_distance(self):
        with self.assertRaises(ValueError):
            RoutingLevel("L3_industry_context", 2, True, True, 1.0, {"a": 1.0}).validate()

    def test_highest_specificity_means_smallest_backoff_distance(self):
        candidates = [
            LensCandidate("generic", 5, True, True, True, True),
            LensCandidate("company", 0, True, True, True, True),
            LensCandidate("industry", 3, True, True, True, True),
        ]
        selected = select_highest_specificity(candidates)
        self.assertIsNotNone(selected)
        self.assertEqual(selected.lens_id, "company")

    def test_request_runtime_constraints_match_schema_intent(self):
        request = self._request()
        duplicate = replace(request, categories=request.categories + [request.categories[0]])
        with self.assertRaises(ValueError):
            duplicate.validate()
        unknown_evidence = replace(
            request,
            evidence=request.evidence + [EvidenceRecord("unknown", True, 1.0, 0)],
        )
        with self.assertRaises(ValueError):
            unknown_evidence.validate()

    def test_abstention_gate_is_exercised(self):
        request = replace(self._request(), evidence=[], abstention_threshold=0.3)
        out = prioritize_followups(request)
        self.assertEqual(out["mode"], "abstain")
        self.assertEqual(out["reason"], "insufficient_data_support")

    def test_eq10_11_uncertainty_and_support(self):
        self.assertAlmostEqual(normalized_entropy({"a": 0.5, "b": 0.5}, 2), 1.0)
        self.assertAlmostEqual(data_support(8.0, 8.0), 1 - math.exp(-1))

    def test_eq12_13_calibration_metrics(self):
        preds = [[0.8, 0.2], [0.3, 0.7]]
        ys = [0, 1]
        self.assertGreaterEqual(multiclass_brier(preds, ys), 0)
        self.assertGreaterEqual(vector_ece(preds, ys, bins=2), 0)
        self.assertGreaterEqual(multiclass_log_loss(preds, ys), 0)

    def test_eq14_drift_kl(self):
        self.assertAlmostEqual(kl_divergence([0.5, 0.5], [0.5, 0.5]), 0.0)
        self.assertGreater(kl_divergence([0.8, 0.2], [0.5, 0.5]), 0.0)

    def test_eq15_information_gain(self):
        self.assertGreater(expected_information_gain({"a": 2.0, "b": 2.0}), 0.0)

    def test_interview_dna_example_validates(self):
        lens = load_lens(ROOT / "examples/paper/interview_dna.example.json")
        self.assertEqual(lens["maturity"], "reviewed_practice")

    def test_demo_is_candidate_side_and_deterministic(self):
        a = prioritize_followups(self._request())
        b = prioritize_followups(self._request())
        self.assertEqual(a, b)
        self.assertEqual(a["mode"], "ordered_practice_priority")
        self.assertIn("not a prediction", a["disclaimer"])
        self.assertNotIn("collaboration", a["priority_order"])


if __name__ == "__main__":
    unittest.main()
