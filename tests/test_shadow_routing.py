import unittest

from runtime_core import (
    BackoffCandidate,
    evaluate_shadow_routing,
    observe_context_divergence,
    select_support_aware_backoff,
)


def candidate(
    name,
    distance,
    mass,
    distribution,
    *,
    authorized=True,
    applicable=True,
    fresh=True,
    maturity=True,
):
    return BackoffCandidate(
        name=name,
        backoff_distance=distance,
        authorized=authorized,
        applicable=applicable,
        fresh=fresh,
        maturity_allows_output=maturity,
        effective_permitted_evidence_mass=mass,
        distribution=distribution,
    )


class SupportAwareBackoffTests(unittest.TestCase):
    def test_keeps_l0_when_local_support_is_adequate(self):
        selection = select_support_aware_backoff(
            candidates=[
                candidate(
                    "L0_full_parent_context",
                    0,
                    4.0,
                    {"ownership": 0.8, "evidence": 0.2},
                ),
                candidate(
                    "L3_industry_context",
                    3,
                    12.0,
                    {"ownership": 0.3, "evidence": 0.7},
                ),
            ],
            categories=["ownership", "evidence"],
            permitted_categories=["ownership", "evidence"],
            support_tau=8.0,
            support_threshold=0.3,
        )
        self.assertEqual(selection.selected_level, "L0_full_parent_context")
        self.assertEqual(selection.backoff_distance, 0)
        self.assertEqual(selection.enforcement_mode, "shadow")

    def test_backs_off_when_l0_support_is_below_threshold(self):
        selection = select_support_aware_backoff(
            candidates=[
                candidate(
                    "L0_full_parent_context",
                    0,
                    1.0,
                    {"ownership": 0.8, "evidence": 0.2},
                ),
                candidate(
                    "L3_industry_context",
                    3,
                    8.0,
                    {"ownership": 0.3, "evidence": 0.7},
                ),
            ],
            categories=["ownership", "evidence"],
            permitted_categories=["ownership", "evidence"],
            support_tau=8.0,
            support_threshold=0.3,
        )
        self.assertEqual(selection.selected_level, "L3_industry_context")
        self.assertEqual(selection.backoff_distance, 3)

    def test_ineligible_more_specific_level_is_skipped(self):
        selection = select_support_aware_backoff(
            candidates=[
                candidate(
                    "L0_full_parent_context",
                    0,
                    12.0,
                    {"ownership": 0.8, "evidence": 0.2},
                    authorized=False,
                ),
                candidate(
                    "L1_drop_one_parent",
                    1,
                    12.0,
                    {"ownership": 0.6, "evidence": 0.4},
                ),
            ],
            categories=["ownership", "evidence"],
            permitted_categories=["ownership", "evidence"],
            support_tau=8.0,
            support_threshold=0.3,
        )
        self.assertEqual(selection.selected_level, "L1_drop_one_parent")

    def test_zero_permitted_mass_level_is_skipped(self):
        selection = select_support_aware_backoff(
            candidates=[
                candidate(
                    "L0_full_parent_context",
                    0,
                    12.0,
                    {"ownership": 0.0, "evidence": 1.0},
                ),
                candidate(
                    "L3_industry_context",
                    3,
                    12.0,
                    {"ownership": 1.0, "evidence": 0.0},
                ),
            ],
            categories=["ownership", "evidence"],
            permitted_categories=["ownership"],
            support_tau=8.0,
            support_threshold=0.3,
        )
        self.assertEqual(selection.selected_level, "L3_industry_context")
        self.assertEqual(
            selection.diagnostic_distribution,
            {"ownership": 1.0},
        )

    def test_no_supported_level_fails_closed(self):
        selection = select_support_aware_backoff(
            candidates=[
                candidate(
                    "L0_full_parent_context",
                    0,
                    0.0,
                    {"ownership": 1.0},
                )
            ],
            categories=["ownership"],
            permitted_categories=["ownership"],
            support_tau=8.0,
            support_threshold=0.1,
        )
        self.assertIsNone(selection.selected_level)
        self.assertEqual(selection.reason, "no_supported_backoff_level")
        self.assertEqual(selection.diagnostic_distribution, {})
        self.assertEqual(selection.enforcement_mode, "shadow")

    def test_duplicate_backoff_distance_fails_closed(self):
        with self.assertRaises(ValueError):
            select_support_aware_backoff(
                candidates=[
                    candidate(
                        "L0_full_parent_context",
                        0,
                        8.0,
                        {"ownership": 1.0},
                    ),
                    BackoffCandidate(
                        name="L0_other",
                        backoff_distance=0,
                        authorized=True,
                        applicable=True,
                        fresh=True,
                        maturity_allows_output=True,
                        effective_permitted_evidence_mass=8.0,
                        distribution={"ownership": 1.0},
                    ),
                ],
                categories=["ownership"],
                permitted_categories=["ownership"],
                support_tau=8.0,
                support_threshold=0.1,
            )

    def test_malformed_ineligible_distribution_still_fails_closed(self):
        with self.assertRaises(ValueError):
            select_support_aware_backoff(
                candidates=[
                    candidate(
                        "L0_full_parent_context",
                        0,
                        8.0,
                        {"ownership": float("nan")},
                        authorized=False,
                    )
                ],
                categories=["ownership"],
                permitted_categories=["ownership"],
                support_tau=8.0,
                support_threshold=0.1,
            )


