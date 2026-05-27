from model_engine.run_engine import run_engine_logic
from datetime import datetime, UTC
from uuid import uuid4

from pilot_session.schemas import ParticipantSession, SessionStatus
from pilot_session.store import PilotSessionStore


class PilotSessionService:
    def __init__(self, store: PilotSessionStore):
        self.store = store

    def create_session(self, participant_id: str) -> ParticipantSession:
        session = ParticipantSession(
            session_id=str(uuid4()),
            participant_id=participant_id,
        )

        self.store.save(session)
        return session

    def submit_answers(
        self,
        session_id: str,
        answers: dict,
    ) -> ParticipantSession:
        session = self.store.get(session_id)

        if session is None:
            raise ValueError("SESSION_NOT_FOUND")

        if session.status != SessionStatus.CREATED:
            raise ValueError("INVALID_SESSION_STATUS")

        session.answers = answers
        session.status = SessionStatus.ANSWERS_RECEIVED
        session.updated_at = datetime.now(UTC)

        self.store.save(session)
        return session

    def get_session(self, session_id: str) -> ParticipantSession:
        session = self.store.get(session_id)

        if session is None:
            raise ValueError("SESSION_NOT_FOUND")

        return session

    def run_session(self, session_id: str) -> ParticipantSession:
        session = self.store.get(session_id)

        if session is None:
            raise ValueError("SESSION_NOT_FOUND")

        if session.status != SessionStatus.ANSWERS_RECEIVED:
            raise ValueError("INVALID_SESSION_STATUS")

        try:
            result = run_engine_logic(session.answers)
        except Exception as exc:
            session.status = SessionStatus.RUN_FAILED
            session.updated_at = datetime.now(UTC)
            self.store.save(session)
            raise RuntimeError("SESSION_RUN_FAILED") from exc

        session.raw_engine_result = result
        session.public_output = result.get("output", {})
        session.next_question_snapshots = result.get("next_questions", [])
        session.acquisition_request_snapshots = result.get(
            "data_acquisition_requests",
            {},
        )
        session.uncertainty_snapshot = result.get("uncertainty", {})
        session.status = SessionStatus.RUN_COMPLETED
        session.updated_at = datetime.now(UTC)

        self.store.save(session)
        return session
