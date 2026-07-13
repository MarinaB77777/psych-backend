from collections import defaultdict
from datetime import datetime
from typing import Any

from research.analyses.health_model.model_parameter_catalog import (
    collect_health_model_parameter_records,
)


MODEL_PARAMETER_PAIR_DATASET_SCHEMA_VERSION = (
    "health-model-parameter-pair-dataset-1"
)

ANALYSIS_SCOPE_CROSS_PARTICIPANT = "CROSS_PARTICIPANT"
ANALYSIS_SCOPE_WITHIN_PARTICIPANT = "WITHIN_PARTICIPANT"

REPEATED_POLICY_REJECT = "reject_repeated"
REPEATED_POLICY_LATEST = "latest"
REPEATED_POLICY_EARLIEST = "earliest"

SUPPORTED_REPEATED_POLICIES = {
    REPEATED_POLICY_REJECT,
    REPEATED_POLICY_LATEST,
    REPEATED_POLICY_EARLIEST,
}


def _iso_value(value) -> str | None:
    if value is None:
        return None

    if isinstance(value, datetime):
        return value.isoformat()

    return str(value)

def _human_parameter_title(
    parameter_code: str,
) -> str:
    final_part = parameter_code.split(".")[-1]

    return final_part.replace("_", " ").strip().title()


def _observation_reference(
    observation: dict,
    *,
    variable_1_code: str,
    variable_2_code: str,
) -> dict:
    return {
        "participant_reference": (
            observation.get("participant_key")
        ),
        "session_id": observation.get("session_id"),
        "observation_time": observation.get(
            "observation_time"
        ),
        "variable_1": {
            "name": _human_parameter_title(
                variable_1_code
            ),
            "code": variable_1_code,
            "value": observation.get("left_value"),
        },
        "variable_2": {
            "name": _human_parameter_title(
                variable_2_code
            ),
            "code": variable_2_code,
            "value": observation.get("right_value"),
        },
    }


def _excluded_observation_reference(
    observation: dict,
    *,
    reason_code: str,
    reason_text: str,
    variable_1_code: str,
    variable_2_code: str,
) -> dict:
    return {
        **_observation_reference(
            observation,
            variable_1_code=variable_1_code,
            variable_2_code=variable_2_code,
        ),
        "exclusion_reason_code": reason_code,
        "exclusion_reason": reason_text,
    }


def _build_dataset_formation(
    *,
    analysis_scope: str,
    repeated_measure_policy: str,
    participant_reference: str | None,
    candidate_observations: list[dict],
    included_observations: list[dict],
    excluded_observations: list[dict],
    selection_status: str,
) -> dict:
    candidate_participants = {
        observation.get("participant_key")
        for observation in candidate_observations
        if observation.get("participant_key")
    }

    included_participants = {
        observation.get("participant_key")
        for observation in included_observations
        if observation.get("participant_key")
    }

    excluded_participants = {
        observation.get("participant_reference")
        for observation in excluded_observations
        if (
            observation.get("participant_reference")
            and observation.get("participant_reference")
            not in included_participants
        )
    }

    participants_with_excluded_observations = {
        observation.get("participant_reference")
        for observation in excluded_observations
        if observation.get("participant_reference")
    }
    if (
        analysis_scope
        == ANALYSIS_SCOPE_CROSS_PARTICIPANT
    ):
        scope_label = "Across participants"
        observation_unit_label = "Participant"
    else:
        scope_label = "Within one participant"
        observation_unit_label = "Session"

    policy_labels = {
        REPEATED_POLICY_REJECT: (
            "Do not select observations when a participant "
            "has repeated sessions"
        ),
        REPEATED_POLICY_LATEST: (
            "Use the latest paired session for each participant"
        ),
        REPEATED_POLICY_EARLIEST: (
            "Use the earliest paired session for each participant"
        ),
    }

    return {
        "selection_status": selection_status,
        "analysis_scope": analysis_scope,
        "analysis_scope_label": scope_label,
        "observation_unit": (
            "participant"
            if analysis_scope
            == ANALYSIS_SCOPE_CROSS_PARTICIPANT
            else "session"
        ),
        "observation_unit_label": (
            observation_unit_label
        ),
        "participant_reference": (
            participant_reference
        ),
        "repeated_measure_policy": (
            repeated_measure_policy
        ),
        "repeated_measure_policy_label": (
            policy_labels.get(
                repeated_measure_policy,
                repeated_measure_policy,
            )
        ),
        "observation_summary": {
            "eligible_observation_count": len(
                candidate_observations
            ),
            "included_observation_count": len(
                included_observations
            ),
            "excluded_observation_count": len(
                excluded_observations
            ),
        },
        "participant_summary": {
            "eligible_participant_count": len(
                candidate_participants
            ),
            "included_participant_count": len(
                included_participants
            ),
            "excluded_participant_count": len(
                excluded_participants
            ),
            "participants_with_excluded_observations_count": len(
                participants_with_excluded_observations
            ),
        },
        "included_session_ids": [
            observation.get("session_id")
            for observation
            in included_observations
            if observation.get("session_id")
        ],
        "excluded_session_ids": [
            observation.get("session_id")
            for observation
            in excluded_observations
            if observation.get("session_id")
        ],
        "included_participant_references": sorted(
            included_participants
        ),
        "excluded_participant_references": sorted(
            excluded_participants
        ),
        "participants_with_excluded_observations": sorted(
            participants_with_excluded_observations
        ),
    }


