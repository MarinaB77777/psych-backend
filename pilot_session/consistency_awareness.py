from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
import hashlib
import json
from uuid import uuid4
from typing import Any

from pilot_session.schemas import ParticipantSession


SUPPORTED_LANGUAGES = ("ru", "en", "es")


@dataclass(frozen=True)
class ConsistencyObservation:
    observation_id: str
    observation_key: str
    participant_id: str
    current_session_id: str
    compared_session_id: str | None
    current_answer_ref: dict
    compared_answer_ref: dict | None
    domain: str | None
    discrepancy_type: str
    temporal_scope: dict
    source_types: list[str]
    severity: str
    possible_explanations: list[str]
    requires_clarification: bool
    uncertainty_notes: list[str]
    created_at: str


@dataclass(frozen=True)
class ClarificationProposal:
    proposal_id: str
    observation_id: str
    localized_question: dict[str, str]
    answer_options: list[dict[str, Any]] | None
    reason: dict[str, str]
    does_not_assume_deception: bool
    created_at: str


@dataclass(frozen=True)
class RayColleagueResponse:
    status: str
    message: str
    blocks: dict[str, str]
    confidence: str
    requires_clarification: bool
    suggested_next_research_step: str | None = None
    recommendation_allowed: bool = False
    forecast_allowed: bool = False
    interpretation: None = None
    debug: None = None


def _now() -> str:
    return datetime.now(UTC).isoformat()


def _lang(lang: str) -> str:
    return lang if lang in SUPPORTED_LANGUAGES else "ru"


def _value(record: dict) -> Any:
    return record.get("answer_value")


def _answer_ref(record: dict) -> dict:
    return {
        "session_id": record.get("session_id"),
        "question_code": record.get("question_code"),
        "question_id": record.get("question_id"),
        "question_uuid": record.get("question_uuid"),
        "question_version": record.get("question_version"),
        "answer_value": record.get("answer_value"),
        "answer_revision": record.get("answer_revision"),
        "source_mode": record.get("source_mode"),
        "source_type": record.get("source_type") or record.get("source_mode") or "self_report",
        "created_at": record.get("created_at"),
    }


def _public_answer_ref(record: dict | None) -> dict | None:
    if not record:
        return None
    return {
        "session_id": record.get("session_id"),
        "question_code": record.get("question_code"),
        "answer_value": record.get("answer_value"),
        "answer_revision": record.get("answer_revision"),
        "source_type": _source_type(record),
        "created_at": record.get("created_at"),
    }


def _question_key(record: dict) -> str | None:
    return (
        record.get("question_uuid")
        or record.get("question_id")
        or record.get("question_code")
    )


def _identity(record: dict) -> dict:
    identity = record.get("domain_data_identity")
    return identity if isinstance(identity, dict) else {}


def _temporal_scope(record: dict | None) -> dict:
    if not record:
        return {}
    identity = _identity(record)
    return {
        "temporal_scope": identity.get("temporal_scope"),
        "measurement_time": identity.get("measurement_time") or record.get("created_at"),
        "context": identity.get("context"),
        "unit": identity.get("unit"),
        "language": identity.get("language"),
        "question_version": record.get("question_version") or identity.get("question_version"),
    }


def _has_context(record: dict) -> bool:
    identity = _identity(record)
    return bool(identity.get("context") or identity.get("temporal_scope"))


def _source_type(record: dict | None) -> str:
    if not record:
        return "unknown"
    return record.get("source_type") or record.get("source_mode") or "self_report"


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _values_differ(left: Any, right: Any) -> bool:
    return left != right


