from itertools import combinations

from assessment.analysis.analysis_method_registry import METHODS
from assessment.analysis.variable_metadata import build_variable_metadata


def _scale_pattern_matches(
    method: dict,
    left_scale: str | None,
    right_scale: str | None,
) -> bool:
    if left_scale is None or right_scale is None:
        return False

    for pattern in method.get("scale_patterns", []):
        if (
            left_scale in pattern.get("left", [])
            and right_scale in pattern.get("right", [])
        ):
            return True

    return False


def build_available_dependencies(
    study_id: str,
    answer_records: list[dict],
) -> dict:
    variable_metadata = build_variable_metadata(study_id)

    available_codes = sorted({
        record.get("question_code")
        for record in answer_records
        if record.get("question_code")
    })

    available_variables = []

    for code in available_codes:
        metadata = variable_metadata.get(code, {})

        available_variables.append({
            "question_code": code,
            "title": metadata.get("title"),
            "scale_type": metadata.get("scale_type"),
            "question_type": metadata.get("question_type"),
            "available_records_count": sum(
                1
                for record in answer_records
                if record.get("question_code") == code
            ),
        })

    available_dependencies = []

    for left_code, right_code in combinations(available_codes, 2):
        left_metadata = variable_metadata.get(left_code, {})
        right_metadata = variable_metadata.get(right_code, {})

        left_scale = left_metadata.get("scale_type")
        right_scale = right_metadata.get("scale_type")

        standard_methods = []

        for method in METHODS:
            if method.get("category") != "standard":
                continue

            if _scale_pattern_matches(method, left_scale, right_scale):
                standard_methods.append({
                    **method,
                    "selection_status": "candidate_requires_condition_check",
                    "missing_condition_checks": method.get(
                        "required_conditions",
                        [],
                    ),
            })

        available_dependencies.append({
            "dependency_id": f"{left_code}__{right_code}",
            "left": {
                "question_code": left_code,
                "title": left_metadata.get("title"),
                "scale_type": left_scale,
                "question_type": left_metadata.get("question_type"),
            },
            "right": {
                "question_code": right_code,
                "title": right_metadata.get("title"),
                "scale_type": right_scale,
                "question_type": right_metadata.get("question_type"),
            },
            "available_standard_methods": standard_methods,
            "available_author_methods": [],
            "method_selection_status": (
                "methods_available"
                if standard_methods
                else "no_applicable_methods_from_metadata"
            ),
        })

    return {
        "ok": True,
        "study_id": study_id,
        "available_variables_count": len(available_variables),
        "available_dependencies_count": len(available_dependencies),
        "available_variables": available_variables,
        "available_dependencies": available_dependencies,
    }