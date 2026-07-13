from __future__ import annotations

from copy import deepcopy
from uuid import NAMESPACE_URL, uuid5


def _question_uuid(game_id: str, question_id: str) -> str:
    return str(uuid5(NAMESPACE_URL, f"ray-research-game:{game_id}:question:{question_id}"))


GAME_ID = "world_choice"
GAME_VERSION = "world_choice_v0_1"
OBJECT_CATALOG_VERSION = "world_choice_objects_v1"
EVENT_REGISTRY_VERSION = "world_choice_events_v1"
STAGE_CONFIG_VERSION = "world_choice_stages_v1"
SIMULATION_VERSION = "living_world_sim_v1"
SCENARIO_ID = "living_world_vertical_slice"
SCENARIO_VERSION = "living_world_vertical_slice_v1"
ECONOMIC_RULES_VERSION = "living_world_economy_v1"
VISUAL_STATE_VERSION = "living_world_visual_state_v1"


_RESEARCH_QUESTIONS = [
    {
        "question_id": "world_initial_work_choice",
        "question_uuid": _question_uuid(GAME_ID, "world_initial_work_choice"),
        "answer_value_type": "object_id",
        "required": False,
        "prompt": {
            "ru": "Какой рабочий объект был создан в мире?",
            "en": "Which work object was created in the world?",
            "es": "Que objeto de trabajo se creo en el mundo?",
        },
    },
    {
        "question_id": "world_initial_housing_choice",
        "question_uuid": _question_uuid(GAME_ID, "world_initial_housing_choice"),
        "answer_value_type": "object_id",
        "required": False,
        "prompt": {
            "ru": "Какой объект жилья был создан в мире?",
            "en": "Which housing object was created in the world?",
            "es": "Que objeto de vivienda se creo en el mundo?",
        },
    },
    {
        "question_id": "world_initial_item_order",
        "question_uuid": _question_uuid(GAME_ID, "world_initial_item_order"),
        "answer_value_type": "ordered_object_ids",
        "required": True,
        "prompt": {
            "ru": "В каком порядке элементы были добавлены при построении мира?",
            "en": "In which order were items added while building the world?",
            "es": "En que orden se agregaron los elementos al construir el mundo?",
        },
    },
    {
        "question_id": "living_world_timeline",
        "question_uuid": _question_uuid(GAME_ID, "living_world_timeline"),
        "answer_value_type": "event_trace",
        "required": True,
        "prompt": {
            "ru": "Какая последовательность событий произошла в живом мире?",
            "en": "Which sequence of events occurred in the living world?",
            "es": "Que secuencia de eventos ocurrio en el mundo vivo?",
        },
    },
    {
        "question_id": "economic_state_trace",
        "question_uuid": _question_uuid(GAME_ID, "economic_state_trace"),
        "answer_value_type": "economic_trace",
        "required": True,
        "prompt": {
            "ru": "Как менялось ограниченное экономическое состояние мира?",
            "en": "How did the bounded economic state of the world change?",
            "es": "Como cambio el estado economico acotado del mundo?",
        },
    },
    {
        "question_id": "casino_behavior_trace",
        "question_uuid": _question_uuid(GAME_ID, "casino_behavior_trace"),
        "answer_value_type": "casino_trace",
        "required": False,
        "prompt": {
            "ru": "Как участник взаимодействовал с подсистемой казино?",
            "en": "How did the participant interact with the casino subsystem?",
            "es": "Como interactuo la persona con el subsistema de casino?",
        },
    },
    {
        "question_id": "local_crisis_response",
        "question_uuid": _question_uuid(GAME_ID, "local_crisis_response"),
        "answer_value_type": "bounded_event_response",
        "required": True,
        "prompt": {
            "ru": "Как локальный кризис изменил созданный мир?",
            "en": "How did the local crisis change the created world?",
            "es": "Como cambio el mundo creado la crisis local?",
        },
    },
    {
        "question_id": "crisis_event_presented",
        "question_uuid": _question_uuid(GAME_ID, "crisis_event_presented"),
        "answer_value_type": "event_id",
        "required": True,
        "prompt": {
            "ru": "Какое глобальное кризисное событие было предъявлено?",
            "en": "Which global crisis event was presented?",
            "es": "Que evento de crisis global se presento?",
        },
    },
    {
        "question_id": "loss_event_trace",
        "question_uuid": _question_uuid(GAME_ID, "loss_event_trace"),
        "answer_value_type": "loss_trace",
        "required": True,
        "prompt": {
            "ru": "Какие игровые элементы исчезали при сужении мира?",
            "en": "Which game items disappeared while the world narrowed?",
            "es": "Que elementos del juego desaparecieron al reducirse el mundo?",
        },
    },
    {
        "question_id": "retained_stage_3",
        "question_uuid": _question_uuid(GAME_ID, "retained_stage_3"),
        "answer_value_type": "object_id_list",
        "required": True,
        "prompt": {
            "ru": "Какие три элемента были сохранены на первой стадии сужения?",
            "en": "Which three items were retained at the first narrowing stage?",
            "es": "Que tres elementos se conservaron en la primera etapa de reduccion?",
        },
    },
    {
        "question_id": "retained_stage_2",
        "question_uuid": _question_uuid(GAME_ID, "retained_stage_2"),
        "answer_value_type": "object_id_list",
        "required": True,
        "prompt": {
            "ru": "Какие два элемента были сохранены на второй стадии сужения?",
            "en": "Which two items were retained at the second narrowing stage?",
            "es": "Que dos elementos se conservaron en la segunda etapa de reduccion?",
        },
    },
    {
        "question_id": "retained_stage_1",
        "question_uuid": _question_uuid(GAME_ID, "retained_stage_1"),
        "answer_value_type": "object_id_list",
        "required": True,
        "prompt": {
            "ru": "Какой один элемент был сохранен в финале?",
            "en": "Which one item was retained at the end?",
            "es": "Que unico elemento se conservo al final?",
        },
    },
    {
        "question_id": "final_retained_objects",
        "question_uuid": _question_uuid(GAME_ID, "final_retained_objects"),
        "answer_value_type": "object_id_list",
        "required": True,
        "prompt": {
            "ru": "Какие объекты остались в финале?",
            "en": "Which objects remained at the end?",
            "es": "Que objetos quedaron al final?",
        },
    },
]


