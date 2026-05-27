from pilot_session.export import generate_session_export
from pilot_session.schemas import ParticipantSession, SessionStatus


def test_generate_session_export_uses_public_snapshot_only():
    session = ParticipantSession(
        session_id="session-1",
        participant_id="participant-1",
        status=SessionStatus.RUN_COMPLETED,
    )

    session.raw_engine_result = {"internal": "do-not-export"}
    session.public_output = {"summary_text": "Public summary"}
    session.uncertainty_snapshot = {"level": "low"}
    session.next_question_snapshots = [{"code": "q1"}]

    export = generate_session_export(session)

    assert export["session_id"] == "session-1"
    assert export["participant_id"] == "participant-1"
    assert export["public_output"] == {"summary_text": "Public summary"}
    assert export["uncertainty"] == {"level": "low"}
    assert export["next_questions"] == [{"code": "q1"}]
    assert "raw_engine_result" not in export
    assert "internal" not in export