def _compatible_question(left: dict, right: dict) -> tuple[bool, str | None]:
    left_uuid = left.get("question_uuid") or left.get("question_id")
    right_uuid = right.get("question_uuid") or right.get("question_id")
    if left_uuid and right_uuid and left_uuid != right_uuid:
        return False, "question_identity_mismatch"

    left_version = left.get("question_version") or _identity(left).get("question_version")
    right_version = right.get("question_version") or _identity(right).get("question_version")
    if left_version and right_version and left_version != right_version:
        return False, "question_version_mismatch"

    left_unit = _identity(left).get("unit")
    right_unit = _identity(right).get("unit")
    if left_unit and right_unit and left_unit != right_unit:
        return False, "unit_mismatch"

    return True, None


def _possible_explanations(discrepancy_type: str) -> list[str]:
    common = [
        "situation_changed",
        "different_time_period",
        "different_question_understanding",
        "data_entry_or_mapping_issue",
    ]
    if discrepancy_type == "sensor_self_report_disagreement":
        return [
            "sensor_context_mismatch",
            "sensor_calibration_or_availability_issue",
            "different_time_period",
            "self_report_and_sensor_capture_different_aspects",
        ]
    if discrepancy_type == "missing_context":
        return [
            "context_not_recorded",
            "temporal_scope_not_recorded",
            "comparison_not_safe_until_context_is_known",
        ]
    if discrepancy_type == "comparison_blocked":
        return [
            "question_or_unit_not_comparable",
            "comparison_requires_version_mapping",
        ]
    return common


def _observation_key(
    *,
    current_session_id: str,
    compared_session_id: str | None,
    current_record: dict,
    compared_record: dict | None,
    discrepancy_type: str,
) -> str:
    payload = {
        "current_session_id": current_session_id,
        "compared_session_id": compared_session_id,
        "question_key": _question_key(current_record),
        "current_revision": current_record.get("answer_revision"),
        "compared_revision": (
            compared_record.get("answer_revision")
            if compared_record
            else None
        ),
        "current_created_at": current_record.get("created_at"),
        "compared_created_at": (
            compared_record.get("created_at")
            if compared_record
            else None
        ),
        "discrepancy_type": discrepancy_type,
    }
    canonical = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        default=str,
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:20]


def _observation(
    *,
    participant_id: str,
    current_session_id: str,
    compared_session_id: str | None,
    current_record: dict,
    compared_record: dict | None,
    discrepancy_type: str,
    severity: str,
    requires_clarification: bool,
    uncertainty_notes: list[str] | None = None,
) -> ConsistencyObservation:
    return ConsistencyObservation(
        observation_id=str(uuid4()),
        observation_key=_observation_key(
            current_session_id=current_session_id,
            compared_session_id=compared_session_id,
            current_record=current_record,
            compared_record=compared_record,
            discrepancy_type=discrepancy_type,
        ),
        participant_id=participant_id,
        current_session_id=current_session_id,
        compared_session_id=compared_session_id,
        current_answer_ref=_answer_ref(current_record),
        compared_answer_ref=_answer_ref(compared_record) if compared_record else None,
        domain=current_record.get("question_domain") or _identity(current_record).get("domain_id"),
        discrepancy_type=discrepancy_type,
        temporal_scope={
            "current": _temporal_scope(current_record),
            "compared": _temporal_scope(compared_record),
        },
        source_types=list(dict.fromkeys([
            _source_type(current_record),
            _source_type(compared_record),
        ])),
        severity=severity,
        possible_explanations=_possible_explanations(discrepancy_type),
        requires_clarification=requires_clarification,
        uncertainty_notes=uncertainty_notes or [],
        created_at=_now(),
    )


def _records_by_question(session: ParticipantSession) -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = {}
    for record in session.research_answer_records or []:
        key = _question_key(record)
        if not key:
            continue
        grouped.setdefault(key, []).append(record)
    return grouped


def _latest_record_by_question(session: ParticipantSession) -> dict[str, dict]:
    latest = {}
    for key, records in _records_by_question(session).items():
        latest[key] = sorted(
            records,
            key=lambda item: (item.get("created_at") or "", item.get("answer_revision") or 0),
        )[-1]
    return latest