def _item(
    object_id: str,
    category: str,
    label: dict,
    visual: str,
    *,
    state: str = "active",
    ownership_relation: str = "chosen",
    dependencies: list[str] | None = None,
    economic_parameters: dict | None = None,
    future_development_rules: list[str] | None = None,
    attributes: dict | None = None,
) -> dict:
    return {
        "object_id": object_id,
        "item_id": object_id,
        "type": category,
        "category": category,
        "label": label,
        "title": label,
        "visual": visual,
        "state": state,
        "ownership_relation": ownership_relation,
        "dependencies": dependencies or [],
        "economic_parameters": economic_parameters or {},
        "future_development_rules": future_development_rules or [],
        "attributes": attributes or {},
    }


_OBJECT_CATALOG = [
    _item("home_suburb", "housing", {"ru": "Дом", "en": "Home", "es": "Casa"}, "home", economic_parameters={"monthly_expense": 900, "asset_value": 90000}, future_development_rules=["repair_events", "seasonal_visual_state"]),
    _item("place_city", "place", {"ru": "Городской район", "en": "City place", "es": "Barrio urbano"}, "city", economic_parameters={"monthly_expense": 120}, future_development_rules=["local_infrastructure_events"]),
    _item("job_factory", "work", {"ru": "Работа на заводе", "en": "Factory job", "es": "Trabajo en fabrica"}, "factory", economic_parameters={"monthly_income": 4200, "monthly_expense": 120}, future_development_rules=["promotion", "job_loss"]),
    _item("education", "education", {"ru": "Обучение", "en": "Education", "es": "Educacion"}, "education", economic_parameters={"monthly_expense": 450}, future_development_rules=["skill_growth"]),
    _item("partner", "family_social", {"ru": "Партнёр", "en": "Partner", "es": "Pareja"}, "partner", ownership_relation="relationship", economic_parameters={"monthly_income": 1800, "monthly_expense": 380}, future_development_rules=["relationship_change"]),
    _item("child", "family_social", {"ru": "Ребёнок", "en": "Child", "es": "Hijo"}, "child", ownership_relation="care", dependencies=["home_suburb"], economic_parameters={"monthly_expense": 620}, future_development_rules=["age_growth"]),
    _item("pet", "family_social", {"ru": "Питомец", "en": "Pet", "es": "Mascota"}, "pet", ownership_relation="care", economic_parameters={"monthly_expense": 110}, future_development_rules=["care_events"]),
    _item("friends", "family_social", {"ru": "Друзья", "en": "Friends", "es": "Amistades"}, "friends", ownership_relation="relationship", economic_parameters={"monthly_expense": 90}, future_development_rules=["support_events"]),
    _item("project", "project", {"ru": "Проект", "en": "Project", "es": "Proyecto"}, "project", economic_parameters={"monthly_expense": 350, "asset_value": 1200}, future_development_rules=["growth_or_delay"]),
    _item("business", "business", {"ru": "Бизнес", "en": "Business", "es": "Negocio"}, "business", economic_parameters={"monthly_income": 1600, "monthly_expense": 700, "asset_value": 15000}, future_development_rules=["business_growth", "business_drop"]),
    _item("laboratory", "project", {"ru": "Лаборатория", "en": "Laboratory", "es": "Laboratorio"}, "lab", economic_parameters={"monthly_expense": 850, "asset_value": 8000}, future_development_rules=["research_opportunity"]),
    _item("car", "transport", {"ru": "Автомобиль", "en": "Car", "es": "Auto"}, "car", economic_parameters={"monthly_expense": 420, "asset_value": 12000}, future_development_rules=["repair_events"]),
    _item("transport", "transport", {"ru": "Транспорт", "en": "Transport", "es": "Transporte"}, "transport", economic_parameters={"monthly_expense": 260, "asset_value": 5000}, future_development_rules=["route_change", "repair_events"]),
    _item("emergency_savings", "resource", {"ru": "Накопления", "en": "Savings", "es": "Ahorros"}, "savings", economic_parameters={"initial_balance": 6000, "asset_value": 6000}, future_development_rules=["buffer_use"]),
    _item("family", "family_social", {"ru": "Семья", "en": "Family", "es": "Familia"}, "family", ownership_relation="relationship", economic_parameters={"monthly_expense": 480}, future_development_rules=["support_events", "obligation_change"]),
    _item("nature", "recreation", {"ru": "Природа", "en": "Nature", "es": "Naturaleza"}, "nature", economic_parameters={"monthly_expense": 60}, future_development_rules=["recovery_events", "seasonal_visual_state"]),
    _item("hobby", "recreation", {"ru": "Хобби", "en": "Hobby", "es": "Pasatiempo"}, "hobby", economic_parameters={"monthly_expense": 180}, future_development_rules=["recovery_events"]),
    _item("health_activity", "recreation", {"ru": "Здоровье и активность", "en": "Health activity", "es": "Actividad de salud"}, "health", economic_parameters={"monthly_expense": 210}, future_development_rules=["routine_change"]),
    _item("local_infrastructure", "place", {"ru": "Инфраструктура", "en": "Infrastructure", "es": "Infraestructura"}, "infrastructure", economic_parameters={"monthly_expense": 80, "asset_value": 2000}, future_development_rules=["breakdown_events"]),
    _item("care_role", "family_social", {"ru": "Забота о близком", "en": "Care role", "es": "Rol de cuidado"}, "care", ownership_relation="care", economic_parameters={"monthly_expense": 300}, future_development_rules=["obligation_change"]),
    _item("job_restaurant", "work", {"ru": "Работа в ресторане", "en": "Restaurant job", "es": "Trabajo en restaurante"}, "restaurant", economic_parameters={"monthly_income": 3200, "monthly_expense": 90}, future_development_rules=["shift_change", "job_loss"]),
    _item("home_shared", "housing", {"ru": "Общее жильё", "en": "Shared home", "es": "Vivienda compartida"}, "shared_home", economic_parameters={"monthly_expense": 520, "asset_value": 12000}, future_development_rules=["roommate_change", "repair_events"]),
    _item("social_ties", "family_social", {"ru": "Социальные связи", "en": "Social ties", "es": "Vinculos sociales"}, "social", ownership_relation="community", economic_parameters={"monthly_expense": 130}, future_development_rules=["support_events"]),
]


