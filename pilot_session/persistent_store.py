import json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Optional

from pilot_session.schemas import ParticipantSession, SessionStatus


class PilotSessionPersistentStore:
    def __init__(self, storage_path: str):
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self._sessions: dict[str, ParticipantSession] = {}
        self._load()

    def save(self, session: ParticipantSession):
        self._sessions[session.session_id] = session
        self._persist()

    def get(self, session_id: str) -> Optional[ParticipantSession]:
        return self._sessions.get(session_id)

    def exists(self, session_id: str) -> bool:
        return session_id in self._sessions

    def list_all(self) -> list[ParticipantSession]:
        return list(self._sessions.values())

    def _persist(self):
        data = [
            self._serialize_session(session)
            for session in self._sessions.values()
        ]

        self.storage_path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def _load(self):
        if not self.storage_path.exists():
            return

        raw = self.storage_path.read_text(encoding="utf-8").strip()

        if not raw:
            return

        data = json.loads(raw)

        for item in data:
            session = self._deserialize_session(item)
            self._sessions[session.session_id] = session

    def _serialize_session(self, session: ParticipantSession) -> dict:
        data = asdict(session)

        data["status"] = session.status.value
        data["created_at"] = session.created_at.isoformat()
        data["updated_at"] = session.updated_at.isoformat()
        data["closed_at"] = (
            session.closed_at.isoformat()
            if session.closed_at is not None
            else None
        )

        return data

    def _deserialize_session(self, data: dict) -> ParticipantSession:
        return ParticipantSession(
            session_id=data["session_id"],
            participant_id=data["participant_id"],
            status=SessionStatus(data["status"]),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            closed_at=(
                datetime.fromisoformat(data["closed_at"])
                if data.get("closed_at") is not None
                else None
            ),
            answers=data.get("answers", {}),
            engine_version=data.get("engine_version", "mvp-1"),
            engine_snapshot_schema_version=data.get(
                "engine_snapshot_schema_version",
                "mvp-1",
            ),
            public_output_schema_version=data.get(
                "public_output_schema_version",
                "mvp-1",
            ),
            export_schema_version=data.get("export_schema_version", "mvp-1"),
            raw_engine_result=data.get("raw_engine_result", {}),
            public_output=data.get("public_output", {}),
            next_question_snapshots=data.get("next_question_snapshots", []),
            acquisition_request_snapshots=data.get(
                "acquisition_request_snapshots",
                {},
            ),
            uncertainty_snapshot=data.get("uncertainty_snapshot", {}),
            export_generated=data.get("export_generated", False),
            export_policy_version=data.get("export_policy_version", "mvp-1"),
            invalidated=data.get("invalidated", False),
            invalidation_reason=data.get("invalidation_reason"),
        )
