from copy import deepcopy
from datetime import datetime, timedelta, timezone

from pilot_session.consistency_awareness import (
    build_consistency_observations,
    build_first_ray_colleague_clarification,
    build_ray_colleague_response,
)
from pilot_session.interview import build_ray_next_question
from pilot_session.schemas import ParticipantSession
from pilot_session.service import PilotSessionService
from pilot_session.store import PilotSessionStore


def _record(
    session_id,
    participant_id,
    value,
    *,
    question_uuid="q-d0",
    question_code="d0",
    question_version="v1",
    revision=1,
    created_at="2026-07-12T10:00:00+00:00",
    temporal_scope="current",
    context="pilot",
    unit="scale_0_5",
    source_mode="questionnaire",
    source_type=None,
):
    identity = {
        "temporal_scope": temporal_scope,
        "context": context,
        "unit": unit,
        "question_version": question_version,
        "language": "ru",
        "participant_id": participant_id,
        "session_id": session_id,
    }
    return {
        "answer_record_id": f"{session_id}-{question_code}-{revision}",
        "record_type": "questionnaire_answer",
        "created_at": created_at,
        "participant_id": participant_id,
        "session_id": session_id,
        "question_code": question_code,
        "question_id": question_uuid,
        "question_uuid": question_uuid,
        "question_version": question_version,
        "answer_value": value,
        "answer_value_type": type(value).__name__,
        "answer_revision": revision,
        "source_mode": source_mode,
        "source_type": source_type or source_mode,
        "domain_data_identity": identity,
    }


def _session(session_id, participant_id="participant-1", records=None, created_at=None):
    return ParticipantSession(
        session_id=session_id,
        participant_id=participant_id,
        created_at=created_at or datetime.now(timezone.utc),
        research_answer_records=records or [],
    )


def _participant_text(response):
    return " ".join(str(value) for value in response.values())


def test_same_session_answer_difference_requests_bounded_clarification():
    session = _session(
        "s1",
        records=[
            _record("s1", "participant-1", 1, revision=1),
            _record("s1", "participant-1", 4, revision=2),
        ],
    )

    observations = build_consistency_observations(session)
    response = build_first_ray_colleague_clarification(session, lang="en")

    assert observations[0].discrepancy_type == "same_session_answer_difference"
    assert observations[0].requires_clarification is True
    assert response["status"] == "clarification"
    assert response["confidence"] == "bounded_low"
    assert response["recommendation_allowed"] is False
    assert response["forecast_allowed"] is False
    assert response["interpretation"] is None


def test_between_session_change_is_not_treated_as_participant_truth():
    previous = _session(
        "s1",
        records=[_record("s1", "participant-1", 1, created_at="2026-07-12T10:00:00+00:00")],
        created_at=datetime.now(timezone.utc) - timedelta(days=1),
    )
    current = _session(
        "s2",
        records=[_record("s2", "participant-1", 5, created_at="2026-07-13T10:00:00+00:00")],
    )

    observations = build_consistency_observations(
        current,
        previous_sessions=[previous, current],
    )
    response = build_first_ray_colleague_clarification(
        current,
        previous_sessions=[previous, current],
        lang="ru",
    )

    assert observations[0].discrepancy_type == "between_session_change"
    assert observations[0].severity == "trajectory_candidate"
    assert "обман" not in _participant_text(response).lower()


def test_different_temporal_periods_are_clarified_not_contradicted():
    previous = _session(
        "s1",
        records=[_record("s1", "participant-1", 1, temporal_scope="last_week")],
    )
    current = _session(
        "s2",
        records=[_record("s2", "participant-1", 4, temporal_scope="today")],
    )

    observations = build_consistency_observations(
        current,
        previous_sessions=[previous],
    )

    assert observations[0].discrepancy_type == "temporal_scope_difference"
    assert "will not compare them as a direct contradiction" in build_ray_colleague_response(
        observations[0],
        lang="en",
    ).message.lower()


def test_sensor_self_report_difference_keeps_sensor_non_authoritative():
    current = _session(
        "s1",
        records=[_record("s1", "participant-1", 2)],
    )
    sensor_record = _record(
        "sensor-window-1",
        "participant-1",
        5,
        source_mode="sensor_context",
        source_type="sensor_context",
    )

    observations = build_consistency_observations(
        current,
        sensor_context_observations=[sensor_record],
    )
    response = build_first_ray_colleague_clarification(
        current,
        sensor_context_observations=[sensor_record],
        lang="en",
    )

    assert observations[0].discrepancy_type == "sensor_self_report_disagreement"
    assert "sensor is not a truth source" in response["message"].lower()
    assert "sensor shows truth" not in response["message"].lower()


def test_question_version_mismatch_blocks_comparison():
    previous = _session(
        "s1",
        records=[_record("s1", "participant-1", 1, question_version="v1")],
    )
    current = _session(
        "s2",
        records=[_record("s2", "participant-1", 4, question_version="v2")],
    )

    observations = build_consistency_observations(
        current,
        previous_sessions=[previous],
    )
    response = build_first_ray_colleague_clarification(
        current,
        previous_sessions=[previous],
    )

    assert observations[0].discrepancy_type == "comparison_blocked"
    assert observations[0].requires_clarification is False
    assert response is None


