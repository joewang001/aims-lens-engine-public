import math
import unittest

from runtime_core import (
    EvidenceRecord,
    data_support,
    effective_permitted_mass,
    hierarchical_dirichlet_mean,
    masked_and_renormalized,
    should_abstain,
    weighted_counts,
)


class EvidenceWeightingTests(unittest.TestCase):
    def test_unauthorized_evidence_contributes_zero_mass(self):
        records = [
            EvidenceRecord("ownership", True, 1.0, 0.0),
            EvidenceRecord("evidence", False, 1.0, 0.0),
        ]
        counts, total = weighted_counts(
            records,
            ["ownership", "evidence"],
            decay_rate_per_day=0.0,
        )
        self.assertEqual(counts, {"ownership": 1.0, "evidence": 0.0})
        self.assertEqual(total, 1.0)

    def test_quality_and_recency_reduce_effective_mass(self):
        records = [EvidenceRecord("evidence", True, 0.5, 10.0)]
        counts, total = weighted_counts(
            records,
            ["evidence"],
            decay_rate_per_day=0.1,
        )
        expected = 0.5 * math.exp(-1.0)
        self.assertAlmostEqual(counts["evidence"], expected)
        self.assertAlmostEqual(total, expected)

    def test_unknown_category_fails_closed(self):
        with self.assertRaises(ValueError):
            weighted_counts(
                [EvidenceRecord("unknown", False, 1.0, 0.0)],
                ["ownership"],
                decay_rate_per_day=0.0,
            )

    def test_non_finite_evidence_inputs_fail_closed(self):
        with self.assertRaises(ValueError):
            weighted_counts(
                [EvidenceRecord("ownership", True, 1.0, float("nan"))],
                ["ownership"],
                decay_rate_per_day=0.0,
            )
        with self.assertRaises(ValueError):
            weighted_counts(
                [EvidenceRecord("ownership", True, 1.0, 0.0)],
                ["ownership"],
                decay_rate_per_day=float("nan"),
            )


class CompatibilityTests(unittest.TestCase):
    def test_masking_removes_non_permitted_categories_and_renormalizes(self):
        masked = masked_and_renormalized(
            {"ownership": 0.2, "evidence": 0.3, "reflection": 0.5},
            ["ownership", "evidence", "reflection"],
            ["ownership", "evidence"],
        )
        self.assertAlmostEqual(masked["ownership"], 0.4)
        self.assertAlmostEqual(masked["evidence"], 0.6)
        self.assertNotIn("reflection", masked)

    def test_zero_permitted_mass_returns_empty_mapping(self):
        masked = masked_and_renormalized(
            {"ownership": 0.0, "evidence": 1.0},
            ["ownership", "evidence"],
            ["ownership"],
        )
        self.assertEqual(masked, {})

    def test_unknown_distribution_category_fails_closed(self):
        with self.assertRaises(ValueError):
            masked_and_renormalized(
                {"ownership": 1.0, "unexpected": 1.0},
                ["ownership"],
                ["ownership"],
            )

    def test_non_finite_distribution_fails_closed(self):
        with self.assertRaises(ValueError):
            masked_and_renormalized(
                {"ownership": float("nan")},
                ["ownership"],
                ["ownership"],
            )


class LocalShrinkageTests(unittest.TestCase):
    def test_company_counts_are_shrunk_toward_parent(self):
        result = hierarchical_dirichlet_mean(
            {"ownership": 0.25, "evidence": 0.75},
            {"ownership": 2.0, "evidence": 0.0},
            ["ownership", "evidence"],
            kappa_company=2.0,
        )
        self.assertAlmostEqual(result["ownership"], 0.625)
        self.assertAlmostEqual(result["evidence"], 0.375)

    def test_zero_parent_mass_is_rejected_not_uniformized(self):
        with self.assertRaises(ValueError):
            hierarchical_dirichlet_mean(
                {"ownership": 0.0, "evidence": 0.0},
                {"ownership": 1.0},
                ["ownership", "evidence"],
                kappa_company=2.0,
            )

    def test_unknown_parent_category_fails_closed(self):
        with self.assertRaises(ValueError):
            hierarchical_dirichlet_mean(
                {"ownership": 1.0, "unexpected": 1.0},
                {"ownership": 1.0},
                ["ownership"],
                kappa_company=2.0,
            )

    def test_negative_counts_fail_closed(self):
        with self.assertRaises(ValueError):
            hierarchical_dirichlet_mean(
                {"ownership": 1.0},
                {"ownership": -1.0},
                ["ownership"],
                kappa_company=2.0,
            )

    def test_non_finite_inference_inputs_fail_closed(self):
        with self.assertRaises(ValueError):
            hierarchical_dirichlet_mean(
                {"ownership": float("nan")},
                {"ownership": 1.0},
                ["ownership"],
                kappa_company=2.0,
            )
        with self.assertRaises(ValueError):
            hierarchical_dirichlet_mean(
                {"ownership": 1.0},
                {"ownership": float("nan")},
                ["ownership"],
                kappa_company=2.0,
            )
        with self.assertRaises(ValueError):
            hierarchical_dirichlet_mean(
                {"ownership": 1.0},
                {"ownership": 1.0},
                ["ownership"],
                kappa_company=float("nan"),
            )


class SupportTests(unittest.TestCase):
    def test_masked_category_evidence_does_not_increase_release_support(self):
        records = [
            EvidenceRecord("ownership", True, 1.0, 0.0),
            EvidenceRecord("reflection", True, 1.0, 0.0),
            EvidenceRecord("reflection", True, 1.0, 0.0),
        ]
        counts, total = weighted_counts(
            records,
            ["ownership", "reflection"],
            decay_rate_per_day=0.0,
        )
        permitted_mass = effective_permitted_mass(counts, ["ownership"])
        self.assertEqual(total, 3.0)
        self.assertEqual(permitted_mass, 1.0)
        self.assertAlmostEqual(data_support(permitted_mass, tau=8.0), 1.0 - math.exp(-0.125))

    def test_abstention_uses_declared_support_threshold(self):
        support = data_support(1.0, tau=8.0)
        self.assertTrue(should_abstain(support, threshold=0.3))
        self.assertFalse(should_abstain(support, threshold=0.1))

    def test_non_finite_support_inputs_fail_closed(self):
        with self.assertRaises(ValueError):
            effective_permitted_mass({"ownership": float("nan")}, ["ownership"])
        with self.assertRaises(ValueError):
            data_support(float("nan"), tau=8.0)
        with self.assertRaises(ValueError):
            data_support(1.0, tau=float("nan"))
        with self.assertRaises(ValueError):
            should_abstain(float("nan"), threshold=0.3)


if __name__ == "__main__":
    unittest.main()
