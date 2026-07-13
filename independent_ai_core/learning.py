from __future__ import annotations

from collections import Counter

from independent_ai_core.contract_compliance import CORE_INVARIANTS
from independent_ai_core.schemas import (
    OfflineLearningEventType,
    OfflineLearningProfile,
    utc_now,
)


def _top_unique_texts(events: list[dict], event_type: str, limit: int = 8) -> list[str]:
    seen = set()
    result = []

    for event in reversed(events):
        if event.get("event_type") != event_type:
            continue

        text = str(event.get("content") or "").strip()

        if not text or text in seen:
            continue

        seen.add(text)
        result.append(text)

        if len(result) >= limit:
            break

    return list(reversed(result))


def build_learning_profile(events: list[dict]) -> dict:
    event_type_counts = Counter()
    tag_counts = Counter()
    language_counts = Counter()

    for event in events:
        event_type_counts[str(event.get("event_type") or "unknown")] += 1
        language_counts[str(event.get("language") or "unknown")] += 1

        for tag in event.get("tags") or []:
            tag_counts[str(tag)] += 1

    profile = OfflineLearningProfile(
        events_count=len(events),
        event_type_counts=dict(event_type_counts),
        tag_counts=dict(tag_counts.most_common(24)),
        language_counts=dict(language_counts),
        preference_notes=_top_unique_texts(
            events,
            OfflineLearningEventType.user_preference.value,
        ),
        boundary_rules=_top_unique_texts(
            events,
            OfflineLearningEventType.boundary_rule.value,
        ),
        contract_invariants=CORE_INVARIANTS,
        updated_at=utc_now(),
    )

    return profile.to_dict()


def build_offline_suggestions(
    *,
    profile: dict,
    context: dict | None = None,
    language: str = "ru",
) -> list[dict]:
    context = context or {}
    events_count = int(profile.get("events_count") or 0)
    event_type_counts = profile.get("event_type_counts") or {}
    tag_counts = profile.get("tag_counts") or {}
    suggestions = []

    labels = {
        "ru": {
            "seed": "Добавить первые обучающие события: предпочтения, границы, коррекции и рабочие паттерны.",
            "boundary": "Зафиксировать рабочие границы: что оффлайн-ядро может запоминать, а что должно игнорировать.",
            "correction": "Добавить коррекции после ручной проверки, чтобы обучение не строилось только на исходных наблюдениях.",
            "pilot": "Держать пилот отдельно от индивидуального ИИ: использовать ядро как локальную память, не как автономный исполнитель.",
            "tag": "Самые частые темы обучения сейчас: ",
        },
        "en": {
            "seed": "Add first learning events: preferences, boundaries, corrections, and workflow patterns.",
            "boundary": "Record working boundaries: what the offline core may remember and what it must ignore.",
            "correction": "Add corrections after manual review so learning is not based only on raw observations.",
            "pilot": "Keep the pilot separate from individual AI: use this core as local memory, not as an autonomous executor.",
            "tag": "Current strongest learning topics: ",
        },
        "es": {
            "seed": "Añadir los primeros eventos de aprendizaje: preferencias, límites, correcciones y patrones de trabajo.",
            "boundary": "Registrar límites de trabajo: qué puede recordar el núcleo offline y qué debe ignorar.",
            "correction": "Añadir correcciones después de revisión manual para que el aprendizaje no dependa solo de observaciones iniciales.",
            "pilot": "Mantener el piloto separado del IA individual: usar este núcleo como memoria local, no como ejecutor autónomo.",
            "tag": "Temas de aprendizaje más fuertes ahora: ",
        },
    }

    text = labels.get(language, labels["ru"])

    if events_count == 0:
        suggestions.append({
            "suggestion_type": "next_step",
            "priority": "high",
            "text": text["seed"],
            "reason": "empty_learning_store",
            "requires_human_review": True,
            "creates_permission": False,
        })

    if not event_type_counts.get("boundary_rule"):
        suggestions.append({
            "suggestion_type": "missing_context",
            "priority": "high",
            "text": text["boundary"],
            "reason": "no_boundary_rules",
            "requires_human_review": True,
            "creates_permission": False,
        })

    if not event_type_counts.get("correction"):
        suggestions.append({
            "suggestion_type": "workflow_hint",
            "priority": "medium",
            "text": text["correction"],
            "reason": "no_corrections_yet",
            "requires_human_review": True,
            "creates_permission": False,
        })

    if context.get("pilot_priority", True):
        suggestions.append({
            "suggestion_type": "consistency_warning",
            "priority": "medium",
            "text": text["pilot"],
            "reason": "pilot_priority_guardrail",
            "requires_human_review": True,
            "creates_permission": False,
        })

    if tag_counts:
        strongest_tags = ", ".join(list(tag_counts.keys())[:5])
        suggestions.append({
            "suggestion_type": "workflow_hint",
            "priority": "low",
            "text": text["tag"] + strongest_tags,
            "reason": "learned_tag_distribution",
            "requires_human_review": True,
            "creates_permission": False,
        })

    return suggestions
