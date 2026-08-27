"use client";

import React, { useState, useEffect } from "react";
import { LocalizedLink as Link } from "@/components/navigation/LocalizedLink";
import { useParams, useRouter } from "next/navigation";
import { Navbar } from "@/components/layout/Navbar";
import { Footer } from "@/components/layout/Footer";
import { fetchApi } from "@/lib/api";
import { Quiz, QuizSubmitResult } from "@/types/learning";
import { QuestionRenderer } from "@/components/quiz/QuestionRenderer";
import { QuizTimer } from "@/components/quiz/QuizTimer";
import { LevelUpCelebration } from "@/components/gamification/LevelUpCelebration";
import {
  ArrowLeft,
  ArrowRight,
  CheckCircle2,
  AlertCircle,
  HelpCircle,
  Zap,
  RotateCcw,
  Trophy,
} from "lucide-react";

export default function QuizPlayPage() {
  const params = useParams();
  const router = useRouter();
  const quizId = params?.id as string;

  const [quiz, setQuiz] = useState<Quiz | null>(null);
  const [loading, setLoading] = useState(true);
  const [currentIndex, setCurrentIndex] = useState(0);

  // User responses state: map of questionId -> { selectedOptions: number[], textAnswer: string }
  const [userAnswers, setUserAnswers] = useState<
    Record<number, { selectedOptions: number[]; textAnswer: string }>
  >({});

  const [submitting, setSubmitting] = useState(false);
  const [submitResult, setSubmitResult] = useState<QuizSubmitResult | null>(null);
  const [timeSpent, setTimeSpent] = useState(0);
  const [celebration, setCelebration] = useState<{ newLevel: number; xp: number } | null>(null);

  useEffect(() => {
    if (!quizId) return;

    const loadQuiz = async () => {
      try {
        const data = await fetchApi<Quiz>(`/quizzes/${quizId}`);
        setQuiz(data);

        // Initialize state
        const initialAnswers: Record<number, { selectedOptions: number[]; textAnswer: string }> = {};
        data.questions?.forEach((q) => {
          initialAnswers[q.id] = { selectedOptions: [], textAnswer: "" };
        });
        setUserAnswers(initialAnswers);
      } catch (err) {
        console.error("Failed to load quiz", err);
      } finally {
        setLoading(false);
      }
    };

    loadQuiz();
  }, [quizId]);

  const handleOptionToggle = (optionId: number) => {
    if (!quiz?.questions) return;
    const currentQ = quiz.questions[currentIndex];
    const prev = userAnswers[currentQ.id] || { selectedOptions: [], textAnswer: "" };

    let newOptions: number[];
    if (currentQ.question_type === "multiple_choice") {
      newOptions = prev.selectedOptions.includes(optionId)
        ? prev.selectedOptions.filter((id) => id !== optionId)
        : [...prev.selectedOptions, optionId];
    } else {
      newOptions = [optionId];
    }

    setUserAnswers({
      ...userAnswers,
      [currentQ.id]: { ...prev, selectedOptions: newOptions },
    });
  };

  const handleTextAnswerChange = (text: string) => {
    if (!quiz?.questions) return;
    const currentQ = quiz.questions[currentIndex];
    const prev = userAnswers[currentQ.id] || { selectedOptions: [], textAnswer: "" };

    setUserAnswers({
      ...userAnswers,
      [currentQ.id]: { ...prev, textAnswer: text },
    });
  };

  const handleSubmitQuiz = async () => {
    if (!quiz?.questions || submitting) return;
    setSubmitting(true);

    try {
      const payload = {
        time_spent_seconds: timeSpent,
        answers: quiz.questions.map((q) => {
          const ans = userAnswers[q.id] || { selectedOptions: [], textAnswer: "" };
          return {
            question_id: q.id,
            selected_option_ids: ans.selectedOptions.length > 0 ? ans.selectedOptions : undefined,
            text_answer: ans.textAnswer ? ans.textAnswer : undefined,
          };
        }),
      };

      const result = await fetchApi<QuizSubmitResult>(`/quizzes/${quiz.id}/submit`, {
        method: "POST",
        body: JSON.stringify(payload),
      });

      setSubmitResult(result);

      if (result.leveled_up) {
        setCelebration({
          newLevel: result.new_level,
          xp: result.xp_earned,
        });
      }
    } catch (err: any) {
      alert(err.message || "Ошибка при отправке теста");
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#f6f5f4]">
        <div className="w-8 h-8 border-3 border-[#0075de] border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (!quiz || !quiz.questions || quiz.questions.length === 0) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-[#f6f5f4] p-6 text-center">
        <h2 className="heading-2 mb-2">Тест не содержит вопросов</h2>
        <Link href="/practice" className="btn-primary text-xs">
          Вернуться к тренажеру
        </Link>
      </div>
    );
  }

  // If Quiz Submitted -> Show Result Review Screen
  if (submitResult) {
    return (
      <div className="min-h-screen flex flex-col bg-[#f6f5f4]">
        <Navbar />

        <main className="max-w-4xl mx-auto w-full px-4 sm:px-6 py-10 space-y-8 flex-1">
          
          {/* Result Banner Card */}
          <div className="notion-card-elevated p-8 bg-white text-center">
            <div className={`w-16 h-16 rounded-2xl mx-auto mb-4 flex items-center justify-center ${
              submitResult.passed ? "bg-green-100 text-[#1aae39]" : "bg-amber-100 text-amber-700"
            }`}>
              <Trophy className="w-8 h-8" />
            </div>

            <span className="eyebrow text-[#0075de] block mb-1">
              Результат тестирования
            </span>
            <h1 className="heading-1 text-[#000000] mb-2">
              {submitResult.passed ? "Тест успешно сдан!" : "Тест завершен"}
            </h1>
            <p className="text-xs sm:text-sm text-[#615d59] max-w-md mx-auto mb-6">
              Вы набрали <span className="font-bold text-[#000000]">{submitResult.score}</span> из{" "}
              <span className="font-bold text-[#000000]">{submitResult.max_score} баллов</span> (
              {submitResult.percentage}%)
            </p>

            {/* XP Gained & Level Indicator */}
            <div className="flex flex-wrap items-center justify-center gap-4 mb-8">
              <div className="flex items-center gap-1.5 px-4 py-1.5 bg-blue-50 border border-blue-200/60 rounded-full text-xs font-bold text-[#0075de]">
                <Zap className="w-4 h-4 fill-[#0075de]" />
                <span>+{submitResult.xp_earned} XP заработано</span>
              </div>

              {submitResult.streak_extended && (
                <div className="flex items-center gap-1.5 px-4 py-1.5 bg-orange-50 border border-orange-200/60 rounded-full text-xs font-bold text-[#dd5b00]">
                  <span>Стрик продлен: {submitResult.current_streak} дн. 🔥</span>
                </div>
              )}
            </div>

            <div className="flex flex-wrap items-center justify-center gap-3">
              <Link href="/practice" className="btn-primary text-xs py-2 px-5">
                К списку тестов
              </Link>
              <button
                onClick={() => {
                  setSubmitResult(null);
                  setCurrentIndex(0);
                }}
                className="btn-secondary text-xs py-2 px-5"
              >
                <RotateCcw className="w-3.5 h-3.5" />
                <span>Пройти заново</span>
              </button>
            </div>
          </div>

          {/* Detailed Question Review & Explanations */}
          <div className="space-y-4">
            <h2 className="heading-3 text-[#000000]">Разбор ответов и пояснения</h2>

            <div className="space-y-4">
              {submitResult.answers_review.map((item, idx) => (
                <div
                  key={item.question_id}
                  className={`notion-card p-5 bg-white border-l-4 ${
                    item.is_correct ? "border-l-[#1aae39]" : "border-l-red-500"
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-bold text-[#a39e98]">
                      Вопрос {idx + 1}
                    </span>
                    <span
                      className={`text-xs font-bold px-2 py-0.5 rounded-full ${
                        item.is_correct
                          ? "bg-green-50 text-[#1aae39]"
                          : "bg-red-50 text-red-600"
                      }`}
                    >
                      {item.is_correct ? "Верно (+1)" : "Ошибка (0)"}
                    </span>
                  </div>

                  <h4 className="text-sm font-semibold text-[#000000] mb-3">
                    {item.question_text}
                  </h4>

                  {item.explanation && (
                    <div className="p-3 bg-[#f6f5f4] rounded-xl text-xs text-[#31302e] border border-[#e6e6e6]">
                      <span className="font-bold text-[#0075de] block mb-1">
                        Объяснение эксперта ЕНТ:
                      </span>
                      {item.explanation}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

        </main>

        {celebration && (
          <LevelUpCelebration
            newLevel={celebration.newLevel}
            xpEarned={celebration.xp}
            onClose={() => setCelebration(null)}
          />
        )}

        <Footer />
      </div>
    );
  }

  // Active Quiz Execution Mode
  const currentQuestion = quiz.questions[currentIndex];
  const currentAnswer = userAnswers[currentQuestion.id] || {
    selectedOptions: [],
    textAnswer: "",
  };

  const answeredCount = Object.values(userAnswers).filter(
    (a) => a.selectedOptions.length > 0 || a.textAnswer.trim() !== ""
  ).length;

  return (
    <div className="min-h-screen flex flex-col bg-[#f6f5f4]">
      <Navbar />

      <main className="max-w-4xl mx-auto w-full px-4 sm:px-6 py-6 flex-1 space-y-6">
        
        {/* Top Control Bar with Timer and Progress */}
        <div className="bg-white border border-[#e6e6e6] rounded-2xl p-4 sm:p-5 flex items-center justify-between shadow-xs">
          <div className="flex items-center gap-3">
            <Link
              href="/practice"
              className="p-1.5 text-[#615d59] hover:text-[#000000] rounded-lg hover:bg-[#f6f5f4] transition-colors"
            >
              <ArrowLeft className="w-5 h-5" />
            </Link>
            <div>
              <h2 className="font-bold text-sm text-[#000000] line-clamp-1">{quiz.title}</h2>
              <span className="text-[11px] text-[#615d59]">
                Отвечено {answeredCount} из {quiz.questions.length} вопросов
              </span>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <QuizTimer
              initialSeconds={quiz.time_limit_seconds}
              onTimeExpired={handleSubmitQuiz}
              onTick={(elapsed) => setTimeSpent(elapsed)}
            />
            <button
              onClick={handleSubmitQuiz}
              disabled={submitting}
              className="btn-primary text-xs py-1.5 px-3.5 shadow-xs"
            >
              <span>{submitting ? "Завершение..." : "Завершить тест"}</span>
            </button>
          </div>
        </div>

        {/* Question Numbers Navigator Pill Bar */}
        <div className="flex items-center gap-1.5 overflow-x-auto pb-2">
          {quiz.questions.map((q, idx) => {
            const isAnswered =
              (userAnswers[q.id]?.selectedOptions.length || 0) > 0 ||
              userAnswers[q.id]?.textAnswer?.trim() !== "";
            const isCurrent = currentIndex === idx;

            return (
              <button
                key={q.id}
                onClick={() => setCurrentIndex(idx)}
                className={`w-8 h-8 rounded-lg text-xs font-bold transition-all shrink-0 cursor-pointer ${
                  isCurrent
                    ? "bg-[#0075de] text-white shadow-xs"
                    : isAnswered
                    ? "bg-green-100 text-green-800 border border-green-300"
                    : "bg-white text-[#615d59] border border-[#e6e6e6] hover:bg-[#f6f5f4]"
                }`}
              >
                {idx + 1}
              </button>
            );
          })}
        </div>

        {/* Question Active Card */}
        <div className="notion-card-elevated p-6 sm:p-8 bg-white min-h-[380px] flex flex-col justify-between">
          <div className="mb-8">
            <div className="text-[11px] font-bold text-[#a39e98] uppercase tracking-wider mb-2">
              Вопрос {currentIndex + 1} из {quiz.questions.length}
            </div>

            <QuestionRenderer
              question={currentQuestion}
              selectedOptionIds={currentAnswer.selectedOptions}
              textAnswer={currentAnswer.textAnswer}
              onOptionToggle={handleOptionToggle}
              onTextAnswerChange={handleTextAnswerChange}
            />
          </div>

          {/* Navigation Controls */}
          <div className="pt-6 border-t border-[#e6e6e6] flex items-center justify-between">
            <button
              onClick={() => setCurrentIndex((prev) => Math.max(0, prev - 1))}
              disabled={currentIndex === 0}
              className="btn-secondary text-xs py-2 px-4 disabled:opacity-40"
            >
              <ArrowLeft className="w-3.5 h-3.5" />
              <span>Предыдущий</span>
            </button>

            {currentIndex + 1 < quiz.questions.length ? (
              <button
                onClick={() => setCurrentIndex((prev) => prev + 1)}
                className="btn-primary text-xs py-2 px-4 shadow-xs"
              >
                <span>Следующий вопрос</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            ) : (
              <button
                onClick={handleSubmitQuiz}
                disabled={submitting}
                className="btn-primary text-xs py-2 px-5 bg-[#1aae39] hover:bg-[#158f2e] text-white shadow-xs font-semibold"
              >
                <CheckCircle2 className="w-4 h-4" />
                <span>{submitting ? "Проверка..." : "Сдать тест"}</span>
              </button>
            )}
          </div>
        </div>

      </main>

      <Footer />
    </div>
  );
}
