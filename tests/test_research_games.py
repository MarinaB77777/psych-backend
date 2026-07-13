from research.games import store
from research.games.registry import get_game
from games.living_world.app import living_world_result, living_world_start, participant_game_card
from games.living_world.app import LivingWorldResultInput, LivingWorldStartInput


def test_world_choice_registry_uses_stable_question_uuids():
    game = get_game("world_choice")

    assert game["game_version"] == "world_choice_v0_1"
    assert game["object_catalog_version"] == "world_choice_objects_v1"
    assert game["research_questions"]
    assert all(question["question_uuid"] for question in game["research_questions"])
    assert game["event_registry_version"] == "world_choice_events_v1"
    assert game["stage_config_version"] == "world_choice_stages_v1"
    assert len(game["event_registry"]) >= 7
    assert [stage["selection_limit"] for stage in game["stage_config"] if stage["phase"] == "narrowing"] == [3, 2, 1]
    assert game["sensor_extension_contracts"]["sensor_absence_blocks_game"] is False
    assert game["sensor_extension_contracts"]["fake_sensors_allowed"] is False
    assert game["simulation_version"] == "living_world_sim_v1"
    assert game["scenario_id"] == "living_world_vertical_slice"
    assert game["economic_rules_registry"]["version"] == "living_world_economy_v1"
    assert game["visual_state_model"]["version"] == "living_world_visual_state_v1"
    assert game["scenario_registry"]["ordered_phases"][:3] == [
        "build_world",
        "living_world",
        "natural_development_event",
    ]
    assert {"home_repair", "casino_opportunity", "local_economic_pressure"} <= {
        event["event_id"] for event in game["event_registry"]
    }
    assert {"natural", "temptation", "local_crisis", "global_crisis", "simulation"} <= {
        event["scope"] for event in game["event_registry"]
    }
    assert all(item["item_id"] == item["object_id"] for item in game["object_catalog"])
    assert all("economic_parameters" in item for item in game["object_catalog"])
    assert all("future_development_rules" in item for item in game["object_catalog"])


def test_game_events_preserve_provenance_and_no_interpretation(tmp_path):
    original_file = store.DATA_FILE
    store.DATA_FILE = tmp_path / "game_sessions.json"

    try:
        session = store.start_game_session(
            "world_choice",
            participant_id="p1",
            study_id="health_model",
            source_session_id="pilot-session-1",
        )

        event = store.append_game_event(
            game_session_id=session["game_session_id"],
            screen_id="world_builder",
            event_type="object_selected",
            object_id="job_factory",
            question_id="world_initial_work_choice",
            answer="job_factory",
            value={"object_id": "job_factory"},
            decision_time_ms=1200,
            confirmation_step="initial_choice",
        )

        completed = store.complete_game_session(session["game_session_id"])
        bundle = completed["prepared_signal_bundle"]

        assert event["game_id"] == "world_choice"
        assert event["game_version"] == "world_choice_v0_1"
        assert event["question_id"] == "world_initial_work_choice"
        assert event["question_uuid"]
        assert event["answer"] == "job_factory"
        assert event["value"] == {"object_id": "job_factory"}
        assert event["shared_timestamp_utc"]
        assert event["session_id"] == "pilot-session-1"
        assert bundle["interpretation"] is None
        assert bundle["question_answers"][0]["question_uuid"] == event["question_uuid"]
        assert "diagnosis" not in bundle
        assert "truth" not in bundle
    finally:
        store.DATA_FILE = original_file


def test_game_events_reject_diagnostic_authority_fields(tmp_path):
    original_file = store.DATA_FILE
    store.DATA_FILE = tmp_path / "game_sessions.json"

    try:
        session = store.start_game_session("world_choice")

        try:
            store.append_game_event(
                game_session_id=session["game_session_id"],
                screen_id="world_builder",
                event_type="object_selected",
                metadata={"diagnosis": "not allowed"},
            )
            assert False, "diagnostic metadata must be rejected"
        except ValueError as exc:
            assert "diagnostic authority" in str(exc)
    finally:
        store.DATA_FILE = original_file


