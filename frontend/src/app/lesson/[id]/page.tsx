"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { Navbar } from "@/components/layout/Navbar";
import { Footer } from "@/components/layout/Footer";
import { fetchApi } from "@/lib/api";
import { Lesson } from "@/types/learning";
import { LevelUpCelebration } from "@/components/gamification/LevelUpCelebration";
import {
  ArrowLeft,
  CheckCircle2,
  HelpCircle,
  Zap,
  Sparkles,
  BookOpen,
  ArrowRight,
} from "lucide-react";

export default function LessonDetailPage() {
  const params = useParams();
  const router = useRouter();
  const lessonId = params?.id as string;

  const [lesson, setLesson] = useState<Lesson | null>(null);
  const [loading, setLoading] = useState(true);
  const [completing, setCompleting] = useState(false);
  const [completed, setCompleted] = useState(false);
  const [celebration, setCelebration] = useState<{ newLevel: number; xp: number } | null>(null);

  useEffect(() => {
    if (!lessonId) return;

    const loadLesson = async () => {
      try {
        const data = await fetchApi<Lesson>(`/courses/lessons/${lessonId}`);
        setLesson(data);
        setCompleted(!!data.is_completed_by_user);
      } catch (err) {
        console.error("Failed to load lesson", err);
      } finally {
        setLoading(false);
      }
    };

    loadLesson();
  }, [lessonId]);

  const handleComplete = async () => {
    if (!lesson || completing) return;
    setCompleting(true);

    try {
      const res = await fetchApi<{
        is_completed: boolean;
        xp_earned: number;
        new_total_xp: number;
        new_level: number;
        leveled_up: boolean;
      }>(`/courses/lessons/${lesson.id}/complete`, { method: "POST" });

      setCompleted(true);

      if (res.leveled_up) {
        setCelebration({
          newLevel: res.new_level,
          xp: res.xp_earned,
        });
      }
    } catch (err: any) {
      alert(err.message);
    } finally {
      setCompleting(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#f6f5f4]">
        <div className="w-8 h-8 border-3 border-[#0075de] border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (!lesson) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-[#f6f5f4] p-6 text-center">
        <h2 className="heading-2 mb-2">Урок не найден</h2>
        <Link href="/learn" className="btn-primary text-xs">
          Вернуться к темам
        </Link>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col bg-[#f6f5f4]">
      <Navbar />

      <main className="max-w-4xl mx-auto w-full px-4 sm:px-6 py-8 flex-1 space-y-8">
        
        {/* Navigation Breadcrumbs */}
        <div className="flex items-center justify-between gap-4">
          <Link
            href="/learn"
            className="inline-flex items-center gap-1.5 text-xs font-semibold text-[#615d59] hover:text-[#000000] transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Назад к программе</span>
          </Link>

          <div className="flex items-center gap-1.5 text-xs font-bold text-[#0075de] bg-blue-50 px-3 py-1 rounded-full border border-blue-200/50">
            <Zap className="w-3.5 h-3.5 fill-[#0075de]" />
            <span>+{lesson.xp_reward} XP за завершение</span>
          </div>
        </div>

        {/* Lesson Article Paper Card */}
        <article className="notion-card-elevated p-6 sm:p-10 bg-white">
          <div className="mb-6 pb-6 border-b border-[#e6e6e6]">
            <span className="eyebrow text-[#0075de] block mb-2 font-semibold">
              Теория и Практика ЕНТ
            </span>
            <h1 className="heading-1 text-[#000000] mb-3">{lesson.title}</h1>
            {lesson.summary && (
              <p className="text-sm text-[#615d59] leading-relaxed">
                {lesson.summary}
              </p>
            )}
          </div>

          {/* Lesson Body Content formatted in structured blocks */}
          <div className="prose prose-stone max-w-none text-sm leading-relaxed text-[#31302e] space-y-6">
            <div className="whitespace-pre-wrap font-sans text-sm sm:text-base leading-7">
              {lesson.content}
            </div>
          </div>

          {/* Key Takeaways & Exam Tips Box */}
          <div className="mt-10 p-5 bg-blue-50/70 border border-blue-200/60 rounded-xl">
            <div className="flex items-center gap-2 font-bold text-xs text-[#0075de] uppercase tracking-wider mb-2">
              <Sparkles className="w-4 h-4" />
              <span>Совет для ЕНТ (Ловушка составителей тестов)</span>
            </div>
            <p className="text-xs text-[#31302e] leading-relaxed">
              В вопросах по этой теме внимательно обращайте внимание на граничные условия и систему счисления. В тестах НЦТ часто дают похожие варианты ответов со сдвигом на единицу.
            </p>
          </div>

          {/* Action Footer */}
          <div className="mt-10 pt-6 border-t border-[#e6e6e6] flex flex-col sm:flex-row items-center justify-between gap-4">
            <button
              onClick={handleComplete}
              disabled={completing || completed}
              className={`btn-primary w-full sm:w-auto px-6 py-2.5 text-xs font-semibold ${
                completed
                  ? "bg-green-600 hover:bg-green-700 cursor-default"
                  : "bg-[#0075de] hover:bg-[#005bab]"
              }`}
            >
              <CheckCircle2 className="w-4 h-4" />
              <span>
                {completed ? "Урок пройден ✓" : completing ? "Сохранение..." : "Отметить урок как пройденный"}
              </span>
            </button>

            <Link
              href="/practice"
              className="btn-secondary w-full sm:w-auto px-5 py-2.5 text-xs font-medium"
            >
              <span>Закрепить тему в тесте</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>
        </article>

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
