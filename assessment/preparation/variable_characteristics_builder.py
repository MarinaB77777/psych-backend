from assessment.questionnaire_components import (
    normalize_question_type_id,
    normalize_response_type_id,
    normalize_scale_type_id,
)


def build_variable_characteristics(
    *,
    source_category: str,
    source_definition: dict,
) -> list[str]:
    if source_category == "questionnaire":
        return _build_questionnaire_variable_characteristics(
            source_definition
        )

    return []


def _build_questionnaire_variable_characteristics(
    source_definition: dict,
) -> list[str]:
    questions = source_definition.get(
        "questions",
        {},
    )

    characteristics = set()

    for question in questions.values():

        question_type = normalize_question_type_id(
            question.get("question_type") or question.get("type")
        )

        answer_type = normalize_response_type_id(
            question.get("answer_type")
            or question.get("response_type")
            or question_type
        )

        scale = normalize_scale_type_id(
            question.get("scale_type") or question.get("scale")
        )

        if question_type == "single_choice":
            characteristics.add(
                "single_response"
            )

        if question_type == "multiple_choice":
            characteristics.add(
                "multiple_response"
            )

        if answer_type == "numeric":
            characteristics.add(
                "numeric"
            )

        if scale in {"ordinal", "likert"}:
            characteristics.add(
                "ordered"
            )

        if scale == "nominal":
            characteristics.add(
                "unordered"
            )

        if scale in {
            "interval",
            "ratio",
            "continuous",
            "duration",
            "visual_analog",
        }:
            characteristics.add(
                "numeric"
            )

    return sorted(characteristics)