def _participant_key(record: dict) -> str | None:
    # subject_link_id is preferred because it is intended
    # to link the same research subject across sessions.
    return (
        record.get("subject_link_id")
        or record.get("participant_id")
    )


def _research_record_session_time(
    research_record: dict,
) -> str | None:
    snapshot = research_record.get("research_snapshot") or {}
    source_session = snapshot.get("source_session") or {}

    return _iso_value(
        source_session.get("updated_at")
        or source_session.get("created_at")
        or research_record.get("updated_at")
        or research_record.get("created_at")
    )


def _pilot_session_time(session: Any) -> str | None:
    return _iso_value(
        getattr(session, "updated_at", None)
        or getattr(session, "created_at", None)
    )


def _build_session_metadata(
    *,
    research_records: list[dict],
    pilot_sessions: list[Any],
) -> dict[str, dict]:
    metadata = {}

    for research_record in research_records:
        session_id = research_record.get("session_id")

        if not session_id:
            snapshot = (
                research_record.get("research_snapshot")
                or {}
            )
            source_session = (
                snapshot.get("source_session")
                or {}
            )
            session_id = source_session.get("session_id")

        if not session_id:
            continue

        snapshot = (
            research_record.get("research_snapshot")
            or {}
        )
        source_session = (
            snapshot.get("source_session")
            or {}
        )

        metadata[session_id] = {
            "session_id": session_id,
            "participant_id": (
                research_record.get("participant_id")
            ),
            "subject_link_id": (
                research_record.get("subject_link_id")
            ),
            "observation_time": (
                _research_record_session_time(
                    research_record
                )
            ),
            "record_source": "research_snapshot",
        }

        participant_reference = (
            snapshot.get("participant_reference")
            or {}
        )

        if not metadata[session_id].get(
            "participant_id"
        ):
            metadata[session_id]["participant_id"] = (
                participant_reference.get(
                    "participant_reference"
                )
                or participant_reference.get(
                    "export_scoped_participant_reference"
                )
            )

        if not metadata[session_id].get(
            "subject_link_id"
        ):
            metadata[session_id]["subject_link_id"] = (
                source_session.get("subject_link_id")
            )

    # Pilot session metadata fills gaps and is used for
    # sessions without a saved research snapshot.
    for session in pilot_sessions:
        session_id = getattr(
            session,
            "session_id",
            None,
        )

        if not session_id:
            continue

        pilot_metadata = {
            "session_id": session_id,
            "participant_id": getattr(
                session,
                "participant_id",
                None,
            ),
            "subject_link_id": getattr(
                session,
                "subject_link_id",
                None,
            ),
            "observation_time": _pilot_session_time(
                session
            ),
            "record_source": "pilot_session",
        }

        if session_id not in metadata:
            metadata[session_id] = pilot_metadata
            continue

        for key in [
            "participant_id",
            "subject_link_id",
            "observation_time",
        ]:
            if not metadata[session_id].get(key):
                metadata[session_id][key] = (
                    pilot_metadata.get(key)
                )

    return metadata


