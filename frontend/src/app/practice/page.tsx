"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { Navbar } from "@/components/layout/Navbar";
import { Sidebar } from "@/components/layout/Sidebar";
import { Footer } from "@/components/layout/Footer";
import { fetchApi } from "@/lib/api";
import { Quiz } from "@/types/learning";
import { SpacedCard, MistakeLogItem } from "@/types/analytics";
import {
  CheckSquare,
  Clock,
  BrainCircuit,
  AlertTriangle,
  Play,
  RotateCcw,
  Sparkles,
  Trophy,
  Zap,
  CheckCircle2,
} from "lucide-react";

export default function PracticePage() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [quizzes, setQuizzes] = useState<Quiz[]>([]);
  const [srsCards, setSrsCards] = useState<SpacedCard[]>([]);
  const [mistakes, setMistakes] = useState<MistakeLogItem[]>([]);
  const [activeCardIndex, setActiveCardIndex] = useState(0);
  const [isCardRevealed, setIsCardRevealed] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadPracticeData = async () => {
      try {
        const [quizList, cards, mistakeList] = await Promise.all([
          fetchApi<Quiz[]>("/quizzes"),
          fetchApi<SpacedCard[]>("/analytics/spaced-repetition/due").catch(() => []),
          fetchApi<MistakeLogItem[]>("/analytics/mistakes").catch(() => []),
        ]);
        setQuizzes(quizList);
        setSrsCards(cards);
        setMistakes(mistakeList);
      } catch (err) {
        console.error("Failed to load practice data", err);
      } finally {
        setLoading(false);
      }
    };

    loadPracticeData();
  }, []);

  const handleSrsRating = async (rating: number) => {
    const currentCard = srsCards[activeCardIndex];
    if (!currentCard) return;

    try {
      await fetchApi("/analytics/spaced-repetition/review", {
        method: "POST",
        body: JSON.stringify({
          card_id: currentCard.card_id,
          rating,
        }),
      });

      setIsCardRevealed(false);
      if (activeCardIndex + 1 < srsCards.length) {
        setActiveCardIndex((prev) => prev + 1);
      } else {
        setSrsCards([]);
        setActiveCardIndex(0);
      }
    } catch (err: any) {
      alert(err.message);
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-[#f6f5f4]">
      <Navbar onToggleSidebar={() => setSidebarOpen(!sidebarOpen)} />

      <div className="flex-1 flex max-w-7xl w-full mx-auto">
        <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

        <main className="flex-1 lg:pl-64 p-4 sm:p-6 lg:p-8 space-y-8 max-w-5xl">
          
          {/* Header Banner */}
          <div className="bg-white border border-[#e6e6e6] rounded-2xl p-6 sm:p-8 shadow-xs">
            <span className="eyebrow text-[#0075de] block mb-1 font-semibold">
              Тренажерный зал ЕНТ
            </span>
            <h1 className="heading-1 text-[#000000] mb-2">
              Практика тестирования и умное повторение
            </h1>
            <p className="text-xs sm:text-sm text-[#615d59] max-w-2xl leading-relaxed">
              Решайте тесты в формате настоящего ЕНТ с ограничением по времени и закрепляйте сложные вопросы через интервальное повторение.
            </p>
          </div>

          {/* Featured Exam Modes Bento Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
            
            {/* Mode 1: Full UNT Mock Exam */}
            <div className="notion-card p-6 bg-[#213183] text-white flex flex-col justify-between">
              <div>
                <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-white/20 text-white text-[11px] font-bold uppercase tracking-wider mb-3">
                  <Trophy className="w-3.5 h-3.5 text-yellow-300" />
                  <span>Полный пробник</span>
                </div>
                <h3 className="font-bold text-lg mb-2">Симулятор ЕНТ (50/50)</h3>
                <p className="text-xs text-blue-100/80 leading-relaxed mb-6">
                  50 вопросов из всех тем: одиночный выбор, множественный выбор, контекстные задачи. Таймер на 50 минут.
                </p>
              </div>

              {quizzes.length > 0 ? (
                <Link
                  href={`/quiz/${quizzes[0].id}`}
                  className="btn-primary w-full py-2.5 text-xs bg-white text-[#213183] hover:bg-blue-50 font-bold justify-center shadow-md"
                >
                  <Play className="w-3.5 h-3.5 fill-[#213183]" />
                  <span>Начать экзамен</span>
                </Link>
              ) : (
                <button disabled className="btn-secondary w-full text-xs py-2 text-white/50">
                  Тесты загружаются...
                </button>
              )}
            </div>

            {/* Mode 2: SM-2 Spaced Repetition */}
            <div className="notion-card p-6 bg-white flex flex-col justify-between">
              <div>
                <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-teal-50 text-teal-800 text-[11px] font-bold uppercase tracking-wider mb-3 border border-teal-200">
                  <BrainCircuit className="w-3.5 h-3.5" />
                  <span>SuperMemo SM-2</span>
                </div>
                <h3 className="font-bold text-lg text-[#000000] mb-2">Интервальные карточки</h3>
                <p className="text-xs text-[#615d59] leading-relaxed mb-6">
                  Повторение вопросов, в которых вы допускали ошибки. Алгоритм выстраивает оптимальные интервалы для долгосрочной памяти.
                </p>
              </div>

              <div className="flex items-center justify-between pt-3 border-t border-[#e6e6e6]">
                <span className="text-xs font-semibold text-[#31302e]">
                  {srsCards.length} {srsCards.length === 1 ? "карточка" : "карточек"} сегодня
                </span>
                <span className="text-xs font-bold text-[#0075de]">+50 XP</span>
              </div>
            </div>

            {/* Mode 3: Mistakes Workout */}
            <div className="notion-card p-6 bg-white flex flex-col justify-between">
              <div>
                <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-red-50 text-red-700 text-[11px] font-bold uppercase tracking-wider mb-3 border border-red-200">
                  <AlertTriangle className="w-3.5 h-3.5" />
                  <span>Банк ошибок</span>
                </div>
                <h3 className="font-bold text-lg text-[#000000] mb-2">Работа над ошибками</h3>
                <p className="text-xs text-[#615d59] leading-relaxed mb-6">
                  Список всех вопросов, где вы ответили неверно. Разберите подробные объяснения и решите заново.
                </p>
              </div>

              <div className="flex items-center justify-between pt-3 border-t border-[#e6e6e6]">
                <span className="text-xs font-semibold text-red-600">
                  {mistakes.length} нерешенных
                </span>
                <span className="text-xs font-bold text-[#1aae39]">До 100% точности</span>
              </div>
            </div>

          </div>

          {/* Interactive SM-2 Flashcard Player if due cards exist */}
          {srsCards.length > 0 && activeCardIndex < srsCards.length && (
            <section className="notion-card-elevated p-6 sm:p-8 bg-white border-2 border-teal-500/30">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                  <BrainCircuit className="w-5 h-5 text-teal-600" />
                  <h3 className="font-bold text-sm text-[#000000]">
                    Интервальное повторение ({activeCardIndex + 1} из {srsCards.length})
                  </h3>
                </div>
                <span className="text-xs text-[#615d59] font-mono font-medium">
                  Интервал: {srsCards[activeCardIndex].interval_days} дн.
                </span>
              </div>

              <div className="p-6 bg-[#f6f5f4] rounded-xl border border-[#e6e6e6] mb-6">
                <p className="text-base font-semibold text-[#000000] leading-relaxed">
                  {srsCards[activeCardIndex].question_text}
                </p>

                {srsCards[activeCardIndex].code_snippet && (
                  <div className="mt-3 p-3 bg-[#213183] text-white rounded-lg font-mono text-xs overflow-x-auto">
                    <pre>{srsCards[activeCardIndex].code_snippet}</pre>
                  </div>
                )}

                {isCardRevealed && (
                  <div className="mt-6 pt-6 border-t border-[#e6e6e6] space-y-2 animate-in fade-in duration-200">
                    <span className="text-[11px] font-bold uppercase tracking-wider text-[#1aae39] block">
                      Варианты ответа:
                    </span>
                    {srsCards[activeCardIndex].options.map((opt) => (
                      <div key={opt.id} className="p-2.5 bg-white rounded-lg border border-[#e6e6e6] text-xs">
                        {opt.text}
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {!isCardRevealed ? (
                <button
                  onClick={() => setIsCardRevealed(true)}
                  className="btn-primary w-full py-2.5 text-xs font-semibold justify-center shadow-xs"
                >
                  Показать ответ и варианты
                </button>
              ) : (
                <div className="space-y-2 text-center">
                  <p className="text-xs font-medium text-[#615d59] mb-2">
                    Оцените, насколько легко вы вспомнили ответ:
                  </p>
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                    <button
                      onClick={() => handleSrsRating(1)}
                      className="btn-utility text-xs py-2 justify-center border-red-200 text-red-700 hover:bg-red-50"
                    >
                      1: Забыл совсем
                    </button>
                    <button
                      onClick={() => handleSrsRating(3)}
                      className="btn-utility text-xs py-2 justify-center border-amber-200 text-amber-700 hover:bg-amber-50"
                    >
                      3: Вспомнил с трудом
                    </button>
                    <button
                      onClick={() => handleSrsRating(4)}
                      className="btn-utility text-xs py-2 justify-center border-blue-200 text-blue-700 hover:bg-blue-50"
                    >
                      4: Хорошо помню
                    </button>
                    <button
                      onClick={() => handleSrsRating(5)}
                      className="btn-utility text-xs py-2 justify-center border-green-200 text-green-700 hover:bg-green-50"
                    >
                      5: Идеально легко
                    </button>
                  </div>
                </div>
              )}
            </section>
          )}

          {/* All Available Quizzes List */}
          <section className="space-y-4">
            <h2 className="heading-3 text-[#000000]">Тематические тесты по разделам ЕНТ</h2>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {quizzes.map((q) => (
                <div key={q.id} className="notion-card p-5 bg-white flex flex-col justify-between">
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-blue-50 text-[#0075de] border border-blue-200/50">
                        {q.quiz_type === "unt_mock" ? "ЕНТ Пробник" : "Тест модуля"}
                      </span>
                      <span className="text-xs font-bold text-[#0075de]">+{q.xp_reward} XP</span>
                    </div>

                    <h4 className="font-bold text-sm text-[#000000] mb-1">{q.title}</h4>
                    <p className="text-xs text-[#615d59] mb-4">{q.description}</p>
                  </div>

                  <div className="pt-3 border-t border-[#e6e6e6] flex items-center justify-between">
                    <span className="flex items-center gap-1 text-xs text-[#615d59]">
                      <Clock className="w-3.5 h-3.5" />
                      {Math.round(q.time_limit_seconds / 60)} мин.
                    </span>

                    <Link
                      href={`/quiz/${q.id}`}
                      className="btn-primary text-xs py-1.5 px-4 shadow-xs"
                    >
                      <span>Пройти тест</span>
                    </Link>
                  </div>
                </div>
              ))}
            </div>
          </section>

        </main>
      </div>

      <Footer />
    </div>
  );
}