class ContextDivergenceShadowTests(unittest.TestCase):
    def test_total_variation_is_observed_in_shadow_mode(self):
        observation = observe_context_divergence(
            reference_distribution={"ownership": 0.8, "evidence": 0.2},
            candidate_distribution={"ownership": 0.3, "evidence": 0.7},
            categories=["ownership", "evidence"],
            threshold=0.4,
        )
        self.assertAlmostEqual(observation.value, 0.5)
        self.assertTrue(observation.triggered)
        self.assertEqual(observation.enforcement_mode, "shadow")

    def test_shadow_guard_does_not_change_backoff_selection(self):
        result = evaluate_shadow_routing(
            candidates=[
                candidate(
                    "L0_full_parent_context",
                    0,
                    1.0,
                    {"ownership": 0.8, "evidence": 0.2},
                ),
                candidate(
                    "L3_industry_context",
                    3,
                    8.0,
                    {"ownership": 0.2, "evidence": 0.8},
                ),
            ],
            local_reference_distribution={"ownership": 0.8, "evidence": 0.2},
            categories=["ownership", "evidence"],
            permitted_categories=["ownership", "evidence"],
            support_tau=8.0,
            support_threshold=0.3,
            divergence_threshold=0.2,
        )
        self.assertEqual(
            result.selection.selected_level,
            "L3_industry_context",
        )
        self.assertIsNotNone(result.divergence)
        self.assertTrue(result.divergence.triggered)
        self.assertEqual(result.divergence.enforcement_mode, "shadow")

    def test_no_selection_produces_no_divergence_observation(self):
        result = evaluate_shadow_routing(
            candidates=[
                candidate(
                    "L0_full_parent_context",
                    0,
                    0.0,
                    {"ownership": 1.0},
                )
            ],
            local_reference_distribution={"ownership": 1.0},
            categories=["ownership"],
            permitted_categories=["ownership"],
            support_tau=8.0,
            support_threshold=0.1,
            divergence_threshold=0.2,
        )
        self.assertIsNone(result.selection.selected_level)
        self.assertIsNone(result.divergence)

    def test_non_finite_inputs_fail_closed(self):
        with self.assertRaises(ValueError):
            observe_context_divergence(
                reference_distribution={"ownership": float("nan")},
                candidate_distribution={"ownership": 1.0},
                categories=["ownership"],
                threshold=0.2,
            )


if __name__ == "__main__":
    unittest.main()