_ECONOMIC_RULES_REGISTRY = {
    "version": ECONOMIC_RULES_VERSION,
    "currency": "bounded_game_units",
    "starting_balance": 3000,
    "credit_limit": 5000,
    "loan_interest_monthly": 0.03,
    "monthly_tick_rule": "sum selected item monthly_income minus monthly_expense",
    "transaction_fields": [
        "event_id",
        "reason",
        "amount",
        "previous_balance",
        "new_balance",
        "timestamp",
        "source",
    ],
    "casino": {
        "min_stake": 100,
        "max_stake": 800,
        "deterministic_outcomes": ["lose", "win", "lose"],
        "win_multiplier": 2,
    },
}


_VISUAL_STATE_MODEL = {
    "version": VISUAL_STATE_VERSION,
    "states": ["active", "changed", "damaged", "unavailable", "lost", "preserved"],
    "loss_transitions": ["fade_out", "dim_and_leave", "collapse_to_shadow"],
}


_SIMULATION_CLOCK = {
    "version": SIMULATION_VERSION,
    "start_period": "2026-01",
    "tick_unit": "month",
    "vertical_slice_ticks": 6,
    "seasons": ["winter", "spring", "summer", "autumn"],
}


def _event(
    event_id: str,
    event_version: str,
    scope: str,
    category: str,
    title: dict,
    description: dict,
    *,
    prerequisites: dict | None = None,
    trigger_rules: dict | None = None,
    probability: float | None = None,
    consequences: dict | None = None,
    affected_categories: list[str] | None = None,
) -> dict:
    return {
        "event_id": event_id,
        "event_version": event_version,
        "scope": scope,
        "category": category,
        "title": title,
        "description": description,
        "prerequisites": prerequisites or {},
        "trigger_rules": trigger_rules or {},
        "probability": probability,
        "consequences": consequences or {},
        "affected_categories": affected_categories or [],
    }


