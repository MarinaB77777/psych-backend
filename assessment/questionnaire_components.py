QUESTIONNAIRE_COMPONENTS_SCHEMA_VERSION = "questionnaire-components-1"


def _component(
    component_id: str,
    title: str,
    component_type: str,
    **metadata,
) -> dict:
    return {
        "id": component_id,
        "title": title,
        "component_type": component_type,
        "schema_version": QUESTIONNAIRE_COMPONENTS_SCHEMA_VERSION,
        **metadata,
    }


QUESTION_TYPES = {
    "single_choice": _component(
        "single_choice",
        "Single choice",
        "question_type",
        description="Respondent selects exactly one option from a predefined list.",
        constructor_hint="Use for radio buttons, dropdowns, categories, Likert-type items, routing choices, and ordered answer options.",
        requires_options=True,
        supports_branching=True,
        compatible_scale_types=["nominal", "ordinal", "binary", "likert"],
    ),
    "multiple_choice": _component(
        "multiple_choice",
        "Multiple choice",
        "question_type",
        description="Respondent may select more than one option from a predefined list.",
        constructor_hint="Use when several categories may be true at the same time. Do not use for ordered severity unless multiple selections are scientifically intended.",
        requires_options=True,
        supports_branching=True,
        compatible_scale_types=["nominal"],
    ),
    "numeric": _component(
        "numeric",
        "Numeric input",
        "question_type",
        description="Respondent enters a numeric value.",
        constructor_hint="Use for measurable quantities, counts, age, duration, frequency, money, or any value with numeric meaning.",
        requires_options=False,
        supports_branching=True,
        compatible_scale_types=["interval", "ratio", "continuous", "duration"],
    ),
    "slider": _component(
        "slider",
        "Slider",
        "question_type",
        description="Respondent selects a value on a continuous or stepwise numeric range.",
        constructor_hint="Use when visual positioning on a range is important. Define min, max and step.",
        requires_options=False,
        supports_branching=True,
        compatible_scale_types=["interval", "ratio", "continuous", "visual_analog"],
    ),
    "visual_analog_scale": _component(
        "visual_analog_scale",
        "Visual analog scale",
        "question_type",
        description="Respondent marks a position on a continuous visual line.",
        constructor_hint="Use for subjective intensity when a continuous representation is intended, such as pain, fatigue, tension or confidence.",
        requires_options=False,
        supports_branching=True,
        compatible_scale_types=["visual_analog"],
    ),
    "text": _component(
        "text",
        "Free text",
        "question_type",
        description="Respondent writes an unrestricted text answer.",
        constructor_hint="Use for explanations, comments, context, or qualitative data. Not directly numeric unless coded later.",
        requires_options=False,
        supports_branching=True,
        compatible_scale_types=["text"],
    ),
    "date": _component(
        "date",
        "Date",
        "question_type",
        description="Respondent provides a calendar date.",
        constructor_hint="Use for dates of events, start dates, deadlines, or temporal anchors.",
        requires_options=False,
        supports_branching=True,
        compatible_scale_types=["date"],
    ),
    "time": _component(
        "time",
        "Time",
        "question_type",
        description="Respondent provides a time of day.",
        constructor_hint="Use for time points within a day. Use duration/numeric for elapsed time.",
        requires_options=False,
        supports_branching=True,
        compatible_scale_types=["time"],
    ),
    "duration": _component(
        "duration",
        "Duration",
        "question_type",
        description="Respondent provides elapsed time or length of time.",
        constructor_hint="Use for sleep duration, waiting time, exposure duration, work time, or recovery time.",
        requires_options=False,
        supports_branching=True,
        compatible_scale_types=["duration", "ratio"],
    ),
    "file": _component(
        "file",
        "File upload",
        "question_type",
        description="Respondent uploads or references a file.",
        constructor_hint="Use for documents, images, attachments, or external measurement files. The answer is a file reference, not a psychometric score.",
        requires_options=False,
        supports_branching=True,
        compatible_scale_types=["file"],
    ),
    "ranking": _component(
        "ranking",
        "Ranking",
        "question_type",
        description="Respondent orders items by priority, preference, importance, or sequence.",
        constructor_hint="Use when relative order matters more than absolute distance between items.",
        requires_options=True,
        supports_branching=False,
        compatible_scale_types=["ordinal"],
    ),
}

