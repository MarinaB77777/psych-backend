QUESTION_TEXTS = {
    "d0": {
        "en": "Do you currently have work, studies, or another main activity?",
        "es": "¿Actualmente tienes trabajo, estudios u otra actividad principal?",
    },
    "d8": {
        "en": "How heavy is your current task load?",
        "es": "¿Qué tan alta es tu carga actual de tareas?",
    },
    "d9": {
        "en": "How strict are your current deadlines?",
        "es": "¿Qué tan estrictos son tus plazos actuales?",
    },
    "e4": {
        "en": "Is there an unresolved or uncertain situation affecting you now?",
        "es": "¿Hay alguna situación pendiente o incierta que te esté afectando ahora?",
    },
    "e8": {
        "en": "Is work or study instability currently creating pressure?",
        "es": "¿La inestabilidad laboral o académica te está generando presión actualmente?",
    },
    "k7": {
        "en": "How is your energy during the day?",
        "es": "¿Cómo está tu energía durante el día?",
    },
    "k10": {
        "en": "Do anxious thoughts appear before sleep?",
        "es": "¿Aparecen pensamientos de ansiedad antes de dormir?",
    },
    "k14": {
        "en": "Do you feel movement toward your goals or a sense of stagnation?",
        "es": "¿Sientes avance hacia tus metas o una sensación de estancamiento?",
    },
    "k22": {
        "en": "Do you have a sense of meaninglessness?",
        "es": "¿Tienes una sensación de falta de sentido?",
    },
    "k23": {
        "en": "Have you had thoughts that you do not want to wake up or continue living?",
        "es": "¿Has tenido pensamientos de no querer despertar o no querer seguir viviendo?",
    },
    "k24": {
        "en": "Have you had urges or actions related to hurting yourself?",
        "es": "¿Has tenido impulsos o acciones relacionadas con hacerte daño?",
    },
}


def build_question(variable_code: str, priority: int, reason_code: str):
    texts = QUESTION_TEXTS.get(variable_code)

    if texts is None:
        texts = {
            "en": f"Please provide a value for {variable_code}.",
            "es": f"Por favor proporciona un valor para {variable_code}.",
        }

    return {
        "variable_code": variable_code,
        "priority": priority,
        "reason_code": reason_code,
        "text": texts,
    }


def build_next_questions(
    coverage_data: dict,
    delta_data: dict,
    consistency_data: dict,
    limit: int = 3,
):
    questions = []

    missing_fields = coverage_data.get("missing_fields", [])

    for field in missing_fields:
        questions.append(
            build_question(
                variable_code=field,
                priority=1,
                reason_code="MISSING_FIELD",
            )
        )

    if len(questions) >= limit:
        return questions[:limit]

    # Later: delta-based questions
    # Later: consistency-based questions

    return questions[:limit]