_EVENT_REGISTRY = [
    _event("monthly_income", "monthly_income_v1", "simulation", "economy", {"ru": "Доход за месяц", "en": "Monthly income", "es": "Ingreso mensual"}, {"ru": "Мир получил доход от активных объектов.", "en": "The world received income from active items.", "es": "El mundo recibio ingresos de objetos activos."}, trigger_rules={"tick": "monthly"}, consequences={"balance_delta": "sum_income"}),
    _event("monthly_expenses", "monthly_expenses_v1", "simulation", "economy", {"ru": "Расходы за месяц", "en": "Monthly expenses", "es": "Gastos mensuales"}, {"ru": "Мир оплатил регулярные расходы.", "en": "The world paid regular expenses.", "es": "El mundo pago gastos regulares."}, trigger_rules={"tick": "monthly"}, consequences={"balance_delta": "minus_sum_expenses"}),
    _event("home_repair", "home_repair_v1", "natural", "development", {"ru": "Ремонт дома", "en": "Home repair", "es": "Reparacion de casa"}, {"ru": "Дом требует спокойного ремонта. Это меняет расходы и состояние объекта.", "en": "The home needs a calm repair. It changes expenses and item state.", "es": "La casa necesita una reparacion tranquila. Cambia gastos y estado."}, prerequisites={"requires_any_item": ["home_suburb"]}, trigger_rules={"deterministic_tick": 3}, probability=0.35, consequences={"balance_delta": -700, "item_state": {"home_suburb": "changed"}}, affected_categories=["housing"]),
    _event("casino_opportunity", "casino_opportunity_v1", "temptation", "casino", {"ru": "Казино у дороги", "en": "Roadside casino", "es": "Casino junto al camino"}, {"ru": "Казино видно в мире. Можно пройти мимо, зайти, сыграть, остановиться или выйти.", "en": "A casino is visible in the world. You may pass, enter, play, stop or leave.", "es": "Un casino es visible en el mundo. Puedes pasar, entrar, jugar, detenerte o salir."}, trigger_rules={"appears_after_tick": 3}, consequences={"subsystem": "casino"}),
    _event("casino_bet_round", "casino_bet_round_v1", "temptation", "casino", {"ru": "Раунд казино", "en": "Casino round", "es": "Ronda de casino"}, {"ru": "Один ограниченный раунд с явной ставкой.", "en": "One bounded round with an explicit stake.", "es": "Una ronda acotada con apuesta explicita."}, trigger_rules={"requires_player_entry": True}, consequences={"balance_delta": "stake_outcome"}),
    _event("local_economic_pressure", "local_economic_pressure_v1", "local_crisis", "economy", {"ru": "Локальное финансовое давление", "en": "Local financial pressure", "es": "Presion financiera local"}, {"ru": "Расходы растут, один объект временно меняет состояние, но мир не уничтожается.", "en": "Expenses rise and one item changes state, but the world is not destroyed.", "es": "Aumentan los gastos y un objeto cambia de estado, pero el mundo no se destruye."}, trigger_rules={"after_living_ticks": 5}, probability=1.0, consequences={"balance_delta": -900, "item_state": "damaged"}, affected_categories=["work", "housing", "business", "transport"]),
    _event("natural_disaster", "natural_disaster_v1", "global_crisis", "global", {"ru": "Природная катастрофа", "en": "Natural disaster", "es": "Desastre natural"}, {"ru": "Часть привычного мира становится недоступной. Нужно выбрать, что сохранить.", "en": "Part of the familiar world becomes unavailable. Choose what to retain.", "es": "Parte del mundo habitual deja de estar disponible. Elige que conservar."}, affected_categories=["housing", "place", "transport", "recreation"]),
    _event("economic_crisis", "economic_crisis_v1", "global_crisis", "global", {"ru": "Экономический кризис", "en": "Economic crisis", "es": "Crisis economica"}, {"ru": "Ресурсов становится меньше, а цена решений выше.", "en": "Resources become scarcer and choices carry higher cost.", "es": "Los recursos disminuyen y las decisiones tienen mayor costo."}, affected_categories=["work", "resource", "housing", "education"]),
    _event("forced_relocation", "forced_relocation_v1", "global_crisis", "global", {"ru": "Вынужденный переезд", "en": "Forced relocation", "es": "Traslado forzado"}, {"ru": "Нужно перенести только часть мира в новое место.", "en": "Only part of the world can move to a new place.", "es": "Solo una parte del mundo puede trasladarse a un lugar nuevo."}, affected_categories=["housing", "transport", "family_social", "work"]),
    _event("infrastructure_breakdown", "infrastructure_breakdown_v1", "global_crisis", "global", {"ru": "Разрушение инфраструктуры", "en": "Infrastructure breakdown", "es": "Fallo de infraestructura"}, {"ru": "Связи, доступ и привычные маршруты нарушены.", "en": "Connections, access and familiar routes are disrupted.", "es": "Se alteran las conexiones, el acceso y las rutas habituales."}, affected_categories=["place", "transport", "work"]),
    _event("resource_loss", "resource_loss_v1", "global_crisis", "global", {"ru": "Потеря ресурсов", "en": "Resource loss", "es": "Perdida de recursos"}, {"ru": "Часть ресурсов больше нельзя использовать.", "en": "Some resources can no longer be used.", "es": "Algunos recursos ya no se pueden usar."}, affected_categories=["resource", "education", "recreation"]),
    _event("obligation_conflict", "obligation_conflict_v1", "global_crisis", "global", {"ru": "Конфликт обязательств", "en": "Conflict of obligations", "es": "Conflicto de obligaciones"}, {"ru": "Несколько важных обязательств одновременно требуют выбора.", "en": "Several important obligations demand a choice at the same time.", "es": "Varias obligaciones importantes exigen una eleccion al mismo tiempo."}, affected_categories=["family_social", "work", "project"]),
    _event("limited_rescue_resource", "limited_rescue_resource_v1", "global_crisis", "global", {"ru": "Ограниченный спасательный ресурс", "en": "Limited rescue resource", "es": "Recurso de rescate limitado"}, {"ru": "Есть ресурс, который может сохранить только часть мира.", "en": "A resource can protect only part of the world.", "es": "Un recurso puede proteger solo una parte del mundo."}, affected_categories=["resource", "family_social", "housing"]),
]


