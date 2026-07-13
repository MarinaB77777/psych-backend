from assessment.registry import get_assessment
from question_banks import get_question_bank


def _title(value, fallback):
    if isinstance(value, dict):
        return value.get("en") or value.get("ru") or value.get("es") or fallback
    return value or fallback


def resolve(connector: dict, context: dict | None = None) -> dict:
    context = context or {}
    lang = context.get("lang", "en")
    assessment_id = connector.get("connector_id")

    assessment = get_assessment(
        assessment_id=assessment_id,
        question_bank=get_question_bank(lang),
    )

    if assessment is None or assessment.get("ok") is False:
        return {
            "metadata_status": "not_found",
            "instrument": {
                "instrument_type": "questionnaire",
                "instrument_name": assessment_id,
                "instrument_version": None,
                "manufacturer": None,
                "device_id": assessment_id,
                "software_version": None,
            },
            "measurement_description": {
                "data_kind": "questionnaire_answers",
                "data_format": None,
                "measurement_scales": [],
                "units": [],
                "variables": [],
                "question_count": None,
                "item_metadata_available": False,
            },
        }

    questions = assessment.get("questions", {}) or {}
    variables = []

    for code, question in questions.items():
        variables.append({
            "code": code,
            "question_type": question.get("question_type") or question.get("type"),
            "answer_type": question.get("answer_type"),
            "scale": question.get("scale"),
            "score_direction": question.get("score_direction"),
            "domain": question.get("domain"),
            "family": question.get("family"),
            "required": question.get("required", False),
            "active": question.get("active", question.get("status") == "active"),
        })

    return {
        "metadata_status": "resolved",
        "metadata_source": "questionnaire_registry",
        "instrument": {
            "instrument_type": "questionnaire",
            "instrument_name": _title(assessment.get("title"), assessment_id),
            "instrument_version": assessment.get("version"),
            "manufacturer": None,
            "device_id": assessment_id,
            "software_version": None,
        },
        "measurement_description": {
            "data_kind": "questionnaire_answers",
            "data_format": "questionnaire_session",
            "measurement_scales": sorted({
                str(v.get("scale")) for v in variables if v.get("scale")
            }),
            "units": [],
            "sampling_rate": None,
            "temporal_resolution": None,
            "spatial_resolution": None,
            "variables": variables,
            "question_count": len(questions),
            "item_metadata_available": True,
        },
    }