def _same_session_observations(session: ParticipantSession) -> list[ConsistencyObservation]:
    observations = []
    for records in _records_by_question(session).values():
        ordered = sorted(
            records,
            key=lambda item: (item.get("created_at") or "", item.get("answer_revision") or 0),
        )
        if len(ordered) < 2:
            continue
        previous = ordered[-2]
        current = ordered[-1]
        if not _values_differ(_value(previous), _value(current)):
            continue
        compatible, reason = _compatible_question(current, previous)
        if not compatible:
            observations.append(_observation(
                participant_id=session.participant_id,
                current_session_id=session.session_id,
                compared_session_id=session.session_id,
                current_record=current,
                compared_record=previous,
                discrepancy_type="comparison_blocked",
                severity="not_comparable",
                requires_clarification=False,
                uncertainty_notes=[reason or "not_comparable"],
            ))
            continue
        observations.append(_observation(
            participant_id=session.participant_id,
            current_session_id=session.session_id,
            compared_session_id=session.session_id,
            current_record=current,
            compared_record=previous,
            discrepancy_type="same_session_answer_difference",
            severity="data_quality_clarification",
            requires_clarification=True,
            uncertainty_notes=["same_session_answer_changed"],
        ))
    return observations


def _previous_session_observations(
    session: ParticipantSession,
    previous_sessions: list[ParticipantSession],
) -> list[ConsistencyObservation]:
    observations = []
    current_by_key = _latest_record_by_question(session)
    comparable_previous = [
        item for item in previous_sessions
        if item.participant_id == session.participant_id
        and item.session_id != session.session_id
    ]
    comparable_previous = sorted(comparable_previous, key=lambda item: item.created_at)

    for previous_session in comparable_previous:
        previous_by_key = _latest_record_by_question(previous_session)
        for key, current in current_by_key.items():
            previous = previous_by_key.get(key)
            if not previous:
                continue
            if not _values_differ(_value(current), _value(previous)):
                continue

            compatible, reason = _compatible_question(current, previous)
            if not compatible:
                observations.append(_observation(
                    participant_id=session.participant_id,
                    current_session_id=session.session_id,
                    compared_session_id=previous_session.session_id,
                    current_record=current,
                    compared_record=previous,
                    discrepancy_type="comparison_blocked",
                    severity="not_comparable",
                    requires_clarification=False,
                    uncertainty_notes=[reason or "not_comparable"],
                ))
                continue

            current_scope = _identity(current).get("temporal_scope")
            previous_scope = _identity(previous).get("temporal_scope")
            if current_scope and previous_scope and current_scope != previous_scope:
                observations.append(_observation(
                    participant_id=session.participant_id,
                    current_session_id=session.session_id,
                    compared_session_id=previous_session.session_id,
                    current_record=current,
                    compared_record=previous,
                    discrepancy_type="temporal_scope_difference",
                    severity="context_clarification",
                    requires_clarification=True,
                    uncertainty_notes=["answers_refer_to_different_time_periods"],
                ))
                continue

            if not _has_context(current) or not _has_context(previous):
                observations.append(_observation(
                    participant_id=session.participant_id,
                    current_session_id=session.session_id,
                    compared_session_id=previous_session.session_id,
                    current_record=current,
                    compared_record=previous,
                    discrepancy_type="missing_context",
                    severity="not_enough_data",
                    requires_clarification=True,
                    uncertainty_notes=["context_or_temporal_scope_missing"],
                ))
                continue

            discrepancy_type = "between_session_change"
            if _is_number(_value(current)) != _is_number(_value(previous)):
                discrepancy_type = "numeric_categorical_difference"

            observations.append(_observation(
                participant_id=session.participant_id,
                current_session_id=session.session_id,
                compared_session_id=previous_session.session_id,
                current_record=current,
                compared_record=previous,
                discrepancy_type=discrepancy_type,
                severity="trajectory_candidate",
                requires_clarification=True,
                uncertainty_notes=["change_between_sessions_is_not_error"],
            ))
    return observations


