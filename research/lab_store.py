from datetime import datetime, timezone
from uuid import uuid4
from research.repository import load_objects, save_objects


RESEARCH_OBJECTS = load_objects()


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def create_research_object(
    object_type: str,
    owner: str,
    title: str,
    description: str = "",
    status: str = "draft",
    study_id: str | None = None,
    variables: list | None = None,
    analysis_methods: list | None = None,
    research_question: str | None = None,
    hypothesis_basis: str | None = None,
    basis_notes: str | None = None,
) -> dict:
    record = {
        "id": str(uuid4()),
        "object_type": object_type,
        "owner": owner,
        "status": status,
        "study_id": study_id,
        "title": title,
        "description": description,
        "research_question": research_question,
        "hypothesis_basis": hypothesis_basis,
        "basis_notes": basis_notes,
        "variables": variables or [],
        "analysis_methods": analysis_methods or [],
        "evidence": [],
        "validation": {},
        "created_at": now_utc(),
        "updated_at": now_utc(),
        "approved_by_researcher": owner == "researcher",
    }

    RESEARCH_OBJECTS.append(record)
    save_objects(RESEARCH_OBJECTS)
    return record


def list_research_objects(
    owner: str | None = None,
    object_type: str | None = None,
    study_id: str | None = None,
) -> list[dict]:
    result = RESEARCH_OBJECTS

    if owner:
        result = [item for item in result if item.get("owner") == owner]

    if object_type:
        result = [item for item in result if item.get("object_type") == object_type]

    if study_id:
        result = [item for item in result if item.get("study_id") == study_id]

    return result
