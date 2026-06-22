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
from pilot_session.export import (
    generate_participant_export,
    generate_research_export,
)

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

        session.answer_revision_count += 1
        session.answer_merge_history.append({
            "type": "initial_answers",
            "answered_keys": list(answers.keys()),
            "answers_count_after_merge": len(session.answers),
            "created_at": datetime.now(UTC).isoformat(),
        })

        session.status = SessionStatus.ANSWERS_RECEIVED
        session.updated_at = datetime.now(UTC)

        self.store.save(session)
        return session

    def submit_followup_answers(
        self,
        session_id: str,
        answers: dict,
    ) -> ParticipantSession:
        session = self.store.get(session_id)

        if session is None:
            raise SessionNotFoundError(
                "Session not found"
            )

        if session.invalidated:
            raise SessionInvalidatedError(
                "Session is invalidated"
            )

        if session.status not in {
            SessionStatus.RUN_COMPLETED,
            SessionStatus.WAITING_FOR_INPUT,
            SessionStatus.PARTIAL_RESULT,
        }:
            raise InvalidStatusTransitionError(
                "Invalid session status transition"
            )

        previous_keys = set(session.answers.keys())

        session.answers.update(answers)

        new_keys = [
            key for key in answers.keys()
            if key not in previous_keys
        ]

        updated_keys = [
            key for key in answers.keys()
            if key in previous_keys
        ]

        session.answer_revision_count += 1
        session.answer_merge_history.append({
            "type": "followup_answers",
            "answered_keys": list(answers.keys()),
            "new_keys": new_keys,
            "updated_keys": updated_keys,
            "answers_count_after_merge": len(session.answers),
            "created_at": datetime.now(UTC).isoformat(),
        })

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

        session.run_count += 1
        session.run_history.append({
            "type": "engine_run",
            "run_number": session.run_count,
            "answers_count": len(session.answers),
            "next_questions_count": len(
                result.get("next_questions", [])
            ),
            "created_at": datetime.now(UTC).isoformat(),
        })

        session.raw_engine_result = result
        session.public_output = result.get(
            "pilot_public_output",
            result.get("output", {}),
        )
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

    def generate_participant_export(self, session_id: str) -> dict:
        session = self.get_session(session_id)

        if not can_generate_export(session):
            raise ExportBlockedError(
                "Participant export generation blocked"
            )

        return generate_participant_export(session)

    def generate_research_export(self, session_id: str) -> dict:
        session = self.get_session(session_id)

        return generate_research_export(session)

    def generate_export(self, session_id: str) -> dict:
        # Backward-compatible alias for participant export.
        # TODO: remove after legacy /export endpoint is deprecated.
        return self.generate_participant_export(session_id)

    def close_session(self, session_id: str) -> ParticipantSession:
        session = self.get_session(session_id)

        if session.invalidated:
            raise SessionInvalidatedError(
                "Session is invalidated"
            )

        if session.status == SessionStatus.CLOSED:
            return session

        if session.status not in {
            SessionStatus.RUN_COMPLETED,
            SessionStatus.EXPORT_READY,
            SessionStatus.EXPORT_BLOCKED,
            SessionStatus.RUN_FAILED,
        }:
            raise InvalidStatusTransitionError(
                "Invalid session status transition"
            )

        session.status = SessionStatus.CLOSED
        session.closed_at = datetime.now(UTC)
        session.updated_at = datetime.now(UTC)

        self.store.save(session)
        return session

    def invalidate_session(
        self,
        session_id: str,
        reason: str,
    ) -> ParticipantSession:
        session = self.get_session(session_id)

        session.status = SessionStatus.INVALIDATED
        session.invalidated = True
        session.invalidation_reason = reason
        session.updated_at = datetime.now(UTC)

        self.store.save(session)
        return session