def test_missing_context_requires_context_clarification():
    previous = _session(
        "s1",
        records=[_record("s1", "participant-1", 1, temporal_scope=None, context=None)],
    )
    current = _session(
        "s2",
        records=[_record("s2", "participant-1", 3, temporal_scope=None, context=None)],
    )

    observations = build_consistency_observations(
        current,
        previous_sessions=[previous],
    )

    assert observations[0].discrepancy_type == "missing_context"
    assert observations[0].requires_clarification is True


def test_consistent_records_produce_no_clarification():
    previous = _session("s1", records=[_record("s1", "participant-1", 2)])
    current = _session("s2", records=[_record("s2", "participant-1", 2)])

    assert build_consistency_observations(current, previous_sessions=[previous]) == []
    assert build_first_ray_colleague_clarification(
        current,
        previous_sessions=[previous],
    ) is None


def test_colleague_check_does_not_modify_health_model_or_learning_memory():
    session = _session(
        "s1",
        records=[
            _record("s1", "participant-1", 1, revision=1),
            _record("s1", "participant-1", 3, revision=2),
        ],
    )
    session.raw_engine_result = {"health_model": {"score": 10}}
    before = deepcopy(session.raw_engine_result)

    response = build_first_ray_colleague_clarification(session, lang="en")

    assert session.raw_engine_result == before
    assert "health_model" not in response
    assert "learning" not in response
    assert "memory" not in response


def test_localization_is_available_for_ru_en_es():
    session = _session(
        "s1",
        records=[
            _record("s1", "participant-1", 1, revision=1),
            _record("s1", "participant-1", 3, revision=2),
        ],
    )

    for lang in ("ru", "en", "es"):
        response = build_first_ray_colleague_clarification(session, lang=lang)
        assert response["message"]
        assert set(response["blocks"].keys()) == {
            "known",
            "uncertain",
            "needs",
            "possible",
            "step",
        }


def test_participant_response_exposes_no_internal_ids_or_debug_metadata():
    session = _session(
        "s1",
        records=[
            _record("s1", "participant-1", 1, revision=1),
            _record("s1", "participant-1", 3, revision=2),
        ],
    )

    response = build_first_ray_colleague_clarification(session, lang="en")
    text = _participant_text(response)

    assert "observation_id" not in response
    assert "proposal_id" not in response
    assert "current_answer_ref" not in response
    assert "compared_answer_ref" not in response
    assert "debug" not in response
    assert "q-d0" not in text
    assert "answer_record_id" not in text
    assert [option["value"] for option in response["answer_options"]] == [
        "situation_changed",
        "different_period",
        "different_understanding",
        "previous_inaccurate",
        "both_true",
        "prefer_not_to_clarify",
    ]


def test_acceptance_flow_preserves_answer_records_and_routes_to_clarification():
    store = PilotSessionStore()
    service = PilotSessionService(store)
    session = service.create_session(participant_id="participant-1")

    service.submit_answers(
        session.session_id,
        {"d0": 1},
        domain_data_identity={
            "context": "pilot",
            "temporal_scope": "current",
            "unit": "scale_0_5",
        },
    )
    service.run_session(session.session_id)
    service.submit_followup_answers(session.session_id, {"d0": 4})
    updated = service.run_session(session.session_id)

    ray = build_ray_next_question(updated, lang="ru", previous_sessions=store.list_all())
    d0_records = [
        record for record in updated.research_answer_records
        if record["question_code"] == "d0"
    ]

    assert len(d0_records) == 2
    assert [record["answer_value"] for record in d0_records] == [1, 4]
    assert ray["status"] == "clarification"
    assert ray["confidence"] == "bounded_low"


def test_clarification_is_stored_separately_and_not_requested_again():
    store = PilotSessionStore()
    service = PilotSessionService(store)
    session = service.create_session(participant_id="participant-1")

    service.submit_answers(
        session.session_id,
        {"d0": 1},
        domain_data_identity={
            "context": "pilot",
            "temporal_scope": "current",
            "unit": "scale_0_5",
        },
    )
    service.run_session(session.session_id)
    service.submit_followup_answers(session.session_id, {"d0": 4})
    updated = service.run_session(session.session_id)

    clarification = service.record_consistency_clarification(
        updated.session_id,
        selected_option="situation_changed",
        free_text="Schedule changed",
        language="en",
        previous_sessions=store.list_all(),
    )
    after = service.get_session(updated.session_id)
    ray = build_ray_next_question(after, lang="en", previous_sessions=store.list_all())

    assert clarification["status"] == "clarified"
    assert len(after.consistency_clarifications) == 1
    assert after.answers["d0"] == 4
    assert [record["answer_value"] for record in after.research_answer_records if record["question_code"] == "d0"] == [1, 4]
    assert ray["status"] != "clarification"


if __name__ == "__main__":
    test_same_session_answer_difference_requests_bounded_clarification()
    test_between_session_change_is_not_treated_as_participant_truth()
    test_different_temporal_periods_are_clarified_not_contradicted()
    test_sensor_self_report_difference_keeps_sensor_non_authoritative()
    test_question_version_mismatch_blocks_comparison()
    test_missing_context_requires_context_clarification()
    test_consistent_records_produce_no_clarification()
    test_colleague_check_does_not_modify_health_model_or_learning_memory()
    test_localization_is_available_for_ru_en_es()
    test_participant_response_exposes_no_internal_ids_or_debug_metadata()
    test_acceptance_flow_preserves_answer_records_and_routes_to_clarification()
    test_clarification_is_stored_separately_and_not_requested_again()
