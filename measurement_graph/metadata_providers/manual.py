def resolve(connector: dict, context: dict | None = None) -> dict:
    context = context or {}

    return {
        "metadata_status": "manual",
        "metadata_source": "manual_form",
        "instrument": {
            "instrument_type": context.get("instrument_type"),
            "instrument_name": context.get("instrument_name"),
            "instrument_version": context.get("instrument_version"),
            "manufacturer": context.get("manufacturer"),
            "device_id": context.get("device_id"),
            "software_version": context.get("software_version"),
        },
        "measurement_description": {
            "data_kind": context.get("data_kind"),
            "data_format": context.get("data_format"),
            "measurement_scales": context.get("measurement_scales", []),
            "units": context.get("units", []),
            "sampling_rate": context.get("sampling_rate"),
            "temporal_resolution": context.get("temporal_resolution"),
            "spatial_resolution": context.get("spatial_resolution"),
            "variables": context.get("variables", []),
            "question_count": context.get("question_count"),
            "item_metadata_available": False,
        },
    }