def _sensor_observations(
    session: ParticipantSession,
    sensor_context_observations: list[dict] | None,
) -> list[ConsistencyObservation]:
    observations = []
    if not sensor_context_observations:
        return observations
    current_by_key = _latest_record_by_question(session)
    for sensor_record in sensor_context_observations:
        key = _question_key(sensor_record)
        if not key:
            key = sensor_record.get("question_code")
        current = current_by_key.get(key)
        if not current or not _values_differ(_value(current), _value(sensor_record)):
            continue
        observations.append(_observation(
            participant_id=session.participant_id,
            current_session_id=session.session_id,
            compared_session_id=None,
            current_record=current,
            compared_record={
                **sensor_record,
                "session_id": sensor_record.get("session_id") or session.session_id,
                "source_type": sensor_record.get("source_type") or "sensor_context",
            },
            discrepancy_type="sensor_self_report_disagreement",
            severity="data_quality_clarification",
            requires_clarification=True,
            uncertainty_notes=["sensor_is_not_truth_authority"],
        ))
    return observations


def build_consistency_observations(
    session: ParticipantSession,
    *,
    previous_sessions: list[ParticipantSession] | None = None,
    sensor_context_observations: list[dict] | None = None,
) -> list[ConsistencyObservation]:
    previous_sessions = previous_sessions or []
    observations = []
    observations.extend(_same_session_observations(session))
    observations.extend(_previous_session_observations(session, previous_sessions))
    observations.extend(_sensor_observations(session, sensor_context_observations))
    return observations


_QUESTIONS = {
    "same_session_answer_difference": {
        "ru": "Я заметил, что этот ответ отличается от более раннего ответа в этой же сессии. Это может быть связано с изменением ситуации, периодом времени или пониманием вопроса. Уточним, какой вариант сейчас описывает ситуацию лучше?",
        "en": "I noticed that this answer differs from an earlier answer in this same session. This may be due to a change in situation, time period, or question interpretation. Could we clarify which version best describes the situation now?",
        "es": "Noté que esta respuesta difiere de una respuesta anterior en esta misma sesión. Puede deberse a un cambio de situación, periodo de tiempo o interpretación de la pregunta. ¿Podemos aclarar qué versión describe mejor la situación ahora?",
    },
    "between_session_change": {
        "ru": "Я заметил отличие от предыдущей сессии. Это может быть изменением ситуации, а не ошибкой. Уточним, относится ли текущий ответ к тому же периоду и контексту?",
        "en": "I noticed a difference from a previous session. This may reflect a changed situation, not an error. Could we clarify whether the current answer refers to the same period and context?",
        "es": "Noté una diferencia respecto a una sesión anterior. Puede reflejar un cambio de situación, no un error. ¿Podemos aclarar si la respuesta actual se refiere al mismo periodo y contexto?",
    },
    "temporal_scope_difference": {
        "ru": "Похоже, ответы могут относиться к разным временным периодам. Я не буду сравнивать их как прямое противоречие. Уточним период текущего ответа?",
        "en": "These answers may refer to different time periods. I will not compare them as a direct contradiction. Could we clarify the period for the current answer?",
        "es": "Estas respuestas pueden referirse a periodos distintos. No las compararé como una contradicción directa. ¿Podemos aclarar el periodo de la respuesta actual?",
    },
    "sensor_self_report_disagreement": {
        "ru": "Самоотчёт и доступное наблюдение расходятся. Датчик не является источником истины: возможны разные периоды, контекст или качество измерения. Уточним условия?",
        "en": "The self-report and available observation differ. The sensor is not a truth source: time period, context, or measurement quality may differ. Could we clarify the conditions?",
        "es": "El autoinforme y la observación disponible difieren. El sensor no es fuente de verdad: pueden diferir el periodo, el contexto o la calidad de medición. ¿Podemos aclarar las condiciones?",
    },
    "numeric_categorical_difference": {
        "ru": "Числовой ответ и категориальное описание не совпадают напрямую. Возможно, они отражают разные шкалы. Уточним, как их сопоставлять?",
        "en": "The numeric answer and categorical description do not directly align. They may reflect different scales. Could we clarify how to compare them?",
        "es": "La respuesta numérica y la descripción categórica no coinciden directamente. Pueden reflejar escalas distintas. ¿Podemos aclarar cómo compararlas?",
    },
    "missing_context": {
        "ru": "Для безопасного сравнения не хватает контекста или временного периода. Уточним, к какой ситуации и периоду относится текущий ответ?",
        "en": "There is not enough context or time-scope information for a safe comparison. Could we clarify which situation and period the current answer refers to?",
        "es": "No hay suficiente contexto o periodo temporal para una comparación segura. ¿Podemos aclarar a qué situación y periodo se refiere la respuesta actual?",
    },
    "comparison_blocked": {
        "ru": "Эти ответы нельзя безопасно сравнить: вопрос, версия или единицы измерения могут различаться. Лучше сначала проверить совместимость данных.",
        "en": "These answers cannot be safely compared: the question, version, or units may differ. It is better to check data compatibility first.",
        "es": "Estas respuestas no se pueden comparar con seguridad: la pregunta, versión o unidades pueden diferir. Es mejor verificar primero la compatibilidad de los datos.",
    },
}

