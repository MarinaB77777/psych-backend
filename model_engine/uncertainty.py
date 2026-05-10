def build_uncertainty_profile(
    coverage: float,
    q_global: float,
    c_final: float,
    state: str,
    forecast_data: dict,
    delta_data: dict,
):
    uncertainty_score = 0

    if coverage < 0.4:
        uncertainty_score += 3
    elif coverage < 0.7:
        uncertainty_score += 1

    if q_global > 1.5:
        uncertainty_score += 2
    elif q_global > 0.5:
        uncertainty_score += 1

    if c_final > 4:
        uncertainty_score += 2
    elif c_final > 2:
        uncertainty_score += 1

    if state in [
        "HIDDEN_FACTOR",
        "SAFE_DATA_REQUEST",
        "STATE_NOT_ENOUGH_DATA",
    ]:
        uncertainty_score += 2

    if forecast_data.get("allowed") is False:
        uncertainty_score += 1

    calculated_domains = 0

    for item in delta_data.values():
        if item.get("calculated") is True:
            calculated_domains += 1

    if calculated_domains < 3:
        uncertainty_score += 2

    if uncertainty_score >= 7:
        level = "high"
    elif uncertainty_score >= 4:
        level = "medium"
    else:
        level = "low"

    allow_recommendations = uncertainty_score < 7
    allow_strong_recommendations = uncertainty_score < 4

    return {
        "uncertainty_score": uncertainty_score,
        "uncertainty_level": level,
        "allow_recommendations": allow_recommendations,
        "allow_strong_recommendations": (
            allow_strong_recommendations
        ),
        "dialogue_mode": (
            "soft"
            if level == "high"
            else "standard"
        ),
    }