import copy
import json
import unittest
from pathlib import Path

from reference_adapters import (
    CandidateSignal,
    CandidateSignalPacket,
    adapt_current_aims_scores,
    adapt_jobace_payload_v2,
)


def jobace_payload():
    return {
        "tenant_id": "synthetic_tenant",
        "user_id": 101,
        "conversation_id": "conv-7",
        "message_id": 9,
        "company": "Example Company",
        "role": "Example Role",
        "question": "Tell me about a difficult decision.",
        "answer": (
            "I clarified the constraints, compared options, "
            "and measured the result."
        ),
        "job_description": "Synthetic role description.",
        "resume_summary": "Synthetic candidate summary.",
        "jobace_mode": "mock",
        "jobace_sub_mode": "company_lens",
    }


class CandidateSignalAdapterTests(unittest.TestCase):
    def test_normalizes_current_aims_scores_without_category_binding(self):
        packet = adapt_current_aims_scores(
            aims_scores={
                "structured_thinking": 6.5,
                "ownership_execution": 7.0,
            },
            confidence={
                "structured_thinking": 0.8,
                "ownership_execution": 0.7,
            },
            authorized_dimensions={"structured_thinking"},
            evidence_refs_by_dimension={
                "structured_thinking": ["synthetic-evidence-1"],
            },
        )

        self.assertEqual(packet.decision_binding_status, "unbound")
        self.assertEqual(len(packet.signals), 2)
        self.assertEqual(
            packet.signals[0].dimension,
            "structured_thinking",
        )
        self.assertTrue(packet.signals[0].authorized)
        self.assertFalse(packet.signals[1].authorized)
        self.assertEqual(packet.signals[0].age_days, 0.0)

    def test_scalar_confidence_does_not_derive_a_practice_gap(self):
        packet = adapt_current_aims_scores(
            aims_scores={"impact_results": 4.0},
            confidence=0.75,
            authorized_dimensions={"impact_results"},
        )
        self.assertEqual(packet.signals[0].score, 4.0)
        self.assertEqual(packet.signals[0].confidence, 0.75)

    def test_unknown_aims_dimension_fails_closed(self):
        with self.assertRaises(ValueError):
            adapt_current_aims_scores(
                aims_scores={"structure": 5.0},
                confidence=0.8,
                authorized_dimensions={"structure"},
            )

    def test_missing_per_dimension_confidence_fails_closed(self):
        with self.assertRaises(ValueError):
            adapt_current_aims_scores(
                aims_scores={
                    "structured_thinking": 5.0,
                    "impact_results": 5.0,
                },
                confidence={"structured_thinking": 0.8},
                authorized_dimensions={"structured_thinking"},
            )

    def test_non_finite_signal_inputs_fail_closed(self):
        signal = CandidateSignal(
            dimension="growth_mindset",
            score=float("nan"),
            confidence=0.8,
            authorized=True,
            age_days=0.0,
        )
        with self.assertRaises(ValueError):
            signal.validate()

    def test_boolean_score_fails_closed(self):
        with self.assertRaises(ValueError):
            adapt_current_aims_scores(
                aims_scores={"growth_mindset": True},
                confidence=0.8,
                authorized_dimensions={"growth_mindset"},
            )

    def test_extra_confidence_dimension_fails_closed(self):
        with self.assertRaises(ValueError):
            adapt_current_aims_scores(
                aims_scores={"growth_mindset": 6.0},
                confidence={
                    "growth_mindset": 0.8,
                    "impact_results": 0.7,
                },
                authorized_dimensions={"growth_mindset"},
            )

    def test_string_evidence_refs_fail_closed(self):
        with self.assertRaises(ValueError):
            adapt_current_aims_scores(
                aims_scores={"growth_mindset": 6.0},
                confidence=0.8,
                authorized_dimensions={"growth_mindset"},
                evidence_refs_by_dimension={
                    "growth_mindset": "not-a-list",
                },
            )

    def test_duplicate_signal_dimensions_fail_closed(self):
        signal = CandidateSignal(
            dimension="growth_mindset",
            score=6.0,
            confidence=0.8,
            authorized=True,
            age_days=0.0,
        )
        packet = CandidateSignalPacket(signals=(signal, signal))
        with self.assertRaises(ValueError):
            packet.validate()