# Canonical response-value structures used by the new constructor.
# QUESTION_TYPES remains unchanged for backward compatibility.
RESPONSE_TYPES = {
    "single_choice": _component(
        "single_choice",
        "Single selected value",
        "response_type",
        description=(
            "The response contains exactly one selected value "
            "from a predefined set of options."
        ),
        requires_options=True,
        supports_branching=True,
        compatible_scale_types=[
            "nominal",
            "ordinal",
            "binary",
            "likert",
        ],
        compatible_presentation_types=[
            "radio",
            "dropdown",
            "cards",
        ],
    ),
    "multiple_choice": _component(
        "multiple_choice",
        "Multiple selected values",
        "response_type",
        description=(
            "The response contains zero, one, or several selected "
            "values from a predefined set of options."
        ),
        requires_options=True,
        supports_branching=True,
        compatible_scale_types=[
            "nominal",
        ],
        compatible_presentation_types=[
            "checkbox",
            "cards",
        ],
    ),
    "numeric": _component(
        "numeric",
        "Numeric value",
        "response_type",
        description=(
            "The response contains one numeric value."
        ),
        requires_options=False,
        supports_branching=True,
        compatible_scale_types=[
            "interval",
            "ratio",
            "continuous",
            "duration",
            "visual_analog",
        ],
        compatible_presentation_types=[
            "number_input",
            "slider",
            "visual_analog_line",
        ],
    ),
    "text": _component(
        "text",
        "Text value",
        "response_type",
        description=(
            "The response contains free-form text."
        ),
        requires_options=False,
        supports_branching=True,
        compatible_scale_types=[
            "text",
        ],
        compatible_presentation_types=[
            "text_input",
        ],
    ),
    "date": _component(
        "date",
        "Date value",
        "response_type",
        description=(
            "The response contains a calendar date."
        ),
        requires_options=False,
        supports_branching=True,
        compatible_scale_types=[
            "date",
        ],
        compatible_presentation_types=[
            "date_input",
        ],
    ),
    "time": _component(
        "time",
        "Time value",
        "response_type",
        description=(
            "The response contains a time of day."
        ),
        requires_options=False,
        supports_branching=True,
        compatible_scale_types=[
            "time",
        ],
        compatible_presentation_types=[
            "time_input",
        ],
    ),
    "duration": _component(
        "duration",
        "Duration value",
        "response_type",
        description=(
            "The response contains an elapsed-time value "
            "with an explicit unit."
        ),
        requires_options=False,
        supports_branching=True,
        compatible_scale_types=[
            "duration",
            "ratio",
        ],
        compatible_presentation_types=[
            "duration_input",
            "number_input",
        ],
    ),
    "file": _component(
        "file",
        "File reference",
        "response_type",
        description=(
            "The response contains a stored file reference "
            "or upload identifier."
        ),
        requires_options=False,
        supports_branching=True,
        compatible_scale_types=[
            "file",
        ],
        compatible_presentation_types=[
            "file_input",
        ],
    ),
    "ranking": _component(
        "ranking",
        "Ordered list of values",
        "response_type",
        description=(
            "The response contains an ordered sequence of predefined items."
        ),
        requires_options=True,
        supports_branching=False,
        compatible_scale_types=[
            "ordinal",
        ],
        compatible_presentation_types=[
            "ranking",
        ],
    ),
}

