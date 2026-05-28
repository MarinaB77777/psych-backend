from datetime import UTC, datetime
from uuid import uuid4

from pilot_session.errors import ExportBlockedError
from pilot_session.schemas import ParticipantSession, SessionStatus


ALLOWED_PARTICIPANT_EXPORT_STATUSES = {
    SessionStatus.RUN_COMPLETED,
    SessionStatus.EXPORT_READY,
    SessionStatus.CLOSED,
}


def generate_participant_export(session: ParticipantSession) -> dict:
    if session.invalidated or session.status == SessionStatus.INVALIDATED:
        raise ExportBlockedError(
            "Participant export is blocked for invalidated session"
        )

    if session.status not in ALLOWED_PARTICIPANT_EXPORT_STATUSES:
        raise ExportBlockedError(
            "Participant export is not allowed for this session status"
        )

    if not session.public_output:
        raise ExportBlockedError(
            "Participant export is blocked because public_output is missing"
        )

    return {
        "export_id": str(uuid4()),
        "export_mode": "participant",
        "export_scope": "public_participant_safe",
        # Valid only for this generated participant export snapshot.
        "export_valid": True,
        "export_schema_version": session.export_schema_version,
        "export_policy_version": session.export_policy_version,
        "engine_version": session.engine_version,
        "generated_at": datetime.now(UTC).isoformat(),
        "generated_by": "pilot_session.export",
        "purpose": "participant_view",
        "session_id": session.session_id,
        # TODO: migrate to participant_code/public pseudonymous id if needed.
        "participant_id": session.participant_id,
        "status": session.status.value,
        "public_output": session.public_output,
        "uncertainty": session.uncertainty_snapshot or {},
        "next_questions": session.next_question_snapshots or [],
    }


def generate_research_export(session: ParticipantSession) -> dict:
    raise ExportBlockedError(
        "Research export is not implemented yet"
    )


# Temporary backward-compatible alias.
# TODO: remove after all callers use generate_participant_export explicitly.
generate_session_export = generate_participant_export