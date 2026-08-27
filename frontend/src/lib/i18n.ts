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

/**
 * Switches the locale while preserving the exact path, dynamic params, and query string.
 * Example: /kk/learn/python?id=10 -> switch to 'ru' -> /ru/learn/python?id=10
 */
export const switchLocaleUrl = (targetLocale: Locale): string => {
  if (typeof window === "undefined") return `/${targetLocale}`;
  const { pathname, search, hash } = window.location;
  const segments = pathname.split("/").filter(Boolean);
  
  if (segments.length > 0 && SUPPORTED_LOCALES.includes(segments[0] as Locale)) {
    segments[0] = targetLocale;
  } else {
    segments.unshift(targetLocale);
  }

  const newPathname = "/" + segments.join("/");
  return `${newPathname}${search || ""}${hash || ""}`;
};

/**
 * Helper to construct an in-app link with the current or target locale.
 * Example: localizePath('/learn', 'kk') -> '/kk/learn'
 */
export const localizePath = (path: string, locale: Locale = DEFAULT_LOCALE): string => {
  const cleanPath = path.startsWith("/") ? path : `/${path}`;
  const firstSegment = cleanPath.split("/")[1] as Locale;
  if (SUPPORTED_LOCALES.includes(firstSegment)) {
    return cleanPath;
  }
  return `/${locale}${cleanPath === "/" ? "" : cleanPath}`;
};

export const setClientLocaleCookie = (locale: Locale): void => {
  if (typeof window !== "undefined") {
    document.cookie = `untverse_locale=${locale}; path=/; max-age=31536000; SameSite=Lax`;
    localStorage.setItem("untverse_locale", locale);
  }
};
