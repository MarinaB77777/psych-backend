import math

from assessment.analysis.statistics.descriptive import (
    mean,
    sample_variance,
)
from assessment.analysis.statistics.p_value import (
    student_t_two_tailed_p_value,
)


def welch_t_test(
    *,
    group_1: list[float],
    group_2: list[float],
    alpha: float = 0.05,
) -> dict:
    n1 = len(group_1)
    n2 = len(group_2)

    if n1 < 2 or n2 < 2:
        return {
            "ok": False,
            "status": "not_enough_group_data",
            "group_sizes": {
                "group_1": n1,
                "group_2": n2,
            },
        }

    mean_1 = mean(group_1)
    mean_2 = mean(group_2)
    variance_1 = sample_variance(group_1)
    variance_2 = sample_variance(group_2)

    if variance_1 is None or variance_2 is None:
        return {
            "ok": False,
            "status": "variance_not_defined",
        }

    standard_error_squared = variance_1 / n1 + variance_2 / n2

    if standard_error_squared <= 0:
        return {
            "ok": False,
            "status": "test_statistic_not_defined",
        }

    t_statistic = (mean_1 - mean_2) / math.sqrt(standard_error_squared)

    numerator = standard_error_squared ** 2
    denominator = (
        ((variance_1 / n1) ** 2) / (n1 - 1)
        + ((variance_2 / n2) ** 2) / (n2 - 1)
    )

    if denominator <= 0:
        return {
            "ok": False,
            "status": "degrees_of_freedom_not_defined",
        }

    degrees_of_freedom = numerator / denominator
    p_value = student_t_two_tailed_p_value(
        t_statistic=t_statistic,
        degrees_of_freedom=max(1, int(round(degrees_of_freedom))),
    )

    significant = p_value is not None and p_value < alpha

    return {
        "ok": True,
        "status": "completed",
        "test_statistic": t_statistic,
        "test_statistic_name": "Welch's t",
        "degrees_of_freedom": degrees_of_freedom,
        "alpha": alpha,
        "p_value": p_value,
        "decision": (
            "Reject H0"
            if significant
            else "Fail to reject H0"
        ),
        "group_summary": {
            "group_1": {
                "n": n1,
                "mean": mean_1,
                "variance": variance_1,
            },
            "group_2": {
                "n": n2,
                "mean": mean_2,
                "variance": variance_2,
            },
        },
    }
