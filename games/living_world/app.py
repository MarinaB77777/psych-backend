from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from research.games.store import (
    append_game_event,
    complete_game_session,
    start_game_session,
)


router = APIRouter()

GAME_ID = "world_choice"
GAME_VERSION = "world_choice_v0_1"
LAUNCH_ROUTE = "/games/living-world"
RESULT_CONTRACT_VERSION = "living_world_result_v1"

PARTICIPANT_GAME_CARD = {
    "game_id": GAME_ID,
    "game_version": GAME_VERSION,
    "activity_type": "game",
    "title": {
        "ru": "Живой мир",
        "en": "Living World",
        "es": "Mundo vivo",
    },
    "description": {
        "ru": "Постройте маленький мир, проживите несколько месяцев и завершите игру.",
        "en": "Build a small world, live through a few months and finish safely.",
        "es": "Construye un mundo pequeno, vive unos meses y termina con seguridad.",
    },
    "availability": "enabled",
    "enabled": True,
    "compatibility": {
        "min_browser": "modern",
        "sensors_required": False,
    },
    "participant_launch_route": LAUNCH_ROUTE,
    "result_contract": RESULT_CONTRACT_VERSION,
    "consent_requirements": ["pilot_or_research_activity_consent"],
    "provenance_requirements": [
        "game_id",
        "game_version",
        "game_session_id",
        "session_id",
        "participant_id",
        "language",
        "event_trace",
        "bounded_result",
    ],
    "sensor_capabilities": {
        "supported_now": False,
        "sensor_absence_blocks_game": False,
        "fake_sensors_allowed": False,
    },
}

BUILD_ITEMS = [
    {
        "item_id": "home_suburb",
        "category": "housing",
        "title": {"ru": "Дом", "en": "Home", "es": "Casa"},
        "kind": "home",
        "income": 0,
        "expense": 500,
    },
    {
        "item_id": "job_factory",
        "category": "work",
        "title": {"ru": "Работа", "en": "Work", "es": "Trabajo"},
        "kind": "work",
        "income": 1800,
        "expense": 100,
    },
    {
        "item_id": "family",
        "category": "family_social",
        "title": {"ru": "Семья", "en": "Family", "es": "Familia"},
        "kind": "family",
        "income": 0,
        "expense": 300,
    },
    {
        "item_id": "project",
        "category": "project",
        "title": {"ru": "Проект", "en": "Project", "es": "Proyecto"},
        "kind": "project",
        "income": 0,
        "expense": 220,
    },
    {
        "item_id": "friends",
        "category": "family_social",
        "title": {"ru": "Друзья", "en": "Friends", "es": "Amistades"},
        "kind": "friends",
        "income": 0,
        "expense": 80,
    },
]


class LivingWorldStartInput(BaseModel):
    participant_id: str | None = None
    study_id: str | None = "health_model"
    source_session_id: str | None = None
    language: str = "ru"


class LivingWorldResultInput(BaseModel):
    game_session_id: str
    participant_id: str | None = None
    language: str = "ru"
    random_seed: int | None = None
    world_items: list[dict] = Field(default_factory=list)
    event_trace: list[dict] = Field(default_factory=list)
    economy: dict = Field(default_factory=dict)
    completed: bool = True
    abandoned: bool = False


def participant_game_card() -> dict:
    return dict(PARTICIPANT_GAME_CARD)


def _lang(value: str | None) -> str:
    if value in {"ru", "en", "es"}:
        return value
    return "ru"


def _known_item_ids() -> set[str]:
    return {item["item_id"] for item in BUILD_ITEMS}


def _screen_for_event(event_type: str) -> str:
    if event_type in {"world_item_created", "world_item_changed"}:
        return "world_builder"
    if event_type in {"simulation_started", "time_advanced", "economic_transaction", "natural_event_triggered"}:
        return "living_world"
    return "final_summary"


def _question_for_event(event_type: str) -> str | None:
    if event_type == "economic_transaction":
        return "economic_state_trace"
    if event_type in {"simulation_started", "time_advanced", "natural_event_triggered"}:
        return "living_world_timeline"
    if event_type == "world_item_created":
        return "world_initial_item_order"
    if event_type == "session_completed":
        return "final_retained_objects"
    return None


@router.get("/games/living-world", response_class=HTMLResponse)
def living_world_page():
    return Path("games/living_world/static/index.html").read_text(encoding="utf-8")


