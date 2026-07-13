PARAMETER_RECORD_SCHEMA_VERSION = "health-model-parameter-record-1"
from uuid import uuid4

def _value_type(value):
    if isinstance(value, bool):
        return "bool"

    if isinstance(value, int):
        return "int"

    if isinstance(value, float):
        return "float"

    return type(value).__name__


def _scale_type(value):
    if isinstance(value, bool):
        return "binary"

    if isinstance(value, (int, float)):
        return "continuous"

    return "unknown"


def _flatten_numeric_values(
    data,
    *,
    prefix: str = "",
) -> list[dict]:
    records = []

    if not isinstance(data, dict):
        return records

    for key, value in data.items():
        parameter_code = (
            f"{prefix}.{key}"
            if prefix
            else str(key)
        )

        if isinstance(value, dict):
            records.extend(
                _flatten_numeric_values(
                    value,
                    prefix=parameter_code,
                )
            )
            continue

        if isinstance(value, bool) or isinstance(value, (int, float)):
            records.append({
                "parameter_code": parameter_code,
                "value": value,
                "value_type": _value_type(value),
                "scale_type": _scale_type(value),
            })

    return records


def build_health_model_parameter_records(
    *,
    session_id: str | None,
    participant_id: str | None,
    subject_link_id: str | None,
    study_id: str,
    analysis_output: dict,
) -> list[dict]:
    model_id = analysis_output.get("model_id", "health_model_v6_1")

    flat_parameters = _flatten_numeric_values(
        analysis_output
    )

    return [
        {
            "parameter_record_id": str(uuid4()),
            "schema_version": PARAMETER_RECORD_SCHEMA_VERSION,
            "record_type": "calculated_model_parameter",
            "model_id": model_id,
            "study_id": study_id,
            "session_id": session_id,
            "participant_id": participant_id,
            "subject_link_id": subject_link_id,
            "parameter_code": item["parameter_code"],
            "parameter_value": item["value"],
            "parameter_value_type": item["value_type"],
            "scale_type": item["scale_type"],
            "source_mode": "health_model_v61_calculation",
        }
        for item in flat_parameters
    ]