class JobACEAdapterV2Tests(unittest.TestCase):
    def test_existing_staging_example_remains_contract_compatible(self):
        path = Path("examples/jobace-staging-screening-request.json")
        payload = json.loads(path.read_text(encoding="utf-8"))
        envelope = adapt_jobace_payload_v2(payload)
        self.assertEqual(
            envelope.context.target_organization,
            payload["company"],
        )
        self.assertEqual(envelope.identifiers.user_id, payload["user_id"])

    def test_preserves_ids_and_normalizes_generic_context(self):
        envelope = adapt_jobace_payload_v2(jobace_payload())
        self.assertEqual(envelope.identifiers.user_id, 101)
        self.assertEqual(envelope.context.subject_id, "101")
        self.assertEqual(
            envelope.context.target_organization,
            "Example Company",
        )
        self.assertEqual(envelope.context.target_role, "Example Role")
        self.assertEqual(envelope.decision_binding_status, "unbound")
        self.assertEqual(envelope.adapter_mode, "reference")

    def test_existing_optional_contract_fields_are_preserved(self):
        envelope = adapt_jobace_payload_v2(jobace_payload())
        self.assertEqual(
            envelope.context.position_description,
            "Synthetic role description.",
        )
        self.assertEqual(
            envelope.context.candidate_profile_summary,
            "Synthetic candidate summary.",
        )
        self.assertEqual(envelope.context.mode, "mock")
        self.assertEqual(envelope.context.sub_mode, "company_lens")

    def test_unknown_extension_is_retained_but_not_interpreted(self):
        payload = jobace_payload()
        payload["future_field"] = {"synthetic": True}
        envelope = adapt_jobace_payload_v2(payload)
        self.assertEqual(
            envelope.extensions,
            {"future_field": {"synthetic": True}},
        )
        envelope.extensions["future_field"]["synthetic"] = False
        self.assertTrue(payload["future_field"]["synthetic"])

    def test_adapter_does_not_mutate_external_payload(self):
        payload = jobace_payload()
        original = copy.deepcopy(payload)
        adapt_jobace_payload_v2(payload)
        self.assertEqual(payload, original)

    def test_missing_required_contract_field_fails_closed(self):
        payload = jobace_payload()
        del payload["answer"]
        with self.assertRaises(ValueError):
            adapt_jobace_payload_v2(payload)

    def test_boolean_identifier_is_rejected(self):
        payload = jobace_payload()
        payload["user_id"] = True
        with self.assertRaises(ValueError):
            adapt_jobace_payload_v2(payload)

    def test_schema_legal_empty_strings_are_not_narrowed(self):
        payload = jobace_payload()
        payload["tenant_id"] = ""
        payload["company"] = ""
        payload["role"] = ""
        payload["question"] = ""
        payload["answer"] = ""
        envelope = adapt_jobace_payload_v2(payload)
        self.assertEqual(envelope.context.target_organization, "")
        self.assertEqual(envelope.context.response_text, "")

    def test_candidate_signal_packet_is_carried_unbound(self):
        signals = adapt_current_aims_scores(
            aims_scores={"analytical_problem_solving": 6.0},
            confidence=0.8,
            authorized_dimensions={"analytical_problem_solving"},
        )
        envelope = adapt_jobace_payload_v2(
            jobace_payload(),
            candidate_signals=signals,
        )
        self.assertIs(envelope.candidate_signals, signals)
        self.assertEqual(
            envelope.candidate_signals.decision_binding_status,
            "unbound",
        )

    def test_wrong_candidate_signal_packet_type_fails_closed(self):
        with self.assertRaises(ValueError):
            adapt_jobace_payload_v2(
                jobace_payload(),
                candidate_signals={"not": "a packet"},
            )


if __name__ == "__main__":
    unittest.main()
