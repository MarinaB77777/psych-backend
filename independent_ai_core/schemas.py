from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

try:
    from enum import StrEnum
except ImportError:
    class StrEnum(str, Enum):
        pass


class OfflineLearningEventType(StrEnum):
    user_preference = "user_preference"
    correction = "correction"
    decision = "decision"
    research_observation = "research_observation"
    workflow_pattern = "workflow_pattern"
    boundary_rule = "boundary_rule"
    language_preference = "language_preference"


class OfflineSuggestionType(StrEnum):
    next_step = "next_step"
    missing_context = "missing_context"
    consistency_warning = "consistency_warning"
    workflow_hint = "workflow_hint"


class OfflineCoreMode(StrEnum):
    offline_learning = "offline_learning"
    review_only = "review_only"


ALLOWED_EVENT_TYPES = {item.value for item in OfflineLearningEventType}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class OfflineLearningEvent:
    event_type: str
    content: str
    source: str = "manual"
    language: str = "ru"
    tags: list[str] = field(default_factory=list)
    importance: int = 1
    metadata: dict[str, Any] = field(default_factory=dict)
    event_id: str = field(default_factory=lambda: str(uuid4()))
    created_at: str = field(default_factory=utc_now)

    def validate(self) -> list[str]:
        errors = []

        if self.event_type not in ALLOWED_EVENT_TYPES:
            errors.append("unsupported_event_type")

        if not self.content.strip():
            errors.append("empty_content")

        if self.importance < 1 or self.importance > 5:
            errors.append("importance_out_of_range")

        if self.language not in {"ru", "en", "es"}:
            errors.append("unsupported_language")

        return errors

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "content": self.content,
            "source": self.source,
            "language": self.language,
            "tags": self.tags,
            "importance": self.importance,
            "metadata": self.metadata,
            "created_at": self.created_at,
        }


@dataclass
class OfflineLearningProfile:
    profile_id: str = "local_independent_ai"
    mode: str = OfflineCoreMode.offline_learning.value
    events_count: int = 0
    event_type_counts: dict[str, int] = field(default_factory=dict)
    tag_counts: dict[str, int] = field(default_factory=dict)
    language_counts: dict[str, int] = field(default_factory=dict)
    preference_notes: list[str] = field(default_factory=list)
    boundary_rules: list[str] = field(default_factory=list)
    contract_invariants: list[str] = field(default_factory=list)
    freshness_policy: str = "requires_review_before_operational_reuse"
    evidence_policy: str = "local_memory_not_research_evidence"
    updated_at: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "profile_id": self.profile_id,
            "mode": self.mode,
            "events_count": self.events_count,
            "event_type_counts": self.event_type_counts,
            "tag_counts": self.tag_counts,
            "language_counts": self.language_counts,
            "preference_notes": self.preference_notes,
            "boundary_rules": self.boundary_rules,
            "contract_invariants": self.contract_invariants,
            "freshness_policy": self.freshness_policy,
            "evidence_policy": self.evidence_policy,
            "updated_at": self.updated_at,
        }