_ANSWER_OPTIONS = [
    {
        "value": "situation_changed",
        "text": {
            "ru": "Ситуация изменилась",
            "en": "The situation changed",
            "es": "La situación cambió",
        },
    },
    {
        "value": "different_period",
        "text": {
            "ru": "Я имел(а) в виду другой период",
            "en": "I meant a different period",
            "es": "Me refería a otro periodo",
        },
    },
    {
        "value": "different_understanding",
        "text": {
            "ru": "Я понял(а) вопрос иначе",
            "en": "I understood the question differently",
            "es": "Entendí la pregunta de otra manera",
        },
    },
    {
        "value": "previous_inaccurate",
        "text": {
            "ru": "Предыдущий ответ был неточным",
            "en": "The previous answer was not precise",
            "es": "La respuesta anterior no fue precisa",
        },
    },
    {
        "value": "both_true",
        "text": {
            "ru": "Оба ответа верны в разных условиях",
            "en": "Both answers are true in different conditions",
            "es": "Ambas respuestas son válidas en condiciones distintas",
        },
    },
    {
        "value": "prefer_not_to_clarify",
        "text": {
            "ru": "Не хочу уточнять",
            "en": "I prefer not to clarify",
            "es": "Prefiero no aclararlo",
        },
    },
]

_TYPE_LABELS = {
    "same_session_answer_difference": {
        "ru": "Расхождение внутри одной сессии",
        "en": "Within-session difference",
        "es": "Diferencia dentro de la sesión",
    },
    "between_session_change": {
        "ru": "Изменение между сессиями",
        "en": "Cross-session change",
        "es": "Cambio entre sesiones",
    },
    "temporal_scope_difference": {
        "ru": "Разный временной период",
        "en": "Different time scope",
        "es": "Periodo temporal distinto",
    },
    "sensor_self_report_disagreement": {
        "ru": "Самоотчёт и наблюдение различаются",
        "en": "Self-report and observation differ",
        "es": "Autoinforme y observación difieren",
    },
    "numeric_categorical_difference": {
        "ru": "Разные типы шкал",
        "en": "Different scale types",
        "es": "Tipos de escala distintos",
    },
    "missing_context": {
        "ru": "Не хватает контекста",
        "en": "Missing context",
        "es": "Falta contexto",
    },
    "comparison_blocked": {
        "ru": "Сравнение заблокировано",
        "en": "Comparison blocked",
        "es": "Comparación bloqueada",
    },
}