def _parameter_metadata(
    parameter_records: list[dict],
    parameter_code: str,
) -> dict:
    matching = [
        record
        for record in parameter_records
        if record.get("parameter_code")
        == parameter_code
    ]

    scale_types = {
        record.get("scale_type")
        for record in matching
        if record.get("scale_type")
    }

    value_types = {
        record.get("parameter_value_type")
        for record in matching
        if record.get("parameter_value_type")
    }

    return {
        "variable_source": (
            "calculated_model_parameter"
        ),
        "variable_code": parameter_code,
        "parameter_code": parameter_code,
        "title": _human_parameter_title(
            parameter_code
        ),
        "scale_type": (
            next(iter(scale_types))
            if len(scale_types) == 1
            else (
                "mixed"
                if scale_types
                else None
            )
        ),
        "parameter_value_type": (
            next(iter(value_types))
            if len(value_types) == 1
            else (
                "mixed"
                if value_types
                else None
            )
        ),
    }


def _build_paired_sessions(
    *,
    parameter_records: list[dict],
    session_metadata: dict[str, dict],
    left_parameter_code: str,
    right_parameter_code: str,
) -> list[dict]:
    by_session = defaultdict(dict)

    for record in parameter_records:
        parameter_code = record.get(
            "parameter_code"
        )

        if parameter_code not in {
            left_parameter_code,
            right_parameter_code,
        }:
            continue

        session_id = record.get("session_id")

        if not session_id:
            continue

        value = record.get("parameter_value")

        if value is None or value == "":
            continue

        by_session[session_id][
            parameter_code
        ] = value

        by_session[session_id][
            "_record_identity"
        ] = {
            "participant_id": record.get(
                "participant_id"
            ),
            "subject_link_id": record.get(
                "subject_link_id"
            ),
        }

    paired_sessions = []

    for session_id, values in by_session.items():
        if left_parameter_code not in values:
            continue

        if right_parameter_code not in values:
            continue

        metadata = dict(
            session_metadata.get(session_id) or {}
        )

        record_identity = (
            values.get("_record_identity")
            or {}
        )

        participant_id = (
            metadata.get("participant_id")
            or record_identity.get("participant_id")
        )

        subject_link_id = (
            metadata.get("subject_link_id")
            or record_identity.get(
                "subject_link_id"
            )
        )

        identity = {
            "participant_id": participant_id,
            "subject_link_id": subject_link_id,
        }

        paired_sessions.append({
            "session_id": session_id,
            "participant_id": participant_id,
            "subject_link_id": subject_link_id,
            "participant_key": _participant_key(
                identity
            ),
            "observation_time": metadata.get(
                "observation_time"
            ),
            "left_value": values[
                left_parameter_code
            ],
            "right_value": values[
                right_parameter_code
            ],
        })

    return sorted(
        paired_sessions,
        key=lambda item: (
            str(item.get("observation_time") or ""),
            str(item.get("session_id") or ""),
        ),
    )

