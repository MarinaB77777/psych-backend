from assessment.questionnaire_components import (
    normalize_question_type_id,
    normalize_response_type_id,
    normalize_scale_type_id,
)


def build_data_types(
    *,
    source_category: str,
    source_definition: dict,
) -> list[str]:
    if source_category == "questionnaire":
        return _build_questionnaire_data_types(
            source_definition
        )

    return []


def _build_questionnaire_data_types(
    source_definition: dict,
) -> list[str]:
    questions = source_definition.get(
        "questions",
        {},
    )

    detected = set()

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

        if answer_type == "text":
            detected.add("text")

        if answer_type == "numeric":
            detected.add("numeric")

        if question_type == "multiple_choice":
            detected.add("categorical")

        if question_type == "single_choice":
            detected.add("categorical")

        if question_type == "binary" or scale == "binary":
            detected.add("boolean")

        if scale in {"ordinal", "likert"}:
            detected.add("ordinal")

        if scale in {
            "interval",
            "ratio",
            "continuous",
            "duration",
            "visual_analog",
        }:
            detected.add("numeric")

    return sorted(detected)