SCALE_TYPES = {
    "nominal": _component(
        "nominal",
        "Nominal scale",
        "scale_type",
        measurement_scale="nominal",
        default_representation="categorical_representation",
    ),
    "ordinal": _component(
        "ordinal",
        "Ordinal scale",
        "scale_type",
        measurement_scale="ordinal",
        default_representation="ordered_categorical_representation",
    ),
    "binary": _component(
        "binary",
        "Binary scale",
        "scale_type",
        measurement_scale="nominal",
        default_representation="binary_categorical_representation",
    ),
    "interval": _component(
        "interval",
        "Interval scale",
        "scale_type",
        measurement_scale="interval",
        default_representation="interval_numeric_representation",
    ),
    "continuous": _component(
        "continuous",
        "Continuous numeric scale",
        "scale_type",
        measurement_scale="interval",
        default_representation="interval_numeric_representation",
    ),
    "ratio": _component(
        "ratio",
        "Ratio scale",
        "scale_type",
        measurement_scale="ratio",
        default_representation="ratio_numeric_representation",
    ),
    "duration": _component(
        "duration",
        "Duration scale",
        "scale_type",
        measurement_scale="ratio",
        default_representation="duration_numeric_representation",
    ),
    "likert": _component(
        "likert",
        "Likert item scale",
        "scale_type",
        measurement_scale="ordinal",
        default_representation="ordered_categorical_representation",
    ),
    "visual_analog": _component(
        "visual_analog",
        "Visual analog scale",
        "scale_type",
        measurement_scale="interval",
        default_representation="interval_numeric_representation",
    ),
    "text": _component(
        "text",
        "Text response",
        "scale_type",
        measurement_scale="text",
        default_representation="text_representation",
    ),
    "date": _component(
        "date",
        "Date scale",
        "scale_type",
        measurement_scale="date",
        default_representation="date_representation",
    ),
    "time": _component(
        "time",
        "Time scale",
        "scale_type",
        measurement_scale="time",
        default_representation="time_representation",
    ),
    "file": _component(
        "file",
        "File reference",
        "scale_type",
        measurement_scale="file",
        default_representation="file_reference_representation",
    ),
}


PRESENTATION_TYPES = {
    "radio": _component(
        "radio",
        "Radio buttons",
        "presentation_type",
    ),
    "dropdown": _component(
        "dropdown",
        "Dropdown",
        "presentation_type",
    ),
    "cards": _component(
        "cards",
        "Cards",
        "presentation_type",
    ),
    "checkbox": _component(
        "checkbox",
        "Checkboxes",
        "presentation_type",
    ),
    "slider": _component(
        "slider",
        "Slider UI",
        "presentation_type",
    ),
    "visual_analog_line": _component(
        "visual_analog_line",
        "Visual analog line",
        "presentation_type",
    ),
    "text_input": _component(
        "text_input",
        "Text input",
        "presentation_type",
    ),
    "number_input": _component(
        "number_input",
        "Number input",
        "presentation_type",
    ),
    "date_input": _component(
        "date_input",
        "Date input",
        "presentation_type",
    ),
    "time_input": _component(
        "time_input",
        "Time input",
        "presentation_type",
    ),
    "duration_input": _component(
        "duration_input",
        "Duration input",
        "presentation_type",
    ),
    "file_input": _component(
        "file_input",
        "File input",
        "presentation_type",
    ),
    "ranking": _component(
        "ranking",
        "Ranking interface",
        "presentation_type",
    ),
}

VALIDATION_COMPONENTS = {
    "required": _component("required", "Required", "validation_component"),
    "optional": _component("optional", "Optional", "validation_component"),
    "min_value": _component("min_value", "Minimum value", "validation_component"),
    "max_value": _component("max_value", "Maximum value", "validation_component"),
    "min_selections": _component(
        "min_selections",
        "Minimum selections",
        "validation_component",
    ),
    "max_selections": _component(
        "max_selections",
        "Maximum selections",
        "validation_component",
    ),
}