def _select_cross_participant_observations(
    *,
    paired_sessions: list[dict],
    repeated_measure_policy: str,
    left_parameter_code: str,
    right_parameter_code: str,
) -> dict:
    by_participant = defaultdict(list)
    missing_identity_observations = []

    for observation in paired_sessions:
        participant_key = observation.get(
            "participant_key"
        )

        if not participant_key:
            missing_identity_observations.append(
                observation
            )
            continue

        by_participant[participant_key].append(
            observation
        )

    repeated_participants = {
        participant_key: observations
        for participant_key, observations
        in by_participant.items()
        if len(observations) > 1
    }

    excluded_observations = [
        _excluded_observation_reference(
            observation,
            reason_code=(
                "participant_identity_missing"
            ),
            reason_text=(
                "The observation has no stable participant "
                "reference and cannot be used in an "
                "across-participants analysis."
            ),
            variable_1_code=left_parameter_code,
            variable_2_code=right_parameter_code,
        )
        for observation
        in missing_identity_observations
    ]

    if (
        repeated_measure_policy
        == REPEATED_POLICY_REJECT
    ):
        selected = []

        for participant_key, observations in (
            by_participant.items()
        ):
            if len(observations) == 1:
                selected.append(
                    observations[0]
                )
                continue

            for observation in observations:
                excluded_observations.append(
                    _excluded_observation_reference(
                        observation,
                        reason_code=(
                            "participant_has_repeated_observations"
                        ),
                        reason_text=(
                            "This participant has more than one "
                            "paired session. All observations from "
                            "this participant were excluded according "
                            "to the selected repeated-observation "
                            "policy."
                        ),
                        variable_1_code=(
                            left_parameter_code
                        ),
                        variable_2_code=(
                            right_parameter_code
                        ),
                    )
                )

        return {
            "ok": True,
            "status": "ready",
            "observations": selected,
            "excluded_observations": (
                excluded_observations
            ),
            "participant_count": len(
                by_participant
            ),
            "selected_observation_count": len(
                selected
            ),
            "participants_with_repeated_pairs": len(
                repeated_participants
            ),
            "excluded_repeated_participant_count": len(
                repeated_participants
            ),
            "missing_identity_sessions": [
                observation.get("session_id")
                for observation
                in missing_identity_observations
            ],
        }

    selected = []

    for participant_key, observations in (
        by_participant.items()
    ):
        if len(observations) == 1:
            selected.append(
                observations[0]
            )
            continue

        observations_with_time = [
            observation
            for observation in observations
            if observation.get(
                "observation_time"
            )
        ]

        if len(observations_with_time) != len(
            observations
        ):
            missing_time_observations = [
                observation
                for observation in observations
                if not observation.get(
                    "observation_time"
                )
            ]

            for observation in (
                missing_time_observations
            ):
                excluded_observations.append(
                    _excluded_observation_reference(
                        observation,
                        reason_code=(
                            "observation_time_missing"
                        ),
                        reason_text=(
                            "The session cannot be ordered because "
                            "its observation time is missing."
                        ),
                        variable_1_code=(
                            left_parameter_code
                        ),
                        variable_2_code=(
                            right_parameter_code
                        ),
                    )
                )

            return {
                "ok": False,
                "status": (
                    "repeated_observation_time_missing"
                ),
                "observations": [],
                "excluded_observations": (
                    excluded_observations
                ),
                "participant_key": (
                    participant_key
                ),
                "session_ids": [
                    observation.get(
                        "session_id"
                    )
                    for observation
                    in observations
                ],
                "missing_identity_sessions": [
                    observation.get(
                        "session_id"
                    )
                    for observation
                    in missing_identity_observations
                ],
            }

        ordered = sorted(
            observations_with_time,
            key=lambda item: (
                item["observation_time"],
                item["session_id"],
            ),
        )

        if (
            repeated_measure_policy
            == REPEATED_POLICY_EARLIEST
        ):
            chosen = ordered[0]
            excluded = ordered[1:]
            reason_code = (
                "not_earliest_session"
            )
            reason_text = (
                "Another paired session was earlier "
                "and was selected according to the "
                "chosen policy."
            )

        elif (
            repeated_measure_policy
            == REPEATED_POLICY_LATEST
        ):
            chosen = ordered[-1]
            excluded = ordered[:-1]
            reason_code = (
                "not_latest_session"
            )
            reason_text = (
                "Another paired session was later "
                "and was selected according to the "
                "chosen policy."
            )

        else:
            return {
                "ok": False,
                "status": (
                    "unsupported_repeated_measure_policy"
                ),
                "observations": [],
                "excluded_observations": (
                    excluded_observations
                ),
            }

        selected.append(chosen)

        for observation in excluded:
            excluded_observations.append(
                _excluded_observation_reference(
                    observation,
                    reason_code=reason_code,
                    reason_text=reason_text,
                    variable_1_code=(
                        left_parameter_code
                    ),
                    variable_2_code=(
                        right_parameter_code
                    ),
                )
            )

    return {
        "ok": True,
        "status": "ready",
        "observations": selected,
        "excluded_observations": (
            excluded_observations
        ),
        "participant_count": len(
            by_participant
        ),
        "selected_observation_count": len(
            selected
        ),
        "participants_with_repeated_pairs": len(
            repeated_participants
        ),
        "excluded_repeated_participant_count": 0,
        "missing_identity_sessions": [
            observation.get("session_id")
            for observation
            in missing_identity_observations
        ],
    }

