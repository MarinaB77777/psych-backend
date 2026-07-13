from assessment.registry import get_assessment
from question_banks import get_question_bank


def _safe_title(value):
    if isinstance(value, dict):
        return (
            value.get("en")
            or value.get("ru")
            or value.get("es")
            or str(value)
        )

    return value


def resolve_questionnaire_metadata(
    *,
    assessment_id: str,
    lang: str = "en",
) -> dict:
    assessment = get_assessment(
        assessment_id=assessment_id,
        question_bank=get_question_bank(lang),
    )

    if assessment is None or assessment.get("ok") is False:
        return {
            "metadata_status": "not_found",
            "measurement_description": {},
            "instrument": {
                "instrument_type": "questionnaire",
                "instrument_name": assessment_id,
                "instrument_version": None,
                "manufacturer": None,
                "device_id": assessment_id,
                "software_version": None,
            },
        }

    questions = assessment.get("questions", {}) or {}

    measurement_scales = []
    variables = []

    for code, question in questions.items():
        scale = question.get("scale")
        question_type = (
            question.get("question_type")
            or question.get("type")
        )

        if scale and scale not in measurement_scales:
            measurement_scales.append(scale)

        variables.append({
            "code": code,
            "question_type": question_type,
            "answer_type": question.get("answer_type"),
            "scale": scale,
            "score_direction": question.get("score_direction"),
            "domain": question.get("domain"),
            "family": question.get("family"),
            "required": question.get("required", False),
            "active": question.get(
                "active",
                question.get("status") == "active",
            ),
        })

    return {
        "metadata_status": "resolved",
        "instrument": {
            "instrument_type": "questionnaire",
            "instrument_name": _safe_title(
                assessment.get("title", assessment_id)
            ),
            "instrument_version": assessment.get("version"),
            "manufacturer": None,
            "device_id": assessment_id,
            "software_version": None,
        },
        "measurement_description": {
            "data_kind": "questionnaire_answers",
            "data_format": "questionnaire_session",
            "measurement_scales": measurement_scales,
            "units": [],
            "sampling_rate": None,
            "temporal_resolution": None,
            "spatial_resolution": None,
            "variables": variables,
            "question_count": len(questions),
            "item_metadata_available": True,
        },
    }


def resolve_connector_metadata(
    *,
    connector: dict,
    lang: str = "en",
) -> dict:
    connector_type = connector.get("connector_type")

    if connector_type == "questionnaire":
        return resolve_questionnaire_metadata(
            assessment_id=connector.get("connector_id"),
            lang=lang,
        )

    return {
        "metadata_status": "connector_only",
        "instrument": {
            "instrument_type": connector_type,
            "instrument_name": connector.get("title"),
            "instrument_version": None,
            "manufacturer": connector.get("manufacturer"),
            "device_id": (
                connector.get("device_path")
                or connector.get("device_index")
                or connector.get("connector_id")
            ),
            "software_version": None,
        },
        "measurement_description": {
            "data_kind": connector_type,
            "data_format": None,
            "measurement_scales": [],
            "units": [],
            "sampling_rate": None,
            "temporal_resolution": None,
            "spatial_resolution": None,
            "variables": [],
            "question_count": None,
            "item_metadata_available": False,
        },
    }