TRANSITION_TYPES = {
    "sequential": _component("sequential", "Sequential", "transition_type"),
    "conditional": _component("conditional", "Conditional", "transition_type"),
    "terminal": _component("terminal", "Terminal", "transition_type"),
}


LEGACY_QUESTION_TYPE_ALIASES = {
    "single_select": "single_choice",
    "multi_select": "multiple_choice",
    "free_text": "text",
    "long_text": "text",
    "number": "numeric",
    "scale": "slider",
}

LEGACY_RESPONSE_TYPE_ALIASES = {
    **LEGACY_QUESTION_TYPE_ALIASES,
    "integer": "numeric",
    "float": "numeric",
    "number_input": "numeric",
    "file_upload": "file",
}

LEGACY_SCALE_TYPE_ALIASES = {
    "number": "ratio",
    "numeric": "ratio",
    "vas": "visual_analog",
    "visual_analog_scale": "visual_analog",
    "free_text": "text",
    "long_text": "text",
    "file_upload": "file",
}


def normalize_question_type_id(question_type_id: str | None) -> str | None:
    if question_type_id is None:
        return None

    return LEGACY_QUESTION_TYPE_ALIASES.get(
        question_type_id,
        question_type_id,
    )


def normalize_response_type_id(response_type_id: str | None) -> str | None:
    if response_type_id is None:
        return None

    return LEGACY_RESPONSE_TYPE_ALIASES.get(
        response_type_id,
        response_type_id,
    )


def normalize_scale_type_id(scale_type_id) -> str | None:
    if scale_type_id is None:
        return None

    if isinstance(scale_type_id, dict):
        scale_type_id = scale_type_id.get("scale_type")

    return LEGACY_SCALE_TYPE_ALIASES.get(
        scale_type_id,
        scale_type_id,
    )


def get_question_type(question_type_id: str) -> dict | None:
    return QUESTION_TYPES.get(normalize_question_type_id(question_type_id))

def get_response_type(response_type_id: str) -> dict | None:
    return RESPONSE_TYPES.get(normalize_response_type_id(response_type_id))

def get_scale_type(scale_type_id: str) -> dict | None:
    return SCALE_TYPES.get(normalize_scale_type_id(scale_type_id))


def get_presentation_type(presentation_type_id: str) -> dict | None:
    return PRESENTATION_TYPES.get(presentation_type_id)


def get_transition_type(transition_type_id: str) -> dict | None:
    return TRANSITION_TYPES.get(transition_type_id)


def list_question_types() -> list[dict]:
    return list(QUESTION_TYPES.values())

def list_response_types() -> list[dict]:
    return list(RESPONSE_TYPES.values())

def list_scale_types() -> list[dict]:
    return list(SCALE_TYPES.values())


def list_presentation_types() -> list[dict]:
    return list(PRESENTATION_TYPES.values())


def list_validation_components() -> list[dict]:
    return list(VALIDATION_COMPONENTS.values())

def list_transition_types() -> list[dict]:
    return list(TRANSITION_TYPES.values())


def is_question_type_compatible_with_scale(
    question_type_id: str,
    scale_type_id: str,
) -> bool:
    question_type = get_question_type(question_type_id)
    scale_type_id = normalize_scale_type_id(scale_type_id)

    if question_type is None:
        return False

    return scale_type_id in question_type.get("compatible_scale_types", [])


def is_response_type_compatible_with_scale(
    response_type_id: str,
    scale_type_id: str,
) -> bool:
    response_type = get_response_type(response_type_id)
    scale_type_id = normalize_scale_type_id(scale_type_id)

    if response_type is None:
        return False

    return scale_type_id in response_type.get("compatible_scale_types", [])


def is_response_type_compatible_with_presentation(
    response_type_id: str,
    presentation_type_id: str,
) -> bool:
    response_type = get_response_type(response_type_id)

    if response_type is None:
        return False

    return presentation_type_id in response_type.get(
        "compatible_presentation_types",
        [],
    )