def _select_within_participant_observations(
    *,
    paired_sessions: list[dict],
    participant_reference: str | None,
    left_parameter_code: str,
    right_parameter_code: str,
) -> dict:
    if not participant_reference:
        return {
            "ok": False,
            "status": (
                "participant_reference_required"
            ),
            "observations": [],
            "excluded_observations": [],
        }

    selected = []
    excluded_observations = []

    for observation in paired_sessions:
        belongs_to_selected_participant = (
            participant_reference in {
                observation.get("subject_link_id"),
                observation.get("participant_id"),
                observation.get("participant_key"),
            }
        )

        if belongs_to_selected_participant:
            selected.append(observation)
            continue

        excluded_observations.append(
            _excluded_observation_reference(
                observation,
                reason_code=(
                    "different_participant"
                ),
                reason_text=(
                    "The session belongs to another participant "
                    "and is outside the selected within-participant "
                    "analysis."
                ),
                variable_1_code=left_parameter_code,
                variable_2_code=right_parameter_code,
            )
        )

    selected = sorted(
        selected,
        key=lambda item: (
            str(item.get("observation_time") or ""),
            str(item.get("session_id") or ""),
        ),
    )

    return {
        "ok": True,
        "status": "ready",
        "observations": selected,
        "excluded_observations": (
            excluded_observations
        ),
        "participant_reference": (
            participant_reference
        ),
        "selected_observation_count": len(
            selected
        ),
        "missing_time_count": sum(
            1
            for observation in selected
            if not observation.get(
                "observation_time"
            )
        ),
    }


def _to_compatible_answer_records(
    *,
    observations: list[dict],
    study_id: str,
    analysis_scope: str,
    left_parameter_code: str,
    right_parameter_code: str,
    left_scale_type: str | None,
    right_scale_type: str | None,
) -> list[dict]:
    answer_records = []

    for observation in observations:
        if (
            analysis_scope
            == ANALYSIS_SCOPE_CROSS_PARTICIPANT
        ):
            observation_key = observation.get(
                "participant_key"
            )
        else:
            observation_key = observation.get(
                "session_id"
            )

        if not observation_key:
            continue

        shared = {
            "record_type": (
                "calculated_model_parameter_observation"
            ),
            "study_id": study_id,
            "participant_id": observation_key,
            "session_id": observation.get(
                "session_id"
            ),
            "observation_time": observation.get(
                "observation_time"
            ),
            "variable_source": (
                "calculated_model_parameter"
            ),
            "analysis_scope": analysis_scope,
        }

        answer_records.append({
            **shared,
            "answer_record_id": (
                f"{observation_key}:left"
            ),
            "question_code": (
                left_parameter_code
            ),
            "original_variable_code": (
                left_parameter_code
            ),
            "answer_value": observation.get(
                "left_value"
            ),
            "scale_type": left_scale_type,
        })

        answer_records.append({
            **shared,
            "answer_record_id": (
                f"{observation_key}:right"
            ),
            "question_code": (
                right_parameter_code
            ),
            "original_variable_code": (
                right_parameter_code
            ),
            "answer_value": observation.get(
                "right_value"
            ),
            "scale_type": right_scale_type,
        })

    return answer_records


