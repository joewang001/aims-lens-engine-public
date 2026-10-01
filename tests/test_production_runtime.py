import dataclasses
import unittest

from runtime_core import (
    BackoffCandidate,
    DecisionEnvelope,
    LocalDecisionRequest,
    PROMOTION_REQUIRED_GATES,
    PromotionGateEvidence,
    build_production_envelope,
    compare_decision_envelopes,
    decide_local_practice_priority,
    evaluate_shadow_routing,
    resolve_runtime_mode,
)


def passing_gates():
    return PromotionGateEvidence(
        regression_suite_passed=True,
        public_safety_scan_passed=True,
        external_contract_compatibility_passed=True,
        provenance_review_passed=True,
        private_production_controls_ready=True,
        human_review_calibration_ready=True,
        owner_approval_recorded=True,
    )


def local_request():
    return LocalDecisionRequest(
        categories=("ownership", "evidence"),
        parent_distribution={"ownership": 0.5, "evidence": 0.5},
        evidence=(),
        permitted_categories=("ownership", "evidence"),
        kappa_company=4.0,
        temporal_decay_rate_per_day=0.0,
        support_tau=8.0,
        abstention_threshold=0.0,
    )


def shadow_routing():
    return evaluate_shadow_routing(
        candidates=(
            BackoffCandidate(
                name="L0_full_parent_context",
                backoff_distance=0,
                authorized=True,
                applicable=True,
                fresh=True,
                maturity_allows_output=True,
                effective_permitted_evidence_mass=0.0,
                distribution={"ownership": 0.8, "evidence": 0.2},
            ),
            BackoffCandidate(
                name="L3_industry_context",
                backoff_distance=3,
                authorized=True,
                applicable=True,
                fresh=True,
                maturity_allows_output=True,
                effective_permitted_evidence_mass=8.0,
                distribution={"ownership": 0.2, "evidence": 0.8},
            ),
        ),
        local_reference_distribution={"ownership": 0.8, "evidence": 0.2},
        categories=("ownership", "evidence"),
        permitted_categories=("ownership", "evidence"),
        support_tau=8.0,
        support_threshold=0.3,
        divergence_threshold=0.2,
    )


class ProductionSwitchTests(unittest.TestCase):
    def test_missing_promotion_gates_fail_closed_to_shadow(self):
        result = resolve_runtime_mode("promoted_local")
        self.assertEqual(result.effective_mode, "shadow")
        self.assertFalse(result.promoted_live)
        self.assertEqual(result.reason, "promotion_gates_not_satisfied")
        self.assertEqual(result.blocking_gates, PROMOTION_REQUIRED_GATES)

    def test_any_failed_gate_blocks_live_promotion(self):
        gates = dataclasses.replace(
            passing_gates(),
            provenance_review_passed=False,
        )
        result = resolve_runtime_mode("promoted_local", gates)
        self.assertEqual(result.effective_mode, "shadow")
        self.assertEqual(
            result.blocking_gates,
            ("provenance_review_passed",),
        )

    def test_all_required_gates_allow_promoted_local(self):
        result = resolve_runtime_mode("promoted_local", passing_gates())
        self.assertEqual(result.effective_mode, "promoted_local")
        self.assertTrue(result.promoted_live)
        self.assertEqual(result.blocking_gates, ())

    def test_legacy_and_shadow_do_not_require_promotion_attestations(self):
        self.assertEqual(
            resolve_runtime_mode("legacy").effective_mode,
            "legacy",
        )
        self.assertEqual(
            resolve_runtime_mode("shadow").effective_mode,
            "shadow",
        )

    def test_non_boolean_gate_fails_closed_as_invalid_input(self):
        gates = dataclasses.replace(
            passing_gates(),
            owner_approval_recorded=1,
        )
        with self.assertRaises(ValueError):
            resolve_runtime_mode("promoted_local", gates)


