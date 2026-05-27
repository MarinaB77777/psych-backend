from datetime import UTC, datetime
from uuid import uuid4

from model_engine.run_engine import run_engine_logic

from pilot_session.errors import (
    ExportBlockedError,
    InvalidStatusTransitionError,
    RunFailedError,
    SessionInvalidatedError,
    SessionNotFoundError,
)
from pilot_session.export import generate_session_export
from pilot_session.schemas import ParticipantSession, SessionStatus
from pilot_session.statuses import can_generate_export
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
            raise SessionNotFoundError(
                "Session not found"
            )

        if session.status != SessionStatus.CREATED:
            raise InvalidStatusTransitionError(
                "Invalid session status transition"
            )

        if session.invalidated:
            raise SessionInvalidatedError(
                "Session is invalidated"
            )

        session.answers = answers
        session.status = SessionStatus.ANSWERS_RECEIVED
        session.updated_at = datetime.now(UTC)

        self.store.save(session)
        return session

    def get_session(self, session_id: str) -> ParticipantSession:
        session = self.store.get(session_id)

        if session is None:
            raise SessionNotFoundError(
                "Session not found"
            )

        return session

    def run_session(self, session_id: str) -> ParticipantSession:
        session = self.store.get(session_id)

        if session is None:
            raise SessionNotFoundError(
                "Session not found"
            )

        if session.invalidated:
            raise SessionInvalidatedError(
                "Session is invalidated"
            )

        if session.status != SessionStatus.ANSWERS_RECEIVED:
            raise InvalidStatusTransitionError(
                "Invalid session status transition"
            )

        try:
            result = run_engine_logic(session.answers)

        except Exception as exc:
            session.status = SessionStatus.RUN_FAILED
            session.updated_at = datetime.now(UTC)

            self.store.save(session)

            raise RunFailedError(
                "Session run failed"
            ) from exc

        session.raw_engine_result = result
        session.public_output = result.get("output", {})
        session.next_question_snapshots = result.get(
            "next_questions",
            [],
        )

        session.acquisition_request_snapshots = result.get(
            "data_acquisition_requests",
            {},
        )

        session.uncertainty_snapshot = result.get(
            "uncertainty",
            {},
        )

        session.status = SessionStatus.RUN_COMPLETED
        session.updated_at = datetime.now(UTC)

        self.store.save(session)
        return session

    def generate_export(self, session_id: str) -> dict:
        session = self.get_session(session_id)

        if not can_generate_export(session):
            raise ExportBlockedError(
                "Export generation blocked"
            )

        return generate_session_export(session)