def test_game_events_reject_unknown_screen_and_object(tmp_path):
    original_file = store.DATA_FILE
    store.DATA_FILE = tmp_path / "game_sessions.json"

    try:
        session = store.start_game_session("world_choice")

        try:
            store.append_game_event(
                game_session_id=session["game_session_id"],
                screen_id="invented_screen",
                event_type="object_selected",
                object_id="job_factory",
            )
            assert False, "unknown screens must be rejected"
        except ValueError as exc:
            assert "Unsupported game screen" in str(exc)

        try:
            store.append_game_event(
                game_session_id=session["game_session_id"],
                screen_id="world_builder",
                event_type="object_selected",
                object_id="invented_object",
            )
            assert False, "unknown objects must be rejected"
        except ValueError as exc:
            assert "Unknown game object" in str(exc)

        try:
            store.append_game_event(
                game_session_id=session["game_session_id"],
                screen_id="narrowing_3",
                event_type="narrowing_selection",
                metadata={
                    "event_id": "invented_event",
                    "available_item_ids": ["job_factory"],
                    "selected_item_ids": ["job_factory"],
                },
            )
            assert False, "unknown registry events must be rejected"
        except ValueError as exc:
            assert "Unknown game registry event" in str(exc)
    finally:
        store.DATA_FILE = original_file


def test_narrowing_stage_observation_is_bounded_and_traceable(tmp_path):
    original_file = store.DATA_FILE
    store.DATA_FILE = tmp_path / "game_sessions.json"

    try:
        session = store.start_game_session(
            "world_choice",
            participant_id="p2",
            source_session_id="session-2",
        )

        event = store.append_game_event(
            game_session_id=session["game_session_id"],
            screen_id="narrowing_3",
            event_type="stage_confirmed",
            question_id="retained_stage_3",
            answer=["job_factory", "home_suburb", "family"],
            value={
                "available_item_ids": [
                    "job_factory",
                    "home_suburb",
                    "family",
                    "nature",
                ],
                "selected_item_ids": ["job_factory", "home_suburb", "family"],
                "removed_item_ids": ["nature"],
            },
            decision_time_ms=3200,
            confirmation_step="retain_3_second_confirmation",
            cancel_count=1,
            metadata={
                "stage_id": "retain_3",
                "event_id": "economic_crisis",
                "event_version": "economic_crisis_v1",
                "available_item_ids": [
                    "job_factory",
                    "home_suburb",
                    "family",
                    "nature",
                ],
                "selected_item_ids": ["job_factory", "home_suburb", "family"],
                "removed_item_ids": ["nature"],
                "order": 1,
                "changes": 2,
            },
        )

        completed = store.complete_game_session(session["game_session_id"])
        bundle = completed["prepared_signal_bundle"]
        observation = bundle["bounded_observations"][0]

        assert event["question_uuid"]
        assert observation["game_id"] == "world_choice"
        assert observation["session_id"] == "session-2"
        assert observation["event_id"] == "economic_crisis"
        assert observation["event_version"] == "economic_crisis_v1"
        assert observation["stage_id"] == "retain_3"
        assert observation["available_item_ids"] == [
            "job_factory",
            "home_suburb",
            "family",
            "nature",
        ]
        assert observation["selected_item_ids"] == [
            "job_factory",
            "home_suburb",
            "family",
        ]
        assert observation["response_time_ms"] == 3200
        assert observation["cancellations"] == 1
        assert bundle["interpretation"] is None
        assert "diagnosis" not in bundle
    finally:
        store.DATA_FILE = original_file