_STAGE_CONFIG = [
    {"stage_id": "build_world", "screen_id": "world_builder", "phase": "build", "minimum_items": 4, "requires_explicit_completion": True},
    {"stage_id": "living_world", "screen_id": "living_world", "phase": "simulation", "ticks": 6, "requires_explicit_completion": True},
    {"stage_id": "casino", "screen_id": "casino", "phase": "temptation", "requires_explicit_exit": True},
    {"stage_id": "local_crisis", "screen_id": "local_crisis", "phase": "local_crisis", "requires_explicit_completion": True},
    {"stage_id": "global_crisis", "screen_id": "global_crisis", "phase": "global_crisis", "requires_explicit_completion": True},
    {"stage_id": "retain_3", "screen_id": "narrowing_3", "phase": "narrowing", "selection_limit": 3, "requires_double_confirmation": True, "question_id": "retained_stage_3"},
    {"stage_id": "retain_2", "screen_id": "narrowing_2", "phase": "narrowing", "selection_limit": 2, "requires_double_confirmation": True, "question_id": "retained_stage_2"},
    {"stage_id": "retain_1", "screen_id": "narrowing_1", "phase": "narrowing", "selection_limit": 1, "requires_double_confirmation": True, "question_id": "retained_stage_1"},
]


_CHARACTER_REGISTRY = {
    "version": "living_world_characters_v1",
    "characters": [
        {"character_id": "participant_avatar", "role": "player_proxy", "visible": True},
        {"character_id": "partner_character", "linked_item_id": "partner", "role": "relationship"},
        {"character_id": "child_character", "linked_item_id": "child", "role": "care"},
    ],
}


