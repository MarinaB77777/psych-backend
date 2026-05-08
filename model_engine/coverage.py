REQUIRED_FIELDS = [
    "d0",
    "d8",
    "d9",
    "e4",
    "e8",
    "k7",
    "k10",
    "k14",
    "k22",
    "k23",
    "k24",
]


def compute_coverage(answers: dict):
    valid_count = 0
    missing_fields = []

    for field in REQUIRED_FIELDS:
        value = answers.get(field)

        if value is None:
            missing_fields.append(field)
            continue

        valid_count += 1

    coverage = valid_count / len(REQUIRED_FIELDS)

    return {
        "coverage": round(coverage, 3),
        "valid_count": valid_count,
        "required_count": len(REQUIRED_FIELDS),
        "missing_fields": missing_fields,
    }
