from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4
import json
import re
from rc_config import data_path


DATA_FILE = data_path(
    "research_admin",
    "research_studies.json",
    legacy="research/research_studies.json",
)


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def _slugify(value: str) -> str:
    normalized = re.sub(r"[^a-zA-Z0-9]+", "_", value.strip().lower())
    normalized = normalized.strip("_")
    return normalized or "study"


def load_studies() -> list[dict]:
    if not DATA_FILE.exists():
        return []

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_studies(studies: list[dict]) -> None:
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(studies, f, ensure_ascii=False, indent=2)


def _default_studies() -> list[dict]:
    created_at = now_utc()
    return [
        {
            "study_id": "health_model",
            "title": "Health Model",
            "description": "Psychophysical Health Model research dataset and model-parameter analysis.",
            "version": "pilot-v1",
            "author": "research_team",
            "status": "active",
            "active": True,
            "primary_research_question": "How do Health Model parameters behave across pilot records?",
            "secondary_questions": [],
            "variables": [],
            "planned_analyses": [],
            "created_at": created_at,
            "updated_at": created_at,
            "system_defined": True,
        },
        {
            "study_id": "decision_under_uncertainty",
            "title": "Decision Under Uncertainty",
            "description": "Decision-making under uncertainty questionnaire study.",
            "version": "pilot-v1",
            "author": "research_team",
            "status": "active",
            "active": True,
            "primary_research_question": "How do participants describe decision-making under uncertainty?",
            "secondary_questions": [],
            "variables": [],
            "planned_analyses": [],
            "created_at": created_at,
            "updated_at": created_at,
            "system_defined": True,
        },
    ]


def ensure_default_studies() -> list[dict]:
    studies = load_studies()
    existing_ids = {study.get("study_id") for study in studies}
    changed = False

    for study in _default_studies():
        if study["study_id"] not in existing_ids:
            studies.append(study)
            changed = True

    if changed:
        save_studies(studies)

    return studies


def list_research_studies(active: bool | None = None) -> list[dict]:
    studies = ensure_default_studies()

    if active is None:
        return studies

    return [
        study
        for study in studies
        if bool(study.get("active", True)) is active
    ]


def get_research_study(study_id: str) -> dict | None:
    for study in ensure_default_studies():
        if study.get("study_id") == study_id:
            return study

    return None


def create_research_study(
    *,
    title: str,
    description: str = "",
    author: str = "researcher",
    primary_research_question: str = "",
    secondary_questions: list | None = None,
    variables: list | None = None,
    planned_analyses: list | None = None,
    study_id: str | None = None,
    version: str = "draft-v1",
) -> dict:
    studies = ensure_default_studies()
    existing_ids = {study.get("study_id") for study in studies}

    base_id = _slugify(study_id or title)
    candidate_id = base_id

    while candidate_id in existing_ids:
        candidate_id = f"{base_id}_{str(uuid4())[:8]}"

    created_at = now_utc()
    study = {
        "study_id": candidate_id,
        "title": title.strip() or "Untitled study",
        "description": description,
        "version": version,
        "author": author,
        "status": "draft",
        "active": True,
        "primary_research_question": primary_research_question,
        "secondary_questions": secondary_questions or [],
        "variables": variables or [],
        "planned_analyses": planned_analyses or [],
        "created_at": created_at,
        "updated_at": created_at,
        "system_defined": False,
    }

    studies.append(study)
    save_studies(studies)
    return study