def build_model_parameter_pair_dataset(
    *,
    research_records: list[dict],
    pilot_sessions: list[Any],
    study_id: str,
    left_parameter_code: str,
    right_parameter_code: str,
    analysis_scope: str,
    repeated_measure_policy: str = (
        REPEATED_POLICY_REJECT
    ),
    participant_reference: str | None = None,
) -> dict:
    if (
        left_parameter_code
        == right_parameter_code
    ):
        return {
            "ok": False,
            "status": "same_variable_selected",
        }

    if repeated_measure_policy not in (
        SUPPORTED_REPEATED_POLICIES
    ):
        return {
            "ok": False,
            "status": (
                "unsupported_repeated_measure_policy"
            ),
            "repeated_measure_policy": (
                repeated_measure_policy
            ),
        }

    parameter_records = (
        collect_health_model_parameter_records(
            research_records=research_records,
            pilot_sessions=pilot_sessions,
            study_id=study_id,
        )
    )

    left_metadata = _parameter_metadata(
        parameter_records,
        left_parameter_code,
    )

    right_metadata = _parameter_metadata(
        parameter_records,
        right_parameter_code,
    )

    if left_metadata.get("scale_type") is None:
        return {
            "ok": False,
            "status": "left_parameter_not_found",
            "left_parameter_code": (
                left_parameter_code
            ),
        }

    if right_metadata.get("scale_type") is None:
        return {
            "ok": False,
            "status": "right_parameter_not_found",
            "right_parameter_code": (
                right_parameter_code
            ),
        }

    session_metadata = _build_session_metadata(
        research_records=research_records,
        pilot_sessions=pilot_sessions,
    )

    paired_sessions = _build_paired_sessions(
        parameter_records=parameter_records,
        session_metadata=session_metadata,
        left_parameter_code=left_parameter_code,
        right_parameter_code=right_parameter_code,
    )

    if (
        analysis_scope
        == ANALYSIS_SCOPE_CROSS_PARTICIPANT
    ):
        selection = (
            _select_cross_participant_observations(
                paired_sessions=paired_sessions,
                repeated_measure_policy=(
                    repeated_measure_policy
                ),
                left_parameter_code=(
                    left_parameter_code
                ),
                right_parameter_code=(
                    right_parameter_code
                ),
            )
        )

    elif (
        analysis_scope
        == ANALYSIS_SCOPE_WITHIN_PARTICIPANT
    ):
        selection = (
            _select_within_participant_observations(
                paired_sessions=paired_sessions,
                participant_reference=(
                    participant_reference
                ),
                left_parameter_code=(
                    left_parameter_code
                ),
                right_parameter_code=(
                    right_parameter_code
                ),
            )
        )

    else:
        return {
            "ok": False,
            "status": "unsupported_analysis_scope",
            "analysis_scope": analysis_scope,
        }

    if not selection.get("ok"):
        excluded_observations = selection.get(
            "excluded_observations",
            [],
        )

        dataset_formation = _build_dataset_formation(
            analysis_scope=analysis_scope,
            repeated_measure_policy=(
                repeated_measure_policy
            ),
            participant_reference=(
                participant_reference
            ),
            candidate_observations=paired_sessions,
            included_observations=[],
            excluded_observations=(
                excluded_observations
            ),
            selection_status=selection.get(
                "status",
                "blocked",
            ),
        )

        return {
            "schema_version": (
                MODEL_PARAMETER_PAIR_DATASET_SCHEMA_VERSION
            ),
            "study_id": study_id,
            "analysis_scope": analysis_scope,
            "repeated_measure_policy": (
                repeated_measure_policy
            ),
            "participant_reference": (
                participant_reference
            ),
            "left_variable": left_metadata,
            "right_variable": right_metadata,
            "comparison": {
                "variable_1": left_metadata,
                "variable_2": right_metadata,
            },
            "paired_session_count": len(
                paired_sessions
            ),
            "dataset_formation": dataset_formation,
            "included_observations": [],
            "excluded_observations": (
                excluded_observations
            ),
            **selection,
        }

    observations = selection.get(
        "observations",
        [],
    )
    
    excluded_observations = selection.get(
    "excluded_observations",
    [],
)

    included_observations = [
        _observation_reference(
            observation,
            variable_1_code=left_parameter_code,
            variable_2_code=right_parameter_code,
        )
        for observation in observations
    ]

    dataset_formation = _build_dataset_formation(
        analysis_scope=analysis_scope,
        repeated_measure_policy=(
            repeated_measure_policy
        ),
        participant_reference=(
            participant_reference
        ),
        candidate_observations=paired_sessions,
        included_observations=observations,
        excluded_observations=(
            excluded_observations
        ),
        selection_status="ready",
    )

    answer_records = (
        _to_compatible_answer_records(
            observations=observations,
            study_id=study_id,
            analysis_scope=analysis_scope,
            left_parameter_code=(
                left_parameter_code
            ),
            right_parameter_code=(
                right_parameter_code
            ),
            left_scale_type=left_metadata.get(
                "scale_type"
            ),
            right_scale_type=right_metadata.get(
                "scale_type"
            ),
        )
    )

    return {
        "ok": True,
        "status": "ready",
        "schema_version": (
            MODEL_PARAMETER_PAIR_DATASET_SCHEMA_VERSION
        ),
        "study_id": study_id,
        "analysis_scope": analysis_scope,
        "observation_unit": (
            "participant"
            if analysis_scope
            == ANALYSIS_SCOPE_CROSS_PARTICIPANT
            else "session"
        ),
        "repeated_measure_policy": (
            repeated_measure_policy
        ),
        "participant_reference": (
            participant_reference
        ),
        "left_variable": left_metadata,
        "right_variable": right_metadata,
        "comparison": {
            "variable_1": left_metadata,
            "variable_2": right_metadata,
        },
        "dataset_formation": dataset_formation,
        "included_observations": (
            included_observations
        ),
        "excluded_observations": (
            excluded_observations
        ),
        "paired_session_count": len(
            paired_sessions
        ),
        "selected_observation_count": len(
            observations
        ),
        "selection_summary": {
            key: value
            for key, value in selection.items()
            if key not in {
                "observations",
                "ok",
                "status",
            }
        },
        "observations": observations,
        "compatible_answer_records": (
            answer_records
        ),
    }