class ProductionEnvelopeTests(unittest.TestCase):
    def test_promoted_local_releases_only_local_decision_live(self):
        decision = decide_local_practice_priority(local_request())
        shadow = shadow_routing()
        self.assertTrue(shadow.divergence.triggered)

        envelope = build_production_envelope(
            decision=decision,
            runtime_switch=resolve_runtime_mode(
                "promoted_local",
                passing_gates(),
            ),
            shadow_routing=shadow,
        )

        self.assertEqual(envelope.release_status, "live_promoted")
        self.assertEqual(envelope.provenance.runtime_path, "promoted_local")
        self.assertEqual(
            envelope.provenance.shadow_routing.enforcement_mode,
            "shadow",
        )
        self.assertTrue(
            envelope.provenance.shadow_routing.divergence_triggered
        )
        self.assertEqual(
            envelope.runtime_switch.shadow_routing_enforcement,
            "shadow",
        )

    def test_blocked_promotion_envelope_is_shadow_only(self):
        decision = decide_local_practice_priority(local_request())
        envelope = build_production_envelope(
            decision=decision,
            runtime_switch=resolve_runtime_mode("promoted_local"),
        )
        self.assertEqual(envelope.release_status, "shadow_only")
        self.assertEqual(
            envelope.explanation.code,
            "promoted_output_shadow_only",
        )

    def test_legacy_mode_does_not_release_promoted_output(self):
        decision = decide_local_practice_priority(local_request())
        envelope = build_production_envelope(
            decision=decision,
            runtime_switch=resolve_runtime_mode("legacy"),
        )
        self.assertEqual(envelope.release_status, "not_released")
        self.assertEqual(
            envelope.explanation.code,
            "promoted_output_not_released",
        )

    def test_public_provenance_excludes_sensitive_audit_fields(self):
        decision = decide_local_practice_priority(local_request())
        envelope = build_production_envelope(
            decision=decision,
            runtime_switch=resolve_runtime_mode("shadow"),
            shadow_routing=shadow_routing(),
        )
        payload = dataclasses.asdict(envelope.provenance)
        rendered = repr(payload)
        for forbidden in (
            "audit_id",
            "timestamp",
            "context_hash",
            "parent_config",
            "evidence_packet_ids",
            "tenant_id",
            "diagnostic_distribution",
        ):
            self.assertNotIn(forbidden, rendered)

    def test_no_supported_shadow_level_has_reason_without_support(self):
        decision = decide_local_practice_priority(local_request())
        no_selection = evaluate_shadow_routing(
            candidates=(
                BackoffCandidate(
                    name="L0_full_parent_context",
                    backoff_distance=0,
                    authorized=True,
                    applicable=True,
                    fresh=True,
                    maturity_allows_output=True,
                    effective_permitted_evidence_mass=0.0,
                    distribution={"ownership": 0.8, "evidence": 0.2},
                ),
            ),
            local_reference_distribution={"ownership": 0.8, "evidence": 0.2},
            categories=("ownership", "evidence"),
            permitted_categories=("ownership", "evidence"),
            support_tau=8.0,
            support_threshold=0.3,
            divergence_threshold=0.2,
        )
        envelope = build_production_envelope(
            decision=decision,
            runtime_switch=resolve_runtime_mode("shadow"),
            shadow_routing=no_selection,
        )
        provenance = envelope.provenance.shadow_routing
        self.assertIsNone(provenance.selected_level)
        self.assertEqual(provenance.selection_reason, "no_supported_backoff_level")
        self.assertIsNone(provenance.data_support)
        self.assertIsNone(provenance.divergence_metric)

    def test_explanation_keeps_practice_not_prediction_boundary(self):
        decision = decide_local_practice_priority(local_request())
        envelope = build_production_envelope(
            decision=decision,
            runtime_switch=resolve_runtime_mode(
                "promoted_local",
                passing_gates(),
            ),
        )
        self.assertIn("prioritizes interview practice", envelope.explanation.disclaimer)
        self.assertIn("not a prediction", envelope.explanation.disclaimer)

    def test_malformed_manual_decision_is_rejected(self):
        malformed = DecisionEnvelope(
            mode="ordered_practice_priority",
            reason=None,
            top_category="ownership",
            priority_order=("ownership", "evidence"),
            diagnostic_distribution={"ownership": 0.8, "evidence": 0.8},
            data_support=0.5,
            effective_evidence_mass=4.0,
        )
        with self.assertRaises(ValueError):
            build_production_envelope(
                decision=malformed,
                runtime_switch=resolve_runtime_mode("shadow"),
            )


class DecisionRegressionTests(unittest.TestCase):
    def test_identical_decision_envelopes_pass_regression(self):
        decision = decide_local_practice_priority(local_request())
        result = compare_decision_envelopes(decision, decision)
        self.assertTrue(result.passed)
        self.assertEqual(result.mismatches, ())

    def test_priority_change_is_detected(self):
        expected = DecisionEnvelope(
            mode="ordered_practice_priority",
            reason=None,
            top_category="ownership",
            priority_order=("ownership", "evidence"),
            diagnostic_distribution={"ownership": 0.6, "evidence": 0.4},
            data_support=0.5,
            effective_evidence_mass=4.0,
        )
        actual = dataclasses.replace(
            expected,
            top_category="evidence",
            priority_order=("evidence", "ownership"),
        )
        result = compare_decision_envelopes(expected, actual)
        self.assertFalse(result.passed)
        self.assertIn("top_category", result.mismatches)
        self.assertIn("priority_order", result.mismatches)

    def test_distribution_change_respects_declared_tolerance(self):
        expected = DecisionEnvelope(
            mode="ordered_practice_priority",
            reason=None,
            top_category="ownership",
            priority_order=("ownership", "evidence"),
            diagnostic_distribution={"ownership": 0.6, "evidence": 0.4},
            data_support=0.5,
            effective_evidence_mass=4.0,
        )
        actual = dataclasses.replace(
            expected,
            diagnostic_distribution={
                "ownership": 0.6000001,
                "evidence": 0.3999999,
            },
        )
        self.assertTrue(
            compare_decision_envelopes(
                expected,
                actual,
                tolerance=1e-6,
            ).passed
        )
        self.assertFalse(
            compare_decision_envelopes(
                expected,
                actual,
                tolerance=1e-9,
            ).passed
        )

    def test_invalid_tolerance_is_rejected(self):
        decision = decide_local_practice_priority(local_request())
        with self.assertRaises(ValueError):
            compare_decision_envelopes(
                decision,
                decision,
                tolerance=float("nan"),
            )

    def test_non_finite_regression_value_is_detected(self):
        expected = DecisionEnvelope(
            mode="ordered_practice_priority",
            reason=None,
            top_category="ownership",
            priority_order=("ownership", "evidence"),
            diagnostic_distribution={"ownership": 0.6, "evidence": 0.4},
            data_support=0.5,
            effective_evidence_mass=4.0,
        )
        actual = dataclasses.replace(
            expected,
            diagnostic_distribution={
                "ownership": float("nan"),
                "evidence": 0.4,
            },
        )
        result = compare_decision_envelopes(expected, actual)
        self.assertFalse(result.passed)
        self.assertIn(
            "diagnostic_distribution[ownership]",
            result.mismatches,
        )


if __name__ == "__main__":
    unittest.main()
