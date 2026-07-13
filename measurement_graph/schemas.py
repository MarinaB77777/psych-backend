MEASUREMENT_GRAPH_SCHEMA_VERSION = "measurement-graph-1"


def build_empty_measurement_graph() -> dict:
    return {
        "schema_version": MEASUREMENT_GRAPH_SCHEMA_VERSION,

        "measurement_identity": {
            "measurement_id": None,
            "measurement_type": None,
            "study_id": None,
            "participant_id": None,
            "session_id": None,
            "series_id": None,
            "series_position": None,
            "is_repeated_measurement": False,
        },

        "time_reference": {
            "started_at": None,
            "finished_at": None,
            "global_time_reference": None,
            "timezone": None,
            "synchronization_reference": None,
        },

        "instrument": {
            "instrument_type": None,
            "instrument_name": None,
            "instrument_version": None,
            "manufacturer": None,
            "device_id": None,
            "software_version": None,
        },

        "measurement_description": {
            "data_kind": None,
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

        "data_file": {
            "file_id": None,
            "file_name": None,
            "file_path": None,
            "file_type": None,
            "checksum": None,
            "data_included": True,
        },

        "quality": {
            "quality_status": "unknown",
            "quality_flags": [],
        },

        "coverage": {
            "expected_item_count": None,
            "available_item_count": None,
            "missing_item_count": None,
            "coverage_score": None,
        },

        "calibration": {
            "calibration_required": False,
            "calibration_available": False,
            "calibration_reference_id": None,
        },

        "permissions": {
            "collection_allowed": True,
            "analysis_allowed": True,
            "research_allowed": True,
            "export_allowed": False,
        },
    }