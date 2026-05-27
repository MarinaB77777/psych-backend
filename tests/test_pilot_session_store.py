from pilot_session.schemas import ParticipantSession
from pilot_session.store import PilotSessionStore


def test_store_save_and_get_session():
    store = PilotSessionStore()

    session = ParticipantSession(
        session_id="session-1",
        participant_id="participant-1",
    )

    store.save(session)

    loaded = store.get("session-1")

    assert loaded is not None
    assert loaded.session_id == "session-1"
    assert loaded.participant_id == "participant-1"


def test_store_exists():
    store = PilotSessionStore()

    session = ParticipantSession(
        session_id="session-2",
        participant_id="participant-2",
    )

    store.save(session)

    assert store.exists("session-2") is True
    assert store.exists("missing") is False


def test_store_list_all_sessions():
    store = PilotSessionStore()

    session_1 = ParticipantSession(
        session_id="s1",
        participant_id="p1",
    )

    session_2 = ParticipantSession(
        session_id="s2",
        participant_id="p2",
    )

    store.save(session_1)
    store.save(session_2)

    sessions = store.list_all()

    assert len(sessions) == 2
