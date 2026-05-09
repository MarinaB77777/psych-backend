def count_valid_calculated_domains(delta_data: dict):
    count = 0

    for item in delta_data.values():
        if item.get("calculated") is True:
            count += 1

    return count


def build_forecast_governance(
    state: str,
    confidence: str,
    coverage: float,
    q_global: float,
    c_final: float,
    s_data: dict,
    delta_data: dict,
    reason_codes: list,
):
    critical_override = s_data.get("critical_override") is True
    calculated_domains = count_valid_calculated_domains(delta_data)

    if state == "CRITICAL" or critical_override:
        return {
            "allowed": False,
            "reason": "CRITICAL_STATE",
            "confidence": confidence,
            "allowed_scope": "none",
        }

    if coverage < 0.4 or "LOW_COVERAGE" in reason_codes:
        return {
            "allowed": False,
            "reason": "LOW_COVERAGE",
            "confidence": confidence,
            "allowed_scope": "none",
        }

    if "STATE_NOT_ENOUGH_DATA" in reason_codes:
        return {
            "allowed": False,
            "reason": "STATE_NOT_ENOUGH_DATA",
            "confidence": confidence,
            "allowed_scope": "none",
        }

    if state == "HIDDEN_FACTOR":
        return {
            "allowed": False,
            "reason": "HIDDEN_FACTOR",
            "confidence": confidence,
            "allowed_scope": "trend_only",
        }

    if state == "CONSISTENCY_FAILURE" or c_final > 4:
        return {
            "allowed": False,
            "reason": "CONSISTENCY_FAILURE",
            "confidence": confidence,
            "allowed_scope": "none",
        }

    if q_global > 1.5:
        return {
            "allowed": False,
            "reason": "LOW_QUALITY",
            "confidence": confidence,
            "allowed_scope": "none",
        }

    if calculated_domains < 3:
        return {
            "allowed": False,
            "reason": "INSUFFICIENT_DOMAIN_COVERAGE",
            "confidence": confidence,
            "allowed_scope": "trend_only",
        }

    if state == "FORECAST":
        return {
            "allowed": True,
            "reason": "FORECAST_ALLOWED",
            "confidence": confidence,
            "allowed_scope": "short_term",
        }

    if state == "DIAGNOSTIC":
        return {
            "allowed": False,
            "reason": "DIAGNOSTIC_ONLY",
            "confidence": confidence,
            "allowed_scope": "trend_only",
        }

    return {
        "allowed": False,
        "reason": "FORECAST_BLOCKED",
        "confidence": confidence,
        "allowed_scope": "none",
    }