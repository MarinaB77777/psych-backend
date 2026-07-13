from typing import Any


MODEL_PARAMETER_CATALOG_SCHEMA_VERSION = (
    "health-model-parameter-catalog-1"
)
EXCLUDED_PARAMETER_PREFIXES = (
    "calculator_input.",
)


def _is_available_model_parameter(
    parameter_code: str,
) -> bool:
    return not parameter_code.startswith(
        EXCLUDED_PARAMETER_PREFIXES
    )


def _extract_research_snapshot_parameter_records(
    research_record: dict,
) -> list[dict]:
    snapshot = research_record.get("research_snapshot") or {}

    health_summary = snapshot.get(
        "health_model_research_model_summary"
    ) or {}

    records = health_summary.get(
        "research_calculated_parameter_records"
    )

    if isinstance(records, list):
        return records

    legacy_records = research_record.get(
        "research_calculated_parameter_records"
    )

    if isinstance(legacy_records, list):
        return legacy_records

    return []


def _extract_pilot_parameter_records(
    session: Any,
) -> list[dict]:
    raw_result = session.raw_engine_result or {}

    records = raw_result.get(
        "research_calculated_parameter_records"
    )

    if isinstance(records, list):
        return records

    return []


def _record_identity(
    record: dict,
) -> tuple[str | None, str | None]:
    return (
        record.get("session_id"),
        record.get("parameter_code"),
    )

def _normalize_parameter_record(
    record: dict,
    *,
    record_source: str,
) -> dict | None:
    parameter_code = record.get("parameter_code")

    if not parameter_code:
        return None

    if not _is_available_model_parameter(
        parameter_code
    ):
        return None

    return {
        **record,
        "record_source": record_source,
        "parameter_code": parameter_code,
        "parameter_value": record.get("parameter_value"),
        "parameter_value_type": record.get(
            "parameter_value_type"
        ),
        "scale_type": record.get("scale_type"),
    }


def collect_health_model_parameter_records(
    *,
    research_records: list[dict],
    pilot_sessions: list[Any],
    study_id: str = "health_model",
) -> list[dict]:
    records_by_identity = {}

    # Research snapshots are preferred when the same
    # session + parameter already exists in both layers.
    for research_record in research_records:
        record_study_id = (
            research_record.get("study_id")
            or study_id
        )

        if record_study_id != study_id:
            continue

        for parameter_record in (
            _extract_research_snapshot_parameter_records(
                research_record
            )
        ):
            normalized = _normalize_parameter_record(
                parameter_record,
                record_source="research_snapshot",
            )

            if normalized is None:
                continue

            identity = _record_identity(normalized)

            if None in identity:
                continue

            records_by_identity[identity] = normalized

    # Pilot sessions are a fallback for sessions that
    # have not yet been exported to a research snapshot.
    for session in pilot_sessions:
        session_study_id = (
            session.study_id
            or "health_model"
        )

        if session_study_id != study_id:
            continue

        for parameter_record in (
            _extract_pilot_parameter_records(session)
        ):
            normalized = _normalize_parameter_record(
                parameter_record,
                record_source="pilot_session",
            )

            if normalized is None:
                continue

            identity = _record_identity(normalized)

            if None in identity:
                continue

            records_by_identity.setdefault(
                identity,
                normalized,
            )

    return sorted(
        records_by_identity.values(),
        key=lambda record: (
            str(record.get("parameter_code") or ""),
            str(record.get("session_id") or ""),
        ),
    )


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


def build_available_model_parameter_catalog(
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

    grouped = {}

    for record in parameter_records:
        parameter_code = record["parameter_code"]

        grouped.setdefault(
            parameter_code,
            {
                "parameter_code": parameter_code,
                "records": [],
                "value_types": set(),
                "scale_types": set(),
                "model_ids": set(),
                "source_modes": set(),
                "record_sources": set(),
                "session_ids": set(),
                "participant_ids": set(),
                "subject_link_ids": set(),
            },
        )

        group = grouped[parameter_code]
        group["records"].append(record)
        group["value_types"].add(
            record.get("parameter_value_type")
        )
        group["scale_types"].add(
            record.get("scale_type")
        )
        group["model_ids"].add(
            record.get("model_id")
        )
        group["source_modes"].add(
            record.get("source_mode")
        )
        group["record_sources"].add(
            record.get("record_source")
        )

        if record.get("session_id"):
            group["session_ids"].add(
                record["session_id"]
            )

        if record.get("participant_id"):
            group["participant_ids"].add(
                record["participant_id"]
            )

        if record.get("subject_link_id"):
            group["subject_link_ids"].add(
                record["subject_link_id"]
            )

    parameters = []

    for parameter_code in sorted(grouped):
        group = grouped[parameter_code]

        parameters.append({
            "variable_source": (
                "calculated_model_parameter"
            ),
            "variable_code": parameter_code,
            "parameter_code": parameter_code,
            "title": parameter_code,
            "study_id": study_id,
            "parameter_value_type": _single_or_mixed(
                group["value_types"]
            ),
            "scale_type": _single_or_mixed(
                group["scale_types"]
            ),
            "available_records_count": len(
                group["records"]
            ),
            "available_session_count": len(
                group["session_ids"]
            ),
            "available_participant_count": len(
                group["participant_ids"]
                or group["subject_link_ids"]
            ),
            "model_ids": sorted(
                value
                for value in group["model_ids"]
                if value
            ),
            "source_modes": sorted(
                value
                for value in group["source_modes"]
                if value
            ),
            "record_sources": sorted(
                value
                for value in group["record_sources"]
                if value
            ),
        })

    return {
        "schema_version": (
            MODEL_PARAMETER_CATALOG_SCHEMA_VERSION
        ),
        "study_id": study_id,
        "parameter_count": len(parameters),
        "parameter_record_count": len(
            parameter_records
        ),
        "parameters": parameters,
    }