def list_model_parameter_pair_participants(
    *,
    research_records: list[dict],
    pilot_sessions: list[Any],
    study_id: str,
    left_parameter_code: str,
    right_parameter_code: str,
) -> dict:
    if left_parameter_code == right_parameter_code:
        return {
            "ok": False,
            "status": "same_variable_selected",
            "participants": [],
        }

    parameter_records = (
        collect_health_model_parameter_records(
            research_records=research_records,
            pilot_sessions=pilot_sessions,
            study_id=study_id,
        )
    )

    session_metadata = _build_session_metadata(
        research_records=research_records,
        pilot_sessions=pilot_sessions,
    )

    paired_sessions = _build_paired_sessions(
        parameter_records=parameter_records,
        session_metadata=session_metadata,
        left_parameter_code=left_parameter_code,
        right_parameter_code=right_parameter_code,
    )

    participants_by_key = {}

    for observation in paired_sessions:
        participant_key = observation.get(
            "participant_key"
        )

        if not participant_key:
            continue

        if participant_key not in participants_by_key:
            participants_by_key[participant_key] = {
                "participant_reference": participant_key,
                "participant_id": observation.get(
                    "participant_id"
                ),
                "subject_link_id": observation.get(
                    "subject_link_id"
                ),
                "paired_session_count": 0,
                "session_ids": [],
                "first_observation_time": None,
                "last_observation_time": None,
            }

        participant = participants_by_key[
            participant_key
        ]

        participant["paired_session_count"] += 1
        participant["session_ids"].append(
            observation.get("session_id")
        )

        observation_time = observation.get(
            "observation_time"
        )

        if observation_time:
            first_time = participant.get(
                "first_observation_time"
            )
            last_time = participant.get(
                "last_observation_time"
            )

            if (
                first_time is None
                or observation_time < first_time
            ):
                participant[
                    "first_observation_time"
                ] = observation_time

            if (
                last_time is None
                or observation_time > last_time
            ):
                participant[
                    "last_observation_time"
                ] = observation_time

    participants = sorted(
        participants_by_key.values(),
        key=lambda item: (
            -item["paired_session_count"],
            str(
                item.get("participant_reference")
                or ""
            ),
        ),
    )

    return {
        "ok": True,
        "status": "ready",
        "schema_version": (
            MODEL_PARAMETER_PAIR_DATASET_SCHEMA_VERSION
        ),
        "study_id": study_id,
        "left_parameter_code": left_parameter_code,
        "right_parameter_code": right_parameter_code,
        "pairing_unit": "session_id",
        "paired_session_count": len(
            paired_sessions
        ),
        "participant_count": len(
            participants
        ),
        "participants": participants,
    }