_SCENARIO_REGISTRY = {
    "scenario_id": SCENARIO_ID,
    "scenario_version": SCENARIO_VERSION,
    "ordered_phases": [
        "build_world",
        "living_world",
        "natural_development_event",
        "casino_opportunity",
        "local_crisis",
        "global_crisis",
        "retain_3",
        "retain_2",
        "retain_1",
        "final",
    ],
}


_SENSOR_EXTENSION_CONTRACTS = {
    "supported_now": False,
    "sensor_absence_blocks_game": False,
    "fake_sensors_allowed": False,
    "future_event_fields": ["sensor_source_id", "sensor_timestamp_utc", "sensor_quality_flag"],
}


_GAMES = [
    {
        "game_id": GAME_ID,
        "game_version": GAME_VERSION,
        "title": {"ru": "Живой мир", "en": "Living World", "es": "Mundo vivo"},
        "source_type": "game",
        "source_name": "world_choice_game",
        "object_catalog_version": OBJECT_CATALOG_VERSION,
        "event_registry_version": EVENT_REGISTRY_VERSION,
        "stage_config_version": STAGE_CONFIG_VERSION,
        "simulation_version": SIMULATION_VERSION,
        "scenario_id": SCENARIO_ID,
        "scenario_version": SCENARIO_VERSION,
        "economic_rules_version": ECONOMIC_RULES_VERSION,
        "visual_state_version": VISUAL_STATE_VERSION,
        "allowed_event_types": [
            "tutorial_seen",
            "object_selected",
            "selection_changed",
            "object_removed",
            "world_item_created",
            "world_item_changed",
            "world_item_removed",
            "choice_confirmed",
            "simulation_started",
            "time_advanced",
            "economic_transaction",
            "natural_event_triggered",
            "temptation_presented",
            "casino_entered",
            "casino_declined",
            "casino_bet",
            "casino_stopped",
            "debt_taken",
            "local_crisis_started",
            "global_crisis_started",
            "crisis_started",
            "narrowing_selection",
            "stage_confirmed",
            "loss_visualized",
            "session_completed",
            "session_abandoned",
            "game_exited",
        ],
        "screens": [
            "tutorial_flowers",
            "world_builder",
            "world_confirmation",
            "living_world",
            "casino",
            "local_crisis",
            "global_crisis",
            "crisis_intro",
            "crisis_1",
            "crisis_2",
            "crisis_3",
            "narrowing_3",
            "narrowing_2",
            "narrowing_1",
            "final_summary",
        ],
        "research_questions": _RESEARCH_QUESTIONS,
        "object_catalog": _OBJECT_CATALOG,
        "world_item_registry": {"version": OBJECT_CATALOG_VERSION, "items": _OBJECT_CATALOG},
        "character_registry": _CHARACTER_REGISTRY,
        "event_registry": _EVENT_REGISTRY,
        "economic_rules_registry": _ECONOMIC_RULES_REGISTRY,
        "crisis_registry": {
            "version": "living_world_crises_v1",
            "local_event_ids": ["local_economic_pressure"],
            "global_event_ids": [
                "natural_disaster",
                "economic_crisis",
                "forced_relocation",
                "infrastructure_breakdown",
                "resource_loss",
                "obligation_conflict",
                "limited_rescue_resource",
            ],
        },
        "scenario_registry": _SCENARIO_REGISTRY,
        "stage_config": _STAGE_CONFIG,
        "visual_state_model": _VISUAL_STATE_MODEL,
        "simulation_clock": _SIMULATION_CLOCK,
        "randomization": {"test_mode": "deterministic_seed", "production_mode": "controlled_random"},
        "sensor_extension_contracts": _SENSOR_EXTENSION_CONTRACTS,
        "boundaries": [
            "game_output_not_participant_truth",
            "built_world_not_real_biography",
            "job_item_not_profession",
            "selected_item_not_identity",
            "saved_item_not_permanent_priority",
            "crisis_choice_not_ordinary_life_priority",
            "casino_or_debt_not_diagnosis_or_irresponsibility",
            "one_game_not_stable_value_structure",
            "game_does_not_interpret_answers",
            "no_diagnosis",
            "no_automatic_health_model_projection_runtime_governance_or_learning_profile_update",
        ],
    }
]


