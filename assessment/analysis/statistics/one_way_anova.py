from assessment.analysis.statistics.descriptive import (
    group_descriptive_summary,
    mean,
)
from assessment.analysis.statistics.p_value import (
    regularized_incomplete_beta,
)


def f_survival_function(
    *,
    f_statistic: float,
    numerator_degrees_of_freedom: int,
    denominator_degrees_of_freedom: int,
) -> float | None:
    if f_statistic < 0:
        return None

    if (
        numerator_degrees_of_freedom <= 0
        or denominator_degrees_of_freedom <= 0
    ):
        return None

    df1 = float(numerator_degrees_of_freedom)
    df2 = float(denominator_degrees_of_freedom)

    x = df2 / (df2 + df1 * f_statistic)

    return regularized_incomplete_beta(
        df2 / 2.0,
        df1 / 2.0,
        x,
    )


def one_way_anova_test(
    *,
    groups: dict[str, list[float]],
    alpha: float = 0.05,
) -> dict:
    usable_groups = {
        group_name: values
        for group_name, values in groups.items()
        if len(values) >= 2
    }

    group_count = len(usable_groups)

    if group_count < 2:
        return {
            "ok": False,
            "status": "two_or_more_groups_required",
            "observed_group_count": group_count,
        }

    all_values = [
        value
        for values in usable_groups.values()
        for value in values
    ]

    total_sample_size = len(all_values)

    if total_sample_size <= group_count:
        return {
            "ok": False,
            "status": "not_enough_degrees_of_freedom",
            "sample_size": total_sample_size,
            "group_count": group_count,
        }

    grand_mean = mean(all_values)

    between_sum_of_squares = sum(
        len(values) * (mean(values) - grand_mean) ** 2
        for values in usable_groups.values()
    )

    within_sum_of_squares = sum(
        sum((value - mean(values)) ** 2 for value in values)
        for values in usable_groups.values()
    )

    df_between = group_count - 1
    df_within = total_sample_size - group_count

    if df_within <= 0:
        return {
            "ok": False,
            "status": "not_enough_within_group_degrees_of_freedom",
        }

    mean_square_between = between_sum_of_squares / df_between
    mean_square_within = within_sum_of_squares / df_within

    if mean_square_within <= 0:
        return {
            "ok": False,
            "status": "within_group_variance_not_defined",
        }

    f_statistic = mean_square_between / mean_square_within
    p_value = f_survival_function(
        f_statistic=f_statistic,
        numerator_degrees_of_freedom=df_between,
        denominator_degrees_of_freedom=df_within,
    )

    significant = p_value is not None and p_value < alpha

    return {
        "ok": True,
        "status": "completed",
        "test_statistic": f_statistic,
        "test_statistic_name": "F",
        "degrees_of_freedom": {
            "between": df_between,
            "within": df_within,
        },
        "alpha": alpha,
        "p_value": p_value,
        "decision": (
            "Reject H0"
            if significant
            else "Fail to reject H0"
        ),
        "sum_of_squares": {
            "between": between_sum_of_squares,
            "within": within_sum_of_squares,
        },
        "mean_squares": {
            "between": mean_square_between,
            "within": mean_square_within,
        },
        "group_summary": {
            group_name: group_descriptive_summary(values)
            for group_name, values in usable_groups.items()
        },
        "sample_size": total_sample_size,
        "group_count": group_count,
    }
