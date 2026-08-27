export type Locale = "kk" | "ru" | "en";
export const SUPPORTED_LOCALES: Locale[] = ["kk", "ru", "en"];
export const DEFAULT_LOCALE: Locale = "kk";

export interface Translations {
  nav: {
    dashboard: string;
    learn: string;
    practice: string;
    coding: string;
    news: string;
    untInfo: string;
    missions: string;
    leaderboard: string;
    achievements: string;
    profile: string;
    settings: string;
    admin: string;
    login: string;
    register: string;
    logout: string;
  };
  common: {
    loading: string;
    searchPlaceholder: string;
    filterBy: string;
    all: string;
    source: string;
    verified: string;
    official: string;
    sample: string;
    points: string;
    difficulty: string;
    level: string;
    streak: string;
    details: string;
    viewAll: string;
    tryAgain: string;
    close: string;
  };
  auth: {
    loginTitle: string;
    loginSubtitle: string;
    registerTitle: string;
    registerSubtitle: string;
    emailLabel: string;
    emailPlaceholder: string;
    passwordLabel: string;
    passwordPlaceholder: string;
    displayNameLabel: string;
    displayNamePlaceholder: string;
    targetScoreLabel: string;
    loginButton: string;
    loggingIn: string;
    registerButton: string;
    registering: string;
    quickDemoTitle: string;
    demoStudent: string;
    demoAdmin: string;
    noAccountPrompt: string;
    registerLink: string;
    hasAccountPrompt: string;
    loginLink: string;
    orDivider: string;
    passwordMinLength: string;
    setPasswordTitle: string;
    setPasswordSubtitle: string;
    newPasswordLabel: string;
    newPasswordPlaceholder: string;
    setPasswordButton: string;
    passwordSetSuccess: string;
  };
  oauth: {
    googleSignIn: string;
    googleSignUp: string;
    connectingGoogle: string;
    redirecting: string;
    authenticating: string;
    callbackTitle: string;
    callbackPreparing: string;
    callbackSuccess: string;
    errorTitle: string;
    errorSubtitle: string;
    retryButton: string;
    homeButton: string;
    accountLinkedNotice: string;
    secureAuthBadge: string;
  };
  errors: {
    AUTH_INVALID_CREDENTIALS: string;
    AUTH_USER_NOT_FOUND: string;
    AUTH_USER_INACTIVE: string;
    AUTH_PASSWORD_NOT_SET: string;
    AUTH_EMAIL_ALREADY_EXISTS: string;
    AUTH_OAUTH_INIT_FAILED: string;
    AUTH_OAUTH_STATE_INVALID: string;
    AUTH_OAUTH_STATE_EXPIRED: string;
    AUTH_OAUTH_CODE_EXCHANGE_FAILED: string;
    AUTH_OAUTH_EMAIL_UNVERIFIED: string;
    AUTH_SESSION_EXPIRED: string;
    AUTH_SESSION_REVOKED: string;
    AUTH_SESSION_REUSE_DETECTED: string;
    AUTH_UNAUTHORIZED: string;
    AUTH_FORBIDDEN: string;
    AUTH_INVALID_REDIRECT_URI: string;
    AUTH_CANNOT_UNLINK_LAST_PROVIDER: string;
    defaultError: string;
    networkError: string;
    unknownError: string;
  };
  news: {
    title: string;
    subtitle: string;
    breakingAlert: string;
    categories: {
      all: string;
      unt: string;
      registration: string;
      grants: string;
      informatics: string;
      deadlines: string;
    };
    sourceAttribution: string;
    readMore: string;
    noNews: string;
  };
  untKnowledge: {
    title: string;
    subtitle: string;
    examStructure: string;
    questionsCount: string;
    maxScore: string;
    duration: string;
    passingThreshold: string;
    itPrograms: string;
    testingWindows: string;
    specifications: string;
  };
  questionBank: {
    title: string;
    subtitle: string;
    exploreByTopic: string;
    allDifficulties: string;
    easy: string;
    medium: string;
    hard: string;
    officialProvenance: string;
    viewSolution: string;
    examTip: string;
  };
}
export const i18nDict: Record<Locale, Translations> = {
  kk: {
    nav: {
      dashboard: "Дашборд",
      learn: "Оқу бағдарламасы",
      practice: "ҰБТ Тренажері",
      coding: "Python тапсырмалары",
      news: "ҰБТ Жаңалықтары",
      untInfo: "ҰБТ Ережелері 2026",
      missions: "Күнделікті квесттер",
      leaderboard: "Көшбасшылар",
      achievements: "Жетістіктер",
      profile: "Аналитика",
      settings: "Баптаулар",
      admin: "Әкімшілік",
      login: "Кіру",
      register: "Тіркелу",
      logout: "Шығу",
    },
    common: {
      loading: "Жүктелуде...",
      searchPlaceholder: "Іздеу...",
      filterBy: "Сүзгілеу",
      all: "Барлығы",
      source: "Дереккөз",
      verified: "Тексерілген",
      official: "Ресми ҰТО",
      sample: "Байқау үлгісі",
      points: "балл",
      difficulty: "Күрделілігі",
      level: "Деңгей",
      streak: "күн қатарынан",
      details: "Толығырақ",
      viewAll: "Барлығын көру",
      tryAgain: "Қайта көру",
      close: "Жабу",
    },
    auth: {
      loginTitle: "Аккаунтқа кіру",
      loginSubtitle: "ҰБТ-ға дайындықты жалғастырыңыз және стрикіңізді сақтаңыз",
      registerTitle: "Жүйеге тіркелу",
      registerSubtitle: "Профиль жасап, ҰБТ-да 50 баллға жету жолын бастаңыз",
      emailLabel: "Email мекенжайы",
      emailPlaceholder: "student@example.com",
      passwordLabel: "Құпиясөз",
      passwordPlaceholder: "••••••••",
      displayNameLabel: "Сіздің есіміңіз немесе лақап атыңыз",
      displayNamePlaceholder: "Әлихан Нұрланов",
      targetScoreLabel: "ҰБТ-дағы мақсатты балл",
      loginButton: "Жүйеге кіру",
      loggingIn: "Авторизация...",
      registerButton: "Аккаунт жасау",
      registering: "Тіркелу жүруде...",
      quickDemoTitle: "Тестілеу үшін жылдам кіру:",
      demoStudent: "Оқушы (student@...)",
      demoAdmin: "Әкімшілік",
      noAccountPrompt: "Әлі аккаунтыңыз жоқ па?",
      registerLink: "Тіркелу",
      hasAccountPrompt: "Тіркеліп қойғансыз ба?",
      loginLink: "Жүйеге кіру",
      orDivider: "немесе",
      passwordMinLength: "Құпиясөз (кемінде 6 таңба)",
      setPasswordTitle: "Құпиясөз орнату",
      setPasswordSubtitle: "Аккаунтқа тікелей кіру үшін тұрақты құпиясөз орнатыңыз",
      newPasswordLabel: "Жаңа құпиясөз",
      newPasswordPlaceholder: "Кемінде 8 таңба",
      setPasswordButton: "Құпиясөзді сақтау",
      passwordSetSuccess: "Құпиясөз сәтті орнатылды!",
    },
    oauth: {
      googleSignIn: "Google арқылы кіру",
      googleSignUp: "Google арқылы тіркелу",
      connectingGoogle: "Google-ге бағытталуда...",
      redirecting: "Қайта бағытталуда...",
      authenticating: "Google арқылы кіру тексерілуде...",
      callbackTitle: "Сәтті авторизация!",
      callbackPreparing: "Оқу кеңістігіңіз дайындалуда, бір сәт күтіңіз...",
      callbackSuccess: "Сіз жүйеге сәтті кірдіңіз!",
      errorTitle: "Авторизация қатесі",
      errorSubtitle: "Жүйеге кіру кезінде қате орын алды",
      retryButton: "Қайта көру",
      homeButton: "Басты бетке оралу",
      accountLinkedNotice: "Google аккаунтыңыз сәтті байланыстырылды",
      secureAuthBadge: "Қауіпсіз OAuth 2.0 PKCE қорғауы",
    },
    errors: {
      AUTH_INVALID_CREDENTIALS: "Email немесе құпиясөз қате",
      AUTH_USER_NOT_FOUND: "Пайдаланушы табылмады",
      AUTH_USER_INACTIVE: "Сіздің аккаунтыңыз бұғатталған",
      AUTH_PASSWORD_NOT_SET: "Аккаунтқа құпиясөз орнатылмаған. Google арқылы кіріңіз немесе кіруді қалпына келтіріңіз",
      AUTH_EMAIL_ALREADY_EXISTS: "Бұл email бар пайдаланушы тіркелген",
      AUTH_OAUTH_INIT_FAILED: "Google OAuth инициализациясының қатесі",
      AUTH_OAUTH_STATE_INVALID: "Авторизация сессиясының қолтаңбасы жарамсыз",
      AUTH_OAUTH_STATE_EXPIRED: "Авторизацияны күту уақыты аяқталды (10 мин). Қайталап көріңіз",
      AUTH_OAUTH_CODE_EXCHANGE_FAILED: "Google авторизация кодын алмасу қатесі",
      AUTH_OAUTH_EMAIL_UNVERIFIED: "Google аккаунтындағы email расталмаған. Байланыстыру мүмкін емес",
      AUTH_SESSION_EXPIRED: "Сессия аяқталды. Қайта кіруіңізді сұраймыз",
      AUTH_SESSION_REVOKED: "Сессия кері қайтарылды",
      AUTH_SESSION_REUSE_DETECTED: "Сессияны қайталап пайдалану әрекеті анықталды. Қауіпсіздік үшін барлық құрылғылар ажыратылды",
      AUTH_UNAUTHORIZED: "Авторизация қажет",
      AUTH_FORBIDDEN: "Қолжетімділікке тыйым салынған",
      AUTH_INVALID_REDIRECT_URI: "Рұқсат етілмеген қайта бағыттау мекенжайы",
      AUTH_CANNOT_UNLINK_LAST_PROVIDER: "Жалғыз кіру әдісін ажыратуға болмайды",
      defaultError: "Авторизация кезінде қате орын алды",
      networkError: "Желілік байланыс қатесі немесе сервер жауап бермеді",
      unknownError: "Белгісіз қате",
    },
    news: {
      title: "ҰБТ / ЕНТ Ресми Жаңалықтары",
      subtitle: "ҚР Ғылым және жоғары білім министрлігі мен Ұлттық тестілеу орталығының күнделікті тексерілген ақпараты",
      breakingAlert: "Шұғыл хабарландыру",
      categories: {
        all: "Барлық жаңалықтар",
        unt: "ҰБТ барысы",
        registration: "Тіркелу және мерзімдер",
        grants: "Грант байқауы",
        informatics: "Информатика спецификациясы",
        deadlines: "Маңызды дедлайндар",
      },
      sourceAttribution: "Ресми дереккөз",
      readMore: "Толық оқу",
      noNews: "Бұл санат бойынша жаңалықтар табылмады.",
    },
    untKnowledge: {
      title: "2026 жылғы ҰБТ Құрылымы мен Ережелері",
      subtitle: "Информатика пәні талапкерлеріне арналған ресми көрсеткіштер мен грант талаптары",
      examStructure: "Емтихан құрылымы",
      questionsCount: "120 сұрақ (бейіндік: 50 сұрақ)",
      maxScore: "140 балл (бейіндік: 50 балл)",
      duration: "240 минут (4 сағат)",
      passingThreshold: "Шекті балл: 50 балл (әр пәннен кемі 5 балл)",
      itPrograms: "IT мамандықтары бойынша гранттық диапазон: 115 — 138 балл",
      testingWindows: "Тестілеу кезеңдері",
      specifications: "Информатика пәнінің тест спецификациясы",
    },
    questionBank: {
      title: "Информатика Банкі және Провенанс",
      subtitle: "ҰТО ресми спецификациясына сай верификацияланған сұрақтар мен талдаулар",
      exploreByTopic: "Бөлімдер мен тақырыптар бойынша шолу",
      allDifficulties: "Барлық деңгейлер",
      easy: "А — Базалық",
      medium: "В — Орташа",
      hard: "С — Жоғары",
      officialProvenance: "Сұрақтың шығу тегі (Provenance)",
      viewSolution: "Қадамдық шешімін көру",
      examTip: "ҰБТ лайфхагы / Ескертпе",
    },
  },
  ru: {
    nav: {
      dashboard: "Дашборд",
      learn: "Обучение",
      practice: "Тренажер ЕНТ",
      coding: "Задачи Python",
      news: "Новости ЕНТ",
      untInfo: "Правила ЕНТ 2026",
      missions: "Квесты",
      leaderboard: "Лидерборд",
      achievements: "Достижения",
      profile: "Аналитика",
      settings: "Настройки",
      admin: "Админ-панель",
      login: "Войти",
      register: "Регистрация",
      logout: "Выйти",
    },
    common: {
      loading: "Загрузка...",
      searchPlaceholder: "Поиск...",
      filterBy: "Фильтр",
      all: "Все",
      source: "Источник",
      verified: "Верифицировано",
      official: "Официально НЦТ",
      sample: "Пробный образец",
      points: "балл(ов)",
      difficulty: "Сложность",
      level: "Уровень",
      streak: "дней подряд",
      details: "Подробнее",
      viewAll: "Смотреть все",
      tryAgain: "Попробовать снова",
      close: "Закрыть",
    },
    auth: {
      loginTitle: "Вход в аккаунт",
      loginSubtitle: "Продолжите подготовку к ЕНТ и сохраняйте свой стрик",
      registerTitle: "Регистрация в системе",
      registerSubtitle: "Создайте профиль и начните путь к 50 баллам на ЕНТ",
      emailLabel: "Email адрес",
      emailPlaceholder: "student@example.com",
      passwordLabel: "Пароль",
      passwordPlaceholder: "••••••••",
      displayNameLabel: "Ваше имя или никнейм",
      displayNamePlaceholder: "Алихан Нурланов",
      targetScoreLabel: "Целевой балл на ЕНТ",
      loginButton: "Войти в систему",
      loggingIn: "Авторизация...",
      registerButton: "Создать аккаунт",
      registering: "Создание аккаунта...",
      quickDemoTitle: "Быстрый вход для тестирования:",
      demoStudent: "Ученик (student@...)",
      demoAdmin: "Администратор",
      noAccountPrompt: "Еще нет аккаунта?",
      registerLink: "Зарегистрироваться",
      hasAccountPrompt: "Уже зарегистрированы?",
      loginLink: "Войти в систему",
      orDivider: "или",
      passwordMinLength: "Пароль (от 6 символов)",
      setPasswordTitle: "Установка пароля",
      setPasswordSubtitle: "Задайте постоянный пароль для прямого входа в аккаунт",
      newPasswordLabel: "Новый пароль",
      newPasswordPlaceholder: "Не менее 8 символов",
      setPasswordButton: "Сохранить пароль",
      passwordSetSuccess: "Пароль успешно установлен!",
    },
    oauth: {
      googleSignIn: "Войти через Google",
      googleSignUp: "Зарегистрироваться через Google",
      connectingGoogle: "Переход в Google...",
      redirecting: "Перенаправление...",
      authenticating: "Проверка авторизации Google...",
      callbackTitle: "Успешная авторизация!",
      callbackPreparing: "Подготовка вашего учебного пространства, пожалуйста, подождите...",
      callbackSuccess: "Вы успешно вошли в систему!",
      errorTitle: "Ошибка авторизации",
      errorSubtitle: "Не удалось выполнить вход в систему",
      retryButton: "Попробовать снова",
      homeButton: "На главную",
      accountLinkedNotice: "Google-аккаунт успешно привязан",
      secureAuthBadge: "Защищено протоколом OAuth 2.0 PKCE",
    },
    errors: {
      AUTH_INVALID_CREDENTIALS: "Неверный email или пароль",
      AUTH_USER_NOT_FOUND: "Пользователь не найден",
      AUTH_USER_INACTIVE: "Ваш аккаунт деактивирован",
      AUTH_PASSWORD_NOT_SET: "Для аккаунта не задан пароль. Войдите через Google или воспользуйтесь восстановлением доступа",
      AUTH_EMAIL_ALREADY_EXISTS: "Пользователь с таким email уже зарегистрирован",
      AUTH_OAUTH_INIT_FAILED: "Ошибка инициализации Google OAuth",
      AUTH_OAUTH_STATE_INVALID: "Недействительная подпись сессии авторизации",
      AUTH_OAUTH_STATE_EXPIRED: "Время ожидания авторизации истекло (10 мин). Повторите попытку",
      AUTH_OAUTH_CODE_EXCHANGE_FAILED: "Ошибка обмена авторизационного кода Google",
      AUTH_OAUTH_EMAIL_UNVERIFIED: "Email в аккаунте Google не подтвержден. Привязка невозможна",
      AUTH_SESSION_EXPIRED: "Сессия завершена. Пожалуйста, выполните повторный вход",
      AUTH_SESSION_REVOKED: "Сессия была отозвана",
      AUTH_SESSION_REUSE_DETECTED: "Обнаружена попытка повторного использования сессии. Все устройства отключены в целях безопасности",
      AUTH_UNAUTHORIZED: "Требуется авторизация",
      AUTH_FORBIDDEN: "Доступ запрещен",
      AUTH_INVALID_REDIRECT_URI: "Недопустимый адрес перенаправления",
      AUTH_CANNOT_UNLINK_LAST_PROVIDER: "Нельзя отвязать единственный способ входа",
      defaultError: "Произошла ошибка при аутентификации",
      networkError: "Ошибка сети или сервер недоступен",
      unknownError: "Неизвестная ошибка",
    },
    news: {
      title: "Официальные новости ЕНТ / ҰБТ",
      subtitle: "Ежедневно верифицированная информация Национального центра тестирования и МНВО РК",
      breakingAlert: "Срочное объявление",
      categories: {
        all: "Все новости",
        unt: "Ход ЕНТ",
        registration: "Регистрация и сроки",
        grants: "Конкурс грантов",
        informatics: "Спецификация Информатики",
        deadlines: "Важные дедлайны",
      },
      sourceAttribution: "Первоисточник",
      readMore: "Читать полностью",
      noNews: "Новостей в данной категории не найдено.",
    },
    untKnowledge: {
      title: "Структура и правила ЕНТ 2026",
      subtitle: "Официальные регламенты и проходные баллы для поступающих на IT-специальности",
      examStructure: "Структура экзамена",
      questionsCount: "120 вопросов (профиль: 50 вопросов)",
      maxScore: "140 баллов (профиль: 50 баллов)",
      duration: "240 минут (4 часа)",
      passingThreshold: "Пороговый балл: 50 баллов (минимум 5 по предмету)",
      itPrograms: "Конкурсный диапазон грантов IT: 115 — 138 баллов",
      testingWindows: "Периоды тестирования",
      specifications: "Спецификация теста по Информатике",
    },
    questionBank: {
      title: "Банк вопросов Информатики",
      subtitle: "Верифицированные задачи по спецификации НЦТ с разборами и провенансом",
      exploreByTopic: "Обзор по разделам и темам",
      allDifficulties: "Все уровни сложности",
      easy: "А — Базовый",
      medium: "В — Средний",
      hard: "С — Сложный",
      officialProvenance: "Происхождение вопроса (Provenance)",
      viewSolution: "Пошаговый разбор",
      examTip: "Совет / Ловушка ЕНТ",
    },
  },
  en: {
    nav: {
      dashboard: "Dashboard",
      learn: "Curriculum",
      practice: "UNT Practice",
      coding: "Python Coding",
      news: "UNT News",
      untInfo: "UNT 2026 Rules",
      missions: "Daily Quests",
      leaderboard: "Leaderboard",
      achievements: "Achievements",
      profile: "Analytics",
      settings: "Settings",
      admin: "Admin Panel",
      login: "Sign In",
      register: "Sign Up",
      logout: "Sign Out",
    },
    common: {
      loading: "Loading...",
      searchPlaceholder: "Search...",
      filterBy: "Filter",
      all: "All",
      source: "Source",
      verified: "Verified",
      official: "NTC Official",
      sample: "Official Sample",
      points: "points",
      difficulty: "Difficulty",
      level: "Level",
      streak: "days streak",
      details: "Details",
      viewAll: "View All",
      tryAgain: "Try Again",
      close: "Close",
    },
    auth: {
      loginTitle: "Sign in to account",
      loginSubtitle: "Continue your UNT preparation and maintain your study streak",
      registerTitle: "Create an account",
      registerSubtitle: "Set up your profile and begin your journey to 50/50 on UNT",
      emailLabel: "Email address",
      emailPlaceholder: "student@example.com",
      passwordLabel: "Password",
      passwordPlaceholder: "••••••••",
      displayNameLabel: "Full name or nickname",
      displayNamePlaceholder: "Alikhan Nurlanov",
      targetScoreLabel: "Target UNT score",
      loginButton: "Sign In",
      loggingIn: "Signing in...",
      registerButton: "Create Account",
      registering: "Creating account...",
      quickDemoTitle: "Quick demo login for testing:",
      demoStudent: "Student (student@...)",
      demoAdmin: "Administrator",
      noAccountPrompt: "Don't have an account yet?",
      registerLink: "Sign Up",
      hasAccountPrompt: "Already registered?",
      loginLink: "Sign In",
      orDivider: "or",
      passwordMinLength: "Password (min 6 characters)",
      setPasswordTitle: "Set account password",
      setPasswordSubtitle: "Create a permanent password for direct account access",
      newPasswordLabel: "New password",
      newPasswordPlaceholder: "At least 8 characters",
      setPasswordButton: "Save password",
      passwordSetSuccess: "Password successfully set!",
    },
    oauth: {
      googleSignIn: "Sign in with Google",
      googleSignUp: "Sign up with Google",
      connectingGoogle: "Connecting to Google...",
      redirecting: "Redirecting...",
      authenticating: "Verifying Google authentication...",
      callbackTitle: "Authentication successful!",
      callbackPreparing: "Preparing your learning environment, please wait...",
      callbackSuccess: "You have successfully signed in!",
      errorTitle: "Authentication Error",
      errorSubtitle: "Could not complete sign in",
      retryButton: "Try again",
      homeButton: "Back to Home",
      accountLinkedNotice: "Google account successfully linked",
      secureAuthBadge: "Secured with OAuth 2.0 PKCE",
    },
    errors: {
      AUTH_INVALID_CREDENTIALS: "Invalid email or password",
      AUTH_USER_NOT_FOUND: "User not found",
      AUTH_USER_INACTIVE: "Your account has been deactivated",
      AUTH_PASSWORD_NOT_SET: "Password is not set for this account. Please sign in with Google",
      AUTH_EMAIL_ALREADY_EXISTS: "A user with this email already exists",
      AUTH_OAUTH_INIT_FAILED: "Failed to initialize Google OAuth",
      AUTH_OAUTH_STATE_INVALID: "Invalid authorization session state",
      AUTH_OAUTH_STATE_EXPIRED: "Authorization session expired (10 min). Please try again",
      AUTH_OAUTH_CODE_EXCHANGE_FAILED: "Failed to exchange Google authorization code",
      AUTH_OAUTH_EMAIL_UNVERIFIED: "Google email is unverified. Account linking rejected",
      AUTH_SESSION_EXPIRED: "Session expired. Please log in again",
      AUTH_SESSION_REVOKED: "Session was revoked",
      AUTH_SESSION_REUSE_DETECTED: "Token reuse detected. All sessions revoked for security",
      AUTH_UNAUTHORIZED: "Authentication required",
      AUTH_FORBIDDEN: "Access forbidden",
      AUTH_INVALID_REDIRECT_URI: "Invalid redirect URI",
      AUTH_CANNOT_UNLINK_LAST_PROVIDER: "Cannot unlink the only login method",
      defaultError: "An error occurred during authentication",
      networkError: "Network error or server unreachable",
      unknownError: "Unknown error",
    },
    news: {
      title: "Official UNT / ҰБТ News Feed",
      subtitle: "Verified daily updates from the National Testing Center and the Ministry of Science and Higher Education",
      breakingAlert: "Breaking Announcement",
      categories: {
        all: "All News",
        unt: "UNT Updates",
        registration: "Registration & Dates",
        grants: "State Grants",
        informatics: "Informatics Specs",
        deadlines: "Deadlines",
      },
      sourceAttribution: "Official Source",
      readMore: "Read Full Story",
      noNews: "No news articles found in this category.",
    },
    untKnowledge: {
      title: "UNT 2026 Official Rules & Structure",
      subtitle: "Verified guidelines, scoring matrices, and grant cutoffs for IT applicants",
      examStructure: "Exam Structure",
      questionsCount: "120 questions (Profile: 50 questions)",
      maxScore: "140 points (Profile: 50 points)",
      duration: "240 minutes (4 hours)",
      passingThreshold: "Passing cutoff: 50 points (min 5 per subject)",
      itPrograms: "IT competitive grant score range: 115 — 138 points",
      testingWindows: "Examination Windows",
      specifications: "Informatics Specification Breakdown",
    },
    questionBank: {
      title: "Informatics Question Bank",
      subtitle: "Verified questions aligned with NTC standards, step-by-step solutions and provenance",
      exploreByTopic: "Browse by topic and section",
      allDifficulties: "All difficulty levels",
      easy: "A — Basic",
      medium: "B — Intermediate",
      hard: "C — Advanced",
      officialProvenance: "Question Provenance",
      viewSolution: "View Step-by-Step Solution",
      examTip: "Exam Strategy Tip",
    },
  },
};

