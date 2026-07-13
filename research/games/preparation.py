from __future__ import annotations

from collections import defaultdict

from .registry import get_event, get_game, get_object


def build_game_signal_bundle(session: dict) -> dict:
    game = get_game(session["game_id"])
    if not game:
        raise ValueError("Unknown game")

    events = session.get("events", [])
    world_initial_choices = {}
    crisis_events = defaultdict(lambda: {"removed_order": [], "kept": []})
    question_answers = []
    total_decision_time_ms = 0
    selection_changes_total = 0
    confirmation_cancel_total = 0
    bounded_observations = []
    event_trace = []

    for event in events:
        decision_time_ms = event.get("decision_time_ms")
        if isinstance(decision_time_ms, int) and decision_time_ms > 0:
            total_decision_time_ms += decision_time_ms

        confirmation_cancel_total += int(event.get("cancel_count") or 0)

        if event.get("event_type") == "selection_changed":
            selection_changes_total += 1

        object_id = event.get("object_id")
        obj = get_object(session["game_id"], object_id)

        if event.get("screen_id") == "world_builder" and event.get("event_type") in {
            "object_selected",
            "choice_confirmed",
        } and obj:
            world_initial_choices[obj["category"]] = object_id

        if str(event.get("screen_id", "")).startswith("crisis"):
            crisis_id = event.get("screen_id")
            if event.get("event_type") == "object_removed" and object_id:
                crisis_events[crisis_id]["removed_order"].append(object_id)
            kept = event.get("metadata", {}).get("kept")
            if isinstance(kept, list):
                crisis_events[crisis_id]["kept"] = kept

        if event.get("question_id") or event.get("question_uuid"):
            question_answers.append({
                "question_id": event.get("question_id"),
                "question_uuid": event.get("question_uuid"),
                "answer": event.get("answer"),
                "value": event.get("value"),
                "timestamp": event.get("shared_timestamp_utc"),
                "screen_id": event.get("screen_id"),
                "event_type": event.get("event_type"),
                "object_id": object_id,
            })

        metadata = event.get("metadata", {}) or {}
        registry_event = get_event(session["game_id"], metadata.get("event_id"))
        event_version = metadata.get("event_version")
        if not event_version and registry_event:
            event_version = registry_event.get("event_version")
        bounded_observations.append({
            "event_trace_id": event.get("event_id"),
            "game_id": event.get("game_id"),
            "game_version": event.get("game_version"),
            "simulation_version": game.get("simulation_version"),
            "scenario_id": game.get("scenario_id"),
            "scenario_version": game.get("scenario_version"),
            "session_id": event.get("session_id"),
            "game_session_id": event.get("game_session_id"),
            "participant_id": session.get("participant_id"),
            "event_id": metadata.get("event_id"),
            "event_version": event_version,
            "event_scope": registry_event.get("scope") if registry_event else None,
            "event_category": registry_event.get("category") if registry_event else None,
            "stage_id": metadata.get("stage_id"),
            "available_item_ids": metadata.get("available_item_ids"),
            "selected_item_ids": metadata.get("selected_item_ids"),
            "removed_item_ids": metadata.get("removed_item_ids"),
            "world_item_ids": metadata.get("world_item_ids"),
            "active_item_ids": metadata.get("active_item_ids"),
            "lost_item_id": metadata.get("lost_item_id"),
            "lost_item_ids": metadata.get("lost_item_ids"),
            "explicitly_selected_for_preservation": metadata.get("explicitly_selected_for_preservation"),
            "unavailable_due_to_previous_consequences": metadata.get("unavailable_due_to_previous_consequences"),
            "visual_transition": metadata.get("visual_transition"),
            "order": metadata.get("order"),
            "response_time_ms": event.get("decision_time_ms") or metadata.get("response_time_ms"),
            "changes": metadata.get("changes"),
            "cancellations": event.get("cancel_count"),
            "confirmation_step": event.get("confirmation_step"),
            "random_seed": metadata.get("random_seed"),
            "language": metadata.get("language"),
            "simulation_tick": metadata.get("simulation_tick"),
            "simulation_period": metadata.get("simulation_period"),
            "season": metadata.get("season"),
            "economic_event": metadata.get("economic_event"),
            "economy": metadata.get("economy"),
            "casino": metadata.get("casino"),
            "event_trace": metadata.get("event_trace"),
            "question_id": event.get("question_id"),
            "question_uuid": event.get("question_uuid"),
            "timestamp": event.get("shared_timestamp_utc"),
        })

        event_trace.append({
            "event_trace_id": event.get("event_id"),
            "timestamp": event.get("shared_timestamp_utc"),
            "screen_id": event.get("screen_id"),
            "event_type": event.get("event_type"),
            "object_id": object_id,
            "question_id": event.get("question_id"),
            "question_uuid": event.get("question_uuid"),
            "stage_id": metadata.get("stage_id"),
            "registry_event_id": metadata.get("event_id"),
            "registry_event_version": event_version,
            "simulation_tick": metadata.get("simulation_tick"),
            "economy": metadata.get("economy"),
        })

    crisis_sequence = [
        {"crisis_id": crisis_id, **details}
        for crisis_id, details in sorted(crisis_events.items())
    ]

    return {
        "source_type": "game",
        "source_name": game["source_name"],
        "game_id": session["game_id"],
        "game_version": session["game_version"],
        "object_catalog_version": session["object_catalog_version"],
        "simulation_version": game.get("simulation_version"),
        "scenario_id": game.get("scenario_id"),
        "scenario_version": game.get("scenario_version"),
        "economic_rules_version": game.get("economic_rules_version"),
        "visual_state_version": game.get("visual_state_version"),
        "game_session_id": session["game_session_id"],
        "session_id": session["session_id"],
        "participant_id": session.get("participant_id"),
        "study_id": session.get("study_id"),
        "shared_time_reference": True,
        "completed": session.get("completed", False),
        "abandoned": session.get("abandoned", False),
        "tutorial_excluded_from_analysis": any(
            event.get("screen_id") == "tutorial_flowers" and event.get("excluded_from_analysis")
            for event in events
        ),
        "raw_event_count": len(events),
        "question_answers": question_answers,
        "bounded_observations": bounded_observations,
        "event_trace": event_trace,
        "world_initial_choices": world_initial_choices,
        "crisis_sequence": crisis_sequence,
        "metrics": {
            "total_decision_time_ms": total_decision_time_ms,
            "selection_changes_total": selection_changes_total,
            "confirmation_cancel_total": confirmation_cancel_total,
        },
        "interpretation": None,
        "boundaries": game["boundaries"],
    }
