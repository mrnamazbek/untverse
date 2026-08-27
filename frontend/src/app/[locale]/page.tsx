"use client";

import React, { useState } from "react";
import { LocalizedLink as Link } from "@/components/navigation/LocalizedLink";
import { useParams } from "next/navigation";
import { Navbar } from "@/components/layout/Navbar";
import { Footer } from "@/components/layout/Footer";
import dynamic from "next/dynamic";
import { DotShaderBackground } from "@/components/visuals/DotShaderBackground";
import { Locale, SUPPORTED_LOCALES, localizePath } from "@/lib/i18n";

const RobotScene = dynamic(
  () => import("@/components/visuals/RobotScene").then((m) => m.RobotScene),
  { ssr: false }
);
import {
  Sparkles,
  CheckCircle2,
  Code2,
  Database,
  Shield,
  Network,
  Cpu,
  BrainCircuit,
  ArrowRight,
  Trophy,
  Flame,
  Zap,
  Target,
  BarChart,
} from "lucide-react";

const homeCopy = {
  kk: {
    badge: "Қазақстан ҰБТ 2026 • Информатика 50/50",
    title: "Информатикадан ҰБТ-ға жаңа буын дайындығы",
    intro: "ҰБТ-ның нақты тапсырмалары, Python кодын жедел тексеру, SuperMemo SM-2 арқылы қателерді аралықпен қайталау және үздіктер рейтингі бар интерактивті платформа.",
    start: "Тегін бастау",
    sample: "ҰБТ байқау тестін өту",
    stats: ["Ең жоғары балл", "ҰТО бағдарламасына сәйкестік", "Қателерді ақылды қайталау", "Тапсырмаларды жедел тексеру"],
    curriculum: "ҰБТ бағдарламасы",
    curriculumTitle: "Грантқа түсуге арналған 6 негізгі бөлім",
    curriculumIntro: "Әр тақырып іргелі ұғымдардан ҰТО тестеріндегі күрделі тұстарға дейін түсіндіріледі.",
    module: "Бөлімді оқу",
    ideLabel: "Браузердегі интерактивті IDE",
    ideTitle: "Орта орнатпай-ақ код жазыңыз",
    ideIntro: "Кодты тікелей браузерде жазыңыз. Жүйе шешімді ашық және жасырын тестілерден өткізіп, орындау уақытын өлшейді және синтаксис қателерін көрсетеді.",
    codeTask: "# Тапсырма: аралықтағы жұп сандардың қосындысы",
    codePassed: "✓ Барлық 3 тест өтті",
    codeTime: "Уақыт: 12 мс",
    spacedTitle: "Қателермен жұмыс",
    spacedIntro: "Қате жіберген сұрақтар жеке қайталау кезегіне түсіп, берік есте сақтау үшін 1, 6 және 14 күннен соң қайта ұсынылады.",
    interval: "Бекіту аралығы",
    days: "14 күн",
    calculator: "Грант калькуляторы",
    calculatorTitle: "IT мамандықтарына түсу мүмкіндігіңізді бағалаңыз",
    calculatorIntro: "Информатикадан ағымдағы балыңызды жылжытыңыз:",
    score: "Информатика балы:",
    threshold: "Грантқа өту шегі:",
    chance: "Жетекші ЖОО-лардағы IT грантына мүмкіндік:",
    levels: ["99% (жоғары мүмкіндік)", "80% (жақсы мүмкіндік)", "50% (орташа)", "төмен мүмкіндік"],
    elevate: "Балды 50/50-ге жеткізу",
  },
  ru: {
    badge: "Казахстан, ЕНТ 2026 • Информатика 50/50",
    title: "Подготовка к ЕНТ по информатике нового поколения",
    intro: "Интерактивная платформа с реальными заданиями ЕНТ, проверкой Python-кода, интервальным повторением ошибок по SuperMemo SM-2 и рейтингом учеников Казахстана.",
    start: "Начать бесплатно",
    sample: "Пройти пробный тест ЕНТ",
    stats: ["Максимальный балл", "Соответствие программе НЦТ", "Умное повторение ошибок", "Проверка задач в реальном времени"],
    curriculum: "Программа ЕНТ",
    curriculumTitle: "6 ключевых разделов для поступления на грант",
    curriculumIntro: "Каждая тема разобрана от фундаментальных принципов до сложных ловушек тестов НЦТ.",
    module: "Изучить модуль",
    ideLabel: "Интерактивная IDE в браузере",
    ideTitle: "Практикуйте код без установки среды",
    ideIntro: "Пишите код прямо в браузере. Система проверит решение на открытых и скрытых тестах, измерит время выполнения и подскажет синтаксические ошибки.",
    codeTask: "# Задача: сумма чётных чисел в диапазоне",
    codePassed: "✓ Все 3 теста пройдены",
    codeTime: "Время: 12 мс",
    spacedTitle: "Работа над ошибками",
    spacedIntro: "Вопросы с ошибками попадают в личную очередь повторения и возвращаются через 1, 6 и 14 дней для надёжного запоминания.",
    interval: "Интервал закрепления",
    days: "14 дней",
    calculator: "Калькулятор гранта",
    calculatorTitle: "Оцените шансы на поступление на IT-специальность",
    calculatorIntro: "Передвиньте ползунок текущего балла по информатике:",
    score: "Балл по информатике:",
    threshold: "Проходной порог на грант:",
    chance: "Шанс на IT-грант в ведущих вузах:",
    levels: ["99% (высокий шанс)", "80% (хороший шанс)", "50% (средний)", "низкий шанс"],
    elevate: "Поднять балл до 50/50",
  },
  en: {
    badge: "Kazakhstan UNT 2026 • Informatics 50/50",
    title: "Next-generation UNT Informatics preparation",
    intro: "An interactive platform with real UNT-style tasks, live Python checking, SuperMemo SM-2 error review, and a nationwide learner leaderboard.",
    start: "Start for free",
    sample: "Take a UNT practice test",
    stats: ["Maximum score", "Aligned with NTC curriculum", "Smart error review", "Live task checking"],
    curriculum: "UNT curriculum",
    curriculumTitle: "Six essential sections for an IT grant",
    curriculumIntro: "Each topic moves from core principles to the common traps used in NTC exam questions.",
    module: "Explore module",
    ideLabel: "Interactive IDE in the browser",
    ideTitle: "Practise code without installing a setup",
    ideIntro: "Write code in the browser. The system runs open and hidden tests, measures execution time, and points out syntax errors.",
    codeTask: "# Task: sum of even numbers in a range",
    codePassed: "✓ All 3 tests passed",
    codeTime: "Time: 12 ms",
    spacedTitle: "Learn from mistakes",
    spacedIntro: "Questions answered incorrectly enter a personal review queue and return after 1, 6, and 14 days for reliable retention.",
    interval: "Review interval",
    days: "14 days",
    calculator: "Grant calculator",
    calculatorTitle: "Estimate your chances of entering an IT programme",
    calculatorIntro: "Move the slider for your current Informatics score:",
    score: "Informatics score:",
    threshold: "Grant threshold:",
    chance: "Chance of an IT grant at leading universities:",
    levels: ["99% (high chance)", "80% (good chance)", "50% (moderate)", "low chance"],
    elevate: "Raise your score to 50/50",
  },
} satisfies Record<Locale, Record<string, string | string[]>>;

