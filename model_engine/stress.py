import math


def safe_num(value, default=0.0):
    if value is None:
        return default
    return float(value)


def cap(value, min_value=0.0, max_value=10.0):
    return max(min_value, min(max_value, value))


def compute_s(loads_data: dict, r_data: dict):
    l_environment = safe_num(loads_data.get("l_environment"))
    l_requirements = safe_num(loads_data.get("l_requirements"))
    l_external = safe_num(loads_data.get("l_external"))
    l_additional = safe_num(loads_data.get("l_additional"))

    r_total = safe_num(r_data.get("r_total"))

    # MVP: P and multipliers will be added later.
    p_total = 0.0
    m_total = 1.0

    s_raw = (
        l_environment
        + l_requirements
        + l_external
        + l_additional
        + r_total
        + p_total
    ) * m_total

    s_norm = math.log10(s_raw + 1) / math.log10(700) * 10

    s_final = cap(s_norm, 0, 10)

    return {
        "s_raw": round(s_raw, 3),
        "s_norm": round(s_norm, 3),
        "s_final": round(s_final, 3),
        "p_total": p_total,
        "m_total": m_total,
    }