def test_living_world_observation_keeps_simulation_and_loss_provenance(tmp_path):
    original_file = store.DATA_FILE
    store.DATA_FILE = tmp_path / "game_sessions.json"

    try:
        session = store.start_game_session(
            "world_choice",
            participant_id="p3",
            source_session_id="session-3",
        )

        store.append_game_event(
            game_session_id=session["game_session_id"],
            screen_id="narrowing_3",
            event_type="loss_visualized",
            object_id="car",
            question_id="loss_event_trace",
            value={
                "lost_item_id": "car",
                "world_item_ids": ["home_suburb", "job_factory"],
            },
            metadata={
                "simulation_version": "living_world_sim_v1",
                "scenario_id": "living_world_vertical_slice",
                "scenario_version": "living_world_vertical_slice_v1",
                "random_seed": 11,
                "language": "en",
                "simulation_tick": 5,
                "simulation_period": "2026-06",
                "season": "summer",
                "stage_id": "retain_3",
                "event_id": "economic_crisis",
                "lost_item_id": "car",
                "lost_item_ids": ["car"],
                "available_item_ids": ["home_suburb", "job_factory", "car"],
                "selected_item_ids": ["home_suburb", "job_factory"],
                "world_item_ids": ["home_suburb", "job_factory"],
                "explicitly_selected_for_preservation": False,
                "unavailable_due_to_previous_consequences": False,
                "visual_transition": "fade_out",
                "economy": {"balance": 1200, "debt": 500},
            },
        )

        completed = store.complete_game_session(session["game_session_id"])
        bundle = completed["prepared_signal_bundle"]
        observation = bundle["bounded_observations"][0]

        assert bundle["simulation_version"] == "living_world_sim_v1"
        assert bundle["scenario_id"] == "living_world_vertical_slice"
        assert observation["lost_item_id"] == "car"
        assert observation["visual_transition"] == "fade_out"
        assert observation["random_seed"] == 11
        assert observation["language"] == "en"
        assert observation["economy"] == {"balance": 1200, "debt": 500}
        assert observation["explicitly_selected_for_preservation"] is False
        assert bundle["interpretation"] is None
    finally:
        store.DATA_FILE = original_file


def test_living_world_app_contract_is_participant_launch_only():
    card = participant_game_card()

    assert card["game_id"] == "world_choice"
    assert card["participant_launch_route"] == "/games/living-world"
    assert card["result_contract"] == "living_world_result_v1"
    assert card["enabled"] is True
    assert card["sensor_capabilities"]["sensor_absence_blocks_game"] is False
    assert "question UUID mappings" not in str(card["title"])


def test_living_world_app_result_adapter_persists_bounded_result(tmp_path):
    original_file = store.DATA_FILE
    store.DATA_FILE = tmp_path / "game_sessions.json"

    try:
        started = living_world_start(
            LivingWorldStartInput(
                participant_id="p4",
                source_session_id="portal-session-1",
                language="en",
            )
        )
        session = started["session"]

        result = living_world_result(
            LivingWorldResultInput(
                game_session_id=session["game_session_id"],
                participant_id="p4",
                language="en",
                random_seed=5,
                world_items=[
                    {"item_id": "home_suburb", "category": "housing", "state": "changed"},
                    {"item_id": "job_factory", "category": "work", "state": "active"},
                    {"item_id": "family", "category": "family_social", "state": "active"},
                ],
                economy={"balance": 2400, "income": 1800, "expenses": 900},
                event_trace=[
                    {
                        "event_type": "world_item_created",
                        "stage_id": "build",
                        "item_id": "home_suburb",
                        "answer": "home_suburb",
                        "value": {"item_id": "home_suburb"},
                    },
                    {
                        "event_type": "time_advanced",
                        "stage_id": "live",
                        "simulation_tick": 2,
                        "simulation_period": "2",
                        "season": "spring",
                        "value": {"new_balance": 2400},
                    },
                    {
                        "event_type": "natural_event_triggered",
                        "stage_id": "live",
                        "registry_event_id": "home_repair",
                        "item_id": "home_suburb",
                        "value": {"changed_item_id": "home_suburb"},
                    },
                ],
            )
        )

        completed = store.get_game_session(session["game_session_id"])
        bundle = completed["prepared_signal_bundle"]

        assert result["ok"] is True
        assert result["bounded_result"]["result_contract"] == "living_world_result_v1"
        assert completed["completed"] is True
        assert completed["session_id"] == "portal-session-1"
        assert bundle["interpretation"] is None
        assert any(
            event["event_type"] == "natural_event_triggered"
            for event in completed["events"]
        )
        assert any(
            observation.get("event_id") == "home_repair"
            for observation in bundle["bounded_observations"]
        )
    finally:
        store.DATA_FILE = original_file


def test_game_store_does_not_silently_continue_after_corruption(tmp_path):
    original_file = store.DATA_FILE
    store.DATA_FILE = tmp_path / "game_sessions.json"
    store.DATA_FILE.write_text("{not valid json", encoding="utf-8")

    try:
        try:
            store.start_game_session("world_choice")
            assert False, "corrupt storage must fail explicitly"
        except ValueError:
            pass
    finally:
        store.DATA_FILE = original_file
