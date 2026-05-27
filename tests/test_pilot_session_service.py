import pytest

from pilot_session.schemas import SessionStatus
from pilot_session.service import PilotSessionService
from pilot_session.store import PilotSessionStore
from pilot_session.errors import (
    ExportBlockedError,
    InvalidStatusTransitionError,
    SessionInvalidatedError,
    SessionNotFoundError,
)


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

    with pytest.raises(SessionNotFoundError):
        service.submit_answers(
            session_id="missing",
            answers={"b1": 3},
        )


def test_submit_answers_rejects_invalid_status():
    store = PilotSessionStore()
    service = PilotSessionService(store)

    session = service.create_session(participant_id="participant-1")
    service.submit_answers(session.session_id, {"b1": 3})

    with pytest.raises(InvalidStatusTransitionError):
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

    with pytest.raises(InvalidStatusTransitionError):
        service.run_session(session.session_id)

def test_get_session_requires_existing_session():
    store = PilotSessionStore()
    service = PilotSessionService(store)

    with pytest.raises(SessionNotFoundError):
        service.get_session("missing-session")


def test_run_session_blocks_invalidated_session():
    store = PilotSessionStore()
    service = PilotSessionService(store)

    session = service.create_session(participant_id="participant-2")
    stored = service.get_session(session.session_id)
    stored.invalidated = True

    with pytest.raises(SessionInvalidatedError):
        service.run_session(session.session_id)


def test_generate_export_blocks_invalidated_session():
    store = PilotSessionStore()
    service = PilotSessionService(store)

    session = service.create_session(participant_id="participant-3")
    service.submit_answers(session.session_id, {"k23": 0, "k24": 0})
    service.run_session(session.session_id)

    stored = service.get_session(session.session_id)
    stored.invalidated = True

    with pytest.raises(ExportBlockedError):
        service.generate_export(session.session_id)


def test_close_session_marks_completed_session_closed():
    store = PilotSessionStore()
    service = PilotSessionService(store)

    session = service.create_session(participant_id="participant-4")
    service.submit_answers(session.session_id, {"k23": 0, "k24": 0})
    service.run_session(session.session_id)

    closed = service.close_session(session.session_id)

    assert closed.status == SessionStatus.CLOSED
    assert closed.closed_at is not None


def test_close_session_rejects_unfinished_session():
    store = PilotSessionStore()
    service = PilotSessionService(store)

    session = service.create_session(participant_id="participant-5")

    with pytest.raises(InvalidStatusTransitionError):
        service.close_session(session.session_id)


def test_invalidate_session_marks_session_invalidated():
    store = PilotSessionStore()
    service = PilotSessionService(store)

    session = service.create_session(participant_id="participant-6")

    invalidated = service.invalidate_session(
        session_id=session.session_id,
        reason="test invalidation",
    )

    assert invalidated.status == SessionStatus.INVALIDATED
    assert invalidated.invalidated is True
    assert invalidated.invalidation_reason == "test invalidation"


def test_close_session_blocks_invalidated_session():
    store = PilotSessionStore()
    service = PilotSessionService(store)

    session = service.create_session(participant_id="participant-7")

    service.invalidate_session(
        session_id=session.session_id,
        reason="test invalidation",
    )

    with pytest.raises(SessionInvalidatedError):
        service.close_session(session.session_id)
