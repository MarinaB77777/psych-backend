from copy import deepcopy

from assessment.prepared_output import build_prepared_domain_output
from pilot_session.schemas import SessionStatus
from pilot_session.service import PilotSessionService
from pilot_session.store import PilotSessionStore


def _completed_session(service, participant_id, answers):
    session = service.create_session(participant_id=participant_id)
    service.submit_answers(session.session_id, deepcopy(answers))
    return service.run_session(session.session_id)


def _analysis_sessions(store, *, include_invalidated=False, include_incomplete=False):
    allowed_statuses = {SessionStatus.RUN_COMPLETED, SessionStatus.EXPORT_READY, SessionStatus.CLOSED}
    sessions = []

    for session in store.list_all():
        if session.invalidated and not include_invalidated:
            continue

        if session.status not in allowed_statuses and not include_incomplete:
            continue

        sessions.append(session)

    return sessions


def test_participant_can_have_multiple_sessions_without_mutating_old_session():
    store = PilotSessionStore()
    service = PilotSessionService(store)

    answers = {"d0": 1, "d1": 2}
    first = _completed_session(service, "participant-1", answers)
    first_snapshot = deepcopy(first)

    second = _completed_session(service, "participant-1", answers)

    assert first.session_id != second.session_id
    assert first.participant_id == second.participant_id == "participant-1"
    assert store.get(first.session_id) == first_snapshot
    assert store.get(first.session_id).answers == answers
    assert store.get(second.session_id).answers == answers
    assert len(store.get(first.session_id).research_answer_records) == len(answers)
    assert len(store.get(second.session_id).research_answer_records) == len(answers)


def test_counts_use_stable_participant_id_and_session_id():
    store = PilotSessionStore()
    service = PilotSessionService(store)

    _completed_session(service, "participant-1", {"d0": 1})
    _completed_session(service, "participant-1", {"d0": 2})
    _completed_session(service, "participant-2", {"d0": 3})

    sessions = store.list_all()
    unique_participants = {session.participant_id for session in sessions}
    unique_sessions = {session.session_id for session in sessions}

    assert len(unique_participants) == 2
    assert len(unique_sessions) == 3
    assert len(sessions) == 3


def test_trajectory_is_sorted_by_measurement_time():
    store = PilotSessionStore()
    service = PilotSessionService(store)

    first = _completed_session(service, "participant-1", {"d0": 1})
    second = _completed_session(service, "participant-1", {"d0": 2})
    third = _completed_session(service, "participant-1", {"d0": 3})

    trajectory = sorted(
        store.list_all(),
        key=lambda session: session.created_at,
    )

    assert [session.session_id for session in trajectory] == [
        first.session_id,
        second.session_id,
        third.session_id,
    ]


def test_invalidated_and_incomplete_sessions_are_preserved_but_policy_filtered():
    store = PilotSessionStore()
    service = PilotSessionService(store)

    completed = _completed_session(service, "participant-1", {"d0": 1})
    incomplete = service.create_session(participant_id="participant-1")
    invalidated = service.create_session(participant_id="participant-1")
    service.invalidate_session(invalidated.session_id, "participant withdrew")

    all_sessions = store.list_all()
    default_analysis_sessions = _analysis_sessions(store)
    explicit_policy_sessions = _analysis_sessions(
        store,
        include_invalidated=True,
        include_incomplete=True,
    )

    assert {session.session_id for session in all_sessions} == {
        completed.session_id,
        incomplete.session_id,
        invalidated.session_id,
    }
    assert [session.session_id for session in default_analysis_sessions] == [
        completed.session_id,
    ]
    assert {session.session_id for session in explicit_policy_sessions} == {
        completed.session_id,
        incomplete.session_id,
        invalidated.session_id,
    }


def test_prepared_domain_output_id_is_stable_for_same_snapshot():
    domain_data_identity = {
        "domain_id": "questionnaire",
        "source_type": "pilot_session",
        "study_id": "health_model",
        "session_id": "session-1",
        "participant_id": "participant-1",
    }
    raw_payload = {
        "payload_type": "questionnaire_answers",
        "study_id": "health_model",
        "answers": {"d0": 1, "d1": 2},
    }
    analysis_output = {
        "status": "completed",
        "public_explanation": {"title": "Saved"},
    }

    first = build_prepared_domain_output(
        domain_data_identity=domain_data_identity,
        raw_payload=raw_payload,
        analysis_output=analysis_output,
    )
    second = build_prepared_domain_output(
        domain_data_identity=deepcopy(domain_data_identity),
        raw_payload=deepcopy(raw_payload),
        analysis_output=deepcopy(analysis_output),
    )

    changed_payload = deepcopy(raw_payload)
    changed_payload["answers"]["d1"] = 3
    changed = build_prepared_domain_output(
        domain_data_identity=deepcopy(domain_data_identity),
        raw_payload=changed_payload,
        analysis_output=deepcopy(analysis_output),
    )

    assert first["prepared_output_id"] == second["prepared_output_id"]
    assert first["prepared_output_id"] != changed["prepared_output_id"]


if __name__ == "__main__":
    test_participant_can_have_multiple_sessions_without_mutating_old_session()
    test_counts_use_stable_participant_id_and_session_id()
    test_trajectory_is_sorted_by_measurement_time()
    test_invalidated_and_incomplete_sessions_are_preserved_but_policy_filtered()
    test_prepared_domain_output_id_is_stable_for_same_snapshot()
