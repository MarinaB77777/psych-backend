import uuid
import json
import shutil
from pathlib import Path
from typing import Any
import importlib.util
import os
import hmac
import hashlib
import secrets
from pydantic import BaseModel, Field
from pilot_session.interview import (
    build_ray_next_question,
    build_ray_chat_response,
    parse_numeric_reply,
)
from pilot_session.consistency_awareness import (
    build_researcher_consistency_summary,
)
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse, Response
from fastapi import FastAPI, HTTPException, Request
from urllib.parse import parse_qs
from rc_config import (
    RESEARCHER_PASSWORD_ENV,
    RESEARCHER_SESSION_SECRET_ENV,
    RESEARCHER_USERNAME_ENV,
    data_path,
    validate_persistent_data_root,
    validate_researcher_access_config,
)
from assessment.studies.decision_under_uncertainty.service import DecisionUnderUncertaintyService
from assessment.questionnaire_components import (
    list_question_types,
    list_response_types,
    list_scale_types,
    list_presentation_types,
)

from assessment.prepared_output import build_prepared_domain_output
from assessment.analysis.analysis_checker import (
    check_pair_analysis,
)
from assessment.analysis.run_statistical_method import (
    run_statistical_method,
)
from measurement_graph.connectors import discover_measurement_connectors
from measurement_graph.session import (
    create_measurement_session,
    mark_finished,
    mark_saved,
)
from measurement_graph.graph_builder import (
    build_measurement_graph_from_session,
)
from measurement_graph.storage import (
    save_measurement_graph,
)
from measurement_graph.instruments.session_runtime import (
    connect_instrument,
    disconnect_instrument,
    list_connected_instruments,
)

from model_engine.run_engine import run_engine_logic
from model_engine.intro_session_ru import (
    create_intro_session,
    process_intro_message,
)

from pilot_session.errors import PilotSessionError
from pilot_session.persistent_store import (
    PilotSessionPersistentStore,
)
from pilot_session.service import PilotSessionService
from pilot_account.persistent_store import PilotAccountPersistentStore
from pilot_account.service import PilotAccountService
from pilot_account.session_start_flow import PilotSessionStartFlow
from fastapi.responses import FileResponse
from assessment.studies.decision_under_uncertainty import QUESTION_BANK
from assessment.studies.decision_under_uncertainty.router import get_next_question_code
from question_banks import get_question_bank
from assessment.registry import get_assessment, list_assessments
from assessment.services.result_service import ResultService
from research.lab_store import create_research_object, list_research_objects
from research.study_store import (
    create_research_study,
    get_research_study,
    list_research_studies,
)
from research.games.registry import list_games
from research.games.store import (
    append_game_event,
    complete_game_session,
    get_game_session,
    list_game_sessions,
    start_game_session,
)
from games.living_world.app import participant_game_card
from games.living_world.app import router as living_world_router
from research.records_store import (
    list_research_records,
    save_du_research_record,
)
from assessment.analysis.analysis_selector import (
    build_analysis_catalog,
)
from research.entity_registry import list_entities
from research.analysis_runner import run_health_model_research_analysis
from research.analysis_store import load_analysis_results
from assessment.analysis.dependency_builder import (
    build_available_dependencies,
)
from research.analyses.health_model.level_map_analysis import (
    analyze_record_level_maps,
)
from research.public_output.health_model.participant_report import (
    build_participant_report,
)
from research.analyses.health_model.research_variable_registry import (
    list_health_model_research_variables,
)
from research.analyses.health_model.model_parameter_catalog import (
    build_available_model_parameter_catalog,
)
from research.analyses.health_model.model_parameter_dependency_builder import (
    build_available_model_parameter_dependencies,
)
from research.analyses.health_model.v61_calculator import (
    calculate_health_model_v61,
)
from research.analyses.health_model.model_parameter_pair_dataset import (
    build_model_parameter_pair_dataset,
    list_model_parameter_pair_participants,
)
from research.analyses.health_model.model_parameter_analysis_checker import (
    check_model_parameter_pair_analysis,
)
from independent_ai_core.service import OfflineIndependentAIService
from pprint import pformat
from pathlib import Path

app = FastAPI()
from fastapi.staticfiles import StaticFiles

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static",
)

app.include_router(living_world_router)


store = PilotSessionPersistentStore(
    str(data_path(
        "primary",
        "pilot_sessions.json",
        legacy="data/pilot_sessions.json",
    ))
)

pilot_service = PilotSessionService(store)
account_store = PilotAccountPersistentStore(
    str(data_path(
        "primary",
        "pilot_accounts.json",
        legacy="data/pilot_accounts.json",
    ))
)

account_service = PilotAccountService(account_store)

session_start_flow = PilotSessionStartFlow(
    account_service=account_service,
    session_service=pilot_service,
)

intro_sessions = {}
result_service = ResultService()
offline_ai_service = OfflineIndependentAIService()

RESEARCHER_COOKIE_NAME = "pilot_rc_researcher"
RESEARCHER_PROTECTED_EXACT_PATHS = {
    "/research-workspace",
    "/data-check",
    "/data-preparation",
    "/analysis-builder",
    "/analysis-check",
    "/scientific-results",
}
RESEARCHER_PROTECTED_PREFIXES = (
    "/research/",
)
RESEARCHER_PROTECTED_PILOT_SUFFIXES = (
    "/research-answers",
    "/research-export",
    "/consistency-clarifications",
    "/export",
    "/invalidate",
)


@app.on_event("startup")
def validate_rc_startup_configuration():
    validate_persistent_data_root()
    validate_researcher_access_config()


def researcher_access_enabled() -> bool:
    return all(
        os.getenv(name)
        for name in (
            RESEARCHER_USERNAME_ENV,
            RESEARCHER_PASSWORD_ENV,
            RESEARCHER_SESSION_SECRET_ENV,
        )
    )


