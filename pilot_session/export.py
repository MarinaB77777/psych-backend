from datetime import datetime, UTC

from pilot_session.schemas import ParticipantSession


def generate_session_export(session: ParticipantSession) -> dict:
    return {
        "export_schema_version": session.export_schema_version,
        "export_policy_version": session.export_policy_version,
        "generated_at": datetime.now(UTC).isoformat(),
        "session_id": session.session_id,
        "participant_id": session.participant_id,
        "status": session.status.value,
        "public_output": session.public_output,
        "uncertainty": session.uncertainty_snapshot,
        "next_questions": session.next_question_snapshots,
    }
