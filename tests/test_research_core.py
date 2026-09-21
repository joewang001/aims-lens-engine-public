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
from research_core.active_learning import expected_information_gain, predictive_entropy_reduction
from research_core.compatibility import masked_and_renormalized
from research_core.dag import PARENT_CARDINALITY_CAPS, joint_factorization, parent_configuration_count, validate_dag
from research_core.evaluation import kl_divergence, multiclass_brier, multiclass_log_loss, top_label_ece, vector_ece
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

    def test_zero_permitted_mass_routing_component_is_excluded(self):
        levels = [
            RoutingLevel("L0", 0, True, True, 0.5, {"a": 1.0, "b": 0.0}),
            RoutingLevel("L5", 5, True, True, 1.0, {"a": 0.0, "b": 1.0}),
        ]
        mix, provenance = route_mixture(levels, ["a"], 0.7)

        self.assertEqual(mix, {"a": 1.0})
        self.assertEqual(len(provenance), 1)
        self.assertEqual(provenance[0]["level"], "L0")
        self.assertEqual(provenance[0]["routing_weight"], 1.0)

    def test_all_zero_permitted_mass_routing_fails_closed(self):
        levels = [
            RoutingLevel("L3_industry_context", 3, True, True, 0.9, {"b": 1.0}),
            RoutingLevel("L5_generic_context", 5, True, True, 1.0, {"b": 1.0}),
        ]
        mix, provenance = route_mixture(levels, ["a"], 0.7)

        self.assertEqual(mix, {})
        self.assertEqual(provenance, [])

    def test_service_distinguishes_zero_supported_mass_from_unauthorized_routes(self):
        request = self._request()
        massless_levels = [
            RoutingLevel(
                "L0_full_context",
                0,
                True,
                True,
                0.0,
                {"ownership": 1.0},
            ),
            RoutingLevel(
                "L3_industry_context",
                3,
                True,
                True,
                1.0,
                {"collaboration": 1.0},
            ),
            RoutingLevel(
                "L5_generic_context",
                5,
                True,
                True,
                1.0,
                {"collaboration": 1.0},
            ),
        ]
        massless_request = replace(
            request,
            permitted_categories=["ownership"],
            routing_levels=massless_levels,
            abstention_threshold=0.0,
        )
        massless_out = prioritize_followups(massless_request)
        self.assertEqual(massless_out["mode"], "abstain")
        self.assertEqual(massless_out["reason"], "no_supported_routing_mass")

        unauthorized_levels = [
            replace(level, authorized=False)
            for level in request.routing_levels
        ]
        unauthorized_request = replace(
            request,
            routing_levels=unauthorized_levels,
            abstention_threshold=0.0,
        )
        unauthorized_out = prioritize_followups(unauthorized_request)
        self.assertEqual(unauthorized_out["mode"], "abstain")
        self.assertEqual(unauthorized_out["reason"], "no_eligible_routing_level")

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

    def test_masked_only_evidence_cannot_cross_support_threshold(self):
        base = replace(
            self._request(),
            evidence=[EvidenceRecord("ownership", True, 1.0, 0.0)],
            abstention_threshold=0.2,
        )
        masked_evidence = [
            EvidenceRecord("collaboration", True, 1.0, 0.0)
            for _ in range(100)
        ]
        attacked = replace(base, evidence=base.evidence + masked_evidence)

        base_out = prioritize_followups(base)
        attacked_out = prioritize_followups(attacked)

        self.assertEqual(base_out["mode"], "abstain")
        self.assertEqual(attacked_out["mode"], "abstain")
        self.assertEqual(base_out["reason"], "insufficient_data_support")
        self.assertEqual(attacked_out["reason"], "insufficient_data_support")
        self.assertEqual(
            attacked_out["effective_evidence_mass"],
            base_out["effective_evidence_mass"],
        )
        self.assertEqual(attacked_out["data_support"], base_out["data_support"])

    def test_masked_evidence_does_not_change_released_support_or_priority(self):
        base = self._request()
        masked_evidence = [
            EvidenceRecord("collaboration", True, 1.0, 0.0)
            for _ in range(50)
        ]
        attacked = replace(base, evidence=base.evidence + masked_evidence)

        base_out = prioritize_followups(base)
        attacked_out = prioritize_followups(attacked)

        self.assertEqual(base_out["mode"], "ordered_practice_priority")
        self.assertEqual(attacked_out["mode"], "ordered_practice_priority")
        self.assertEqual(
            attacked_out["effective_evidence_mass"],
            base_out["effective_evidence_mass"],
        )
        self.assertEqual(attacked_out["data_support"], base_out["data_support"])
        self.assertEqual(
            attacked_out["diagnostic_distribution"],
            base_out["diagnostic_distribution"],
        )
        self.assertEqual(attacked_out["priority_order"], base_out["priority_order"])

    def test_local_posterior_targets_l0_not_list_position(self):
        request = self._request()
        baseline = prioritize_followups(request)
        reordered = replace(
            request,
            routing_levels=[request.routing_levels[1], request.routing_levels[0], request.routing_levels[2]],
        )
        out = prioritize_followups(reordered)
        self.assertEqual(out["diagnostic_distribution"], baseline["diagnostic_distribution"])
        self.assertEqual(out["top_category"], baseline["top_category"])

    def test_request_requires_exactly_one_l0_level(self):
        request = self._request()
        without_l0 = replace(
            request,
            routing_levels=[level for level in request.routing_levels if level.backoff_distance != 0],
        )
        with self.assertRaisesRegex(ValueError, "exactly one L0"):
            without_l0.validate()

        l0 = next(level for level in request.routing_levels if level.backoff_distance == 0)
        duplicate_l0 = RoutingLevel(
            "L0_alternate_context",
            0,
            l0.authorized,
            l0.applicable,
            l0.coverage,
            l0.distribution,
        )
        with_two_l0 = replace(request, routing_levels=request.routing_levels + [duplicate_l0])
        with self.assertRaisesRegex(ValueError, "exactly one L0"):
            with_two_l0.validate()

    def test_request_schema_matches_runtime_routing_contract(self):
        schema = json.loads((ROOT / "schemas/followup_priority_request.schema.json").read_text())
        routing = schema["properties"]["routing_levels"]
        item = routing["items"]
        self.assertEqual(routing["minContains"], 1)
        self.assertEqual(routing["maxContains"], 1)
        self.assertEqual(routing["contains"]["properties"]["backoff_distance"]["const"], 0)
        self.assertEqual(item["properties"]["backoff_distance"]["maximum"], 5)
        self.assertEqual(item["properties"]["name"]["pattern"], "^L[0-5](?:_|$)")
        self.assertEqual(len(item["allOf"]), 6)

    def test_eq10_11_uncertainty_and_support(self):
        self.assertAlmostEqual(normalized_entropy({"a": 0.5, "b": 0.5}, 2), 1.0)
        self.assertAlmostEqual(data_support(8.0, 8.0), 1 - math.exp(-1))

    def test_eq12_13_calibration_metrics(self):
        preds = [[0.8, 0.2], [0.3, 0.7]]
        ys = [0, 1]
        self.assertGreaterEqual(multiclass_brier(preds, ys), 0)
        self.assertGreaterEqual(top_label_ece(preds, ys, bins=2), 0)
        self.assertGreaterEqual(multiclass_log_loss(preds, ys), 0)

    def test_top_label_ece_exposes_high_confidence_error_cancellation(self):
        preds = [[0.9, 0.1], [0.1, 0.9]]
        ys = [1, 0]

        legacy_vector = vector_ece(preds, ys, bins=10)
        top_label = top_label_ece(preds, ys, bins=10)

        self.assertAlmostEqual(legacy_vector, 0.0, places=12)
        self.assertAlmostEqual(top_label, 0.9, places=12)
        self.assertGreater(multiclass_brier(preds, ys), 0.0)
        self.assertGreater(multiclass_log_loss(preds, ys), 0.0)

    def test_eq14_drift_kl(self):
        self.assertAlmostEqual(kl_divergence([0.5, 0.5], [0.5, 0.5]), 0.0)
        self.assertGreater(kl_divergence([0.8, 0.2], [0.5, 0.5]), 0.0)

    def test_eq15_information_gain(self):
        alpha = {"a": 1.0, "b": 1.0}
        parameter_ig = expected_information_gain(alpha)
        predictive_reduction = predictive_entropy_reduction(alpha)

        self.assertAlmostEqual(
            parameter_ig,
            math.log(2.0) - 0.5,
            places=12,
        )
        self.assertAlmostEqual(
            parameter_ig,
            0.1931471805599453,
            places=12,
        )
        self.assertAlmostEqual(
            predictive_reduction,
            0.0566330122651325,
            places=12,
        )
        self.assertNotAlmostEqual(parameter_ig, predictive_reduction, places=6)

        with self.assertRaises(ValueError):
            expected_information_gain({"a": 1.0, "b": 0.0})

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
