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


class RunInput(BaseModel):
    answers: dict


class SubmitAnswersInput(BaseModel):
    answers: dict

class InvalidateSessionInput(BaseModel):
    reason: str

@app.get("/")
def root():
    return {"status": "ok"}


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