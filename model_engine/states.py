def determine_initial_state(coverage_data: dict, q_data: dict, answers: dict):
    reason_codes = []
    warnings = []

    k23 = answers.get("k23")
    k24 = answers.get("k24")

    if k23 is not None and k23 >= 3:
        reason_codes.append("CRITICAL_K23")
        warnings.append({
            "severity": "critical",
            "message": "Critical response detected: k23",
        })
        return {
            "state": "CRITICAL",
            "reason_codes": reason_codes,
            "warnings": warnings,
        }

    if k24 is not None and k24 >= 2:
        reason_codes.append("CRITICAL_K24")
        warnings.append({
            "severity": "critical",
            "message": "Critical response detected: k24",
        })
        return {
            "state": "CRITICAL",
            "reason_codes": reason_codes,
            "warnings": warnings,
        }

    if coverage_data["coverage"] < 0.4:
        reason_codes.append("LOW_COVERAGE")
        return {
            "state": "SAFE_DATA_REQUEST",
            "reason_codes": reason_codes,
            "warnings": warnings,
        }

    if q_data["q_global"] > 1:
        reason_codes.append("LOW_QUALITY")
        return {
            "state": "LOW_QUALITY",
            "reason_codes": reason_codes,
            "warnings": warnings,
        }

    return {
        "state": "ORIENTING",
        "reason_codes": reason_codes,
        "warnings": warnings,
    }

def determine_final_state(
    s_data: dict,
    k_self_data: dict,
    consistency_data: dict,
    coverage_data: dict,
    q_data: dict,
):
    reason_codes = []

    s_norm = s_data.get("s_norm")
    k_self_norm = k_self_data.get("k_self_norm")
    c_final = consistency_data.get("c_final", 0)

    coverage = coverage_data.get("coverage", 0)
    q_global = q_data.get("q_global", 999)

    # no enough data
    if s_norm is None or k_self_norm is None:
        reason_codes.append("STATE_NOT_ENOUGH_DATA")

        return {
            "state": "ORIENTING",
            "reason_codes": reason_codes,
        }

    # consistency failure
    if c_final > 4:
        reason_codes.append("CONSISTENCY_FAILURE")

        return {
            "state": "CONSISTENCY_FAILURE",
            "reason_codes": reason_codes,
        }

    delta_total = s_norm - k_self_norm

    # aligned
    if abs(delta_total) <= 1.5:
        reason_codes.append("STATE_DIAGNOSTIC")

        return {
            "state": "DIAGNOSTIC",
            "reason_codes": reason_codes,
        }

    # accumulated pressure
    if (
        s_norm > k_self_norm + 1.5
        and coverage >= 0.6
        and q_global <= 1.5
        and c_final <= 4
    ):
        reason_codes.append("STATE_FORECAST")

        return {
            "state": "FORECAST",
            "reason_codes": reason_codes,
        }

    # hidden factor
    if k_self_norm > s_norm + 1.5:
        reason_codes.append("STATE_HIDDEN_FACTOR")

        return {
            "state": "HIDDEN_FACTOR",
            "reason_codes": reason_codes,
        }

    return {
        "state": "ORIENTING",
        "reason_codes": ["STATE_ORIENTING"],
    }