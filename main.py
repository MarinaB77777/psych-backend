from fastapi import FastAPI
from pydantic import BaseModel

from model_engine.run_engine import run_engine_logic

from pilot_session.export import generate_session_export
from pilot_session.service import PilotSessionService
from pilot_session.store import PilotSessionStore

app = FastAPI()


store = PilotSessionStore()
pilot_service = PilotSessionService(store)


class RunInput(BaseModel):
    answers: dict


class SubmitAnswersInput(BaseModel):
    answers: dict


@app.get("/")
def root():
    return {"status": "ok"}


@app.post("/run")
def run_engine(data: RunInput):
    result = run_engine_logic(data.answers)

    return {
        "ok": True,
        "result": result
    }


@app.post("/pilot/sessions")
def create_pilot_session(participant_id: str):
    session = pilot_service.create_session(
        participant_id=participant_id,
    )

    return {
        "ok": True,
        "session_id": session.session_id,
        "status": session.status.value,
    }


@app.post("/pilot/sessions/{session_id}/answers")
def submit_pilot_answers(
    session_id: str,
    data: SubmitAnswersInput,
):
    session = pilot_service.submit_answers(
        session_id=session_id,
        answers=data.answers,
    )

    return {
        "ok": True,
        "status": session.status.value,
    }


@app.post("/pilot/sessions/{session_id}/run")
def run_pilot_session(session_id: str):
    session = pilot_service.run_session(session_id)

    return {
        "ok": True,
        "status": session.status.value,
    }


@app.get("/pilot/sessions/{session_id}/export")
def export_pilot_session(session_id: str):
    session = pilot_service.get_session(session_id)

    export_data = generate_session_export(session)

    return {
        "ok": True,
        "export": export_data,
    }