from measurement_graph.schemas import build_empty_measurement_graph
from measurement_graph.metadata_providers.registry import resolve_metadata


def build_measurement_graph_from_session(
    measurement_session: dict,
    context: dict | None = None,
) -> dict:
    graph = build_empty_measurement_graph()

    identity = measurement_session.get("identity", {})
    time = measurement_session.get("time", {})
    connector = measurement_session.get("connector", {})
    raw_data = measurement_session.get("raw_data", {})

    metadata = resolve_metadata(
        connector=connector,
        context=context or {},
    )

    graph["measurement_identity"] = {
        "measurement_id": measurement_session.get("measurement_id"),
        "measurement_type": identity.get("measurement_type"),
        "study_id": identity.get("study_id"),
        "participant_id": identity.get("participant_id"),
        "session_id": identity.get("session_id"),
        "series_id": identity.get("series_id"),
        "series_position": identity.get("series_position"),
        "is_repeated_measurement": identity.get(
            "is_repeated_measurement",
            False,
        ),
    }

    graph["time_reference"] = {
        "started_at": time.get("started_at"),
        "finished_at": time.get("finished_at"),
        "global_time_reference": time.get("global_time_reference"),
        "timezone": (context or {}).get("timezone"),
        "synchronization_reference": (context or {}).get(
            "synchronization_reference"
        ),
    }

    graph["instrument"] = metadata.get("instrument", {})
    graph["measurement_description"] = metadata.get(
        "measurement_description",
        {},
    )

    graph["metadata"] = {
        "metadata_status": metadata.get("metadata_status"),
        "metadata_source": metadata.get("metadata_source"),
    }

    graph["data_file"] = {
        "file_id": measurement_session.get("measurement_id"),
        "file_name": raw_data.get("original_file_name"),
        "file_path": raw_data.get("raw_file_path"),
        "file_type": raw_data.get("file_type"),
        "checksum": raw_data.get("checksum"),
        "data_included": raw_data.get("data_exists", False),
    }

    return graph