def build_clarification_proposal(
    observation: ConsistencyObservation,
    *,
    lang: str = "ru",
) -> ClarificationProposal:
    localized_question = _QUESTIONS.get(
        observation.discrepancy_type,
        _QUESTIONS["missing_context"],
    )
    reason = {
        "ru": "Это уточнение нужно только для качества данных. Оно не предполагает ошибку или обман.",
        "en": "This clarification is only for data quality. It does not assume error or deception.",
        "es": "Esta aclaración es solo para calidad de datos. No supone error ni engaño.",
    }
    return ClarificationProposal(
        proposal_id=str(uuid4()),
        observation_id=observation.observation_id,
        localized_question=localized_question,
        answer_options=_ANSWER_OPTIONS,
        reason=reason,
        does_not_assume_deception=True,
        created_at=_now(),
    )


def _blocks(observation: ConsistencyObservation, proposal: ClarificationProposal, lang: str) -> dict[str, str]:
    lang = _lang(lang)
    templates = {
        "ru": {
            "known": "Есть два сохранённых ответа или наблюдения, которые не совпадают напрямую.",
            "uncertain": "Пока нельзя выбрать одну интерпретацию как верную.",
            "needs": proposal.localized_question[lang],
            "possible": "Возможные объяснения: изменилась ситуация, отличается период времени, контекст или понимание вопроса.",
            "step": "Шаг проверки: уточнить период, контекст и совместимость вопроса перед научной интерпретацией.",
        },
        "en": {
            "known": "There are two saved answers or observations that do not directly align.",
            "uncertain": "The available data are not enough to choose one interpretation as true.",
            "needs": proposal.localized_question[lang],
            "possible": "Possible explanations include a changed situation, different time period, context, or question interpretation.",
            "step": "Suggested validation step: clarify period, context, and question compatibility before scientific interpretation.",
        },
        "es": {
            "known": "Hay dos respuestas u observaciones guardadas que no coinciden directamente.",
            "uncertain": "Los datos disponibles no bastan para elegir una interpretación como verdadera.",
            "needs": proposal.localized_question[lang],
            "possible": "Las explicaciones posibles incluyen cambio de situación, periodo distinto, contexto o interpretación de la pregunta.",
            "step": "Paso de validación: aclarar periodo, contexto y compatibilidad de la pregunta antes de la interpretación científica.",
        },
    }
    return templates[lang]


def build_ray_colleague_response(
    observation: ConsistencyObservation,
    *,
    lang: str = "ru",
) -> RayColleagueResponse:
    lang = _lang(lang)
    proposal = build_clarification_proposal(observation, lang=lang)
    blocks = _blocks(observation, proposal, lang)
    labels = {
        "ru": {
            "known": "Что известно",
            "uncertain": "Что остаётся неопределённым",
            "needs": "Что нужно уточнить",
            "possible": "Возможное объяснение",
            "step": "Исследовательская гипотеза / шаг проверки",
        },
        "en": {
            "known": "What is known",
            "uncertain": "What is uncertain",
            "needs": "What needs clarification",
            "possible": "Possible explanation",
            "step": "Research hypothesis / Suggested validation step",
        },
        "es": {
            "known": "Lo que se sabe",
            "uncertain": "Lo que sigue siendo incierto",
            "needs": "Lo que necesita aclaración",
            "possible": "Posible explicación",
            "step": "Hipótesis de investigación / paso de validación",
        },
    }[lang]
    message = "\n\n".join(
        f"{labels[key]}: {blocks[key]}"
        for key in ("known", "uncertain", "needs", "possible", "step")
    )
    return RayColleagueResponse(
        status="clarification",
        message=message,
        blocks=blocks,
        confidence="bounded_low" if observation.requires_clarification else "bounded_medium",
        requires_clarification=observation.requires_clarification,
        suggested_next_research_step=blocks["step"],
        recommendation_allowed=False,
        forecast_allowed=False,
        interpretation=None,
        debug=None,
    )