@router.get("/games/living-world/config")
def living_world_config():
    return {
        "ok": True,
        "game": participant_game_card(),
        "build_items": BUILD_ITEMS,
        "minimum_items": 3,
        "result_contract_version": RESULT_CONTRACT_VERSION,
        "simulation": {
            "simulation_version": "living_world_game_app_slice_v1",
            "months_in_slice": 3,
            "starting_balance": 1000,
            "natural_event_id": "home_repair",
        },
    }


@router.post("/games/living-world/sessions/start")
def living_world_start(payload: LivingWorldStartInput):
    try:
        session = start_game_session(
            game_id=GAME_ID,
            participant_id=payload.participant_id,
            study_id=payload.study_id,
            source_session_id=payload.source_session_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return {
        "ok": True,
        "session": session,
        "launch_contract": {
            "game_id": GAME_ID,
            "game_version": GAME_VERSION,
            "participant_launch_route": LAUNCH_ROUTE,
            "result_contract": RESULT_CONTRACT_VERSION,
            "language": _lang(payload.language),
        },
    }


@router.post("/games/living-world/results")
def living_world_result(payload: LivingWorldResultInput):
    known_items = _known_item_ids()
    for item in payload.world_items:
        item_id = item.get("item_id")
        if item_id not in known_items:
            raise HTTPException(status_code=400, detail=f"Unknown Living World item: {item_id}")

    accepted_events = []
    for index, event in enumerate(payload.event_trace, start=1):
        event_type = event.get("event_type")
        if event_type not in {
            "world_item_created",
            "world_item_changed",
            "simulation_started",
            "time_advanced",
            "economic_transaction",
            "natural_event_triggered",
        }:
            raise HTTPException(status_code=400, detail=f"Unsupported Living World event: {event_type}")

        metadata = {
            "stage_id": event.get("stage_id") or "living_world_slice",
            "language": _lang(payload.language),
            "random_seed": payload.random_seed,
            "world_item_ids": [item["item_id"] for item in payload.world_items],
            "active_item_ids": [item["item_id"] for item in payload.world_items if item.get("state") != "lost"],
            "simulation_tick": event.get("simulation_tick"),
            "simulation_period": event.get("simulation_period"),
            "season": event.get("season"),
            "economy": payload.economy,
            "event_trace_order": index,
        }
        if event.get("registry_event_id"):
            metadata["event_id"] = event["registry_event_id"]
        if event.get("item_id"):
            metadata["item_id"] = event["item_id"]

        try:
            accepted_events.append(
                append_game_event(
                    game_session_id=payload.game_session_id,
                    screen_id=_screen_for_event(event_type),
                    event_type=event_type,
                    object_id=event.get("item_id"),
                    question_id=_question_for_event(event_type),
                    answer=event.get("answer"),
                    value=event.get("value"),
                    decision_time_ms=event.get("decision_time_ms"),
                    metadata=metadata,
                )
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))

    try:
        accepted_events.append(
            append_game_event(
                game_session_id=payload.game_session_id,
                screen_id="final_summary",
                event_type="session_completed" if payload.completed else "session_abandoned",
                question_id="final_retained_objects" if payload.completed else None,
                answer=[item["item_id"] for item in payload.world_items],
                value={
                    "world_item_ids": [item["item_id"] for item in payload.world_items],
                    "selected_item_ids": [item["item_id"] for item in payload.world_items],
                    "economy": payload.economy,
                },
                metadata={
                    "stage_id": "finish",
                    "language": _lang(payload.language),
                    "random_seed": payload.random_seed,
                    "world_item_ids": [item["item_id"] for item in payload.world_items],
                    "active_item_ids": [item["item_id"] for item in payload.world_items],
                    "selected_item_ids": [item["item_id"] for item in payload.world_items],
                    "economy": payload.economy,
                    "result_contract": RESULT_CONTRACT_VERSION,
                },
            )
        )
        session = complete_game_session(
            payload.game_session_id,
            completed=payload.completed,
            abandoned=payload.abandoned,
            metadata={"result_contract": RESULT_CONTRACT_VERSION},
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return {
        "ok": True,
        "accepted_event_count": len(accepted_events),
        "session": session,
        "bounded_result": {
            "game_id": GAME_ID,
            "game_version": GAME_VERSION,
            "result_contract": RESULT_CONTRACT_VERSION,
            "game_session_id": payload.game_session_id,
            "participant_id": payload.participant_id,
            "language": _lang(payload.language),
            "world_item_ids": [item["item_id"] for item in payload.world_items],
            "economy": payload.economy,
        },
    }