def list_games() -> list[dict]:
    return deepcopy(_GAMES)


def get_game(game_id: str) -> dict | None:
    for game in _GAMES:
        if game["game_id"] == game_id:
            return deepcopy(game)
    return None


def get_question(game_id: str, question_id: str | None = None, question_uuid: str | None = None) -> dict | None:
    game = get_game(game_id)
    if not game:
        return None
    for question in game["research_questions"]:
        if question_id and question["question_id"] == question_id:
            return question
        if question_uuid and question["question_uuid"] == question_uuid:
            return question
    return None


def get_object(game_id: str, object_id: str | None) -> dict | None:
    if not object_id:
        return None
    game = get_game(game_id)
    if not game:
        return None
    for item in game["object_catalog"]:
        if item["object_id"] == object_id or item.get("item_id") == object_id:
            return item
    return None


def get_event(game_id: str, event_id: str | None) -> dict | None:
    if not event_id:
        return None
    game = get_game(game_id)
    if not game:
        return None
    for item in game["event_registry"]:
        if item["event_id"] == event_id:
            return item
    return None


def is_allowed_screen(game_id: str, screen_id: str) -> bool:
    game = get_game(game_id)
    return bool(game and screen_id in game["screens"])


def is_allowed_event_type(game_id: str, event_type: str) -> bool:
    game = get_game(game_id)
    return bool(game and event_type in game["allowed_event_types"])
