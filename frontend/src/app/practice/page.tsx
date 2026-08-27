"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { Navbar } from "@/components/layout/Navbar";
import { Sidebar } from "@/components/layout/Sidebar";
import { Footer } from "@/components/layout/Footer";
import { fetchApi } from "@/lib/api";
import { Quiz } from "@/types/learning";
import { SpacedCard, MistakeLogItem } from "@/types/analytics";
import { BankQuestion, ExamSpecification } from "@/types/data_platform";
import { getClientLocale, i18nDict, Locale } from "@/lib/i18n";
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
  HelpCircle,
  ShieldCheck,
  ExternalLink,
  BookOpen,
  Filter,
  Lightbulb,
  Layers,
  ChevronDown,
  ChevronUp,
} from "lucide-react";

export default function PracticePage() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [locale, setLocale] = useState<Locale>("kk");
  const [activeTab, setActiveTab] = useState<"bank" | "quizzes" | "srs" | "mistakes">("bank");
  
  // Data states
  const [quizzes, setQuizzes] = useState<Quiz[]>([]);
  const [srsCards, setSrsCards] = useState<SpacedCard[]>([]);
  const [mistakes, setMistakes] = useState<MistakeLogItem[]>([]);
  const [bankQuestions, setBankQuestions] = useState<BankQuestion[]>([]);
  const [totalQuestions, setTotalQuestions] = useState(0);
  
  // Filters for Question Bank
  const [difficultyFilter, setDifficultyFilter] = useState<string>("all");
  const [selectedTopicId, setSelectedTopicId] = useState<string>("all");
  const [expandedSolutions, setExpandedSolutions] = useState<Record<number, boolean>>({});
  
  // SRS flashcards states
  const [activeCardIndex, setActiveCardIndex] = useState(0);
  const [isCardRevealed, setIsCardRevealed] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLocale(getClientLocale());
    const handleLocale = () => setLocale(getClientLocale());
    window.addEventListener("localeChange", handleLocale);
    return () => window.removeEventListener("localeChange", handleLocale);
  }, []);

  useEffect(() => {
    loadBaseData();
  }, []);

  useEffect(() => {
    fetchBankQuestions();
  }, [locale, difficultyFilter, selectedTopicId]);

  const loadBaseData = async () => {
    try {
      const [quizList, cards, mistakeList] = await Promise.all([
        fetchApi<Quiz[]>("/quizzes").catch(() => []),
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

  const fetchBankQuestions = async () => {
    try {
      const diffParam = difficultyFilter !== "all" ? `&difficulty=${difficultyFilter}` : "";
      const topicParam = selectedTopicId !== "all" ? `&topic_id=${selectedTopicId}` : "";
      const res = await fetch(`/api/v1/questions?locale=${locale}&limit=20${diffParam}${topicParam}`);
      if (res.ok) {
        const data = await res.json();
        setBankQuestions(data.items || []);
        setTotalQuestions(data.total || 0);
      }
    } catch (err) {
      console.error("Failed to load bank questions", err);
    }
  };

  const toggleSolution = async (qId: number) => {
    const isExpanded = !!expandedSolutions[qId];
    if (!isExpanded) {
      // Fetch full detail if solutions not loaded
      try {
        const res = await fetch(`/api/v1/questions/${qId}?locale=${locale}`);
        if (res.ok) {
          const detail: BankQuestion = await res.json();
          setBankQuestions((prev) =>
            prev.map((q) => (q.id === qId ? { ...q, solutions: detail.solutions } : q))
          );
        }
      } catch (e) {
        console.error(e);
      }
    }
    setExpandedSolutions((prev) => ({ ...prev, [qId]: !isExpanded }));
  };

  const handleSrsRating = async (rating: number) => {
    const currentCard = srsCards[activeCardIndex];
    if (!currentCard) return;

    try {
      await fetchApi("/analytics/spaced-repetition/review", {
        method: "POST",
        body: JSON.stringify({
          question_id: currentCard.question_id,
          quality_rating: rating,
        }),
      });

      setIsCardRevealed(false);
      if (activeCardIndex + 1 < srsCards.length) {
        setActiveCardIndex(activeCardIndex + 1);
      } else {
        setSrsCards([]);
      }
    } catch (err) {
      console.error("Failed to submit rating", err);
    }
  };

  const t = i18nDict[locale] || i18nDict.kk;

  return (
    <div className="min-h-screen bg-[#fbfbfa] text-[#000000]">
      <Navbar onToggleSidebar={() => setSidebarOpen(!sidebarOpen)} />
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      <div className="lg:pl-64 flex flex-col min-h-[calc(100vh-57px)]">
        <main className="flex-1 p-4 sm:p-8 max-w-6xl w-full mx-auto space-y-8">
          
          {/* Header & Quick UNT 50 Action */}
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
              <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-[#0075de] mb-1">
                <CheckSquare className="w-4 h-4" />
                <span>ҰБТ 50/50 Информатика Тренажері</span>
              </div>
              <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-[#000000]">
                {locale === "kk" ? "Практика және Сұрақтар Банкі" : "Практика и Банк Вопросов"}
              </h1>
              <p className="text-xs sm:text-sm text-[#615d59] mt-1">
                {locale === "kk"
                  ? "ҰТО ресми таксономиясы мен провенансы бекітілген сұрақтар, пошаговые разборы және сынақ тесттері"
                  : "Официальный банк заданий НЦТ РК с провенансом, пошаговыми решениями и симуляцией 50 вопросов"}
              </p>
            </div>

            <Link
              href="/unt"
              className="btn-utility text-xs py-2 px-3.5 flex items-center gap-2 self-start md:self-auto border-purple-200 text-[#9d34da] hover:bg-purple-50"
            >
              <Layers className="w-4 h-4" />
              <span>{t.untKnowledge.specifications}</span>
            </Link>
          </div>

          {/* Navigation Tabs */}
          <div className="flex items-center gap-2 border-b border-[#e6e6e6] pb-2 overflow-x-auto scrollbar-none">
            <button
              onClick={() => setActiveTab("bank")}
              className={`px-4 py-2 text-xs font-bold rounded-lg transition-colors whitespace-nowrap ${
                activeTab === "bank"
                  ? "bg-[#0075de] text-white shadow-xs"
                  : "text-[#615d59] hover:bg-[#f6f5f4] hover:text-[#000000]"
              }`}
            >
              🏛️ {locale === "kk" ? "Ресми сұрақтар банкі" : "Банк вопросов ЕНТ"} ({totalQuestions})
            </button>
            <button
              onClick={() => setActiveTab("quizzes")}
              className={`px-4 py-2 text-xs font-bold rounded-lg transition-colors whitespace-nowrap ${
                activeTab === "quizzes"
                  ? "bg-[#0075de] text-white shadow-xs"
                  : "text-[#615d59] hover:bg-[#f6f5f4] hover:text-[#000000]"
              }`}
            >
              📝 {locale === "kk" ? "Тематикалық тестілер" : "Тематические тесты"} ({quizzes.length})
            </button>
            <button
              onClick={() => setActiveTab("srs")}
              className={`px-4 py-2 text-xs font-bold rounded-lg transition-colors whitespace-nowrap ${
                activeTab === "srs"
                  ? "bg-[#0075de] text-white shadow-xs"
                  : "text-[#615d59] hover:bg-[#f6f5f4] hover:text-[#000000]"
              }`}
            >
              ⚡ {locale === "kk" ? "Интервалды қайталау (SRS)" : "SRS Карточки"} ({srsCards.length})
            </button>
          </div>

          {/* TAB 1: OFFICIAL QUESTION BANK WITH PROVENANCE & SOLUTIONS */}
          {activeTab === "bank" && (
            <div className="space-y-6">
              {/* Filter Toolbar */}
              <div className="card-warm p-4 bg-white border border-[#e6e6e6] rounded-xl flex flex-wrap items-center justify-between gap-3">
                <div className="flex items-center gap-2 flex-wrap">
                  <span className="text-xs font-semibold text-[#615d59] flex items-center gap-1">
                    <Filter className="w-3.5 h-3.5" />
                    {t.common.filterBy}:
                  </span>

                  {/* Difficulty Filter */}
                  <select
                    value={difficultyFilter}
                    onChange={(e) => setDifficultyFilter(e.target.value)}
                    className="text-xs bg-[#f6f5f4] border border-[#e6e6e6] rounded-lg px-2.5 py-1.5 focus:outline-none focus:border-[#0075de]"
                  >
                    <option value="all">{t.questionBank.allDifficulties}</option>
                    <option value="A">{t.questionBank.easy}</option>
                    <option value="B">{t.questionBank.medium}</option>
                    <option value="C">{t.questionBank.hard}</option>
                  </select>
                </div>

                <div className="text-xs font-medium text-[#615d59]">
                  {locale === "kk" ? `Табылды: ${totalQuestions} сұрақ` : `Найдено: ${totalQuestions} вопросов`}
                </div>
              </div>

              {/* Question List */}
              <div className="space-y-4">
                {bankQuestions.map((q, idx) => {
                  const isExpanded = !!expandedSolutions[q.id];
                  return (
                    <div
                      key={q.id}
                      className="card-warm bg-white border border-[#e6e6e6] rounded-xl p-5 shadow-2xs space-y-4"
                    >
                      {/* Question Top Metadata */}
                      <div className="flex flex-wrap items-center justify-between gap-2">
                        <div className="flex items-center gap-2 flex-wrap">
                          <span className="text-[11px] font-extrabold px-2 py-0.5 rounded bg-blue-100 text-[#0075de]">
                            №{idx + 1} • Деңгей {q.difficulty}
                          </span>
                          <span className="inline-flex items-center gap-1 text-[11px] font-medium text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-100">
                            <ShieldCheck className="w-3 h-3" />
                            {q.official_status === "official" ? "ҰТО Ресми" : "Байқау үлгісі"}
                          </span>
                          {q.topic_title && (
                            <span className="text-[11px] text-[#615d59] font-medium">
                              • {q.topic_title}
                            </span>
                          )}
                        </div>

                        <span className="text-xs font-semibold text-[#8a8580]">
                          {q.year} жылғы ЕНТ
                        </span>
                      </div>

                      {/* Question Text */}
                      <div className="text-sm sm:text-base font-semibold text-[#000000] leading-relaxed">
                        {q.text}
                      </div>

                      {/* Code Snippet if present */}
                      {q.code_snippet && (
                        <div className="p-3.5 bg-[#1e1e1e] text-[#d4d4d4] rounded-lg font-mono text-xs overflow-x-auto leading-relaxed border border-[#333]">
                          <pre>{q.code_snippet}</pre>
                        </div>
                      )}

                      {/* Options */}
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 pt-2">
                        {q.options.map((opt) => (
                          <div
                            key={opt.id}
                            className={`p-3 rounded-lg border text-xs font-medium transition-all ${
                              opt.is_correct
                                ? "bg-emerald-50/70 border-emerald-300 text-emerald-950 font-semibold"
                                : "bg-[#fbfbfa] border-[#e6e6e6] text-[#31302e]"
                            }`}
                          >
                            <span className="font-bold text-[#615d59] mr-2">
                              {opt.option_key})
                            </span>
                            {opt.text}
                          </div>
                        ))}
                      </div>

                      {/* Provenance Metadata Bar */}
                      {q.provenance && q.provenance.length > 0 && (
                        <div className="pt-3 border-t border-[#f0efee] flex flex-wrap items-center justify-between text-[11px] text-[#8a8580] gap-2">
                          <div className="flex items-center gap-1.5">
                            <ShieldCheck className="w-3.5 h-3.5 text-[#0075de]" />
                            <span>
                              {t.questionBank.officialProvenance}: <strong>{q.provenance[0].source_title}</strong>
                            </span>
                          </div>
                          {q.provenance[0].source_url && (
                            <a
                              href={q.provenance[0].source_url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-[#0075de] hover:underline flex items-center gap-1"
                            >
                              <span>testcenter.kz</span>
                              <ExternalLink className="w-3 h-3" />
                            </a>
                          )}
                        </div>
                      )}

                      {/* Step-by-Step Solution Button & Drawer */}
                      <div className="pt-2">
                        <button
                          onClick={() => toggleSolution(q.id)}
                          className="inline-flex items-center gap-1.5 text-xs font-bold text-[#0075de] hover:text-[#005bb5] transition-colors"
                        >
                          <Lightbulb className="w-3.5 h-3.5" />
                          <span>{t.questionBank.viewSolution}</span>
                          {isExpanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                        </button>

                        {isExpanded && q.solutions && q.solutions.length > 0 && (
                          <div className="mt-3 p-4 bg-blue-50/60 border border-blue-200/70 rounded-xl text-xs space-y-2 animate-in fade-in duration-150">
                            <div className="font-bold text-[#0075de] uppercase tracking-wider text-[10px]">
                              Пошаговое аналитическое решение ({q.solutions[0].approach_type})
                            </div>
                            <p className="text-[#1e293b] leading-relaxed whitespace-pre-line">
                              {q.solutions[0].step_by_step_explanation}
                            </p>
                            {q.solutions[0].exam_tip && (
                              <div className="mt-2 pt-2 border-t border-blue-200/50 text-[#0369a1] font-medium flex items-start gap-1.5">
                                <Sparkles className="w-3.5 h-3.5 shrink-0 text-amber-500 mt-0.5" />
                                <span><strong>{t.questionBank.examTip}:</strong> {q.solutions[0].exam_tip}</span>
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* TAB 2: AVAILABLE THEMATIC QUIZZES */}
          {activeTab === "quizzes" && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {quizzes.map((q) => (
                <div key={q.id} className="card-warm p-5 bg-white border border-[#e6e6e6] rounded-xl flex flex-col justify-between">
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
          )}

          {/* TAB 3: SPACED REPETITION FLASHCARDS */}
          {activeTab === "srs" && (
            <div className="max-w-2xl mx-auto space-y-6">
              {srsCards.length === 0 ? (
                <div className="card-warm p-8 text-center bg-white border border-[#e6e6e6] rounded-xl">
                  <CheckCircle2 className="w-12 h-12 text-emerald-500 mx-auto mb-3" />
                  <h3 className="text-base font-bold text-[#000000]">Барлық карточкалар қайталанды!</h3>
                  <p className="text-xs text-[#615d59] mt-1">Интервалды қайталау жүйесі жаңа сұрақтарды ертең ұсынады.</p>
                </div>
              ) : (
                <div className="card-warm p-6 bg-white border border-[#e6e6e6] rounded-2xl shadow-xs space-y-4">
                  <div className="flex justify-between text-xs text-[#615d59]">
                    <span>Карточка {activeCardIndex + 1} / {srsCards.length}</span>
                    <span className="font-semibold text-[#0075de]">SM-2 алгоритмі</span>
                  </div>

                  <div className="text-base font-bold text-[#000000] pt-2">
                    {srsCards[activeCardIndex].question_text}
                  </div>

                  {isCardRevealed && (
                    <div className="space-y-2 pt-4 border-t border-[#f0efee] animate-in fade-in">
                      {srsCards[activeCardIndex].options.map((opt) => (
                        <div key={opt.id} className="p-3 bg-[#f6f5f4] rounded-lg text-xs font-medium">
                          {opt.text}
                        </div>
                      ))}
                    </div>
                  )}

                  {!isCardRevealed ? (
                    <button
                      onClick={() => setIsCardRevealed(true)}
                      className="btn-primary w-full py-2.5 text-xs font-semibold justify-center shadow-xs mt-4"
                    >
                      Жауабын көрсету
                    </button>
                  ) : (
                    <div className="grid grid-cols-4 gap-2 pt-4">
                      <button onClick={() => handleSrsRating(1)} className="btn-utility text-xs py-2 text-red-600 hover:bg-red-50">1: Ұмыттым</button>
                      <button onClick={() => handleSrsRating(3)} className="btn-utility text-xs py-2 text-amber-600 hover:bg-amber-50">3: Қиналдым</button>
                      <button onClick={() => handleSrsRating(4)} className="btn-utility text-xs py-2 text-blue-600 hover:bg-blue-50">4: Есімде</button>
                      <button onClick={() => handleSrsRating(5)} className="btn-utility text-xs py-2 text-emerald-600 hover:bg-emerald-50">5: Өте оңай</button>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}

        </main>
      </div>

      <Footer />
    </div>
  );
}