const topicCopy: Record<Locale, Array<{ title: string; desc: string; badge: string }>> = {
  kk: [
    { title: "Санау жүйелері және логика", desc: "Екілік, сегіздік және он алтылық арифметика, ақиқат кестелері мен логикалық өрнектер.", badge: "ҰБТ-да 6–8 сұрақ" },
    { title: "Python бағдарламалау", desc: "Жол тілімдері, тізімдер, сөздіктер, рекурсия, сұрыптау алгоритмдері және код талдауы.", badge: "ҰБТ-да 15–18 сұрақ" },
    { title: "Дерекқорлар және SQL", desc: "Реляциялық үлгілер, бастапқы және сыртқы кілттер, қалыптандыру, SELECT, JOIN және GROUP BY.", badge: "ҰБТ-да 6–8 сұрақ" },
    { title: "Компьютерлік желілер және интернет", desc: "IP адрестеу, ішкі желі маскалары, DNS, TCP/IP хаттамалары, OSI моделі және трафик.", badge: "ҰБТ-да 5–7 сұрақ" },
    { title: "Ақпараттық қауіпсіздік", desc: "Шифрлау, стеганография, аутентификация, киберқауіптер және дербес деректерді қорғау.", badge: "ҰБТ-да 4–6 сұрақ" },
    { title: "Алгоритмдер мен деректер құрылымдары", desc: "Екілік іздеу, стек, кезек, ағаш, граф және Big O күрделілігін бағалау.", badge: "ҰБТ-да 5–8 сұрақ" },
  ],
  ru: [
    { title: "Системы счисления и логика", desc: "Двоичная, восьмеричная и шестнадцатеричная арифметика, таблицы истинности и логические выражения.", badge: "6–8 вопросов на ЕНТ" },
    { title: "Программирование на Python", desc: "Срезы строк, списки, словари, рекурсия, алгоритмы сортировки и анализ кода.", badge: "15–18 вопросов на ЕНТ" },
    { title: "Базы данных и SQL", desc: "Реляционные модели, первичные и внешние ключи, нормализация, SELECT, JOIN и GROUP BY.", badge: "6–8 вопросов на ЕНТ" },
    { title: "Компьютерные сети и интернет", desc: "IP-адресация, маски подсети, DNS, протоколы TCP/IP, модель OSI и расчёт трафика.", badge: "5–7 вопросов на ЕНТ" },
    { title: "Информационная безопасность", desc: "Шифрование, стеганография, аутентификация, киберугрозы и защита персональных данных.", badge: "4–6 вопросов на ЕНТ" },
    { title: "Алгоритмы и структуры данных", desc: "Двоичный поиск, стеки, очереди, деревья, графы и оценка сложности Big O.", badge: "5–8 вопросов на ЕНТ" },
  ],
  en: [
    { title: "Number systems and logic", desc: "Binary, octal, and hexadecimal arithmetic, truth tables, and logical expressions.", badge: "6–8 UNT questions" },
    { title: "Python programming", desc: "String slices, lists, dictionaries, recursion, sorting algorithms, and code analysis.", badge: "15–18 UNT questions" },
    { title: "Databases and SQL", desc: "Relational models, primary and foreign keys, normalization, SELECT, JOIN, and GROUP BY.", badge: "6–8 UNT questions" },
    { title: "Computer networks and the internet", desc: "IP addressing, subnet masks, DNS, TCP/IP protocols, the OSI model, and traffic calculation.", badge: "5–7 UNT questions" },
    { title: "Information security", desc: "Encryption, steganography, authentication, cyber threats, and personal-data protection.", badge: "4–6 UNT questions" },
    { title: "Algorithms and data structures", desc: "Binary search, stacks, queues, trees, graphs, and Big O complexity.", badge: "5–8 UNT questions" },
  ],
};