/**
 * Extracts the locale from current pathname in browser or defaults to 'kk'.
 */
export const getClientLocale = (): Locale => {
  if (typeof window === "undefined") return DEFAULT_LOCALE;
  const path = window.location.pathname;
  const firstSegment = path.split("/")[1] as Locale;
  if (SUPPORTED_LOCALES.includes(firstSegment)) {
    return firstSegment;
  }
  // Check cookie or localStorage fallback
  const match = document.cookie.match(/untverse_locale=([^;]+)/);
  if (match && SUPPORTED_LOCALES.includes(match[1] as Locale)) {
    return match[1] as Locale;
  }
  return DEFAULT_LOCALE;
};

export const getLocaleFromPathname = (pathname: string): Locale => {
  const firstSegment = pathname.split("/").filter(Boolean)[0] as Locale | undefined;
  return firstSegment && SUPPORTED_LOCALES.includes(firstSegment)
    ? firstSegment
    : DEFAULT_LOCALE;
};

export const localeToLanguageTag = (locale: Locale): string => {
  switch (locale) {
    case "kk":
      return "kk-KZ";
    case "ru":
      return "ru-KZ";
    default:
      return "en";
  }
};

/**
 * Switches the locale while preserving the exact path, dynamic params, and query string.
 * Example: /kk/learn/python?id=10 -> switch to 'ru' -> /ru/learn/python?id=10
 */
