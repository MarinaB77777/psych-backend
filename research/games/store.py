from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .preparation import build_game_signal_bundle
from .registry import (
    get_game,
    get_event,
    get_object,
    get_question,
    is_allowed_event_type,
    is_allowed_screen,
)
from rc_config import data_path


DATA_FILE = data_path(
    "games",
    "game_sessions.json",
    legacy=Path(__file__).resolve().parent.parent / "game_sessions.json",
)
FORBIDDEN_AUTHORITY_KEYS = {
    "diagnosis",
    "truth",
    "interpretation",
    "conclusion",
    "current_state_score",
    "trajectory_failure_risk",
    "s",
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _read() -> list[dict]:
    if not DATA_FILE.exists():
        return []
    data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("Game session store must contain a list")
    return data if isinstance(data, list) else []


def _write(sessions: list[dict]) -> None:
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    DATA_FILE.write_text(
        json.dumps(sessions, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _find_index(sessions: list[dict], game_session_id: str) -> int | None:
    for index, session in enumerate(sessions):
        if session.get("game_session_id") == game_session_id:
            return index
    return None


def _assert_no_authority_payload(metadata: dict | None) -> None:
    if not metadata:
        return
    lowered = {str(key).lower() for key in metadata.keys()}
    found = sorted(lowered & FORBIDDEN_AUTHORITY_KEYS)
    if found:
        raise ValueError(
            "Game events cannot carry interpretation or diagnostic authority fields: "
            + ", ".join(found)
        )


def _assert_known_object_list(game_id: str, values: Any, field_name: str) -> None:
    if values is None:
        return
    if not isinstance(values, list):
        raise ValueError(f"{field_name} must be a list")
    for object_id in values:
        if not get_object(game_id, object_id):
            raise ValueError(f"Unknown game object in {field_name}")


def _assert_event_metadata(game_id: str, metadata: dict) -> None:
    event_id = metadata.get("event_id")
    if event_id and not get_event(game_id, event_id):
        raise ValueError("Unknown game registry event")

    for field_name in (
        "available_item_ids",
        "selected_item_ids",
        "removed_item_ids",
        "world_item_ids",
        "active_item_ids",
        "lost_item_ids",
        "explicitly_preserved_item_ids",
        "unavailable_item_ids",
    ):
        _assert_known_object_list(game_id, metadata.get(field_name), field_name)

    for field_name in ("item_id", "lost_item_id"):
        item_id = metadata.get(field_name)
        if item_id and not get_object(game_id, item_id):
            raise ValueError(f"Unknown game object in {field_name}")


def start_game_session(
    game_id: str,
    participant_id: str | None = None,
    study_id: str | None = None,
    source_session_id: str | None = None,
) -> dict:
    game = get_game(game_id)
    if not game:
        raise ValueError("Unknown game")

    game_session_id = str(uuid.uuid4())
    session = {
        "game_session_id": game_session_id,
        "session_id": source_session_id or game_session_id,
        "participant_id": participant_id,
        "study_id": study_id,
        "game_id": game["game_id"],
        "game_version": game["game_version"],
        "object_catalog_version": game["object_catalog_version"],
        "started_at": _now(),
        "completed_at": None,
        "completed": False,
        "abandoned": False,
        "events": [],
        "prepared_signal_bundle": None,
    }

    sessions = _read()
    sessions.append(session)
    _write(sessions)
    return session


def append_game_event(
    game_session_id: str,
    screen_id: str,
    event_type: str,
    object_id: str | None = None,
    previous_object_id: str | None = None,
    question_id: str | None = None,
    question_uuid: str | None = None,
    answer: Any = None,
    value: Any = None,
    decision_time_ms: int | None = None,
    confirmation_step: str | None = None,
    cancel_count: int = 0,
    excluded_from_analysis: bool = False,
    metadata: dict | None = None,
) -> dict:
    metadata = metadata or {}
    _assert_no_authority_payload(metadata)

    sessions = _read()
    index = _find_index(sessions, game_session_id)
    if index is None:
        raise ValueError("Game session not found")

    session = sessions[index]
    game = get_game(session["game_id"])
    if not game:
        raise ValueError("Unknown game")

    if not is_allowed_screen(session["game_id"], screen_id):
        raise ValueError("Unsupported game screen")

    if not is_allowed_event_type(session["game_id"], event_type):
        raise ValueError("Unsupported game event type")

    if object_id and not get_object(session["game_id"], object_id):
        raise ValueError("Unknown game object")

    if previous_object_id and not get_object(session["game_id"], previous_object_id):
        raise ValueError("Unknown previous game object")

    _assert_event_metadata(session["game_id"], metadata)

    if isinstance(value, dict):
        for field_name in (
            "available_item_ids",
            "selected_item_ids",
            "removed_item_ids",
            "world_item_ids",
            "active_item_ids",
            "lost_item_ids",
            "explicitly_preserved_item_ids",
            "unavailable_item_ids",
        ):
            _assert_known_object_list(session["game_id"], value.get(field_name), field_name)
        for field_name in ("item_id", "lost_item_id"):
            item_id = value.get(field_name)
            if item_id and not get_object(session["game_id"], item_id):
                raise ValueError(f"Unknown game object in {field_name}")

    question = None
    if question_id or question_uuid:
        question = get_question(session["game_id"], question_id, question_uuid)
        if not question:
            raise ValueError("Unknown game research question")
        question_id = question["question_id"]
        question_uuid = question["question_uuid"]

    event = {
        "event_id": str(uuid.uuid4()),
        "game_session_id": game_session_id,
        "session_id": session["session_id"],
        "game_id": session["game_id"],
        "game_version": session["game_version"],
        "question_id": question_id,
        "question_uuid": question_uuid,
        "answer": answer,
        "value": value,
        "shared_timestamp_utc": _now(),
        "screen_id": screen_id,
        "event_type": event_type,
        "object_id": object_id,
        "previous_object_id": previous_object_id,
        "decision_time_ms": decision_time_ms,
        "confirmation_step": confirmation_step,
        "cancel_count": cancel_count,
        "excluded_from_analysis": excluded_from_analysis,
        "metadata": metadata,
    }

    session["events"].append(event)
    session["prepared_signal_bundle"] = build_game_signal_bundle(session)
    sessions[index] = session
    _write(sessions)
    return event


def complete_game_session(
    game_session_id: str,
    completed: bool = True,
    abandoned: bool = False,
    metadata: dict | None = None,
) -> dict:
    _assert_no_authority_payload(metadata or {})

    sessions = _read()
    index = _find_index(sessions, game_session_id)
    if index is None:
        raise ValueError("Game session not found")

    session = sessions[index]
    session["completed"] = completed
    session["abandoned"] = abandoned
    session["completed_at"] = _now()
    session["completion_metadata"] = metadata or {}
    session["prepared_signal_bundle"] = build_game_signal_bundle(session)
    sessions[index] = session
    _write(sessions)
    return session


def get_game_session(game_session_id: str) -> dict | None:
    sessions = _read()
    index = _find_index(sessions, game_session_id)
    if index is None:
        return None
    return sessions[index]


def list_game_sessions() -> list[dict]:
    return _read()