export default function HomePage() {
  const params = useParams();
  const rawLocale = params?.locale as string;
  const locale: Locale = (SUPPORTED_LOCALES.includes(rawLocale as Locale) ? rawLocale : "kk") as Locale;
  const [calculatorScore, setCalculatorScore] = useState(38);
  const copy = homeCopy[locale];

  const topicStyles = [
    {
      icon: Cpu,
      color: "bg-blue-50 text-[#0075de] border-blue-200",
    },
    {
      icon: Code2,
      color: "bg-purple-50 text-purple-700 border-purple-200",
    },
    {
      icon: Database,
      color: "bg-teal-50 text-teal-700 border-teal-200",
    },
    {
      icon: Network,
      color: "bg-orange-50 text-[#dd5b00] border-orange-200",
    },
    {
      icon: Shield,
      color: "bg-emerald-50 text-[#1aae39] border-emerald-200",
    },
    {
      icon: BrainCircuit,
      color: "bg-amber-50 text-amber-800 border-amber-200",
    },
  ];
  const topics = topicStyles.map((topic, index) => ({ ...topic, ...topicCopy[locale][index] }));

  return (
    <div className="min-h-screen flex flex-col bg-[#f6f5f4]">
      <Navbar />

      <section className="hero-surface text-white pt-12 pb-14 sm:pt-16 sm:pb-18 px-6 lg:px-12 relative overflow-hidden min-h-[580px] lg:min-h-[660px] flex flex-col justify-center">
        <DotShaderBackground variant="hero" />

        {/* Grand 3D Robot in the Background (right side) */}
        <div
          className="absolute top-1/2 right-[-2%] sm:right-[0%] lg:right-[2%] xl:right-[4%] -translate-y-1/2 w-[85%] sm:w-[55%] md:w-[48%] lg:w-[44%] xl:w-[39%] max-w-[550px] h-[80%] sm:h-[88%] lg:h-[96%] pointer-events-auto z-0 overflow-visible opacity-25 sm:opacity-45 md:opacity-75 lg:opacity-90"
          aria-hidden="true"
        >
          <div className="absolute inset-0 w-full h-full scale-[1.02] sm:scale-[1.08] lg:scale-[1.15] xl:scale-[1.20] translate-y-[4%] sm:translate-y-[1%] lg:translate-y-[-2%] origin-center">
            <RobotScene
              scene="/spline/scene.splinecode"
              className="w-full h-full [&_canvas]:!w-full [&_canvas]:!h-full"
              trackCursor
            />
          </div>
        </div>

        {/* Hero Content (left column, high z-index) */}
        <div className="max-w-6xl mx-auto w-full relative z-10">
          <div className="max-w-2xl lg:max-w-2xl text-center lg:text-left py-4 sm:py-6">
            <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-white/10 border border-white/20 text-xs font-semibold text-white mb-6 backdrop-blur-sm">
              <Sparkles className="w-3.5 h-3.5 text-blue-300" />
              <span>{copy.badge}</span>
            </div>

            <h1 className="display-1 text-white font-bold tracking-tight mb-6 max-w-2xl leading-tight drop-shadow-sm">
              {copy.title}
            </h1>

            <p className="text-base sm:text-lg text-blue-100/90 font-normal max-w-xl mx-auto lg:mx-0 mb-8 leading-relaxed">
              {copy.intro}
            </p>

            <div className="flex flex-col sm:flex-row items-center lg:items-start justify-center lg:justify-start gap-4">
              <Link
                href={localizePath("/register", locale)}
                className="btn-primary w-full sm:w-auto px-8 py-3 text-base shadow-lg shadow-blue-500/30 bg-[#0075de] hover:bg-[#005bab] font-semibold"
              >
                <span>{copy.start}</span>
                <ArrowRight className="w-4 h-4" />
              </Link>
              <Link
                href={localizePath("/practice", locale)}
                className="btn-secondary w-full sm:w-auto px-7 py-3 text-base bg-white/10 text-white border-white/20 hover:bg-white/20 backdrop-blur-sm"
              >
                {copy.sample}
              </Link>
            </div>
          </div>

          {/* Stats Bar */}
          <div className="mt-8 pt-6 border-t border-white/10 grid grid-cols-2 md:grid-cols-4 gap-6 text-center relative z-10 backdrop-blur-[2px]">
            <div>
              <div className="text-2xl sm:text-3xl font-bold text-white">50/50</div>
              <div className="text-xs text-blue-200/80 mt-1">{copy.stats[0]}</div>
            </div>
            <div>
              <div className="text-2xl sm:text-3xl font-bold text-white">100%</div>
              <div className="text-xs text-blue-200/80 mt-1">{copy.stats[1]}</div>
            </div>
            <div>
              <div className="text-2xl sm:text-3xl font-bold text-white">SM-2</div>
              <div className="text-xs text-blue-200/80 mt-1">{copy.stats[2]}</div>
            </div>
            <div>
              <div className="text-2xl sm:text-3xl font-bold text-white">Python + SQL</div>
              <div className="text-xs text-blue-200/80 mt-1">{copy.stats[3]}</div>
            </div>
          </div>
        </div>
      </section>

      {/* Main Content Areas on Warm Canvas (#f6f5f4) */}
      <main className="max-w-6xl mx-auto px-6 py-16 space-y-20 flex-1">
        
        {/* Curriculum Sections Grid */}
        <section>
          <div className="text-center max-w-2xl mx-auto mb-12">
            <span className="eyebrow text-[#0075de] block mb-2 font-semibold">{copy.curriculum}</span>
            <h2 className="heading-1 text-[#000000] mb-3">{copy.curriculumTitle}</h2>
            <p className="text-sm text-[#615d59]">
              {copy.curriculumIntro}
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {topics.map((topic, i) => {
              const Icon = topic.icon;
              return (
                <div key={i} className="notion-card p-6 flex flex-col justify-between group">
                  <div>
                    <div className="flex items-center justify-between mb-4">
                      <div className={`w-10 h-10 rounded-xl flex items-center justify-center border ${topic.color}`}>
                        <Icon className="w-5 h-5" />
                      </div>
                      <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full bg-[#f6f5f4] text-[#615d59] border border-[#e6e6e6]">
                        {topic.badge}
                      </span>
                    </div>

                    <h3 className="font-bold text-base text-[#000000] mb-2 group-hover:text-[#0075de] transition-colors">
                      {topic.title}
                    </h3>
                    <p className="text-xs text-[#615d59] leading-relaxed mb-4">
                      {topic.desc}
                    </p>
                  </div>

                  <Link
                    href={localizePath("/learn", locale)}
                    className="inline-flex items-center gap-1.5 text-xs font-semibold text-[#0075de] hover:underline pt-2 border-t border-[#e6e6e6]"
                  >
                    <span>{copy.module}</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </Link>
                </div>
              );
            })}
          </div>
        </section>

        {/* Feature Bento Grid: Python Runner, SM-2, Gamification */}
        <section className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          
          {/* Card 1: Safe Python Sandbox */}
          <div className="lg:col-span-2 notion-card p-8 bg-white flex flex-col justify-between">
            <div>
              <div className="inline-flex items-center gap-1.5 px-3 py-1 bg-purple-50 border border-purple-200 text-purple-800 text-xs font-semibold rounded-full mb-4">
                <Code2 className="w-3.5 h-3.5" />
                <span>{copy.ideLabel}</span>
              </div>
              <h3 className="heading-2 text-[#000000] mb-3">
                {copy.ideTitle}
              </h3>
              <p className="text-sm text-[#615d59] leading-relaxed mb-6">
                {copy.ideIntro}
              </p>
            </div>

            <div className="p-4 bg-[#1e2337] rounded-xl text-white font-mono text-xs shadow-inner">
              <div className="text-gray-400 mb-1">{copy.codeTask}</div>
              <div className="text-purple-300">def <span className="text-blue-300">sum_evens</span>(n: int) -&gt; int:</div>
              <div className="pl-4 text-emerald-300">return sum(x for x in range(2, n + 1, 2))</div>
              <div className="mt-2 pt-2 border-t border-gray-800 flex items-center justify-between text-[11px] text-gray-400">
                <span className="text-emerald-400">{copy.codePassed}</span>
                <span>{copy.codeTime}</span>
              </div>
            </div>
          </div>

          {/* Card 2: SM-2 Spaced Repetition */}
          <div className="notion-card p-8 bg-white flex flex-col justify-between">
            <div>
              <div className="inline-flex items-center gap-1.5 px-3 py-1 bg-teal-50 border border-teal-200 text-teal-800 text-xs font-semibold rounded-full mb-4">
                <BrainCircuit className="w-3.5 h-3.5" />
                <span>SuperMemo SM-2</span>
              </div>
              <h3 className="heading-2 text-[#000000] mb-3">
                {copy.spacedTitle}
              </h3>
              <p className="text-sm text-[#615d59] leading-relaxed mb-4">
                {copy.spacedIntro}
              </p>
            </div>

            <div className="p-4 bg-[#f6f5f4] rounded-xl border border-[#e6e6e6] text-xs">
              <div className="flex items-center justify-between mb-2">
                <span className="font-semibold text-[#000000]">{copy.interval}</span>
                <span className="text-[#0075de] font-bold">{copy.days}</span>
              </div>
              <div className="w-full h-2 bg-white rounded-full overflow-hidden border border-[#e6e6e6]">
                <div className="h-full bg-[#0075de] w-3/4 rounded-full" />
              </div>
            </div>
          </div>

        </section>

        {/* Interactive UNT Target Calculator */}
        <section className="notion-card-elevated p-8 sm:p-12 bg-white">
          <div className="max-w-3xl mx-auto text-center">
            <span className="eyebrow text-[#0075de] block mb-2">{copy.calculator}</span>
            <h2 className="heading-2 text-[#000000] mb-4">
              {copy.calculatorTitle}
            </h2>
            <p className="text-sm text-[#615d59] mb-8">
              {copy.calculatorIntro}
            </p>

            <div className="p-6 bg-[#f6f5f4] rounded-2xl border border-[#e6e6e6] max-w-xl mx-auto mb-6">
              <div className="flex items-center justify-between text-base font-bold text-[#000000] mb-3">
                <span>{copy.score}</span>
                <span className="text-2xl text-[#0075de] font-mono">{calculatorScore} / 50</span>
              </div>
              <input
                type="range"
                min="10"
                max="50"
                value={calculatorScore}
                onChange={(e) => setCalculatorScore(Number(e.target.value))}
                className="w-full h-2.5 bg-white border border-[#e6e6e6] rounded-lg appearance-none cursor-pointer accent-[#0075de]"
              />

              <div className="mt-4 pt-4 border-t border-[#e6e6e6] text-left text-xs space-y-1.5">
                <div className="flex items-center justify-between">
                  <span className="text-[#615d59]">{copy.threshold}</span>
                  <span className="font-semibold text-[#000000]">35+</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-[#615d59]">{copy.chance}</span>
                  <span className={`font-bold ${calculatorScore >= 42 ? "text-[#1aae39]" : calculatorScore >= 35 ? "text-amber-600" : "text-red-500"}`}>
                    {calculatorScore >= 45 ? copy.levels[0] : calculatorScore >= 40 ? copy.levels[1] : calculatorScore >= 35 ? copy.levels[2] : copy.levels[3]}
                  </span>
                </div>
              </div>
            </div>

            <Link
              href={localizePath("/register", locale)}
              className="btn-primary px-8 py-3 text-sm shadow-md"
            >
              {copy.elevate}
            </Link>
          </div>
        </section>

      </main>

      <Footer />
    </div>
  );
}
