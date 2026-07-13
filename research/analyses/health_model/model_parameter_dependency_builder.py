from itertools import combinations
from typing import Any

from assessment.analysis.analysis_method_registry import METHODS
from research.analyses.health_model.model_parameter_catalog import (
    collect_health_model_parameter_records,
)


MODEL_PARAMETER_DEPENDENCY_SCHEMA_VERSION = (
    "health-model-parameter-dependency-catalog-1"
)


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


def _single_or_mixed(
    values: set,
) -> str | None:
    clean = {
        value
        for value in values
        if value is not None and value != ""
    }

    if not clean:
        return None

    if len(clean) == 1:
        return next(iter(clean))

    return "mixed"


def _build_variable_catalog(
    parameter_records: list[dict],
) -> dict[str, dict]:
    grouped = {}

    for record in parameter_records:
        parameter_code = record.get("parameter_code")

        if not parameter_code:
            continue

        grouped.setdefault(
            parameter_code,
            {
                "parameter_code": parameter_code,
                "scale_types": set(),
                "value_types": set(),
                "session_ids": set(),
                "record_count": 0,
            },
        )

        group = grouped[parameter_code]

        group["record_count"] += 1
        group["scale_types"].add(
            record.get("scale_type")
        )
        group["value_types"].add(
            record.get("parameter_value_type")
        )

        session_id = record.get("session_id")

        if session_id:
            group["session_ids"].add(session_id)

    variables = {}

    for parameter_code, group in grouped.items():
        variables[parameter_code] = {
            "variable_source": (
                "calculated_model_parameter"
            ),
            "variable_code": parameter_code,
            "parameter_code": parameter_code,
            "title": parameter_code,
            "scale_type": _single_or_mixed(
                group["scale_types"]
            ),
            "parameter_value_type": _single_or_mixed(
                group["value_types"]
            ),
            "available_records_count": group[
                "record_count"
            ],
            "available_session_count": len(
                group["session_ids"]
            ),
        }

    return variables


def _paired_session_count(
    parameter_records: list[dict],
    left_parameter_code: str,
    right_parameter_code: str,
) -> int:
    left_sessions = {
        record.get("session_id")
        for record in parameter_records
        if (
            record.get("parameter_code")
            == left_parameter_code
            and record.get("session_id")
        )
    }

    right_sessions = {
        record.get("session_id")
        for record in parameter_records
        if (
            record.get("parameter_code")
            == right_parameter_code
            and record.get("session_id")
        )
    }

    return len(left_sessions & right_sessions)


def build_available_model_parameter_dependencies(
    *,
    research_records: list[dict],
    pilot_sessions: list[Any],
    study_id: str = "health_model",
) -> dict:
    parameter_records = (
        collect_health_model_parameter_records(
            research_records=research_records,
            pilot_sessions=pilot_sessions,
            study_id=study_id,
        )
    )

    variables_by_code = _build_variable_catalog(
        parameter_records
    )

    available_codes = sorted(
        variables_by_code.keys()
    )

    available_variables = [
        variables_by_code[code]
        for code in available_codes
    ]

    available_dependencies = []

    for left_code, right_code in combinations(
        available_codes,
        2,
    ):
        left_variable = variables_by_code[left_code]
        right_variable = variables_by_code[right_code]

        left_scale = left_variable.get("scale_type")
        right_scale = right_variable.get("scale_type")

        standard_methods = []

        for method in METHODS:
            if method.get("category") != "standard":
                continue

            if not _scale_pattern_matches(
                method,
                left_scale,
                right_scale,
            ):
                continue

            standard_methods.append({
                "method_id": method.get("method_id"),
                "title": method.get("title"),
                "purpose": method.get("purpose"),
                "selection_status": (
                    "candidate_requires_condition_check"
                ),
                "missing_condition_checks": method.get(
                    "required_conditions",
                    [],
                ),
            })

        paired_session_count = _paired_session_count(
            parameter_records=parameter_records,
            left_parameter_code=left_code,
            right_parameter_code=right_code,
        )

        available_dependencies.append({
            "dependency_id": (
                f"model_parameter:{left_code}"
                f"__model_parameter:{right_code}"
            ),
            "variable_source": (
                "calculated_model_parameter"
            ),
            "pairing_unit": "session_id",
            "left": left_variable,
            "right": right_variable,
            "paired_session_count": (
                paired_session_count
            ),
            "available_standard_methods": (
                standard_methods
            ),
            "available_author_methods": [],
            "method_selection_status": (
                "methods_available"
                if standard_methods
                else (
                    "no_applicable_methods_from_metadata"
                )
            ),
        })

    return {
        "ok": True,
        "schema_version": (
            MODEL_PARAMETER_DEPENDENCY_SCHEMA_VERSION
        ),
        "study_id": study_id,
        "variable_source": (
            "calculated_model_parameter"
        ),
        "pairing_unit": "session_id",
        "available_variables_count": len(
            available_variables
        ),
        "available_dependencies_count": len(
            available_dependencies
        ),
        "available_variables": available_variables,
        "available_dependencies": (
            available_dependencies
        ),
    }