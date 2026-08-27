"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { Navbar } from "@/components/layout/Navbar";
import { Footer } from "@/components/layout/Footer";
import { Locale, SUPPORTED_LOCALES, localizePath } from "@/lib/i18n";
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

export default function HomePage() {
  const params = useParams();
  const rawLocale = params?.locale as string;
  const locale: Locale = (SUPPORTED_LOCALES.includes(rawLocale as Locale) ? rawLocale : "kk") as Locale;
  const [calculatorScore, setCalculatorScore] = useState(38);

  const topics = [
    {
      title: "Системы счисления и логика",
      desc: "Двоичная, восьмеричная, шестнадцатеричная арифметика, таблицы истинности и логические выражения.",
      icon: Cpu,
      color: "bg-blue-50 text-[#0075de] border-blue-200",
      badge: "6-8 вопросов в ЕНТ",
    },
    {
      title: "Программирование на Python",
      desc: "Срезы строк, списки, словари, рекурсия, алгоритмы сортировки и безопасный анализ кода.",
      icon: Code2,
      color: "bg-purple-50 text-purple-700 border-purple-200",
      badge: "15-18 вопросов в ЕНТ",
    },
    {
      title: "Базы данных и язык SQL",
      desc: "Реляционные модели, первичные/внешние ключи, нормализация, операторы SELECT, JOIN, GROUP BY.",
      icon: Database,
      color: "bg-teal-50 text-teal-700 border-teal-200",
      badge: "6-8 вопросов в ЕНТ",
    },
    {
      title: "Компьютерные сети и Интернет",
      desc: "IP-адресация, маски подсети, DNS, протоколы TCP/IP, OSI модель, топологии и расчет трафика.",
      icon: Network,
      color: "bg-orange-50 text-[#dd5b00] border-orange-200",
      badge: "5-7 вопросов в ЕНТ",
    },
    {
      title: "Информационная безопасность",
      desc: "Шифрование, стеганография, методы аутентификации, киберугрозы и защита персональных данных.",
      icon: Shield,
      color: "bg-emerald-50 text-[#1aae39] border-emerald-200",
      badge: "4-6 вопросов в ЕНТ",
    },
    {
      title: "Алгоритмы и структуры данных",
      desc: "Бинарный поиск, стеки, очереди, деревья, графы, оценка сложности Big O.",
      icon: BrainCircuit,
      color: "bg-amber-50 text-amber-800 border-amber-200",
      badge: "5-8 вопросов в ЕНТ",
    },
  ];

  return (
    <div className="min-h-screen flex flex-col bg-[#f6f5f4]">
      <Navbar />

      {/* Hero Section with Deep Indigo Night Band as per DESIGN-notion.md */}
      <section className="bg-[#213183] text-white pt-16 pb-20 px-6 lg:px-12 relative overflow-hidden">
        {/* Subtle geometric grid background */}
        <div className="absolute inset-0 opacity-10 pointer-events-none bg-[radial-gradient(#ffffff_1px,transparent_1px)] [background-size:24px_24px]" />

        <div className="max-w-5xl mx-auto text-center relative z-10">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-white/10 border border-white/20 text-xs font-semibold text-white mb-6 backdrop-blur-sm">
            <Sparkles className="w-3.5 h-3.5 text-blue-300" />
            <span>Казахстан ЕНТ 2026 • Информатика 50/50</span>
          </div>

          <h1 className="display-1 text-white font-bold tracking-tight mb-6 max-w-4xl mx-auto">
            Подготовка к ЕНТ по Информатике нового поколения
          </h1>

          <p className="text-base sm:text-lg text-blue-100/90 font-normal max-w-2xl mx-auto mb-8 leading-relaxed">
            Интерактивная платформа с реальными заданиями ЕНТ, живой проверкой кода на Python, 
            интервальным повторением ошибок SuperMemo SM-2 и рейтингом лучших учеников Казахстана.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link
              href={localizePath("/register", locale)}
              className="btn-primary w-full sm:w-auto px-8 py-3 text-base shadow-lg shadow-blue-500/30 bg-[#0075de] hover:bg-[#005bab] font-semibold"
            >
              <span>Начать бесплатно</span>
              <ArrowRight className="w-4 h-4" />
            </Link>
            <Link
              href={localizePath("/practice", locale)}
              className="btn-secondary w-full sm:w-auto px-7 py-3 text-base bg-white/10 text-white border-white/20 hover:bg-white/20"
            >
              Пройти пробный тест ЕНТ
            </Link>
          </div>

          {/* Quick Stats Bar */}
          <div className="mt-14 pt-8 border-t border-white/10 grid grid-cols-2 md:grid-cols-4 gap-6 text-center">
            <div>
              <div className="text-2xl sm:text-3xl font-bold text-white">50/50</div>
              <div className="text-xs text-blue-200/80 mt-1">Максимальный балл</div>
            </div>
            <div>
              <div className="text-2xl sm:text-3xl font-bold text-white">100%</div>
              <div className="text-xs text-blue-200/80 mt-1">Соответствие базе НЦТ</div>
            </div>
            <div>
              <div className="text-2xl sm:text-3xl font-bold text-white">SM-2</div>
              <div className="text-xs text-blue-200/80 mt-1">Умное повторение ошибок</div>
            </div>
            <div>
              <div className="text-2xl sm:text-3xl font-bold text-white">Python + SQL</div>
              <div className="text-xs text-blue-200/80 mt-1">Живая компиляция задач</div>
            </div>
          </div>
        </div>
      </section>

      {/* Main Content Areas on Warm Canvas (#f6f5f4) */}
      <main className="max-w-6xl mx-auto px-6 py-16 space-y-20 flex-1">
        
        {/* Curriculum Sections Grid */}
        <section>
          <div className="text-center max-w-2xl mx-auto mb-12">
            <span className="eyebrow text-[#0075de] block mb-2 font-semibold">Программа ЕНТ</span>
            <h2 className="heading-1 text-[#000000] mb-3">6 ключевых разделов для сдачи на Грант</h2>
            <p className="text-sm text-[#615d59]">
              Каждая тема разобрана от фундаментальных принципов до хитрых тестовых ловушек НЦТ.
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
                    <span>Изучить модуль</span>
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
                <span>Интерактивная IDE в браузере</span>
              </div>
              <h3 className="heading-2 text-[#000000] mb-3">
                Практика кода без установки окружения
              </h3>
              <p className="text-sm text-[#615d59] leading-relaxed mb-6">
                Пишите код прямо в браузере. Система автоматически прогонит решение через скрытые и открытые тест-кейсы, замерит время выполнения и подскажет ошибки синтаксиса.
              </p>
            </div>

            <div className="p-4 bg-[#1e2337] rounded-xl text-white font-mono text-xs shadow-inner">
              <div className="text-gray-400 mb-1"># Задача: сумма четных чисел в диапазоне</div>
              <div className="text-purple-300">def <span className="text-blue-300">sum_evens</span>(n: int) -&gt; int:</div>
              <div className="pl-4 text-emerald-300">return sum(x for x in range(2, n + 1, 2))</div>
              <div className="mt-2 pt-2 border-t border-gray-800 flex items-center justify-between text-[11px] text-gray-400">
                <span className="text-emerald-400">✓ Все 3 теста пройдены</span>
                <span>Время: 12 мс</span>
              </div>
            </div>
          </div>

          {/* Card 2: SM-2 Spaced Repetition */}
          <div className="notion-card p-8 bg-white flex flex-col justify-between">
            <div>
              <div className="inline-flex items-center gap-1.5 px-3 py-1 bg-teal-50 border border-teal-200 text-teal-800 text-xs font-semibold rounded-full mb-4">
                <BrainCircuit className="w-3.5 h-3.5" />
                <span>Алгоритм SuperMemo SM-2</span>
              </div>
              <h3 className="heading-2 text-[#000000] mb-3">
                Работа над ошибками
              </h3>
              <p className="text-sm text-[#615d59] leading-relaxed mb-4">
                Вопросы, в которых вы ошиблись, попадают в личную очередь повторения и возвращаются через 1, 6 и 14 дней для надежного запоминания.
              </p>
            </div>

            <div className="p-4 bg-[#f6f5f4] rounded-xl border border-[#e6e6e6] text-xs">
              <div className="flex items-center justify-between mb-2">
                <span className="font-semibold text-[#000000]">Интервал закрепления</span>
                <span className="text-[#0075de] font-bold">14 дней</span>
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
            <span className="eyebrow text-[#0075de] block mb-2">Калькулятор Гранта</span>
            <h2 className="heading-2 text-[#000000] mb-4">
              Оцените ваши шансы на поступление в IT-специальности
            </h2>
            <p className="text-sm text-[#615d59] mb-8">
              Двигайте ползунок текущего балла по Информатике:
            </p>

            <div className="p-6 bg-[#f6f5f4] rounded-2xl border border-[#e6e6e6] max-w-xl mx-auto mb-6">
              <div className="flex items-center justify-between text-base font-bold text-[#000000] mb-3">
                <span>Балл за Информатику:</span>
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
                  <span className="text-[#615d59]">Проходной порог на грант:</span>
                  <span className="font-semibold text-[#000000]">35+ баллов</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-[#615d59]">Шанс на грант в ТОП вузы (МУИТ, КБТУ, SDU, Астана IT):</span>
                  <span className={`font-bold ${calculatorScore >= 42 ? "text-[#1aae39]" : calculatorScore >= 35 ? "text-amber-600" : "text-red-500"}`}>
                    {calculatorScore >= 45 ? "99% (Высокий шанс)" : calculatorScore >= 40 ? "80% (Хороший шанс)" : calculatorScore >= 35 ? "50% (Средний)" : "Низкий шанс"}
                  </span>
                </div>
              </div>
            </div>

            <Link
              href={localizePath("/register", locale)}
              className="btn-primary px-8 py-3 text-sm shadow-md"
            >
              Поднять балл до 50/50
            </Link>
          </div>
        </section>

      </main>

      <Footer />
    </div>
  );
}
