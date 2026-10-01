import math
import unittest

from runtime_core import (
    EvidenceRecord,
    LocalDecisionRequest,
    decide_local_practice_priority,
)


class LocalDecisionServiceTests(unittest.TestCase):
    def test_returns_ordered_practice_priority(self):
        envelope = decide_local_practice_priority(
            LocalDecisionRequest(
                categories=["ownership", "evidence"],
                parent_distribution={"ownership": 0.5, "evidence": 0.5},
                evidence=[
                    EvidenceRecord("ownership", True, 1.0, 0.0),
                    EvidenceRecord("ownership", True, 1.0, 0.0),
                ],
                permitted_categories=["ownership", "evidence"],
                kappa_company=2.0,
                temporal_decay_rate_per_day=0.0,
                support_tau=8.0,
                abstention_threshold=0.2,
            )
        )
        self.assertEqual(envelope.mode, "ordered_practice_priority")
        self.assertIsNone(envelope.reason)
        self.assertEqual(envelope.top_category, "ownership")
        self.assertEqual(envelope.priority_order, ("ownership", "evidence"))
        self.assertAlmostEqual(envelope.effective_evidence_mass, 2.0)
        self.assertGreater(envelope.data_support, 0.2)

    def test_compatibility_mask_controls_released_priority(self):
        envelope = decide_local_practice_priority(
            LocalDecisionRequest(
                categories=["ownership", "evidence"],
                parent_distribution={"ownership": 0.05, "evidence": 0.95},
                evidence=[
                    EvidenceRecord("ownership", True, 1.0, 0.0),
                    EvidenceRecord("evidence", True, 1.0, 0.0),
                    EvidenceRecord("evidence", True, 1.0, 0.0),
                ],
                permitted_categories=["ownership"],
                kappa_company=2.0,
                temporal_decay_rate_per_day=0.0,
                support_tau=8.0,
                abstention_threshold=0.1,
            )
        )
        self.assertEqual(envelope.mode, "ordered_practice_priority")
        self.assertEqual(envelope.top_category, "ownership")
        self.assertEqual(envelope.priority_order, ("ownership",))
        self.assertEqual(envelope.diagnostic_distribution, {"ownership": 1.0})

    def test_masked_evidence_does_not_increase_release_support(self):
        envelope = decide_local_practice_priority(
            LocalDecisionRequest(
                categories=["ownership", "reflection"],
                parent_distribution={"ownership": 0.5, "reflection": 0.5},
                evidence=[
                    EvidenceRecord("ownership", True, 1.0, 0.0),
                    EvidenceRecord("reflection", True, 1.0, 0.0),
                    EvidenceRecord("reflection", True, 1.0, 0.0),
                ],
                permitted_categories=["ownership"],
                kappa_company=2.0,
                temporal_decay_rate_per_day=0.0,
                support_tau=8.0,
                abstention_threshold=0.0,
            )
        )
        self.assertEqual(envelope.effective_evidence_mass, 1.0)
        self.assertAlmostEqual(
            envelope.data_support,
            1.0 - math.exp(-0.125),
        )

    def test_insufficient_support_abstains(self):
        envelope = decide_local_practice_priority(
            LocalDecisionRequest(
                categories=["ownership"],
                parent_distribution={"ownership": 1.0},
                evidence=[],
                permitted_categories=["ownership"],
                kappa_company=2.0,
                temporal_decay_rate_per_day=0.0,
                support_tau=8.0,
                abstention_threshold=0.1,
            )
        )
        self.assertEqual(envelope.mode, "abstain")
        self.assertEqual(envelope.reason, "insufficient_data_support")
        self.assertIsNone(envelope.top_category)
        self.assertEqual(envelope.priority_order, ())
        self.assertEqual(envelope.diagnostic_distribution, {})
        self.assertEqual(envelope.data_support, 0.0)

    def test_all_categories_masked_abstains_even_with_zero_threshold(self):
        envelope = decide_local_practice_priority(
            LocalDecisionRequest(
                categories=["ownership", "evidence"],
                parent_distribution={"ownership": 0.0, "evidence": 1.0},
                evidence=[],
                permitted_categories=["ownership"],
                kappa_company=2.0,
                temporal_decay_rate_per_day=0.0,
                support_tau=8.0,
                abstention_threshold=0.0,
            )
        )
        self.assertEqual(envelope.mode, "abstain")
        self.assertEqual(envelope.reason, "all_categories_masked")
        self.assertEqual(envelope.diagnostic_distribution, {})

    def test_ties_follow_research_service_alphabetic_order(self):
        envelope = decide_local_practice_priority(
            LocalDecisionRequest(
                categories=["reflection", "evidence"],
                parent_distribution={"reflection": 0.5, "evidence": 0.5},
                evidence=[],
                permitted_categories=["reflection", "evidence"],
                kappa_company=2.0,
                temporal_decay_rate_per_day=0.0,
                support_tau=8.0,
                abstention_threshold=0.0,
            )
        )
        self.assertEqual(envelope.priority_order, ("evidence", "reflection"))
        self.assertEqual(envelope.top_category, "evidence")

    def test_unknown_evidence_category_fails_closed(self):
        request = LocalDecisionRequest(
            categories=["ownership"],
            parent_distribution={"ownership": 1.0},
            evidence=[EvidenceRecord("unexpected", True, 1.0, 0.0)],
            permitted_categories=["ownership"],
            kappa_company=2.0,
            temporal_decay_rate_per_day=0.0,
            support_tau=8.0,
            abstention_threshold=0.0,
        )
        with self.assertRaises(ValueError):
            decide_local_practice_priority(request)

    def test_non_finite_request_hyperparameters_fail_closed(self):
        base = dict(
            categories=["ownership"],
            parent_distribution={"ownership": 1.0},
            evidence=[],
            permitted_categories=["ownership"],
            kappa_company=2.0,
            temporal_decay_rate_per_day=0.0,
            support_tau=8.0,
            abstention_threshold=0.0,
        )
        for field in (
            "kappa_company",
            "temporal_decay_rate_per_day",
            "support_tau",
            "abstention_threshold",
        ):
            values = dict(base)
            values[field] = float("nan")
            with self.subTest(field=field):
                with self.assertRaises(ValueError):
                    decide_local_practice_priority(LocalDecisionRequest(**values))


if __name__ == "__main__":
    unittest.main()
