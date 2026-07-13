(function () {
  const SUPPORTED = ["ru", "en", "es"];
  const STORAGE_KEY = "platform_language";
  const LEGACY_KEYS = ["health_model_lang"];

  const LABELS = {
    ru: {
      language: "Язык",
      ru: "Русский",
      en: "English",
      es: "Español",
      workspace: "Рабочая область",
      researchLab: "Исследовательская лаборатория",
      analysisBuilder: "Конструктор анализа",
      dataPreparation: "Подготовка данных",
      dataCheck: "Проверка данных",
      scientificResults: "Научные результаты",
      assessment: "Пилот",
      participant: "Участник",
      games: "Исследовательские игры",
      metadata: "Метаданные",
      measurements: "Измерения",
      loaded: "Страница загружена",
      loading: "Загрузка...",
      refresh: "Обновить",
      back: "Назад",
      start: "Начать",
      submit: "Отправить",
      answer: "Ответить",
      open: "Открыть",
      create: "Создать",
      save: "Сохранить",
      dashboard: "Dashboard",
      pilot: "Пилот",
      projects: "Проекты",
      workGroup: "Работа",
      researchGroup: "Исследование",
      independentStudies: "Отдельные исследования",
      assets: "Ресурсы",
      tools: "Инструменты",
      systemGroup: "Система",
      platformMap: "Карта платформы",
      newInvestigation: "Новое исследование",
      workspaceIntro1: "Главный экран для запуска пилота, подготовки данных и исследовательской работы.",
      workspaceIntro2: "Сначала выбери рабочий поток, детали можно открыть ниже.",
      dataPreparationIntro1: "Сначала выберите тип собранных данных. Записи могут приходить из опросников,",
      dataPreparationIntro2: "сенсоров, файлов или measurement packages.",
    },
    en: {
      language: "Language",
      ru: "Русский",
      en: "English",
      es: "Español",
      workspace: "Workspace",
      researchLab: "Research Lab",
      analysisBuilder: "Analysis Builder",
      dataPreparation: "Data Preparation",
      dataCheck: "Data Check",
      scientificResults: "Scientific Results",
      assessment: "Pilot",
      participant: "Participant",
      games: "Research Games",
      metadata: "Metadata",
      measurements: "Measurements",
      loaded: "Page loaded",
      loading: "Loading...",
      refresh: "Refresh",
      back: "Back",
      start: "Start",
      submit: "Submit",
      answer: "Answer",
      open: "Open",
      create: "Create",
      save: "Save",
      dashboard: "Dashboard",
      pilot: "Pilot",
      projects: "Projects",
      workGroup: "Work",
      researchGroup: "Research",
      independentStudies: "Independent studies",
      assets: "Resources",
      tools: "Tools",
      systemGroup: "System",
      platformMap: "Platform map",
      newInvestigation: "New study",
      workspaceIntro1: "Main screen for running the pilot, preparing data, and research work.",
      workspaceIntro2: "Choose a workflow first; details open below.",
      dataPreparationIntro1: "Select the type of collected data first. Records can come from questionnaires,",
      dataPreparationIntro2: "sensors, files, or measurement packages.",
    },
    es: {
      language: "Idioma",
      ru: "Русский",
      en: "English",
      es: "Español",
      workspace: "Espacio de trabajo",
      researchLab: "Laboratorio de investigación",
      analysisBuilder: "Constructor de análisis",
      dataPreparation: "Preparación de datos",
      dataCheck: "Revisión de datos",
      scientificResults: "Resultados científicos",
      assessment: "Piloto",
      participant: "Participante",
      games: "Juegos de investigación",
      metadata: "Metadatos",
      measurements: "Mediciones",
      loaded: "Página cargada",
      loading: "Cargando...",
      refresh: "Actualizar",
      back: "Atrás",
      start: "Empezar",
      submit: "Enviar",
      answer: "Responder",
      open: "Abrir",
      create: "Crear",
      save: "Guardar",
      dashboard: "Dashboard",
      pilot: "Piloto",
      projects: "Proyectos",
      workGroup: "Trabajo",
      researchGroup: "Investigación",
      independentStudies: "Estudios independientes",
      assets: "Recursos",
      tools: "Herramientas",
      systemGroup: "Sistema",
      platformMap: "Mapa de la plataforma",
      newInvestigation: "Nueva investigación",
      workspaceIntro1: "Pantalla principal para ejecutar el piloto, preparar datos y trabajar en la investigación.",
      workspaceIntro2: "Primero elija un flujo; los detalles se abren abajo.",
      dataPreparationIntro1: "Primero seleccione el tipo de datos recopilados. Los registros pueden venir de cuestionarios,",
      dataPreparationIntro2: "sensores, archivos o paquetes de medición.",
    },
  };

  const PHRASES = {
    "Workspace": { ru: "Рабочая область", en: "Workspace", es: "Espacio de trabajo" },
    "Research Workspace": { ru: "Исследовательская платформа", en: "Research Workspace", es: "Plataforma de investigación" },
    "Research Laboratory": { ru: "Исследовательская лаборатория", en: "Research Laboratory", es: "Laboratorio de investigación" },
    "Research Lab": { ru: "Исследовательская лаборатория", en: "Research Lab", es: "Laboratorio de investigación" },
    "Analysis Builder": { ru: "Конструктор анализа", en: "Analysis Builder", es: "Constructor de análisis" },
    "Analysis Check": { ru: "Проверка анализа", en: "Analysis Check", es: "Revisión de análisis" },
    "Data Preparation": { ru: "Подготовка данных", en: "Data Preparation", es: "Preparación de datos" },
    "Research Data Explorer": { ru: "Проводник исследовательских данных", en: "Research Data Explorer", es: "Explorador de datos de investigación" },
    "Data Check": { ru: "Проверка данных", en: "Data Check", es: "Revisión de datos" },
    "Scientific Results": { ru: "Научные результаты", en: "Scientific Results", es: "Resultados científicos" },
    "Research Workbench": { ru: "Исследовательский рабочий стол", en: "Research Workbench", es: "Mesa de trabajo de investigación" },
    "Question Metadata": { ru: "Метаданные вопросов", en: "Question Metadata", es: "Metadatos de preguntas" },
    "Research Games": { ru: "Исследовательские игры", en: "Research Games", es: "Juegos de investigación" },
    "Registered games": { ru: "Зарегистрированные игры", en: "Registered games", es: "Juegos registrados" },
    "Research questions": { ru: "Исследовательские вопросы", en: "Research questions", es: "Preguntas de investigación" },
    "Object catalog": { ru: "Каталог объектов", en: "Object catalog", es: "Catalogo de objetos" },
    "Game session": { ru: "Игровая сессия", en: "Game session", es: "Sesion de juego" },
    "Record event": { ru: "Записать событие", en: "Record event", es: "Registrar evento" },
    "Signal bundle": { ru: "Пакет сигналов", en: "Signal bundle", es: "Paquete de señales" },
    "Start session": { ru: "Начать сессию", en: "Start session", es: "Iniciar sesion" },
    "Mark completed": { ru: "Отметить завершенной", en: "Mark completed", es: "Marcar completada" },
    "Mark abandoned": { ru: "Отметить прерванной", en: "Mark abandoned", es: "Marcar abandonada" },
    "Save event": { ru: "Сохранить событие", en: "Save event", es: "Guardar evento" },
    "No active session.": { ru: "Нет активной сессии.", en: "No active session.", es: "No hay sesion activa." },
    "Participant ID": { ru: "ID участника", en: "Participant ID", es: "ID de participante" },
    "Study ID": { ru: "ID исследования", en: "Study ID", es: "ID del estudio" },
    "Source session ID": { ru: "ID исходной сессии", en: "Source session ID", es: "ID de sesion fuente" },
    "Screen": { ru: "Экран", en: "Screen", es: "Pantalla" },
    "Event type": { ru: "Тип события", en: "Event type", es: "Tipo de evento" },
    "Research question": { ru: "Исследовательский вопрос", en: "Research question", es: "Pregunta de investigación" },
    "Object": { ru: "Объект", en: "Object", es: "Objeto" },
    "Value JSON": { ru: "Значение JSON", en: "Value JSON", es: "Valor JSON" },
    "Decision time, ms": { ru: "Время решения, мс", en: "Decision time, ms", es: "Tiempo de decision, ms" },
    "Confirmation step": { ru: "Шаг подтверждения", en: "Confirmation step", es: "Paso de confirmacion" },
    "Cancel count": { ru: "Количество отмен", en: "Cancel count", es: "Cantidad de cancelaciones" },
    "Excluded from analysis": { ru: "Исключено из анализа", en: "Excluded from analysis", es: "Excluido del analisis" },
    "Open games": { ru: "Открыть игры", en: "Open games", es: "Abrir juegos" },
    "Open resources": { ru: "Открыть ресурсы", en: "Open resources", es: "Abrir recursos" },
    "Open constructor": { ru: "Открыть конструктор", en: "Open constructor", es: "Abrir constructor" },
    "Choose tools": { ru: "Выбрать инструменты", en: "Choose tools", es: "Elegir herramientas" },
    "Create / edit hypotheses": { ru: "Создать / редактировать гипотезы", en: "Create / edit hypotheses", es: "Crear / editar hipotesis" },
    "Записи данных": { ru: "Записи данных", en: "Data records", es: "Registros de datos" },
    "Карта платформы": { ru: "Карта платформы", en: "Platform map", es: "Mapa de la plataforma" },
    "РАБОТА": { ru: "РАБОТА", en: "WORK", es: "TRABAJO" },
    "ИССЛЕДОВАНИЕ": { ru: "ИССЛЕДОВАНИЕ", en: "RESEARCH", es: "INVESTIGACIÓN" },
    "Пилот": { ru: "Пилот", en: "Pilot", es: "Piloto" },
    "Проекты": { ru: "Проекты", en: "Projects", es: "Proyectos" },
    "Обновить": { ru: "Обновить", en: "Refresh", es: "Actualizar" },
    "Записи": { ru: "Записи", en: "Records", es: "Registros" },
    "Анализ": { ru: "Анализ", en: "Analysis", es: "Análisis" },
    "🔄 Обновить": { ru: "🔄 Обновить", en: "🔄 Refresh", es: "🔄 Actualizar" },
    "📄 Записи": { ru: "📄 Записи", en: "📄 Records", es: "📄 Registros" },
    "🧪 Анализ": { ru: "🧪 Анализ", en: "🧪 Analysis", es: "🧪 Análisis" },
    "Технические данные": { ru: "Технические данные", en: "Technical data", es: "Datos técnicos" },
    "Выбранная запись": { ru: "Выбранная запись", en: "Selected record", es: "Registro seleccionado" },
    "Удалить запись": { ru: "Удалить запись", en: "Delete record", es: "Eliminar registro" },
    "Данные": { ru: "Данные", en: "Data", es: "Datos" },
    "Выберите завершённую запись участника. Слева показываются ответы и Prepared Domain Output.": {
      ru: "Выберите завершённую запись участника. Слева показываются ответы и Prepared Domain Output.",
      en: "Choose a completed participant record. Answers and Prepared Domain Output are shown on the left.",
      es: "Seleccione un registro completado del participante. Las respuestas y Prepared Domain Output se muestran a la izquierda."
    },
    "Исследовательский кабинет: snapshots, coverage, UUID → parameter mapping, calculated model parameters.": {
      ru: "Исследовательский кабинет: snapshots, coverage, UUID → parameter mapping, calculated model parameters.",
      en: "Research workbench: snapshots, coverage, UUID → parameter mapping, calculated model parameters.",
      es: "Mesa de investigación: snapshots, coverage, mapeo UUID → parametro y parametros calculados del modelo."
    },
    "Loading research records...": { ru: "Загрузка исследовательских записей...", en: "Loading research records...", es: "Cargando registros de investigación..." },
    "All studies": { ru: "Все исследования", en: "All studies", es: "Todos los estudios" },
    "All statuses": { ru: "Все статусы", en: "All statuses", es: "Todos los estados" },
    "Reload": { ru: "Перезагрузить", en: "Reload", es: "Recargar" },
    "Ready": { ru: "Готово", en: "Ready", es: "Listo" },
    "Dataset records": { ru: "Записи dataset", en: "Dataset records", es: "Registros del dataset" },
    "What would you like to study?": { ru: "Что вы хотите изучить?", en: "What would you like to study?", es: "¿Qué quiere estudiar?" },
    "← Data Preparation": { ru: "← Подготовка данных", en: "← Data Preparation", es: "← Preparación de datos" },
    "Model Explorer": { ru: "Модель", en: "Model Explorer", es: "Explorador del modelo" },
    "Measurements": { ru: "Измерения", en: "Measurements", es: "Mediciones" },
    "Health Model Pilot": { ru: "Пилот Health Model", en: "Health Model Pilot", es: "Piloto Health Model" },
    "Decision Under Uncertainty": { ru: "Принятие решений в условиях неопределенности", en: "Decision Under Uncertainty", es: "Decisión bajo incertidumbre" },
    "Loading...": { ru: "Загрузка...", en: "Loading...", es: "Cargando..." },
    "Page loaded": { ru: "Страница загружена", en: "Page loaded", es: "Página cargada" },
    "Refresh": { ru: "Обновить", en: "Refresh", es: "Actualizar" },
    "Back": { ru: "Назад", en: "Back", es: "Atrás" },
    "Start": { ru: "Начать", en: "Start", es: "Empezar" },
    "Submit": { ru: "Отправить", en: "Submit", es: "Enviar" },
    "Answer": { ru: "Ответить", en: "Answer", es: "Responder" },
    "Ответить": { ru: "Ответить", en: "Answer", es: "Responder" },
    "Назад": { ru: "Назад", en: "Back", es: "Atrás" },
    "Начать": { ru: "Начать", en: "Start", es: "Empezar" },
    "Открыть пилот": { ru: "Открыть пилот", en: "Open pilot", es: "Abrir piloto" },
    "Участник": { ru: "Участник", en: "Participant", es: "Participante" },
    "Измерения": { ru: "Измерения", en: "Measurements", es: "Mediciones" },
    "Отдельные исследования": { ru: "Отдельные исследования", en: "Separate studies", es: "Estudios separados" },
    "Ресурсы": { ru: "Ресурсы", en: "Resources", es: "Recursos" },
    "Инструменты": { ru: "Инструменты", en: "Tools", es: "Herramientas" },
    "Карта платформы": { ru: "Карта платформы", en: "Platform map", es: "Mapa de la plataforma" },
    "Новое исследование": { ru: "Новое исследование", en: "New study", es: "Nuevo estudio" },
    "+ Новое исследование": { ru: "+ Новое исследование", en: "+ New study", es: "+ Nuevo estudio" },
    "Что делаем сейчас?": { ru: "Что делаем сейчас?", en: "What are we doing now?", es: "¿Qué hacemos ahora?" },
    "1. Create / manage research project": { ru: "1. Создать / вести исследовательский проект", en: "1. Create / manage research project", es: "1. Crear / gestionar proyecto de investigación" },
    "Create New Project": { ru: "Создать новый проект", en: "Create New Project", es: "Crear nuevo proyecto" },
    "2. Create / connect instruments and data preparation tools": { ru: "2. Создать / подключить инструменты и подготовку данных", en: "2. Create / connect instruments and data preparation tools", es: "2. Crear / conectar instrumentos y preparación de datos" },
    "Участники и сбор": { ru: "Участники и сбор", en: "Participants and collection", es: "Participantes y recopilación" },
    "Проверка и подготовка данных": { ru: "Проверка и подготовка данных", en: "Data check and preparation", es: "Revisión y preparación de datos" },
    "Исследование и гипотезы": { ru: "Исследование и гипотезы", en: "Research and hypotheses", es: "Investigación e hipótesis" },
    "Question Constructor": { ru: "Конструктор вопросов", en: "Question Constructor", es: "Constructor de preguntas" },
    "Connecting the questionnaire": { ru: "Подключение анкеты", en: "Connecting the questionnaire", es: "Conexión del cuestionario" },
    "Hypotheses": { ru: "Гипотезы", en: "Hypotheses", es: "Hipótesis" },
    "Hypothesis Testing Tools": { ru: "Инструменты проверки гипотез", en: "Hypothesis Testing Tools", es: "Herramientas para probar hipótesis" },
    "Data Preparation Constructor": { ru: "Конструктор подготовки данных", en: "Data Preparation Constructor", es: "Constructor de preparación de datos" },
    "Open participant page": { ru: "Открыть страницу участника", en: "Open participant page", es: "Abrir página del participante" },
    "Open Pilot": { ru: "Открыть пилот", en: "Open Pilot", es: "Abrir piloto" },
    "Open Games": { ru: "Открыть игры", en: "Open Games", es: "Abrir juegos" },
    "Participant Portal": { ru: "Портал участника", en: "Participant Portal", es: "Portal del participante" },
    "Not available in Pilot RC": { ru: "Недоступно в Pilot RC", en: "Not available in Pilot RC", es: "No disponible en Pilot RC" },
    "Internal": { ru: "Внутренний раздел", en: "Internal", es: "Interno" },
    "Opened only after participant session": {
      ru: "Открывается только после сессии участника",
      en: "Opened only after participant session",
      es: "Se abre solo despues de la sesion del participante"
    },
    "Анкеты и измерения: Not available in Pilot RC": {
      ru: "Анкеты и измерения: недоступно в Pilot RC",
      en: "Questionnaires and measurements: Not available in Pilot RC",
      es: "Cuestionarios y mediciones: no disponible en Pilot RC"
    },
    "Research Lab: Not available in Pilot RC": {
      ru: "Research Lab: недоступно в Pilot RC",
      en: "Research Lab: Not available in Pilot RC",
      es: "Research Lab: no disponible en Pilot RC"
    },
    "Model Explorer / Metadata: Not available in Pilot RC": {
      ru: "Model Explorer / Metadata: недоступно в Pilot RC",
      en: "Model Explorer / Metadata: Not available in Pilot RC",
      es: "Model Explorer / Metadata: no disponible en Pilot RC"
    },
    "Open workspace hypotheses": {
      ru: "Открыть гипотезы в Workspace",
      en: "Open workspace hypotheses",
      es: "Abrir hipotesis en Workspace"
    },
    "Open scientific results": {
      ru: "Открыть научные результаты",
      en: "Open scientific results",
      es: "Abrir resultados cientificos"
    },
    "Главный экран для запуска пилота, подготовки данных и исследовательской работы. Сначала выбери рабочий поток, детали можно открыть ниже.": {
      ru: "Главный экран для запуска пилота, подготовки данных и исследовательской работы. Сначала выбери рабочий поток, детали можно открыть ниже.",
      en: "Main screen for running the pilot, preparing data, and research work. Choose a workflow first; details open below.",
      es: "Pantalla principal para ejecutar el piloto, preparar datos y trabajar en la investigación. Primero elija un flujo; los detalles se abren abajo."
    },
    "Главный экран для запуска пилота, подготовки данных и исследовательской работы.": {
      ru: "Главный экран для запуска пилота, подготовки данных и исследовательской работы.",
      en: "Main screen for running the pilot, preparing data, and research work.",
      es: "Pantalla principal para ejecutar el piloto, preparar datos y trabajar en la investigación."
    },
    "Сначала выбери рабочий поток, детали можно открыть ниже.": {
      ru: "Сначала выбери рабочий поток, детали можно открыть ниже.",
      en: "Choose a workflow first; details open below.",
      es: "Primero elija un flujo; los detalles se abren abajo."
    },
    "Пилот — главный приоритет. Исследовательские инструменты рядом, но не мешают первому запуску.": {
      ru: "Пилот — главный приоритет. Исследовательские инструменты рядом, но не мешают первому запуску.",
      en: "The pilot is the priority. Research tools are nearby, but they do not distract from the first launch.",
      es: "El piloto es la prioridad. Las herramientas de investigación están cerca, pero no distraen del primer lanzamiento."
    },
    "1. Сбор": { ru: "1. Сбор", en: "1. Collection", es: "1. Recopilación" },
    "Согласие, анкета, измерения, сессия.": {
      ru: "Согласие, анкета, измерения, сессия.",
      en: "Consent, questionnaire, measurements, session.",
      es: "Consentimiento, cuestionario, mediciones, sesión."
    },
    "2. Проверка": { ru: "2. Проверка", en: "2. Check", es: "2. Revisión" },
    "Покрытие, пропуски, качество данных.": {
      ru: "Покрытие, пропуски, качество данных.",
      en: "Coverage, missing values, data quality.",
      es: "Cobertura, valores faltantes, calidad de datos."
    },
    "3. Подготовка": { ru: "3. Подготовка", en: "3. Preparation", es: "3. Preparación" },
    "Prepared Domain Output и metadata.": {
      ru: "Prepared Domain Output и metadata.",
      en: "Prepared Domain Output and metadata.",
      es: "Prepared Domain Output y metadata."
    },
    "4. Анализ": { ru: "4. Анализ", en: "4. Analysis", es: "4. Análisis" },
    "Гипотезы, пары переменных, методы.": {
      ru: "Гипотезы, пары переменных, методы.",
      en: "Hypotheses, variable pairs, methods.",
      es: "Hipótesis, pares de variables, métodos."
    },
    "5. Результаты": { ru: "5. Результаты", en: "5. Results", es: "5. Resultados" },
    "Scientific results и ограничения.": {
      ru: "Scientific results и ограничения.",
      en: "Scientific results and limitations.",
      es: "Resultados científicos y limitaciones."
    },
    "Всё, что нужно для первого запуска: согласие, анкета, участник, сессия.": {
      ru: "Всё, что нужно для первого запуска: согласие, анкета, участник, сессия.",
      en: "Everything needed for the first launch: consent, questionnaire, participant, session.",
      es: "Todo lo necesario para el primer lanzamiento: consentimiento, cuestionario, participante y sesión."
    },
    "Панель пилота": { ru: "Панель пилота", en: "Pilot panel", es: "Panel del piloto" },
    "Записи сессий и данные, доступные для проверки пилота.": {
      ru: "Записи сессий и данные, доступные для проверки пилота.",
      en: "Session records and data available for pilot review.",
      es: "Registros de sesiones y datos disponibles para revisar el piloto."
    },
    "Проверка записей, покрытие, пропуски и подготовленные представления.": {
      ru: "Проверка записей, покрытие, пропуски и подготовленные представления.",
      en: "Record checks, coverage, missing values, and prepared representations.",
      es: "Revisión de registros, cobertura, valores faltantes y representaciones preparadas."
    },
    "Рабочие гипотезы остаются внутри закрытого workspace; внешний Research Lab не входит в RC.": {
      ru: "Рабочие гипотезы остаются внутри закрытого workspace; внешний Research Lab не входит в RC.",
      en: "Working hypotheses stay inside the closed workspace; the standalone Research Lab is not part of the RC.",
      es: "Las hipótesis de trabajo permanecen dentro del workspace cerrado; Research Lab independiente no forma parte del RC."
    },
    "Внутри Workspace": { ru: "Внутри Workspace", en: "Inside Workspace", es: "Dentro de Workspace" },
    "Сборка анализа, проверка совместимости шкал и метод.": {
      ru: "Сборка анализа, проверка совместимости шкал и метод.",
      en: "Build analysis, check scale compatibility, and select the method.",
      es: "Construir el análisis, revisar compatibilidad de escalas y elegir el método."
    },
    "Результаты проверки доступны; model explorer и metadata остаются внутренними экранами.": {
      ru: "Результаты проверки доступны; model explorer и metadata остаются внутренними экранами.",
      en: "Check results are available; model explorer and metadata remain internal screens.",
      es: "Los resultados de revisión están disponibles; model explorer y metadata siguen siendo pantallas internas."
    },
    "Проверка совместимости двух переменных, их шкал и выбранного метода анализа.": {
      ru: "Проверка совместимости двух переменных, их шкал и выбранного метода анализа.",
      en: "Compatibility check for two variables, their scales, and the selected analysis method.",
      es: "Revisión de compatibilidad de dos variables, sus escalas y el método de análisis seleccionado."
    },
    "Используй это как техническую проверку. Для обычного workflow удобнее идти через Analysis Builder.": {
      ru: "Используй это как техническую проверку. Для обычного workflow удобнее идти через Analysis Builder.",
      en: "Use this as a technical check. For the usual workflow, Analysis Builder is more convenient.",
      es: "Use esto como revisión técnica. Para el flujo habitual, Analysis Builder es más cómodo."
    },
    "Manual check": { ru: "Ручная проверка", en: "Manual check", es: "Revisión manual" },
    "Run check": { ru: "Запустить проверку", en: "Run check", es: "Ejecutar revisión" },
    "Result": { ru: "Результат", en: "Result", es: "Resultado" },
    "No check has been run yet.": {
      ru: "Проверка ещё не запускалась.",
      en: "No check has been run yet.",
      es: "Aún no se ha ejecutado ninguna revisión."
    },
    "Загружаю записи...": { ru: "Загружаю записи...", en: "Loading records...", es: "Cargando registros..." },
    "Выберите завершённую запись слева.": {
      ru: "Выберите завершённую запись слева.",
      en: "Choose a completed record on the left.",
      es: "Seleccione un registro completado a la izquierda."
    },
    "Ошибка загрузки записей.": { ru: "Ошибка загрузки записей.", en: "Failed to load records.", es: "Error al cargar registros." },
    "Ошибка загрузки": { ru: "Ошибка загрузки", en: "Load failed", es: "Error de carga" },
    "Выберите завершённую запись опросника слева.": {
      ru: "Выберите завершённую запись опросника слева.",
      en: "Choose a completed questionnaire record on the left.",
      es: "Seleccione un registro de cuestionario completado a la izquierda."
    },
    "Исследовательский кабинет: snapshots, coverage, UUID → parameter mapping, calculated model parameters.": {
      ru: "Исследовательский кабинет: snapshots, coverage, UUID → parameter mapping, calculated model parameters.",
      en: "Research workspace: snapshots, coverage, UUID-to-parameter mapping, and calculated model parameters.",
      es: "Espacio de investigación: snapshots, cobertura, mapeo UUID a parámetro y parámetros calculados."
    },
    "Researcher Login": { ru: "Вход исследователя", en: "Researcher Login", es: "Acceso de investigador" },
    "Closed Pilot RC researcher access.": {
      ru: "Доступ исследователя к закрытому Pilot RC.",
      en: "Closed Pilot RC researcher access.",
      es: "Acceso de investigador al Pilot RC cerrado."
    },
    "Username": { ru: "Имя пользователя", en: "Username", es: "Usuario" },
    "Password": { ru: "Пароль", en: "Password", es: "Contraseña" },
    "Sign in": { ru: "Войти", en: "Sign in", es: "Entrar" },
    "This agreement applies only to this pilot session and is not approval for unrelated future reuse.": {
      ru: "Это согласие относится только к этой пилотной сессии и не является разрешением на несвязанное будущее использование.",
      en: "This agreement applies only to this pilot session and is not approval for unrelated future reuse.",
      es: "Este acuerdo se aplica solo a esta sesión piloto y no autoriza reutilización futura no relacionada."
    },
    "Результат": { ru: "Результат", en: "Result", es: "Resultado" },
    "Результат сессии": { ru: "Результат сессии", en: "Session result", es: "Resultado de la sesion" },
    "Индивидуальный отчёт": { ru: "Индивидуальный отчёт", en: "Individual report", es: "Informe individual" },
    "Загрузка...": { ru: "Загрузка...", en: "Loading...", es: "Cargando..." },
    "Загрузка результата...": { ru: "Загрузка результата...", en: "Loading result...", es: "Cargando resultado..." },
    "Готово": { ru: "Готово", en: "Ready", es: "Listo" },
    "session_id не найден": { ru: "session_id не найден", en: "session_id not found", es: "session_id no encontrado" },
    "Показан только результат для участника. Технические данные и исследовательские записи здесь не отображаются.": {
      ru: "Показан только результат для участника. Технические данные и исследовательские записи здесь не отображаются.",
      en: "Only the participant-facing result is shown. Technical data and research records are not displayed here.",
      es: "Solo se muestra el resultado para el participante. Los datos tecnicos y los registros de investigacion no se muestran aqui."
    },
    "Неопределённость": { ru: "Неопределённость", en: "Uncertainty", es: "Incertidumbre" },
    "Ограничения": { ru: "Ограничения", en: "Limitations", es: "Limitaciones" },
    "На что стоит обратить внимание": {
      ru: "На что стоит обратить внимание",
      en: "What may need attention",
      es: "A que conviene prestar atencion"
    },
    "Как это может влиять на решения": {
      ru: "Как это может влиять на решения",
      en: "How this may affect decisions",
      es: "Como esto puede influir en las decisiones"
    },
    "Relationship between": { ru: "Связь между", en: "Relationship between", es: "Relación entre" },
    "What would you like to include?": { ru: "Что включить?", en: "What would you like to include?", es: "¿Qué quiere incluir?" },
    "One question": { ru: "Один вопрос", en: "One question", es: "Una pregunta" },
    "Use one questionnaire question.": { ru: "Использовать один вопрос опросника.", en: "Use one questionnaire question.", es: "Usar una pregunta del cuestionario." },
    "Several questions": { ru: "Несколько вопросов", en: "Several questions", es: "Varias preguntas" },
    "Use several selected questions.": { ru: "Использовать несколько выбранных вопросов.", en: "Use several selected questions.", es: "Usar varias preguntas seleccionadas." },
    "Question group": { ru: "Группа вопросов", en: "Question group", es: "Grupo de preguntas" },
    "Use a whole domain, block, or family of questions.": { ru: "Использовать домен, блок или семейство вопросов.", en: "Use a whole domain, block, or family of questions.", es: "Usar un dominio, bloque o familia de preguntas." },
    "Specific answer(s)": { ru: "Конкретные ответы", en: "Specific answer(s)", es: "Respuestas específicas" },
    "Use people who selected specific answers.": { ru: "Использовать участников, выбравших конкретные ответы.", en: "Use people who selected specific answers.", es: "Usar participantes que eligieron respuestas específicas." },
    "Calculated score": { ru: "Рассчитанный показатель", en: "Calculated score", es: "Puntuación calculada" },
    "Use a score calculated from answers.": { ru: "Использовать показатель, рассчитанный из ответов.", en: "Use a score calculated from answers.", es: "Usar una puntuación calculada desde respuestas." },
    "Model indicator": { ru: "Показатель модели", en: "Model indicator", es: "Indicador del modelo" },
    "Use an output from the model.": { ru: "Использовать выходной показатель модели.", en: "Use an output from the model.", es: "Usar una salida del modelo." },
    "Select the type of collected data first. Records can come from questionnaires, sensors, files, or measurement packages.": {
      ru: "Сначала выберите тип собранных данных. Записи могут приходить из опросников, сенсоров, файлов или measurement packages.",
      en: "Select the type of collected data first. Records can come from questionnaires, sensors, files, or measurement packages.",
      es: "Primero seleccione el tipo de datos recopilados. Los registros pueden venir de cuestionarios, sensores, archivos o paquetes de medición."
    },
    "Select the type of collected data first. Records can come from questionnaires,": {
      ru: "Сначала выберите тип собранных данных. Записи могут приходить из опросников,",
      en: "Select the type of collected data first. Records can come from questionnaires,",
      es: "Primero seleccione el tipo de datos recopilados. Los registros pueden venir de cuestionarios,"
    },
    "sensors, files, or measurement packages.": {
      ru: "сенсоров, файлов или measurement packages.",
      en: "sensors, files, or measurement packages.",
      es: "sensores, archivos o paquetes de medición."
    },
    "Seleccione idioma / Choose language / Выберите язык": {
      ru: "Выберите язык",
      en: "Choose language",
      es: "Seleccione idioma"
    },
    "Left question code": { ru: "Код левого вопроса", en: "Left question code", es: "Código de pregunta izquierda" },
    "Right question code": { ru: "Код правого вопроса", en: "Right question code", es: "Código de pregunta derecha" },
    "Method ID": { ru: "ID метода", en: "Method ID", es: "ID del método" },
    "Files": { ru: "Файлы", en: "Files", es: "Archivos" },
    "📄 Files": { ru: "📄 Файлы", en: "📄 Files", es: "📄 Archivos" },
    "🧪 Measurements": { ru: "🧪 Измерения", en: "🧪 Measurements", es: "🧪 Mediciones" },
    "Ready only": { ru: "Только готовые", en: "Ready only", es: "Solo listos" },
    "No records match the selected filters.": {
      ru: "Нет записей по выбранным фильтрам.",
      en: "No records match the selected filters.",
      es: "No hay registros para los filtros seleccionados."
    },
    "Analysis catalog is not available.": {
      ru: "Каталог анализа недоступен.",
      en: "Analysis catalog is not available.",
      es: "El catálogo de análisis no está disponible."
    },
    "No questions available for validation.": {
      ru: "Нет вопросов для проверки.",
      en: "No questions available for validation.",
      es: "No hay preguntas disponibles para validación."
    },
    "After selecting a record on the left, no study questions were found for statistical method validation.": {
      ru: "После выбора записи слева вопросы исследования для проверки статистического метода не найдены.",
      en: "After selecting a record on the left, no study questions were found for statistical method validation.",
      es: "Después de seleccionar un registro a la izquierda, no se encontraron preguntas del estudio para validar el método estadístico."
    },
    "Open data record": { ru: "Открыть запись данных", en: "Open data record", es: "Abrir registro de datos" },
    "Record is not ready yet": { ru: "Запись ещё не готова", en: "Record is not ready yet", es: "El registro aún no está listo" },
    "ready": { ru: "готово", en: "ready", es: "listo" },
    "not ready": { ru: "не готово", en: "not ready", es: "no listo" },
    "Source": { ru: "Источник", en: "Source", es: "Fuente" },
    "Answers": { ru: "Ответы", en: "Answers", es: "Respuestas" },
    "Status": { ru: "Статус", en: "Status", es: "Estado" },
    "Created": { ru: "Создано", en: "Created", es: "Creado" },
    "Question 1": { ru: "Вопрос 1", en: "Question 1", es: "Pregunta 1" },
    "Question 2": { ru: "Вопрос 2", en: "Question 2", es: "Pregunta 2" },
    "Select question": { ru: "Выберите вопрос", en: "Select question", es: "Seleccione pregunta" },
    "Choose data": { ru: "Выбрать данные", en: "Choose data", es: "Elegir datos" },
    "Open Preparation": { ru: "Открыть подготовку", en: "Open Preparation", es: "Abrir preparación" },
    "Selected method": { ru: "Выбранный метод", en: "Selected method", es: "Método seleccionado" },
    "All": { ru: "Все", en: "All", es: "Todo" },
    "🌐 All": { ru: "🌐 Все", en: "🌐 All", es: "🌐 Todo" },
    "Model Parameters": { ru: "Параметры модели", en: "Model Parameters", es: "Parámetros del modelo" },
    "🧮 Model Parameters": { ru: "🧮 Параметры модели", en: "🧮 Model Parameters", es: "🧮 Parámetros del modelo" },
    "Questionnaires": { ru: "Опросники", en: "Questionnaires", es: "Cuestionarios" },
    "📋 Questionnaires": { ru: "📋 Опросники", en: "📋 Questionnaires", es: "📋 Cuestionarios" },
    "Sensors": { ru: "Сенсоры", en: "Sensors", es: "Sensores" },
    "🎥 Sensors": { ru: "🎥 Сенсоры", en: "🎥 Sensors", es: "🎥 Sensores" },
    "⚠ Preparation required": { ru: "⚠ Требуется подготовка", en: "⚠ Preparation required", es: "⚠ Se requiere preparación" },
    "Research records": { ru: "Исследовательские записи", en: "Research records", es: "Registros de investigación" },
    "Calculated model parameters": { ru: "Рассчитанные параметры модели", en: "Calculated model parameters", es: "Parámetros calculados del modelo" },
    "Question UUID → model parameter mapping": { ru: "Связь UUID вопроса → параметр модели", en: "Question UUID → model parameter mapping", es: "Mapeo UUID de pregunta → parámetro del modelo" },
    "Coverage / missing data": { ru: "Покрытие / недостающие данные", en: "Coverage / missing data", es: "Cobertura / datos faltantes" },
    "Parameter statistics": { ru: "Статистика параметров", en: "Parameter statistics", es: "Estadísticas de parámetros" },
    "Raw selected research snapshot": { ru: "Исходный снимок выбранного исследования", en: "Raw selected research snapshot", es: "Instantánea sin procesar de la investigación seleccionada" },
    "Copy JSON": { ru: "Копировать JSON", en: "Copy JSON", es: "Copiar JSON" },
    "Provided inputs": { ru: "Переданные входы", en: "Provided inputs", es: "Entradas proporcionadas" },
    "Missing critical data": { ru: "Нет критических данных", en: "Missing critical data", es: "Faltan datos críticos" },
    "Missing required data": { ru: "Нет обязательных данных", en: "Missing required data", es: "Faltan datos requeridos" },
    "Connected Games": { ru: "Подключённые игры", en: "Connected Games", es: "Juegos conectados" },
    "What stays in Research OS / Pilot": { ru: "Что остаётся в Research OS / Pilot", en: "What stays in Research OS / Pilot", es: "Que queda en Research OS / Pilot" },
    "Принятие решений в условиях неопределенности": { ru: "Принятие решений в условиях неопределенности", en: "Decision Under Uncertainty", es: "Decisión bajo incertidumbre" },
  };

  for (const sourcePhrase of Object.keys({ ...PHRASES })) {
    const variants = PHRASES[sourcePhrase];
    for (const translatedPhrase of Object.values(variants)) {
      if (translatedPhrase && !PHRASES[translatedPhrase]) {
        PHRASES[translatedPhrase] = variants;
      }
    }
  }

  function normalize(value) {
    const lang = String(value || "").slice(0, 2).toLowerCase();
    return SUPPORTED.includes(lang) ? lang : null;
  }

  function readInitialLanguage() {
    const params = new URLSearchParams(window.location.search);
    const fromUrl = normalize(params.get("lang") || params.get("language"));
    if (fromUrl) return fromUrl;

    const fromStorage = normalize(localStorage.getItem(STORAGE_KEY));
    if (fromStorage) return fromStorage;

    for (const key of LEGACY_KEYS) {
      const legacy = normalize(localStorage.getItem(key));
      if (legacy) return legacy;
    }

    return normalize(document.documentElement.lang) || "ru";
  }

  let currentLanguage = readInitialLanguage();

  function t(key) {
    return LABELS[currentLanguage]?.[key] || LABELS.ru[key] || key;
  }

  function register(dictionary = {}) {
    for (const [sourcePhrase, variants] of Object.entries(dictionary)) {
      if (!variants || typeof variants !== "object") continue;
      PHRASES[sourcePhrase] = { ...PHRASES[sourcePhrase], ...variants };
      for (const translatedPhrase of Object.values(variants)) {
        if (translatedPhrase && !PHRASES[translatedPhrase]) {
          PHRASES[translatedPhrase] = PHRASES[sourcePhrase];
        }
      }
    }
    apply();
  }

  function translate(value) {
    const phrase = PHRASES[String(value || "").trim()];
    return phrase?.[currentLanguage] || value;
  }

  function withLanguage(url, paramName) {
    try {
      const parsed = new URL(url, window.location.origin);
      if (parsed.origin !== window.location.origin) return url;
      const path = parsed.pathname;
      const name = paramName || (
        path === "/research/entities" || path === "/du/first-question"
          ? "language"
          : "lang"
      );

      if (parsed.searchParams.has("language")) {
        parsed.searchParams.set("language", currentLanguage);
      } else if (parsed.searchParams.has("lang")) {
        parsed.searchParams.set("lang", currentLanguage);
      } else {
        parsed.searchParams.set(name, currentLanguage);
      }

      return parsed.pathname + parsed.search + parsed.hash;
    } catch {
      return url;
    }
  }

  function syncStorage() {
    localStorage.setItem(STORAGE_KEY, currentLanguage);
    localStorage.setItem("health_model_lang", currentLanguage);
  }

  function setLanguage(lang, options = {}) {
    const next = normalize(lang) || "ru";
    currentLanguage = next;
    syncStorage();
    document.documentElement.lang = next;
    apply();

    window.dispatchEvent(new CustomEvent("platform-language-change", {
      detail: { language: next },
    }));

    if (options.reload) {
      const nextUrl = withLanguage(window.location.href);
      window.location.href = nextUrl;
    }
  }

  function translateTextNode(node) {
    const raw = node.nodeValue;
    const trimmed = raw.trim();
    if (!trimmed || !PHRASES[trimmed]) return;
    const translated = PHRASES[trimmed][currentLanguage];
    if (!translated) return;
    node.nodeValue = raw.replace(trimmed, translated);
  }

  function translateStaticText(root = document.body) {
    if (!root) return;

    root.querySelectorAll("[data-i18n]").forEach((el) => {
      const key = el.getAttribute("data-i18n");
      const value = LABELS[currentLanguage]?.[key];
      if (value) el.textContent = value;
    });

    const walker = document.createTreeWalker(
      root,
      NodeFilter.SHOW_TEXT,
      {
        acceptNode(node) {
          const parent = node.parentElement;
          if (!parent) return NodeFilter.FILTER_REJECT;
          if (["SCRIPT", "STYLE", "TEXTAREA", "INPUT", "OPTION"].includes(parent.tagName)) {
            return NodeFilter.FILTER_REJECT;
          }
          if (parent.closest("[data-i18n-skip]")) return NodeFilter.FILTER_REJECT;
          return NodeFilter.FILTER_ACCEPT;
        },
      }
    );

    const nodes = [];
    while (walker.nextNode()) nodes.push(walker.currentNode);
    nodes.forEach(translateTextNode);

    document.querySelectorAll("[placeholder]").forEach((el) => {
      const phrase = PHRASES[el.getAttribute("placeholder")];
      if (phrase?.[currentLanguage]) el.setAttribute("placeholder", phrase[currentLanguage]);
    });
  }

  function installSwitcher() {
    if (document.getElementById("platformLanguageSwitcher")) return;

    const box = document.createElement("div");
    box.id = "platformLanguageSwitcher";
    box.setAttribute("data-i18n-skip", "true");
    box.innerHTML = `
      <span class="platform-language-label"></span>
      <button type="button" data-lang="ru">RU</button>
      <button type="button" data-lang="en">EN</button>
      <button type="button" data-lang="es">ES</button>
    `;

    const style = document.createElement("style");
    style.textContent = `
      #platformLanguageSwitcher {
        position: fixed;
        top: 12px;
        right: 12px;
        z-index: 9999;
        display: flex;
        align-items: center;
        gap: 6px;
        padding: 6px 8px;
        border: 1px solid rgba(120, 130, 150, 0.35);
        border-radius: 8px;
        background: rgba(255, 255, 255, 0.94);
        box-shadow: 0 8px 24px rgba(15, 23, 42, 0.12);
        font: 12px/1.2 Arial, sans-serif;
      }
      #platformLanguageSwitcher button {
        width: 34px;
        min-width: 34px;
        padding: 5px 0;
        margin: 0;
        border: 1px solid #d6dbe6;
        border-radius: 6px;
        background: #fff;
        color: #253047;
        cursor: pointer;
        font: 700 11px/1 Arial, sans-serif;
      }
      #platformLanguageSwitcher button.is-active {
        background: #253047;
        color: #fff;
        border-color: #253047;
      }
      .platform-language-label {
        color: #536078;
        white-space: nowrap;
      }
      @media (max-width: 680px) {
        #platformLanguageSwitcher {
          top: auto;
          right: 10px;
          bottom: 10px;
        }
        .platform-language-label {
          display: none;
        }
      }
    `;

    document.head.appendChild(style);
    document.body.appendChild(box);

    box.addEventListener("click", (event) => {
      const button = event.target.closest("button[data-lang]");
      if (!button) return;
      setLanguage(button.dataset.lang, { reload: false });
    });
  }

  function syncSwitcher() {
    const box = document.getElementById("platformLanguageSwitcher");
    if (!box) return;
    box.querySelector(".platform-language-label").textContent = t("language");
    box.querySelectorAll("button[data-lang]").forEach((button) => {
      button.classList.toggle("is-active", button.dataset.lang === currentLanguage);
      button.title = LABELS[currentLanguage]?.[button.dataset.lang] || button.dataset.lang;
    });
  }

  function syncLinks(root = document) {
    root.querySelectorAll("a[href^='/']").forEach((link) => {
      link.setAttribute("href", withLanguage(link.getAttribute("href")));
    });
  }

  function patchFetch() {
    if (window.__platformLanguageFetchPatched) return;
    window.__platformLanguageFetchPatched = true;
    const nativeFetch = window.fetch.bind(window);

    window.fetch = function (input, init = {}) {
      if (typeof input === "string") {
        input = withLanguage(input);
      } else if (input instanceof Request) {
        input = new Request(withLanguage(input.url), input);
      }

      if (init && typeof init.body === "string") {
        const contentType = init.headers?.["Content-Type"] || init.headers?.get?.("Content-Type") || "";
        if (contentType.includes("application/json")) {
          try {
            const body = JSON.parse(init.body);
            if (body && typeof body === "object" && !Array.isArray(body)) {
              if ("language" in body && !body.language) body.language = currentLanguage;
              if ("preferred_language" in body && !body.preferred_language) body.preferred_language = currentLanguage;
              init = { ...init, body: JSON.stringify(body) };
            }
          } catch {
            // Keep original request body.
          }
        }
      }

      return nativeFetch(input, init);
    };
  }

  function apply() {
    document.documentElement.lang = currentLanguage;
    document.title = translate(document.title);
    syncSwitcher();
    syncLinks();
    translateStaticText();
  }

  window.PlatformLanguage = {
    supported: SUPPORTED.slice(),
    get: () => currentLanguage,
    set: setLanguage,
    t,
    translate,
    register,
    withLanguage,
    apply,
    refresh: apply,
  };

  syncStorage();
  patchFetch();

  document.addEventListener("DOMContentLoaded", () => {
    installSwitcher();
    apply();
  });
})();
