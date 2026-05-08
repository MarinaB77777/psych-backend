def safe_num(value, default=0.0):
    if value is None:
        return default
    return float(value)


def cap(value, min_value=0.0, max_value=5.0):
    return max(min_value, min(max_value, value))


def compute_pressure(answers: dict, loads_data: dict, r_data: dict):
    d0 = safe_num(answers.get("d0"))

    l_environment = safe_num(loads_data.get("l_environment"))
    l_external = safe_num(loads_data.get("l_external"))

    r_total = safe_num(r_data.get("r_total"))

    # primary life instability
    p_activity = d0 / 5

    # load-resource interaction
    p_load_resource = ((l_environment + l_external) * r_total) / 25

    # external instability amplification
    p_external = l_external / 5

    p_total = (
        p_activity
        + p_load_resource
        + p_external
    )

    p_total = cap(p_total, 0, 5)

    return {
        "p_activity": round(p_activity, 3),
        "p_load_resource": round(p_load_resource, 3),
        "p_external": round(p_external, 3),
        "p_total": round(p_total, 3),
    }