export const switchLocaleUrl = (targetLocale: Locale, currentUrl?: string): string => {
  const current = currentUrl ?? (typeof window !== "undefined"
    ? `${window.location.pathname}${window.location.search}${window.location.hash}`
    : "/");
  return localizePath(current, targetLocale);
};

/**
 * Helper to construct an in-app link with the current or target locale.
 * Example: localizePath('/learn', 'kk') -> '/kk/learn'
 */
export const localizePath = (path: string, locale: Locale = DEFAULT_LOCALE): string => {
  // External URLs are not application routes and must remain unchanged.
  if (/^[a-z][a-z\d+.-]*:/i.test(path)) return path;

  const url = new URL(path.startsWith("/") ? path : `/${path}`, "https://untverse.local");
  const segments = url.pathname.split("/").filter(Boolean);
  if (segments.length && SUPPORTED_LOCALES.includes(segments[0] as Locale)) {
    segments.shift();
  }

  const localizedPathname = segments.length ? `/${locale}/${segments.join("/")}` : `/${locale}`;
  return `${localizedPathname}${url.search}${url.hash}`;
};

export const setClientLocaleCookie = (locale: Locale): void => {
  if (typeof window !== "undefined") {
    document.cookie = `untverse_locale=${locale}; path=/; max-age=31536000; SameSite=Lax`;
    localStorage.setItem("untverse_locale", locale);
  }
};

export function getLocalizedAuthError(
  code?: string,
  locale: Locale = DEFAULT_LOCALE,
  fallbackMessage?: string
): string {
  const dict = i18nDict[locale] || i18nDict.kk;
  if (code && code in dict.errors) {
    return dict.errors[code as keyof typeof dict.errors];
  }
  return fallbackMessage || dict.errors.defaultError;
}