def sign_researcher_session(username: str) -> str:
    secret = os.getenv(RESEARCHER_SESSION_SECRET_ENV, "")
    signature = hmac.new(
        secret.encode("utf-8"),
        username.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return f"{username}.{signature}"


def verify_researcher_session(token: str | None) -> bool:
    if not token or not researcher_access_enabled():
        return False
    username = os.getenv(RESEARCHER_USERNAME_ENV, "")
    expected = sign_researcher_session(username)
    return hmac.compare_digest(token, expected)


def is_researcher_protected_path(path: str) -> bool:
    if path in RESEARCHER_PROTECTED_EXACT_PATHS:
        return True
    if any(path.startswith(prefix) for prefix in RESEARCHER_PROTECTED_PREFIXES):
        return True
    if path.startswith("/pilot/sessions/"):
        return any(path.endswith(suffix) for suffix in RESEARCHER_PROTECTED_PILOT_SUFFIXES)
    return False


@app.middleware("http")
async def researcher_access_gate(request: Request, call_next):
    path = request.url.path
    if (
        path in {"/research-login", "/research-logout", "/health", "/"}
        or path.startswith("/static/")
        or path.startswith("/consent/")
        or not is_researcher_protected_path(path)
    ):
        return await call_next(request)

    if not researcher_access_enabled():
        return Response(
            "Researcher access is not configured for closed Pilot RC.",
            status_code=503,
            media_type="text/plain",
        )

    if verify_researcher_session(request.cookies.get(RESEARCHER_COOKIE_NAME)):
        return await call_next(request)

    wants_html = "text/html" in request.headers.get("accept", "")
    if wants_html:
        return RedirectResponse(
            f"/research-login?next={path}",
            status_code=303,
        )

    return Response(
        "Researcher authentication required.",
        status_code=401,
        media_type="text/plain",
        headers={"WWW-Authenticate": "Cookie"},
    )

class RayChatInput(BaseModel):
    message: str
    lang: str = "ru"

class IntroChatInput(BaseModel):
    message: str

class RayStartInput(BaseModel):
    participant_id: str = "ray_dialogue_user"
    lang: str = "ru"


class CreatePilotAccountInput(BaseModel):
    preferred_language: str = "ru"

class DUCompletePayload(BaseModel):
    session_id: str
    answers: dict
    language: str = "ru"
    account_id: str | None = None
    domain_data_identity: dict | None = None

class StartSessionAfterAgreementInput(BaseModel):
    account_id: str
    consent_record: dict
    study_id: str | None = None
    participant_role: str = "participant"

class ResearchObjectPayload(BaseModel):
    object_type: str
    owner: str
    title: str
    description: str = ""
    status: str = "draft"
    study_id: str | None = None
    variables: list = []
    analysis_methods: list = []
    research_question: str | None = None
    hypothesis_basis: str | None = None
    basis_notes: str | None = None

class ResearchStudyPayload(BaseModel):
    title: str
    description: str = ""
    author: str = "researcher"
    primary_research_question: str = ""
    secondary_questions: list = []
    variables: list = []
    planned_analyses: list = []
    study_id: str | None = None
    version: str = "draft-v1"

class GameSessionStartInput(BaseModel):
    game_id: str
    participant_id: str | None = None
    study_id: str | None = None
    source_session_id: str | None = None

class GameEventInput(BaseModel):
    game_session_id: str
    screen_id: str
    event_type: str
    object_id: str | None = None
    previous_object_id: str | None = None
    question_id: str | None = None
    question_uuid: str | None = None
    answer: Any = None
    value: Any = None
    decision_time_ms: int | None = None
    confirmation_step: str | None = None
    cancel_count: int = 0
    excluded_from_analysis: bool = False
    metadata: dict = Field(default_factory=dict)

class GameSessionCompleteInput(BaseModel):
    game_session_id: str
    completed: bool = True
    abandoned: bool = False
    metadata: dict = Field(default_factory=dict)

class QuestionBankSavePayload(BaseModel):
    language: str = "ru"
    source_file: str | None = None
    variable_name: str | None = None
    questions: list[dict]

class CreateQuestionBankPayload(BaseModel):
    bank_id: str
    title: str

class MeasurementGraphPayload(BaseModel):
    graph: dict

class PilotQuestionnaireBanksPayload(BaseModel):
    enabled_bank_ids: list[str]

class RunInput(BaseModel):
    answers: dict

class HealthModelV61RunInput(BaseModel):
    answers: dict

class RayAnswerInput(BaseModel):
    variable_code: str
    value: Any

class RayClarificationInput(BaseModel):
    selected_option: str
    free_text: str | None = None
    language: str = "ru"

class InvalidateSessionInput(BaseModel):
    reason: str

class SubmitAnswersInput(BaseModel):
    answers: dict
    domain_data_identity: dict | None = None

class CreateMeasurementInput(BaseModel):
    connector: dict
    measurement_type: str
    study_id: str | None = None
    participant_id: str | None = None
    session_id: str | None = None
    series_id: str | None = None
    series_position: int | None = None
    context: dict | None = None

class FinishMeasurementInput(BaseModel):
    measurement_session: dict
    raw_file_path: str | None = None
    original_file_name: str | None = None
    file_type: str | None = None
    checksum: str | None = None
    context: dict | None = None


class SaveMeasurementInput(BaseModel):
    measurement_graph: dict

class ConnectInstrumentInput(BaseModel):
    instrument_id: str
    connector: dict
    measurement_type: str
    study_id: str
    participant_id: str | None = None
    session_id: str | None = None
    context: dict | None = None


class TurnOffInstrumentInput(BaseModel):
    raw_file_path: str | None = None
    original_file_name: str | None = None
    file_type: str | None = None
    checksum: str | None = None

class AnalysisCheckInput(BaseModel):
    study_id: str
    left_question_code: str
    right_question_code: str
    method_id: str

class ParameterAnalysisCheckInput(BaseModel):
    study_id: str
    left_parameter_code: str
    right_parameter_code: str
    method_id: str
    analysis_scope: str = "CROSS_PARTICIPANT"
    repeated_measure_policy: str = "latest"
    participant_reference: str | None = None

class ModelParameterDatasetInput(BaseModel):
    study_id: str = "health_model"
    left_parameter_code: str
    right_parameter_code: str
    analysis_scope: str = "CROSS_PARTICIPANT"
    repeated_measure_policy: str = "reject_repeated"
    participant_reference: str | None = None

class StatisticalAnalysisRunInput(BaseModel):
    study_id: str
    left_question_code: str
    right_question_code: str
    method_id: str

class OfflineLearningEventInput(BaseModel):
    event_type: str
    content: str
    source: str = "manual"
    language: str = "ru"
    tags: list[str] = []
    importance: int = 1
    metadata: dict | None = None

class OfflineSuggestionsInput(BaseModel):
    language: str = "ru"
    context: dict | None = None

@app.get("/")
def root():
    return {"status": "ok"}

@app.get("/health")
def health():
    return {
        "ok": True,
        "status": "healthy",
        "service": "psych-backend-pilot-rc",
    }


@app.get("/research-login", response_class=HTMLResponse)
def research_login_page(next: str = "/research-workspace"):
    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Researcher Login</title>
  <style>
    body {{ font-family: Arial, sans-serif; max-width: 440px; margin: 64px auto; padding: 20px; }}
    label {{ display: block; margin: 12px 0 6px; }}
    input {{ width: 100%; box-sizing: border-box; padding: 10px; border: 1px solid #cbd5e1; border-radius: 8px; }}
    button {{ margin-top: 16px; padding: 10px 14px; border: 0; border-radius: 8px; background: #111827; color: white; cursor: pointer; }}
    .small {{ color: #64748b; font-size: 14px; }}
  </style>
  <script src="/static/platform_i18n.js?v=20260712-sync"></script>
</head>
<body>
  <h1>Researcher Login</h1>
  <p class="small">Closed Pilot RC researcher access.</p>
  <form method="post" action="/research-login">
    <input type="hidden" name="next" value="{next}">
    <label>Username</label>
    <input name="username" autocomplete="username" required>
    <label>Password</label>
    <input name="password" type="password" autocomplete="current-password" required>
    <button type="submit">Sign in</button>
  </form>
</body>
</html>
"""


@app.post("/research-login")
async def research_login(request: Request):
    raw_body = (await request.body()).decode("utf-8")
    form = parse_qs(raw_body, keep_blank_values=True)
    username = form.get("username", [""])[0]
    password = form.get("password", [""])[0]
    next = form.get("next", ["/research-workspace"])[0]
    if not researcher_access_enabled():
        raise HTTPException(
            status_code=503,
            detail="Researcher access is not configured",
        )

    expected_username = os.getenv(RESEARCHER_USERNAME_ENV, "")
    expected_password = os.getenv(RESEARCHER_PASSWORD_ENV, "")

    if not (
        hmac.compare_digest(username, expected_username)
        and hmac.compare_digest(password, expected_password)
    ):
        raise HTTPException(
            status_code=403,
            detail="Invalid researcher credentials",
        )

    safe_next = next if next.startswith("/") and not next.startswith("//") else "/research-workspace"
    response = RedirectResponse(safe_next, status_code=303)
    response.set_cookie(
        RESEARCHER_COOKIE_NAME,
        sign_researcher_session(expected_username),
        httponly=True,
        samesite="lax",
        secure=False,
    )
    return response


@app.get("/research-logout")
def research_logout():
    response = RedirectResponse("/research-login", status_code=303)
    response.delete_cookie(RESEARCHER_COOKIE_NAME)
    return response

@app.get("/offline-ai-core", response_class=HTMLResponse)
def offline_ai_core_page():
    return Path("static/offline_ai_core.html").read_text(encoding="utf-8")

@app.get("/offline-ai-core/status")
def offline_ai_core_status():
    return offline_ai_service.status()

@app.get("/offline-ai-core/compliance")
def offline_ai_core_compliance():
    return offline_ai_service.compliance()

@app.get("/offline-ai-core/health-model/context")
def offline_ai_core_health_model_context():
    return offline_ai_service.health_model_context()

@app.get("/offline-ai-core/events")
def offline_ai_core_events():
    return offline_ai_service.list_events()

@app.post("/offline-ai-core/events")
def offline_ai_core_add_event(payload: OfflineLearningEventInput):
    result = offline_ai_service.add_event(payload.model_dump())

    if not result.get("ok"):
        raise HTTPException(status_code=400, detail=result)

    return result

@app.post("/offline-ai-core/train")
def offline_ai_core_train():
    return offline_ai_service.train()

@app.get("/offline-ai-core/suggestions")
def offline_ai_core_suggestions(language: str = "ru"):
    return offline_ai_service.suggestions(
        language=language,
        context={"pilot_priority": True},
    )

@app.post("/offline-ai-core/suggestions")
def offline_ai_core_suggestions_for_context(payload: OfflineSuggestionsInput):
    return offline_ai_service.suggestions(
        language=payload.language,
        context=payload.context or {"pilot_priority": True},
    )

@app.post("/pilot/accounts")
def create_pilot_account(data: CreatePilotAccountInput):
    account = account_service.create_account(
        preferred_language=data.preferred_language,
    )

    return {
        "ok": True,
        "account_id": account.account_id,
        "participant_id": account.participant_id,
        "subject_link_id": account.subject_link_id,
        "preferred_language": account.preferred_language,
        "status": account.status.value,
    }
@app.get("/pilot/accounts/{account_id}")
def get_pilot_account(account_id: str):
    account = account_service.get_account(account_id)

    if account is None:
        raise HTTPException(
            status_code=404,
            detail="Account not found",
        )

    return {
        "ok": True,
        "account_id": account.account_id,
        "participant_id": account.participant_id,
        "subject_link_id": account.subject_link_id,
        "preferred_language": account.preferred_language,
        "status": account.status.value,
    }


@app.post("/pilot/accounts/start-session")
def start_session_after_agreement(
    data: StartSessionAfterAgreementInput,
):
    try:
        result = session_start_flow.start_session_after_agreement(
            account_id=data.account_id,
            consent_record=data.consent_record,
            study_id=data.study_id,
            participant_role=data.participant_role,
        )

        if result is None:
            raise HTTPException(
                status_code=404,
                detail="Account not found",
            )

        session = result["session"]
        agreement = result["agreement"]

        return {
            "ok": True,
            "account_id": data.account_id,
            "session_id": session.session_id,
            "participant_id": session.participant_id,
            "subject_link_id": session.subject_link_id,
            "agreement_id": agreement["agreement_id"],
            "agreement_status": agreement["agreement_status"],
            "collection_allowed": agreement["collection_allowed"],
            "status": session.status.value,
            "available_start_modes": [
                {
                    "mode": "ray_dialogue",
                    "label": "Диалог с Рэем",
                    "endpoint": f"/ray/chat/{session.session_id}",
                    "method": "POST",
                    "first_question": {
                        "status": "question",
                        "message": (
                            "Привет. Я Рэй. Давай начнём спокойно.\n\n"
                            "Первый вопрос: есть ли у тебя сейчас работа, учёба "
                            "или другая основная деятельность?\n\n"
                            "Ответь числом: 0 — нет, 1 — да."
                        ),
                        "awaiting_variable_code": "d0",
                        "expected_response_target": "answers.d0",
                    },
                },
                {
                    "mode": "questionnaire",
                    "label": "Ответы на вопросы анкеты",
                    "endpoint": (
                        f"/pilot/sessions/{session.session_id}/answers"
                    ),
                    "method": "POST",
                    "expected_payload": {
                        "answers": {
                            "d0": "0 or 1"
                        }
                    },
                },
            ],
        }

    except PilotSessionError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.to_dict(),
        )    

@app.post("/pilot/sessions/{session_id}/intro-chat")
def intro_chat(
    session_id: str,
    data: IntroChatInput,
):
    try:
        pilot_session = pilot_service.get_session(session_id)

        intro_session = intro_sessions.get(session_id)

        if intro_session is None:
            intro_session = create_intro_session(
                session_id=pilot_session.session_id,
                participant_id=pilot_session.participant_id,
                subject_link_id=pilot_session.subject_link_id,
                study_id=pilot_session.study_id or "pilot-study-1",
                participant_role=(
                    pilot_session.participant_role
                    or "participant"
                ),
                synchronization_reference=(
                    pilot_session.synchronization_reference
                ),
            )

        result = process_intro_message(
            session=intro_session,
            message=data.message,
        )

        intro_sessions[session_id] = result["session"]

        return {
            "ok": True,
            "session_id": session_id,
            "intro": result,
        }

    except PilotSessionError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.to_dict()["error"],
        )

@app.post("/ray/start")
def ray_start(data: RayStartInput):
    try:
        session = pilot_service.create_session(
            participant_id=data.participant_id,
        )

        messages = {
            "ru": (
                "Привет. Я Рэй. Давай начнём спокойно.\n\n"
                "Первый вопрос: есть ли у тебя сейчас работа, учёба "
                "или другая основная деятельность?\n\n"
                "Ответь числом: 0 — нет, 1 — да."
            ),
            "en": (
                "Hi. I’m Ray. Let’s start calmly.\n\n"
                "First question: do you currently have work, studies, "
                "or another main activity?\n\n"
                "Answer with a number: 0 — no, 1 — yes."
            ),
            "es": (
                "Hola. Soy Ray. Empecemos con calma.\n\n"
                "Primera pregunta: ¿actualmente tienes trabajo, estudios "
                "u otra actividad principal?\n\n"
                "Responde con un número: 0 — no, 1 — sí."
            ),
        }

        return {
            "ok": True,
            "session_id": session.session_id,
            "lang": data.lang,
            "ray": {
                "status": "question",
                "message": messages.get(data.lang, messages["ru"]),
                "awaiting_variable_code": "d0",
                "expected_response_target": "answers.d0",
            },
        }

    except PilotSessionError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.to_dict()["error"],
        )

@app.post("/ray/chat/{session_id}")
def ray_global_chat(
    session_id: str,
    data: RayChatInput,
):
    try:
        session = pilot_service.get_session(session_id)
        value = parse_numeric_reply(data.message)

        if value is None:
            return {
                "ok": True,
                "session_id": session.session_id,
                "lang": data.lang,
                "ray": {
                    "status": "clarify_answer",
                    "message": (
                        "Я сейчас жду числовой ответ на текущий вопрос. "
                        "Пожалуйста, ответь числом."
                    ),
                },
            }

        if session.status.value == "CREATED":
            pilot_service.submit_answers(
                session_id=session_id,
                answers={"d0": value},
            )
            session = pilot_service.run_session(session_id)

        else:
            current_question = build_ray_next_question(
                session=session,
                lang=data.lang,
                previous_sessions=store.list_all(),
            )

            if current_question.get("status") == "question":
                variable_code = current_question.get("variable_code")

                pilot_service.submit_followup_answers(
                    session_id=session_id,
                    answers={variable_code: value},
                )

                session = pilot_service.run_session(session_id)

        return {
            "ok": True,
            "session_id": session.session_id,
            "lang": data.lang,
            "ray": build_ray_chat_response(
                session=session,
                message=data.message,
                lang=data.lang,
                previous_sessions=store.list_all(),
            ),
        }

    except PilotSessionError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.to_dict()["error"],
        )

@app.post("/run")
def run_engine(data: RunInput):
    result = run_engine_logic(data.answers)

    return {
        "ok": True,
        "result": result,
    }

@app.post("/research/health-model/v61/run")
def run_health_model_v61(data: HealthModelV61RunInput):
    result = calculate_health_model_v61(data.answers)

    return {
        "ok": True,
        "model": result,
    }

@app.post("/pilot/sessions")
def create_pilot_session(participant_id: str):
    try:
        session = pilot_service.create_session(
            participant_id=participant_id,
        )

        return {
            "ok": True,
            "session_id": session.session_id,
            "status": session.status.value,
        }

    except PilotSessionError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.to_dict()["error"],
        )


@app.get("/pilot/sessions/{session_id}")
def get_pilot_session(session_id: str):
    try:
        session = pilot_service.get_session(session_id)

        return {
            "ok": True,
            "session_id": session.session_id,
            "participant_id": session.participant_id,
            "status": session.status.value,
            "invalidated": session.invalidated,
        }

    except PilotSessionError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.to_dict()["error"],
        )

@app.get("/pilot/sessions/{session_id}/research-answers")
def get_pilot_session_research_answers(session_id: str):
    try:
        session = pilot_service.get_session(session_id)

        return {
            "ok": True,
            "session_id": session.session_id,
            "answers_count": len(session.answers or {}),
            "questionnaire_submissions_count": len(
                session.questionnaire_submissions or []
            ),
            "research_answer_records_count": len(
                session.research_answer_records or []
            ),
            "questionnaire_submissions": (
                session.questionnaire_submissions or []
            ),
            "research_answer_records": (
                session.research_answer_records or []
            ),
        }

    except PilotSessionError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.to_dict()["error"],
        )

@app.get("/pilot/sessions/{session_id}/result")
def get_pilot_session_result(session_id: str):
    try:
        session = pilot_service.get_session(session_id)

        return {
            "ok": True,
            "session_id": session.session_id,
            "status": session.status.value,
            "result_available": bool(session.public_output),
            "public_output": session.public_output,
            "uncertainty": session.uncertainty_snapshot or {},
            "next_questions": session.next_question_snapshots or [],
            "result_is_public_safe": True,
            "raw_engine_result_included": False,
        }

    except PilotSessionError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.to_dict()["error"],
        )

@app.get("/pilot/sessions/{session_id}/participant-report")
def get_pilot_participant_report(session_id: str):
    try:
        session = pilot_service.get_session(session_id)

        record = {
            "record_id": session.session_id,
            "session_id": session.session_id,
            "study_id": session.study_id,
            "result": session.raw_engine_result or {},
        }

        level_map_record = analyze_record_level_maps(record)

        analysis = {
            "analysis_type": "health_model_current_session_participant_analysis",
            "analysis_scope": "single_session",
            "study_id": session.study_id,
            "record_count": 1,
            "level_maps": {
                "analysis_type": "resource_level_maps_single_session",
                "record_count": 1,
                "interpreted_record_count": (
                    1 if level_map_record.get("interpreted_domains") else 0
                ),
                "records": [level_map_record],
            },
        }

        report = build_participant_report(analysis)

        return {
            "ok": True,
            "session_id": session.session_id,
            "participant_report": report,
        }

    except PilotSessionError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.to_dict()["error"],
        )

@app.get("/pilot/sessions/{session_id}/participant-export")
def participant_export_pilot_session(session_id: str):
    try:
        export_data = pilot_service.generate_participant_export(
            session_id
        )

        return {
            "ok": True,
            "export": export_data,
        }

    except PilotSessionError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.to_dict()["error"],
        )


@app.post("/research/objects")
def create_research_object_api(payload: ResearchObjectPayload):
    if payload.study_id and get_research_study(payload.study_id) is None:
        raise HTTPException(
            status_code=404,
            detail="Research study not found",
        )

    obj = create_research_object(
        object_type=payload.object_type,
        owner=payload.owner,
        title=payload.title,
        description=payload.description,
        status=payload.status,
        study_id=payload.study_id,
        variables=payload.variables,
        analysis_methods=payload.analysis_methods,
        research_question=payload.research_question,
        hypothesis_basis=payload.hypothesis_basis,
        basis_notes=payload.basis_notes,
    )

    return {
        "ok": True,
        "object": obj,
    }


@app.get("/research/objects")
def list_research_objects_api(
    owner: str | None = None,
    object_type: str | None = None,
    study_id: str | None = None,
):
    return {
        "ok": True,
        "objects": list_research_objects(
            owner=owner,
            object_type=object_type,
            study_id=study_id,
        ),
    }


@app.get("/research/studies")
def list_research_studies_api(active: bool | None = None):
    studies = list_research_studies(active=active)

    return {
        "ok": True,
        "studies": studies,
    }


@app.get("/research/studies/{study_id}")
def get_research_study_api(study_id: str):
    study = get_research_study(study_id)

    if study is None:
        raise HTTPException(
            status_code=404,
            detail="Research study not found",
        )

    return {
        "ok": True,
        "study": study,
    }


@app.post("/research/studies")
def create_research_study_api(payload: ResearchStudyPayload):
    study = create_research_study(
        title=payload.title,
        description=payload.description,
        author=payload.author,
        primary_research_question=payload.primary_research_question,
        secondary_questions=payload.secondary_questions,
        variables=payload.variables,
        planned_analyses=payload.planned_analyses,
        study_id=payload.study_id,
        version=payload.version,
    )

    return {
        "ok": True,
        "study": study,
    }

@app.get("/pilot/sessions/{session_id}/research-export")
def research_export_pilot_session(session_id: str):
    try:
        export_data = pilot_service.generate_research_export(
            session_id
        )

        return {
            "ok": True,
            "export": export_data,
        }

    except PilotSessionError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.to_dict()["error"],
        )

@app.post("/research/analysis/run")
def run_research_analysis(study_id: str | None = None):
    result = run_health_model_research_analysis(
        study_id=study_id,
    )

    return {
        "ok": True,
        "analysis": result,
    }

def serialize_pilot_session_for_research(session):
    return {
        "record_id": session.session_id,
        "record_source": "pilot_session",
        "record_type": "pilot_session",
        "status": session.status.value,
        "created_at": session.created_at.isoformat(),
        "updated_at": session.updated_at.isoformat(),
        "closed_at": (
            session.closed_at.isoformat()
            if session.closed_at is not None
            else None
        ),
        "session_id": session.session_id,
        "account_id": None,
        "participant_id": session.participant_id,
        "subject_link_id": session.subject_link_id,
        "study_id": session.study_id or "health_model",
        "language": None,
        "answers_count": len(session.answers or {}),
        "has_raw_engine_result": bool(session.raw_engine_result),
        "has_public_output": bool(session.public_output),
    }

@app.get("/research/answers/summary")
def summarize_research_answers(
    question_code: str,
    study_id: str | None = None,
):
    values = []

    for research_record in list_research_records(study_id=study_id):
        for answer_record in research_record.get("research_answer_records", []):
            if answer_record.get("question_code") != question_code:
                continue

            value = answer_record.get("answer_value")
            if isinstance(value, (int, float)):
                values.append(value)

    for session in store.list_all():
        if study_id is not None and session.study_id != study_id:
            continue

        for answer_record in session.research_answer_records or []:
            if answer_record.get("question_code") != question_code:
                continue

            value = answer_record.get("answer_value")
            if isinstance(value, (int, float)):
                values.append(value)

    return {
        "ok": True,
        "question_code": question_code,
        "study_id": study_id,
        "count": len(values),
        "values": values,
        "min": min(values) if values else None,
        "max": max(values) if values else None,
        "mean": sum(values) / len(values) if values else None,
    }

@app.get("/research/answers")
def list_research_answers(
    question_code: str | None = None,
    study_id: str | None = None,
):
    records = []

    for research_record in list_research_records(study_id=study_id):
        for answer_record in research_record.get("research_answer_records", []):
            if question_code is not None and answer_record.get("question_code") != question_code:
                continue

            records.append({
                **answer_record,
                "record_source": "research_record",
                "parent_record_id": research_record.get("record_id"),
            })

    for session in store.list_all():
        if study_id is not None and session.study_id != study_id:
            continue

        for answer_record in session.research_answer_records or []:
            if question_code is not None and answer_record.get("question_code") != question_code:
                continue

            records.append({
                **answer_record,
                "record_source": "pilot_session",
                "parent_record_id": session.session_id,
            })

    return {
        "ok": True,
        "question_code": question_code,
        "study_id": study_id,
        "records_count": len(records),
        "records": records,
    }

@app.get("/research/participant-data/records")
def list_participant_data_records(study_id: str | None = None):
    research_records = list_research_records(study_id=study_id)

    research_items = [
        {
            "record_id": record.get("record_id"),
            "record_source": "research_record",
            "record_type": record.get("record_type"),
            "status": record.get("status"),
            "created_at": record.get("created_at"),
            "updated_at": record.get("updated_at"),
            "session_id": record.get("session_id"),
            "account_id": record.get("account_id"),
            "participant_id": None,
            "subject_link_id": None,
            "study_id": record.get("study_id"),
            "language": record.get("language"),
            "answers_count": len(record.get("answers", {}) or {}),
            "has_raw_engine_result": bool(record.get("result")),
            "has_public_output": bool(
                (record.get("result") or {}).get("summary")
            ),
        }
        for record in research_records
    ]

    pilot_sessions = store.list_all()

    pilot_items = [
        serialize_pilot_session_for_research(session)
        for session in pilot_sessions
    ]

    all_items = research_items + pilot_items

    if study_id:
        all_items = [
            item for item in all_items
            if item.get("study_id") == study_id
        ]

    all_items = sorted(
        all_items,
        key=lambda item: item.get("created_at") or "",
        reverse=True,
    )

    return {
        "ok": True,
        "records": all_items,
    }


@app.get("/research/participant-data/records/{record_id}")
def get_participant_data_record(record_id: str):
    records = list_research_records()

    for record in records:
        if record.get("record_id") == record_id:
            return {
                "ok": True,
                "record_source": "research_record",
                "record": record,
            }

    session = pilot_service.get_session(record_id)

    if session is not None:
        raw_payload = {
            "payload_type": "questionnaire_answers",
            "study_id": session.study_id or "health_model",
            "answers": session.answers,
        }

        analysis_output = session.raw_engine_result or {}

        prepared_domain_output = build_prepared_domain_output(
            domain_data_identity=session.domain_data_identity or {},
            raw_payload=raw_payload,
            analysis_output=analysis_output,
        )

        return {
            "ok": True,
            "record_source": "pilot_session",
            "record": {
                **serialize_pilot_session_for_research(session),
                "domain_data_identity": session.domain_data_identity,
                "raw_payload": raw_payload,
                "prepared_domain_output": prepared_domain_output,
                "analysis_output": analysis_output,
                "answers": session.answers,
                "raw_engine_result": session.raw_engine_result,
                "public_output": session.public_output,
                "uncertainty_snapshot": session.uncertainty_snapshot,
                "next_question_snapshots": session.next_question_snapshots,
                "run_history": session.run_history,
            },
        }

    raise HTTPException(status_code=404, detail="Record not found")

@app.post("/research/participant-data/records/{record_id}/analyze")
def analyze_participant_data_record(record_id: str):
    records = list_research_records()

    for record in records:
        if record.get("record_id") == record_id:
            analysis = run_health_model_research_analysis(
                study_id=record.get("study_id"),
            )

            return {
                "ok": True,
                "record_id": record_id,
                "record_source": "research_record",
                "analysis": analysis,
            }

    session = pilot_service.get_session(record_id)

    if session is not None:
        record = {
            "record_id": session.session_id,
            "session_id": session.session_id,
            "study_id": session.study_id or "health_model",
            "result": session.raw_engine_result or {},
        }

        level_map_record = analyze_record_level_maps(record)

        analysis = {
            "analysis_type": "health_model_single_pilot_session_analysis",
            "analysis_scope": "single_pilot_session",
            "study_id": session.study_id or "health_model",
            "record_count": 1,
            "level_maps": {
                "analysis_type": "resource_level_maps_single_session",
                "record_count": 1,
                "interpreted_record_count": (
                    1 if level_map_record.get("interpreted_domains") else 0
                ),
                "records": [level_map_record],
            },
        }

        return {
            "ok": True,
            "record_id": record_id,
            "record_source": "pilot_session",
            "analysis": analysis,
        }

@app.get("/research/analysis/results")
def list_research_analysis_results():
    return {
        "ok": True,
        "results": load_analysis_results(),
    }

@app.get("/data-check", response_class=HTMLResponse)
def data_check_page():
    return Path(
        "static/data_check.html"
    ).read_text(
        encoding="utf-8"
    )

@app.get("/research-lab")
def research_lab_page():
    return FileResponse("static/research_lab.html")

@app.get("/research-workspace", response_class=HTMLResponse)
def research_workspace_page():
    return Path(
        "static/research_workspace.html"
    ).read_text(
        encoding="utf-8"
    )

@app.get("/games", response_class=HTMLResponse)
def research_games_page():
    return Path(
        "static/research_games.html"
    ).read_text(
        encoding="utf-8"
    )

@app.get("/participant-portal", response_class=HTMLResponse)
def participant_portal_page():
    return Path(
        "static/participant_portal.html"
    ).read_text(
        encoding="utf-8"
    )

@app.get("/participant/games/available")
def participant_games_available():
    game = participant_game_card()
    return {
        "ok": True,
        "games": [game] if game.get("enabled") else [],
    }

@app.get("/world-choice", response_class=HTMLResponse)
def world_choice_game_page(request: Request):
    language = request.query_params.get("lang") or request.query_params.get("language")
    target = "/games/living-world"
    if language:
        target = f"{target}?lang={language}"
    return RedirectResponse(url=target)

@app.get("/research/games/registry")
def research_games_registry():
    return {
        "ok": True,
        "games": list_games(),
    }

@app.post("/research/game-sessions/start")
def research_game_session_start(payload: GameSessionStartInput):
    try:
        session = start_game_session(
            game_id=payload.game_id,
            participant_id=payload.participant_id,
            study_id=payload.study_id,
            source_session_id=payload.source_session_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return {
        "ok": True,
        "session": session,
    }

@app.post("/research/game-events")
def research_game_events(payload: GameEventInput):
    try:
        event = append_game_event(
            game_session_id=payload.game_session_id,
            screen_id=payload.screen_id,
            event_type=payload.event_type,
            object_id=payload.object_id,
            previous_object_id=payload.previous_object_id,
            question_id=payload.question_id,
            question_uuid=payload.question_uuid,
            answer=payload.answer,
            value=payload.value,
            decision_time_ms=payload.decision_time_ms,
            confirmation_step=payload.confirmation_step,
            cancel_count=payload.cancel_count,
            excluded_from_analysis=payload.excluded_from_analysis,
            metadata=payload.metadata,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return {
        "ok": True,
        "event": event,
    }

@app.post("/research/game-sessions/complete")
def research_game_session_complete(payload: GameSessionCompleteInput):
    try:
        session = complete_game_session(
            game_session_id=payload.game_session_id,
            completed=payload.completed,
            abandoned=payload.abandoned,
            metadata=payload.metadata,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return {
        "ok": True,
        "session": session,
    }

@app.get("/research/game-sessions")
def research_game_session_list():
    return {
        "ok": True,
        "sessions": list_game_sessions(),
    }

@app.get("/research/game-sessions/{game_session_id}")
def research_game_session_get(game_session_id: str):
    session = get_game_session(game_session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Game session not found")

    return {
        "ok": True,
        "session": session,
    }

@app.get("/data-preparation", response_class=HTMLResponse)
def data_preparation_page():
    return Path(
        "static/data_preparation.html"
    ).read_text(
        encoding="utf-8"
    )

def _question_bank_file_info(bank_id: str, lang: str):
    allowed_langs = {"ru", "en", "es"}

    if lang not in allowed_langs:
        raise HTTPException(status_code=400, detail="Unsupported language")

    variable_name = f"QUESTION_BANK_{lang.upper()}"

    if bank_id == "health_model":
        filename = {
            "ru": "QUESTION_BANK_RU.py",
            "en": "QUESTION_BANK_EN.py",
            "es": "QUESTION_BANK_ES.py",
        }[lang]

        return Path("question_banks") / filename, variable_name

    if bank_id == "decision_under_uncertainty":
        filename = {
            "ru": "decision_under_uncertainty_questions_ru.py",
            "en": "decision_under_uncertainty_questions_en.py",
            "es": "decision_under_uncertainty_questions_es.py",
        }[lang]

        return (
            Path("assessment/studies/decision_under_uncertainty") / filename,
            variable_name,
        )

    filename = {
        "ru": "QUESTION_BANK_RU.py",
        "en": "QUESTION_BANK_EN.py",
        "es": "QUESTION_BANK_ES.py",
    }[lang]

    return Path("question_banks") / bank_id / filename, variable_name


def _load_question_bank_from_file(path: Path, variable_name: str):
    if not path.exists():
        raise HTTPException(status_code=404, detail="Question bank file not found")

    module_name = "dynamic_question_bank_" + path.stem + "_" + str(abs(hash(str(path))))

    spec = importlib.util.spec_from_file_location(module_name, path)

    if spec is None or spec.loader is None:
        raise HTTPException(status_code=500, detail="Question bank import failed")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    bank = getattr(module, variable_name, None)

    if bank is None:
        raise HTTPException(status_code=500, detail="Question bank variable not found")

    return bank

PILOT_BANKS_CONFIG_PATH = data_path(
    "config",
    "pilot_questionnaire_banks.json",
    legacy="data/pilot_questionnaire_banks.json",
)

def load_pilot_questionnaire_banks(project_id: str) -> list[str]:
    if not PILOT_BANKS_CONFIG_PATH.exists():
        return []

    data = json.loads(
        PILOT_BANKS_CONFIG_PATH.read_text(encoding="utf-8")
    )

    return data.get(project_id, [])


def save_pilot_questionnaire_banks(
    project_id: str,
    enabled_bank_ids: list[str],
):
    PILOT_BANKS_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)

    if PILOT_BANKS_CONFIG_PATH.exists():
        data = json.loads(
            PILOT_BANKS_CONFIG_PATH.read_text(encoding="utf-8")
        )
    else:
        data = {}

    data[project_id] = enabled_bank_ids

    PILOT_BANKS_CONFIG_PATH.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

@app.get("/pilot/questionnaire-banks")
def get_pilot_questionnaire_banks(
    project_id: str = "health_model_pilot",
):
    langs = ["ru", "en", "es"]
    banks_by_id = {}

    # 1. Assessment-опросники: intro/resource/decision
    for assessment in list_assessments():
        bank_id = assessment["id"]
        title = assessment.get("title", {})

        banks_by_id[bank_id] = {
            "id": bank_id,
            "status": assessment.get("status", "active"),
            "title_by_lang": {
                "ru": title.get("ru", bank_id) if isinstance(title, dict) else str(title),
                "en": title.get("en", bank_id) if isinstance(title, dict) else str(title),
                "es": title.get("es", bank_id) if isinstance(title, dict) else str(title),
            },
        }

    # 2. Реальные question banks: health_model, DU, созданные банки
    for bank in list_question_banks()["banks"]:
        bank_id = bank["id"]

        if bank_id not in banks_by_id:
            banks_by_id[bank_id] = {
                "id": bank_id,
                "status": bank.get("status", "active"),
                "title_by_lang": {
                    "ru": bank.get("title", bank_id),
                    "en": bank.get("title", bank_id),
                    "es": bank.get("title", bank_id),
                },
            }

    enabled = set(load_pilot_questionnaire_banks(project_id))

    return {
        "ok": True,
        "project_id": project_id,
        "enabled_bank_ids": list(enabled),
        "banks": [
            {
                **bank,
                "enabled": bank["id"] in enabled,
            }
            for bank in banks_by_id.values()
        ],
    }

@app.post("/pilot/questionnaire-banks")
def update_pilot_questionnaire_banks(
    payload: PilotQuestionnaireBanksPayload,
    project_id: str = "health_model_pilot",
):
    save_pilot_questionnaire_banks(
        project_id=project_id,
        enabled_bank_ids=payload.enabled_bank_ids,
    )

    return {
        "ok": True,
        "project_id": project_id,
        "enabled_bank_ids": payload.enabled_bank_ids,
    }

@app.get("/question-banks")
def list_question_banks():
    banks = [
        {
            "id": "health_model",
            "title": "Health Model",
            "status": "active",
        },
        {
            "id": "decision_under_uncertainty",
            "title": "Decision Under Uncertainty",
            "status": "active",
        },
    ]

    custom_root = Path("question_banks")

    if custom_root.exists():
        for bank_dir in custom_root.iterdir():
            if not bank_dir.is_dir():
                continue

            if not (bank_dir / "__init__.py").exists():
                continue

            bank_id = bank_dir.name

            if any(bank["id"] == bank_id for bank in banks):
                continue

            banks.append({
                "id": bank_id,
                "title": bank_id.replace("_", " ").title(),
                "status": "draft",
            })

    return {
        "ok": True,
        "banks": banks,
    }

@app.get("/questionnaire-components")
def get_questionnaire_components():
    return {
        "ok": True,
        "components": {
            "question_types": list_question_types(),
            "response_types": list_response_types(),
            "scale_types": list_scale_types(),
            "presentation_types": list_presentation_types(),
        },
    }

@app.get("/question-banks/{bank_id}")
def read_question_bank(bank_id: str, lang: str = "ru"):
    if bank_id in {"intro", "resource", "decision"}:
        assessment = get_assessment(
            assessment_id=bank_id,
            question_bank=get_question_bank(lang),
        )

        if assessment is None:
            raise HTTPException(status_code=404, detail="Assessment not found")

        if assessment.get("ok") is False:
            raise HTTPException(status_code=404, detail=assessment)

        return {
            "ok": True,
            "bank_id": bank_id,
            "language": lang,
            "source_file": None,
            "variable_name": None,
            "questions": assessment.get("questions", []),
        }

    path, variable_name = _question_bank_file_info(bank_id, lang)
    bank = _load_question_bank_from_file(path, variable_name)

    return {
        "ok": True,
        "bank_id": bank_id,
        "language": lang,
        "source_file": str(path),
        "variable_name": variable_name,
        "questions": list(bank.values()),
    }

@app.post("/question-banks")
def create_question_bank(payload: CreateQuestionBankPayload):
    bank_id = payload.bank_id.strip().lower()

    if not bank_id:
        raise HTTPException(status_code=400, detail="Bank id missing")

    if not bank_id.replace("_", "").isalnum():
        raise HTTPException(
            status_code=400,
            detail="Bank id may contain only letters, numbers and underscore",
        )

    base_path = Path("question_banks") / bank_id

    if base_path.exists():
        raise HTTPException(status_code=400, detail="Question bank already exists")

    base_path.mkdir(parents=True)

    files = {
        "ru": ("QUESTION_BANK_RU.py", "QUESTION_BANK_RU"),
        "en": ("QUESTION_BANK_EN.py", "QUESTION_BANK_EN"),
        "es": ("QUESTION_BANK_ES.py", "QUESTION_BANK_ES"),
    }

    for filename, variable_name in files.values():
        (base_path / filename).write_text(
            f"{variable_name} = {{}}\n",
            encoding="utf-8",
        )

    (base_path / "__init__.py").write_text(
        "from .QUESTION_BANK_RU import QUESTION_BANK_RU\n"
        "from .QUESTION_BANK_EN import QUESTION_BANK_EN\n"
        "from .QUESTION_BANK_ES import QUESTION_BANK_ES\n\n"
        "QUESTION_BANKS = {\n"
        '    "ru": QUESTION_BANK_RU,\n'
        '    "en": QUESTION_BANK_EN,\n'
        '    "es": QUESTION_BANK_ES,\n'
        "}\n\n"
        "def get_question_bank(lang: str):\n"
        '    return QUESTION_BANKS.get(lang, QUESTION_BANK_RU)\n',
        encoding="utf-8",
    )

    return {
        "ok": True,
        "bank": {
            "id": bank_id,
            "title": payload.title,
            "status": "draft",
            "path": str(base_path),
        },
    }

@app.delete("/question-banks/{bank_id}")
def delete_question_bank(bank_id: str):
    protected_bank_ids = {
        "health_model",
        "decision_under_uncertainty",
        "intro",
        "resource",
        "decision",
    }

    normalized_bank_id = bank_id.strip().lower()

    if not normalized_bank_id:
        raise HTTPException(
            status_code=400,
            detail="Bank id missing",
        )

    if normalized_bank_id in protected_bank_ids:
        raise HTTPException(
            status_code=400,
            detail="System question bank cannot be deleted",
        )

    if not normalized_bank_id.replace("_", "").isalnum():
        raise HTTPException(
            status_code=400,
            detail=(
                "Bank id may contain only letters, "
                "numbers and underscore"
            ),
        )

    bank_path = Path("question_banks") / normalized_bank_id

    if not bank_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Question bank not found",
        )

    if not bank_path.is_dir():
        raise HTTPException(
            status_code=400,
            detail="Question bank path is not a directory",
        )

    connected_projects = []

    if PILOT_BANKS_CONFIG_PATH.exists():
        pilot_config = json.loads(
            PILOT_BANKS_CONFIG_PATH.read_text(
                encoding="utf-8",
            )
        )

        for project_id, enabled_bank_ids in pilot_config.items():
            if normalized_bank_id in (
                enabled_bank_ids or []
            ):
                connected_projects.append(project_id)

    if connected_projects:
        raise HTTPException(
            status_code=409,
            detail={
                "error": "QUESTION_BANK_IS_CONNECTED",
                "message": (
                    "Disconnect the question bank "
                    "from the pilot before deleting it"
                ),
                "connected_projects": connected_projects,
            },
        )

    shutil.rmtree(bank_path)

    return {
        "ok": True,
        "deleted_bank_id": normalized_bank_id,
        "deleted_path": str(bank_path),
    }

@app.post("/question-banks/{bank_id}/questions")
def save_question_bank_questions(bank_id: str, payload: QuestionBankSavePayload):
    if not payload.source_file:
        raise HTTPException(status_code=400, detail="Source file missing")

    if not payload.variable_name:
        raise HTTPException(status_code=400, detail="Variable name missing")

    path = Path(payload.source_file)

    if not path.exists():
        raise HTTPException(status_code=404, detail="Source file not found")

    question_bank = {}

    for question in payload.questions:
        code = question.get("code")

        if not code:
            raise HTTPException(status_code=400, detail="Question code missing")

        question_bank[code] = question

    content = (
        f"{payload.variable_name} = "
        f"{pformat(question_bank, width=120, sort_dicts=False)}\n"
    )

    path.write_text(content, encoding="utf-8")

    return {
        "ok": True,
        "bank_id": bank_id,
        "language": payload.language,
        "saved_questions": len(question_bank),
        "file": str(path),
    }

@app.get("/assessments/{assessment_id}")
def read_assessment(assessment_id: str, lang: str = "ru"):
    assessment = get_assessment(
        assessment_id=assessment_id,
        question_bank=get_question_bank(lang),
    )

    if assessment is None:
        raise HTTPException(status_code=404, detail="Assessment not found")

    if assessment.get("ok") is False:
        raise HTTPException(status_code=500, detail=assessment)

    return assessment

@app.post("/assessments/{assessment_id}/questions")
def save_assessment_questions(assessment_id: str, payload: QuestionBankSavePayload):
    allowed_langs = {"ru", "en", "es"}
    if payload.language not in allowed_langs:
        raise HTTPException(status_code=400, detail="Unsupported language")

    file_maps = {
        "health_model": {
            "ru": (Path("question_banks/QUESTION_BANK_RU.py"), "QUESTION_BANK_RU"),
            "en": (Path("question_banks/QUESTION_BANK_EN.py"), "QUESTION_BANK_EN"),
            "es": (Path("question_banks/QUESTION_BANK_ES.py"), "QUESTION_BANK_ES"),
        },
        "decision_under_uncertainty": {
            "ru": (
                Path("assessment/studies/decision_under_uncertainty/decision_under_uncertainty_questions_ru.py"),
                "QUESTION_BANK_RU",
            ),
            "en": (
                Path("assessment/studies/decision_under_uncertainty/decision_under_uncertainty_questions_en.py"),
                "QUESTION_BANK_EN",
            ),
            "es": (
                Path("assessment/studies/decision_under_uncertainty/decision_under_uncertainty_questions_es.py"),
                "QUESTION_BANK_ES",
            ),
        },
    }

    if assessment_id not in file_maps:
        raise HTTPException(status_code=400, detail="Unsupported assessment")

    path, variable_name = file_maps[assessment_id][payload.language]

    question_bank = {}

    for question in payload.questions:
        code = question.get("code")
        if not code:
            raise HTTPException(status_code=400, detail="Question code missing")
        question_bank[code] = question

    content = f"{variable_name} = {pformat(question_bank, width=120, sort_dicts=False)}\n"
    path.write_text(content, encoding="utf-8")

    return {
        "ok": True,
        "assessment_id": assessment_id,
        "language": payload.language,
        "saved_questions": len(question_bank),
        "file": str(path),
    }

@app.get("/research/entities")
def list_research_entities_api(entity_type: str | None = None, language: str = "ru"):
    return {
        "ok": True,
        "entities": list_entities(entity_type=entity_type, language=language),
    }

@app.get("/questionnaire-du")
def questionnaire_du_page():
    return FileResponse("static/questionnaire_du.html")

class DUAnswerPayload(BaseModel):
    session_id: str
    question_code: str
    value: int
    language: str = "ru"


@app.get("/du/first-question")
def du_first_question(language: str = "ru"):
    bank = QUESTION_BANK.get(language, QUESTION_BANK["ru"])
    return {
        "ok": True,
        "question": bank.get("DU1"),
    }


@app.post("/du/answer")
def du_answer(payload: DUAnswerPayload):
    bank = QUESTION_BANK.get(payload.language, QUESTION_BANK["ru"])
    question = bank.get(payload.question_code)

    if question is None:
        return {
            "ok": False,
            "error": "UNKNOWN_QUESTION",
        }

    next_code = get_next_question_code(payload.question_code, payload.value)

    if not next_code or next_code.endswith("_RESERVED"):
        return {
            "ok": True,
            "done": True,
            "next_code": next_code,
            "question": None,
        }

    return {
        "ok": True,
        "done": False,
        "next_code": next_code,
        "question": bank.get(next_code),
    }

@app.post("/pilot/sessions/{session_id}/answers")
def submit_pilot_answers(
    session_id: str,
    data: SubmitAnswersInput,
):
    try:
        session = pilot_service.submit_answers(
            session_id=session_id,
            answers=data.answers,
            domain_data_identity=data.domain_data_identity,
        )

        return {
            "ok": True,
            "status": session.status.value,
        }

    except PilotSessionError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.to_dict()["error"],
        )

@app.post("/pilot/sessions/{session_id}/followup-answers")
def submit_pilot_followup_answers(
    session_id: str,
    data: SubmitAnswersInput,
):
    try:
        session = pilot_service.submit_followup_answers(
            session_id=session_id,
            answers=data.answers,
        )

        return {
            "ok": True,
            "status": session.status.value,
            "answers_count": len(session.answers),
        }

    except PilotSessionError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.to_dict()["error"],
        )

@app.post("/pilot/sessions/{session_id}/run")
def run_pilot_session(session_id: str):
    try:
        session = pilot_service.run_session(session_id)

        health_model_v61 = calculate_health_model_v61(
            session.answers or {},
        )

        return {
            "ok": True,
            "status": session.status.value,
            "health_model_v61": health_model_v61,
        }

    except PilotSessionError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.to_dict()["error"],
        )

@app.get("/pilot/sessions/{session_id}/ray-next-question")
def get_ray_next_question(
    session_id: str,
    lang: str = "ru",
):
    try:
        session = pilot_service.get_session(session_id)

        return {
            "ok": True,
            "ray": build_ray_next_question(
                session=session,
                lang=lang,
                previous_sessions=store.list_all(),
            ),
        }

    except PilotSessionError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.to_dict()["error"],
        )


@app.get("/pilot/sessions/{session_id}/consistency-clarifications")
def get_consistency_clarifications(
    session_id: str,
    lang: str = "ru",
):
    try:
        session = pilot_service.get_session(session_id)

        return {
            "ok": True,
            "session_id": session.session_id,
            "clarifications": build_researcher_consistency_summary(
                session=session,
                previous_sessions=store.list_all(),
                lang=lang,
            ),
            "stored_clarifications": session.consistency_clarifications,
            "boundary": {
                "game_or_dialogue_output_is_not_participant_truth": True,
                "no_diagnosis": True,
                "no_automatic_penalty": True,
                "health_model_not_updated_by_clarification": True,
            },
        }

    except PilotSessionError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.to_dict()["error"],
        )


@app.post("/pilot/sessions/{session_id}/ray-answer")
def submit_ray_answer(
    session_id: str,
    data: RayAnswerInput,
):
    try:
        pilot_service.submit_followup_answers(
            session_id=session_id,
            answers={
                data.variable_code: data.value,
            },
        )

        session = pilot_service.run_session(session_id)

        return {
            "ok": True,
            "status": session.status.value,
            "ray": build_ray_next_question(
                session=session,
                lang="ru",
                previous_sessions=store.list_all(),
            ),
        }

    except PilotSessionError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.to_dict()["error"],
        )

@app.post("/pilot/sessions/{session_id}/ray-clarification")
def submit_ray_clarification(
    session_id: str,
    data: RayClarificationInput,
):
    try:
        clarification = pilot_service.record_consistency_clarification(
            session_id=session_id,
            selected_option=data.selected_option,
            free_text=data.free_text,
            language=data.language,
            previous_sessions=store.list_all(),
        )

        session = pilot_service.get_session(session_id)

        messages = {
            "ru": "Спасибо, уточнение сохранено отдельно от исходных ответов.",
            "en": "Thank you. The clarification was saved separately from the original answers.",
            "es": "Gracias. La aclaración se guardó por separado de las respuestas originales.",
        }

        return {
            "ok": True,
            "status": clarification["status"],
            "message": messages.get(data.language, messages["ru"]),
            "answers_count": len(session.research_answer_records or []),
            "clarification": {
                "status": clarification["status"],
                "selected_option": clarification["selected_option"],
                "free_text_saved": bool(clarification["free_text"]),
            },
        }

    except PilotSessionError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.to_dict()["error"],
        )

@app.post("/pilot/sessions/{session_id}/ray-chat")
def ray_chat(
    session_id: str,
    data: RayChatInput,
):
    try:
        session = pilot_service.get_session(session_id)

        current_question = build_ray_next_question(
            session=session,
            lang=data.lang,
            previous_sessions=store.list_all(),
        )

        if current_question.get("status") == "question":
            value = parse_numeric_reply(data.message)

            if value is not None:
                variable_code = current_question.get("variable_code")

                pilot_service.submit_followup_answers(
                    session_id=session_id,
                    answers={
                        variable_code: value,
                    },
                )

                session = pilot_service.run_session(session_id)

                return {
                    "ok": True,
                    "ray": build_ray_chat_response(
                        session=session,
                        message=data.message,
                        lang=data.lang,
                        previous_sessions=store.list_all(),
                    ),
                }

        return {
            "ok": True,
            "ray": build_ray_chat_response(
                session=session,
                message=data.message,
                lang=data.lang,
                previous_sessions=store.list_all(),
            ),
        }

    except PilotSessionError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.to_dict()["error"],
        )


@app.get("/pilot/sessions/{session_id}/export")
def export_pilot_session(session_id: str):
    try:
        export_data = pilot_service.generate_export(
            session_id
        )

        return {
            "ok": True,
            "export": export_data,
        }

    except PilotSessionError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.to_dict()["error"],
        )


@app.post("/pilot/sessions/{session_id}/close")
def close_pilot_session(session_id: str):
    try:
        session = pilot_service.close_session(
            session_id
        )

        return {
            "ok": True,
            "status": session.status.value,
            "closed_at": (
                session.closed_at.isoformat()
                if session.closed_at is not None
                else None
            ),
        }

    except PilotSessionError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.to_dict()["error"],
        )


@app.post("/pilot/sessions/{session_id}/invalidate")
def invalidate_pilot_session(
    session_id: str,
    data: InvalidateSessionInput,
):
    try:
        session = pilot_service.invalidate_session(
            session_id=session_id,
            reason=data.reason,
        )

        return {
            "ok": True,
            "status": session.status.value,
            "invalidated": session.invalidated,
            "reason": session.invalidation_reason,
        }

    except PilotSessionError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.to_dict()["error"],
        )

@app.get("/assessment", response_class=HTMLResponse)
def assessment_page():
    return Path(
        "static/assessment.html"
    ).read_text(
        encoding="utf-8"
    )

@app.get("/consent/{version}/{lang}", response_class=HTMLResponse)
def consent_page(version: str, lang: str, fragment: bool = False):
    allowed_versions = {"pilot_v1"}
    allowed_langs = {"ru", "en", "es"}

    if version not in allowed_versions:
        raise HTTPException(status_code=404, detail="Consent version not found")

    if lang not in allowed_langs:
        raise HTTPException(status_code=404, detail="Consent language not found")

    path = Path("static/consent") / version / f"{lang}.html"

    if not path.exists():
        raise HTTPException(status_code=404, detail="Consent file not found")

    consent_html = path.read_text(encoding="utf-8")

    if fragment:
        return consent_html

    title = {
        "ru": "Информированное согласие",
        "en": "Informed Consent",
        "es": "Consentimiento informado",
    }[lang]
    checkbox = {
        "ru": "Я принимаю участие в этой пилотной сессии",
        "en": "I agree to participate in this pilot session",
        "es": "Acepto participar en esta sesión piloto",
    }[lang]
    accept = {
        "ru": "Принять и начать",
        "en": "Accept and start",
        "es": "Aceptar y empezar",
    }[lang]
    decline = {
        "ru": "Отказаться",
        "en": "Decline",
        "es": "Rechazar",
    }[lang]
    declined = {
        "ru": "Сессия не создана. Вы можете закрыть страницу или вернуться позже.",
        "en": "No session was created. You can close this page or come back later.",
        "es": "No se creó ninguna sesión. Puedes cerrar esta página o volver más tarde.",
    }[lang]

    return f"""
<!DOCTYPE html>
<html lang="{lang}">
<head>
  <meta charset="UTF-8">
  <title>{title}</title>
  <script src="/static/platform_i18n.js?v=20260712-sync"></script>
  <style>
    body {{ font-family: Arial, sans-serif; max-width: 760px; margin: 40px auto; padding: 20px; }}
    .card {{ border: 1px solid #d8dde6; border-radius: 12px; padding: 18px; margin-bottom: 16px; }}
    button {{ padding: 10px 16px; margin: 6px 6px 6px 0; cursor: pointer; }}
    .primary {{ background: #111827; color: white; border: 0; border-radius: 8px; }}
    .small {{ color: #64748b; font-size: 14px; }}
  </style>
</head>
<body>
  <main class="card">
    <h1>{title}</h1>
    <div id="consentDocument">{consent_html}</div>
    <label>
      <input type="checkbox" id="consentAccepted">
      <span>{checkbox}</span>
    </label>
    <p class="small">This agreement applies only to this pilot session and is not approval for unrelated future reuse.</p>
    <button class="primary" type="button" onclick="acceptConsent()">{accept}</button>
    <button type="button" onclick="declineConsent()">{decline}</button>
    <p id="status" class="small"></p>
  </main>
  <script>
    const lang = "{lang}";
    const studyId = new URLSearchParams(window.location.search).get("study_id") || "health_model";
    async function ensureAccount() {{
      const existing = localStorage.getItem("health_model_account_id");
      if (existing) return existing;
      const response = await fetch("/pilot/accounts", {{
        method: "POST",
        headers: {{"Content-Type": "application/json"}},
        body: JSON.stringify({{ preferred_language: lang }})
      }});
      const data = await response.json();
      if (!response.ok || !data.account_id) throw new Error("account_failed");
      localStorage.setItem("health_model_account_id", data.account_id);
      return data.account_id;
    }}
    async function acceptConsent() {{
      const status = document.getElementById("status");
      if (!document.getElementById("consentAccepted").checked) {{
        status.innerText = "{checkbox}";
        return;
      }}
      status.innerText = "Starting...";
      try {{
        const accountId = await ensureAccount();
        const response = await fetch("/pilot/accounts/start-session", {{
          method: "POST",
          headers: {{"Content-Type": "application/json"}},
          body: JSON.stringify({{
            account_id: accountId,
            participant_role: "participant",
            study_id: studyId,
            consent_record: {{
              consent_status: "granted",
              consent_version: "consent-policy-1",
              consent_scope: ["pilot_participation"],
              granted_at: new Date().toISOString(),
              revoked_at: null,
              expiration_at: null,
              consent_basis: "explicit_checkbox",
              notes: null,
              language: lang,
              assessment_logic_id: studyId,
              study_id: studyId
            }}
          }})
        }});
        const data = await response.json();
        if (!response.ok || !data.ok) throw new Error("session_failed");
        localStorage.setItem("health_model_session_id", data.session_id);
        localStorage.setItem("health_model_selected_study", studyId);
        localStorage.setItem("health_model_lang", lang);
        window.location.href = "/assessment?lang=" + encodeURIComponent(lang) + "&continue=1";
      }} catch (error) {{
        status.innerText = "Session start failed.";
      }}
    }}
    function declineConsent() {{
      document.getElementById("status").innerText = "{declined}";
    }}
  </script>
</body>
</html>
"""

@app.get("/analysis-check", response_class=HTMLResponse)
def analysis_check_page():
    return Path(
        "static/analysis_check.html"
    ).read_text(
        encoding="utf-8"
    )
@app.get("/pilot-result", response_class=HTMLResponse)
def pilot_result_page():
    return Path("static/pilot_result.html").read_text(encoding="utf-8")
   
@app.get("/scientific-results", response_class=HTMLResponse)
def scientific_results_page():
    return Path("static/scientific_results.html").read_text(
        encoding="utf-8"
    )
 
@app.post("/du/complete")
def du_complete(payload: DUCompletePayload):
    service = DecisionUnderUncertaintyService()
    result = service.process_completed_block(payload.answers)

    saved_result = result_service.save(
        account_id=payload.account_id,
        session_id=payload.session_id,
        study_id="decision_under_uncertainty",
        result=result,
    )
    save_du_research_record(
        session_id=payload.session_id,
        account_id=payload.account_id,
        answers=payload.answers,
        result=result,
        language=payload.language,
        domain_data_identity=payload.domain_data_identity,
    )
    return {
        "ok": True,
        "session_id": payload.session_id,
        "result_id": saved_result.get("created_at"),
        "summary": result["summary"],
    }

@app.get("/pilot/accounts/{account_id}/results")
def get_account_results(account_id: str):
    return {
        "ok": True,
        "account_id": account_id,
        "results": result_service.list(account_id),
    }

@app.get("/measurement-setup", response_class=HTMLResponse)
def measurement_setup_page():
    return Path(
        "static/measurement_setup.html"
    ).read_text(
        encoding="utf-8"
    )


@app.get("/measurement/connectors")
def list_measurement_connectors_api():
    return {
        "ok": True,
        "connectors": discover_measurement_connectors(),
    }

@app.post("/measurement/graphs")
def save_measurement_graph_api(payload: MeasurementGraphPayload):
    saved = save_measurement_graph(payload.graph)

    return {
        "ok": True,
        "saved": saved,
    }

@app.post("/measurement/create")
def create_measurement_api(data: CreateMeasurementInput):
    measurement_session = create_measurement_session(
        measurement_type=data.measurement_type,
        connector=data.connector,
        study_id=data.study_id,
        participant_id=data.participant_id,
        session_id=data.session_id,
        series_id=data.series_id,
        series_position=data.series_position,
    )

    return {
        "ok": True,
        "measurement_session": measurement_session,
    }

@app.post("/measurement/finish")
def finish_measurement_api(data: FinishMeasurementInput):
    measurement_session = mark_finished(
        data.measurement_session,
        raw_file_path=data.raw_file_path,
        original_file_name=data.original_file_name,
        file_type=data.file_type,
        checksum=data.checksum,
    )

    graph = build_measurement_graph_from_session(
        measurement_session,
        context=data.context or {},
    )

    return {
        "ok": True,
        "measurement_session": measurement_session,
        "measurement_graph": graph,
    }

@app.post("/measurement/save")
def save_measurement_api(data: SaveMeasurementInput):
    saved = save_measurement_graph(data.measurement_graph)

    return {
        "ok": True,
        "saved": saved,
    }

@app.post("/measurement/instruments/connect")
def connect_measurement_instrument_api(data: ConnectInstrumentInput):
    instrument = connect_instrument(
        instrument_id=data.instrument_id,
        connector=data.connector,
        measurement_type=data.measurement_type,
        study_id=data.study_id,
        participant_id=data.participant_id,
        session_id=data.session_id,
        context=data.context or {},
    )

    return {
        "ok": True,
        "instrument": instrument,
    }


@app.get("/measurement/instruments")
def list_measurement_instruments_api():
    return {
        "ok": True,
        "instruments": list_connected_instruments(),
    }


@app.post("/measurement/instruments/{instrument_id}/disconnect")
def disconnect_measurement_instrument_api(instrument_id: str):
    instrument = disconnect_instrument(instrument_id)

    return {
        "ok": True,
        "instrument": instrument,
    }

@app.get("/research/dependencies/available")
def get_available_research_dependencies(
    study_id: str,
):
    answer_records = []

    for research_record in list_research_records(study_id=study_id):
        answer_records.extend(
            research_record.get("research_answer_records", [])
        )

    for session in store.list_all():
        if session.study_id != study_id:
            continue

        answer_records.extend(
            session.research_answer_records or []
        )

    return build_available_dependencies(
        study_id=study_id,
        answer_records=answer_records,
    )

def build_answer_records_from_answers(
    *,
    study_id: str,
    record_id: str,
    session_id: str | None,
    answers: dict,
) -> list[dict]:
    return [
        {
            "answer_record_id": f"{record_id}:{question_code}",
            "record_type": "questionnaire_answer",
            "study_id": study_id,
            "session_id": session_id,
            "question_code": question_code,
            "answer_value": answer_value,
            "answer_value_type": type(answer_value).__name__,
            "source_mode": "answers_fallback",
        }
        for question_code, answer_value in (answers or {}).items()
    ]

def collect_answer_records_for_study(study_id: str) -> list[dict]:
    answer_records = []

    for research_record in list_research_records(study_id=study_id):
        records = research_record.get("research_answer_records", [])

        if records:
            answer_records.extend(records)
        else:
            answer_records.extend(
                build_answer_records_from_answers(
                    study_id=research_record.get("study_id") or study_id,
                    record_id=research_record.get("record_id") or "research_record",
                    session_id=research_record.get("session_id"),
                    answers=research_record.get("answers", {}),
                )
            )

    for session in store.list_all():
        if session.study_id != study_id:
            continue

        answer_records.extend(
            build_answer_records_from_answers(
                study_id=session.study_id or study_id,
                record_id=session.session_id,
                session_id=session.session_id,
                answers=session.answers or {},
            )
        )

    return answer_records

@app.get("/research/analysis/catalog")
def get_research_analysis_catalog(
    study_id: str,
):
    answer_records = []

    for research_record in list_research_records(study_id=study_id):
        records = research_record.get("research_answer_records", [])

        if records:
            answer_records.extend(records)
        else:
            answer_records.extend(
                build_answer_records_from_answers(
                    study_id=research_record.get("study_id") or study_id,
                    record_id=research_record.get("record_id") or "research_record",
                    session_id=research_record.get("session_id"),
                    answers=research_record.get("answers", {}),
                )
            )

    for session in store.list_all():
        if session.study_id != study_id:
            continue

        records = session.research_answer_records or []

        if records:
            answer_records.extend(records)
        else:
            answer_records.extend(
                build_answer_records_from_answers(
                    study_id=session.study_id or study_id,
                    record_id=session.session_id,
                    session_id=session.session_id,
                    answers=session.answers or {},
                )
            )

    return {
        "ok": True,
        **build_analysis_catalog(
            study_id=study_id,
            answer_records=answer_records,
        ),
    }

@app.get("/research/health-model/research-variables")
def list_health_model_research_variables_api():
    return {
        "ok": True,
        "variables": list_health_model_research_variables(),
    }
@app.get("/research/model-parameters/available")
def list_available_model_parameters_api(
    study_id: str = "health_model",
):
    catalog = build_available_model_parameter_catalog(
        research_records=list_research_records(
            study_id=study_id,
        ),
        pilot_sessions=store.list_all(),
        study_id=study_id,
    )

    return {
        "ok": True,
        **catalog,
    }

@app.get("/research/model-parameters/dependencies")
def list_available_model_parameter_dependencies_api(
    study_id: str = "health_model",
):
    return build_available_model_parameter_dependencies(
        research_records=list_research_records(
            study_id=study_id,
        ),
        pilot_sessions=store.list_all(),
        study_id=study_id,
    )

@app.get("/research/model-parameters/pair-participants")
def list_model_parameter_pair_participants_api(
    left_parameter_code: str,
    right_parameter_code: str,
    study_id: str = "health_model",
):
    return list_model_parameter_pair_participants(
        research_records=list_research_records(
            study_id=study_id,
        ),
        pilot_sessions=store.list_all(),
        study_id=study_id,
        left_parameter_code=left_parameter_code,
        right_parameter_code=right_parameter_code,
    )

@app.post("/research/analysis/check")
def check_research_analysis(
    data: AnalysisCheckInput,
):
    answer_records = collect_answer_records_for_study(
        data.study_id,
    )

    result = check_pair_analysis(
        study_id=data.study_id,
        left_question_code=data.left_question_code,
        right_question_code=data.right_question_code,
        method_id=data.method_id,
        answer_records=answer_records,
    )

    return result

@app.post("/research/model-parameters/dataset")
def build_model_parameter_dataset_api(
    data: ModelParameterDatasetInput,
):
    return build_model_parameter_pair_dataset(
        research_records=list_research_records(
            study_id=data.study_id,
        ),
        pilot_sessions=store.list_all(),
        study_id=data.study_id,
        left_parameter_code=data.left_parameter_code,
        right_parameter_code=data.right_parameter_code,
        analysis_scope=data.analysis_scope,
        repeated_measure_policy=(
            data.repeated_measure_policy
        ),
        participant_reference=(
            data.participant_reference
        ),
    )

@app.post("/research/model-parameters/check")
def check_model_parameter_analysis(
    data: ParameterAnalysisCheckInput,
):
    dataset = build_model_parameter_pair_dataset(
        research_records=list_research_records(
            study_id=data.study_id,
        ),
        pilot_sessions=store.list_all(),
        study_id=data.study_id,
        left_parameter_code=data.left_parameter_code,
        right_parameter_code=data.right_parameter_code,
        analysis_scope=data.analysis_scope,
        repeated_measure_policy=data.repeated_measure_policy,
        participant_reference=data.participant_reference,
    )

    if not dataset.get("ok"):
        return {
            "ok": False,
            "status": "parameter_dataset_not_ready",
            "dataset_status": dataset.get("status"),
            "dataset": dataset,
        }

    return check_model_parameter_pair_analysis(
        dataset=dataset,
        method_id=data.method_id,
    )


@app.post("/research/analysis/statistical/run")
def run_statistical_analysis(
    data: StatisticalAnalysisRunInput,
):
    answer_records = collect_answer_records_for_study(
        data.study_id,
    )

    check_result = check_pair_analysis(
        study_id=data.study_id,
        left_question_code=data.left_question_code,
        right_question_code=data.right_question_code,
        method_id=data.method_id,
        answer_records=answer_records,
    )

    if check_result.get("status") != "applicable":
        return {
            "ok": False,
            "status": "method_not_applicable",
            "check_result": check_result,
        }

    result = run_statistical_method(
        study_id=data.study_id,
        left_question_code=data.left_question_code,
        right_question_code=data.right_question_code,
        method_id=data.method_id,
        answer_records=answer_records,
    )

    return result

@app.get("/analysis-builder", response_class=HTMLResponse)
def analysis_builder_page():
    return Path("static/analysis_builder.html").read_text(encoding="utf-8")

@app.get("/health-model-research-entities", response_class=HTMLResponse)
def health_model_research_entities_page():
    return Path(
        "static/health_model_research_entities.html"
    ).read_text(
        encoding="utf-8"
    )

@app.get("/question-metadata", response_class=HTMLResponse)
def question_metadata_page():
    return Path(
        "static/question_metadata.html"
    ).read_text(
        encoding="utf-8"
    )
