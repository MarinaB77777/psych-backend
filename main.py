from typing import Any
from pilot_session.interview import (
    build_ray_next_question,
    build_ray_chat_response,
    parse_numeric_reply,
)
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from model_engine.run_engine import run_engine_logic

from pilot_session.errors import PilotSessionError
from pilot_session.persistent_store import (
    PilotSessionPersistentStore,
)
from pilot_session.service import PilotSessionService

app = FastAPI()


store = PilotSessionPersistentStore(
    "data/pilot_sessions.json"
)

pilot_service = PilotSessionService(store)


class RayChatInput(BaseModel):
    message: str
    lang: str = "ru"

class RayStartInput(BaseModel):
    participant_id: str = "ray_dialogue_user"
    lang: str = "ru"

class RayStartInput(BaseModel):
    participant_id: str = "ray_dialogue_user"
    lang: str = "ru"

class RunInput(BaseModel):
    answers: dict

class RayAnswerInput(BaseModel):
    variable_code: str
    value: Any

class SubmitAnswersInput(BaseModel):
    answers: dict

class InvalidateSessionInput(BaseModel):
    reason: str

@app.get("/")
def root():
    return {"status": "ok"}

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


@app.post("/pilot/sessions/{session_id}/answers")
def submit_pilot_answers(
    session_id: str,
    data: SubmitAnswersInput,
):
    try:
        session = pilot_service.submit_answers(
            session_id=session_id,
            answers=data.answers,
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

        return {
            "ok": True,
            "status": session.status.value,
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
            ),
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
            ),
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
                    ),
                }

        return {
            "ok": True,
            "ray": build_ray_chat_response(
                session=session,
                message=data.message,
                lang=data.lang,
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