def response_to_participant_dict(response: RayColleagueResponse) -> dict:
    data = asdict(response)
    data.pop("debug", None)
    return data


def localized_answer_options(lang: str = "ru") -> list[dict[str, str]]:
    lang = _lang(lang)
    return [
        {
            "value": option["value"],
            "text": option["text"][lang],
        }
        for option in _ANSWER_OPTIONS
    ]


def build_participant_clarification_payload(
    observation: ConsistencyObservation,
    *,
    lang: str = "ru",
) -> dict:
    lang = _lang(lang)
    response = response_to_participant_dict(
        build_ray_colleague_response(observation, lang=lang)
    )
    response["answer_options"] = localized_answer_options(lang)
    response["display_type"] = _TYPE_LABELS.get(
        observation.discrepancy_type,
        _TYPE_LABELS["missing_context"],
    )[lang]
    return response


def _clarification_by_key(session: ParticipantSession) -> dict[str, dict]:
    return {
        item.get("observation_key"): item
        for item in (session.consistency_clarifications or [])
        if item.get("observation_key")
    }


def build_researcher_consistency_summary(
    session: ParticipantSession,
    *,
    previous_sessions: list[ParticipantSession] | None = None,
    sensor_context_observations: list[dict] | None = None,
    lang: str = "ru",
) -> list[dict]:
    lang = _lang(lang)
    clarifications = _clarification_by_key(session)
    summaries = []

    for observation in build_consistency_observations(
        session,
        previous_sessions=previous_sessions,
        sensor_context_observations=sensor_context_observations,
    ):
        stored = clarifications.get(observation.observation_key)
        if observation.discrepancy_type == "comparison_blocked":
            status = "comparison_blocked"
        elif stored:
            status = "clarified" if stored.get("selected_option") != "prefer_not_to_clarify" else "unresolved"
        elif observation.requires_clarification:
            status = "clarification_requested"
        else:
            status = "detected"

        summaries.append({
            "observation_key": observation.observation_key,
            "detected_at": observation.created_at,
            "session_id": observation.current_session_id,
            "compared_session_id": observation.compared_session_id,
            "question_code": observation.current_answer_ref.get("question_code"),
            "display_type": _TYPE_LABELS.get(
                observation.discrepancy_type,
                _TYPE_LABELS["missing_context"],
            )[lang],
            "discrepancy_type": observation.discrepancy_type,
            "status": status,
            "temporal_context": observation.temporal_scope,
            "source_types": observation.source_types,
            "current_answer": _public_answer_ref(observation.current_answer_ref),
            "compared_answer": _public_answer_ref(observation.compared_answer_ref),
            "participant_clarification": stored,
            "uncertainty_note": "; ".join(observation.uncertainty_notes),
            "readiness_impact": (
                "requires_context_before_interpretation"
                if observation.requires_clarification
                else "not_comparable"
            ),
            "trajectory_candidate": (
                observation.compared_session_id is not None
                and observation.compared_session_id != observation.current_session_id
                and observation.discrepancy_type != "comparison_blocked"
            ),
            "no_automatic_diagnosis_or_penalty": True,
        })

    return summaries


def build_first_ray_colleague_clarification(
    session: ParticipantSession,
    *,
    previous_sessions: list[ParticipantSession] | None = None,
    sensor_context_observations: list[dict] | None = None,
    lang: str = "ru",
) -> dict | None:
    observations = build_consistency_observations(
        session,
        previous_sessions=previous_sessions,
        sensor_context_observations=sensor_context_observations,
    )
    clarified_keys = {
        item.get("observation_key")
        for item in (session.consistency_clarifications or [])
        if item.get("status") == "clarified"
    }
    actionable = [
        item for item in observations
        if item.requires_clarification
        and item.discrepancy_type != "comparison_blocked"
        and item.observation_key not in clarified_keys
    ]
    if not actionable:
        return None
    return build_participant_clarification_payload(actionable[0], lang=lang)
