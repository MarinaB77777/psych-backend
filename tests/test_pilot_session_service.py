import pytest

from pilot_session.schemas import SessionStatus
from pilot_session.service import PilotSessionService
from pilot_session.store import PilotSessionStore


def test_create_session():
    store = PilotSessionStore()
    service = PilotSessionService(store)

    session = service.create_session(participant_id="participant-1")

    assert session.session_id
    assert session.participant_id == "participant-1"
    assert session.status == SessionStatus.CREATED
    assert store.exists(session.session_id) is True


def test_submit_answers_moves_session_to_answers_received():
    store = PilotSessionStore()
    service = PilotSessionService(store)

    session = service.create_session(participant_id="participant-1")

    updated = service.submit_answers(
        session_id=session.session_id,
        answers={"b1": 3},
    )

    assert updated.status == SessionStatus.ANSWERS_RECEIVED
    assert updated.answers == {"b1": 3}


def test_submit_answers_requires_existing_session():
    store = PilotSessionStore()
    service = PilotSessionService(store)

    with pytest.raises(ValueError, match="SESSION_NOT_FOUND"):
        service.submit_answers(
            session_id="missing",
            answers={"b1": 3},
        )


def test_submit_answers_rejects_invalid_status():
    store = PilotSessionStore()
    service = PilotSessionService(store)

    session = service.create_session(participant_id="participant-1")
    service.submit_answers(session.session_id, {"b1": 3})

    with pytest.raises(ValueError, match="INVALID_SESSION_STATUS"):
        service.submit_answers(session.session_id, {"b1": 4})


def test_run_session_stores_engine_snapshots():
    store = PilotSessionStore()
    service = PilotSessionService(store)

    session = service.create_session(participant_id="participant-1")
    service.submit_answers(session.session_id, {"b1": 3})

    updated = service.run_session(session.session_id)

    assert updated.status == SessionStatus.RUN_COMPLETED
    assert updated.raw_engine_result != {}
    assert updated.public_output == updated.raw_engine_result["output"]
    assert updated.next_question_snapshots == updated.raw_engine_result["next_questions"]
    assert (
        updated.acquisition_request_snapshots
        == updated.raw_engine_result["data_acquisition_requests"]
    )
    assert updated.uncertainty_snapshot == updated.raw_engine_result["uncertainty"]


def test_run_session_requires_answers_received_status():
    store = PilotSessionStore()
    service = PilotSessionService(store)

    session = service.create_session(participant_id="participant-1")

    with pytest.raises(ValueError, match="INVALID_SESSION_STATUS"):
        service.run_session(session.session_id)
