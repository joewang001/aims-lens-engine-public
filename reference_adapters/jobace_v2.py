from __future__ import annotations

import copy
from dataclasses import dataclass
from typing import Any, Dict, Mapping, Optional, Union

from .candidate_signals import CandidateSignalPacket


Identifier = Union[str, int]

REQUIRED_EXTERNAL_FIELDS = (
    "tenant_id",
    "user_id",
    "conversation_id",
    "message_id",
    "company",
    "role",
    "question",
    "answer",
)

KNOWN_EXTERNAL_FIELDS = frozenset(
    REQUIRED_EXTERNAL_FIELDS
    + (
        "job_description",
        "resume_summary",
        "jobace_mode",
        "jobace_sub_mode",
    )
)


def _string_value(value: Any, field: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{field} must be a string")
    return value


def _identifier(value: Any, field: str) -> Identifier:
    if isinstance(value, bool) or not isinstance(value, (str, int)):
        raise ValueError(f"{field} must be a string or integer")
    return value


def _optional_string(
    payload: Mapping[str, Any],
    field: str,
    *,
    allow_none: bool = False,
) -> Optional[str]:
    if field not in payload:
        return None
    value = payload[field]
    if value is None and allow_none:
        return None
    return _string_value(value, field)


@dataclass(frozen=True)
class ExternalIdentifiers:
    """Identifiers preserved exactly as accepted by the current contract."""

    tenant_id: str
    user_id: Identifier
    conversation_id: Identifier
    message_id: Identifier


@dataclass(frozen=True)
class PracticeContext:
    """Institution-agnostic practice context normalized from JobACE input."""

    namespace_id: str
    subject_id: str
    session_id: str
    turn_id: str
    target_organization: str
    target_role: str
    prompt_text: str
    response_text: str
    position_description: Optional[str]
    candidate_profile_summary: Optional[str]
    mode: Optional[str]
    sub_mode: Optional[str]


@dataclass(frozen=True)
class AdapterV2Envelope:
    """Public-safe JobACE Adapter v2 reference result.

    The envelope preserves the current external contract while producing a
    generic practice context. It does not bind candidate signals to runtime
    categories, invoke the decision layer, or represent a production mapping.
    """

    identifiers: ExternalIdentifiers
    context: PracticeContext
    candidate_signals: Optional[CandidateSignalPacket]
    extensions: Dict[str, Any]
    source_contract: str = "jobace_adapter_contract.schema.json"
    decision_binding_status: str = "unbound"
    adapter_mode: str = "reference"

    def validate(self) -> None:
        if self.source_contract != "jobace_adapter_contract.schema.json":
            raise ValueError("unexpected source contract")
        if self.decision_binding_status != "unbound":
            raise ValueError(
                "reference adapter must not bind live decision policy"
            )
        if self.adapter_mode != "reference":
            raise ValueError("adapter_mode must remain reference")
        if self.candidate_signals is not None:
            if not isinstance(self.candidate_signals, CandidateSignalPacket):
                raise ValueError(
                    "candidate_signals must be a CandidateSignalPacket"
                )
            self.candidate_signals.validate()


def adapt_jobace_payload_v2(
    payload: Mapping[str, Any],
    candidate_signals: CandidateSignalPacket | None = None,
) -> AdapterV2Envelope:
    """Normalize the existing JobACE payload without changing its contract.

    Unknown JSON fields are retained in extensions but are not interpreted.
    The function performs no persistence, scoring, prompt routing, calibration,
    screening recommendation, or live runtime decision binding.
    """

    if not isinstance(payload, Mapping):
        raise ValueError("payload must be a mapping")

    missing = [
        field for field in REQUIRED_EXTERNAL_FIELDS
        if field not in payload
    ]
    if missing:
        raise ValueError("missing required JobACE adapter field")

    tenant_id = _string_value(payload["tenant_id"], "tenant_id")
    user_id = _identifier(payload["user_id"], "user_id")
    conversation_id = _identifier(
        payload["conversation_id"],
        "conversation_id",
    )
    message_id = _identifier(payload["message_id"], "message_id")

    company = _string_value(payload["company"], "company")
    role = _string_value(payload["role"], "role")
    question = _string_value(payload["question"], "question")
    answer = _string_value(payload["answer"], "answer")

    job_description = _optional_string(payload, "job_description")
    resume_summary = _optional_string(payload, "resume_summary")
    mode = _optional_string(payload, "jobace_mode")
    sub_mode = _optional_string(
        payload,
        "jobace_sub_mode",
        allow_none=True,
    )

    identifiers = ExternalIdentifiers(
        tenant_id=tenant_id,
        user_id=user_id,
        conversation_id=conversation_id,
        message_id=message_id,
    )
    context = PracticeContext(
        namespace_id=tenant_id,
        subject_id=str(user_id),
        session_id=str(conversation_id),
        turn_id=str(message_id),
        target_organization=company,
        target_role=role,
        prompt_text=question,
        response_text=answer,
        position_description=job_description,
        candidate_profile_summary=resume_summary,
        mode=mode,
        sub_mode=sub_mode,
    )
    extensions = {
        key: copy.deepcopy(value)
        for key, value in payload.items()
        if key not in KNOWN_EXTERNAL_FIELDS
    }

    envelope = AdapterV2Envelope(
        identifiers=identifiers,
        context=context,
        candidate_signals=candidate_signals,
        extensions=dict(extensions),
    )
    envelope.validate()
    return envelope
