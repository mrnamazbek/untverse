"use client";

import React, { useState, useEffect } from "react";
import { LocalizedLink as Link } from "@/components/navigation/LocalizedLink";
import { useRouter } from "next/navigation";
import { Navbar } from "@/components/layout/Navbar";
import { Sidebar } from "@/components/layout/Sidebar";
import { Footer } from "@/components/layout/Footer";
import { fetchApi } from "@/lib/api";
import { getAuth } from "@/lib/auth";
import { getClientLocale, localizePath } from "@/lib/i18n";
import { StudentDashboardAnalytics } from "@/types/analytics";
import { GamificationProfile } from "@/types/gamification";
import { DailyQuestsCard } from "@/components/gamification/DailyQuestsCard";
import { LevelUpCelebration } from "@/components/gamification/LevelUpCelebration";
import {
  Flame,
  Zap,
  Target,
  Trophy,
  BookOpen,
  CheckSquare,
  Code2,
  AlertTriangle,
  ArrowRight,
  TrendingUp,
  BrainCircuit,
  Clock,
  Sparkles,
} from "lucide-react";

export default function DashboardPage() {
  const router = useRouter();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [analytics, setAnalytics] = useState<StudentDashboardAnalytics | null>(null);
  const [gamification, setGamification] = useState<GamificationProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [celebration, setCelebration] = useState<{ newLevel: number; xp: number } | null>(null);

  useEffect(() => {
    const auth = getAuth();
    if (!auth) {
      router.push(localizePath("/login", getClientLocale()));
      return;
    }

    const loadData = async () => {
      try {
        const [dashRes, gameRes] = await Promise.all([
          fetchApi<StudentDashboardAnalytics>("/analytics/dashboard"),
          fetchApi<GamificationProfile>("/gamification/profile"),
        ]);
        setAnalytics(dashRes);
        setGamification(gameRes);
      } catch (err) {
        console.error("Failed loading dashboard data", err);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [router]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#f6f5f4]">
        <div className="flex flex-col items-center gap-3">
          <div className="w-8 h-8 border-3 border-[#0075de] border-t-transparent rounded-full animate-spin" />
          <span className="text-xs font-semibold text-[#615d59]">Загрузка командного центра...</span>
        </div>
      </div>
    );
  }

  const readinessScore = analytics?.unt_readiness_score || 72;
  const predictedPoints = Math.round((readinessScore / 100) * 50);

  return (
    <div className="min-h-screen flex flex-col bg-[#f6f5f4]">
      <Navbar onToggleSidebar={() => setSidebarOpen(!sidebarOpen)} />

      <div className="flex-1 flex max-w-7xl w-full mx-auto">
        <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

        <main className="flex-1 lg:pl-64 p-4 sm:p-6 lg:p-8 space-y-8 max-w-6xl">
          
          {/* Welcome Banner */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white border border-[#e6e6e6] rounded-2xl p-6 shadow-xs">
            <div>
              <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-blue-50 text-[#0075de] text-[11px] font-bold uppercase tracking-wider mb-2">
                <Sparkles className="w-3 h-3" />
                <span>{gamification?.rank_title || "Исследователь Информатики"}</span>
              </div>
              <h1 className="heading-2 text-[#000000]">
                С возвращением, {gamification?.display_name || "Ученик"}!
              </h1>
              <p className="text-xs text-[#615d59] mt-1">
                До основного ЕНТ осталось совсем немного. Ваш текущий стрик:{" "}
                <span className="font-bold text-[#dd5b00]">
                  {gamification?.streak.current_streak || 1} {gamification?.streak.current_streak === 1 ? "день" : "дней"} подряд 🔥
                </span>
              </p>
            </div>

            <div className="flex items-center gap-3">
              <Link href="/practice" className="btn-primary text-xs py-2 px-4 shadow-xs">
                <CheckSquare className="w-3.5 h-3.5" />
                <span>Тренировка ЕНТ</span>
              </Link>
              <Link href="/coding" className="btn-secondary text-xs py-2 px-4">
                <Code2 className="w-3.5 h-3.5 text-[#0075de]" />
                <span>Задачи Python</span>
              </Link>
            </div>
          </div>

          {/* Metric KPIs Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            
            {/* KPI 1: UNT Readiness */}
            <div className="notion-card p-5 bg-white flex flex-col justify-between">
              <div className="flex items-center justify-between text-xs text-[#615d59] mb-2">
                <span className="font-medium">Готовность к ЕНТ</span>
                <Target className="w-4 h-4 text-[#0075de]" />
              </div>
              <div className="flex items-baseline gap-2">
                <span className="text-3xl font-bold text-[#000000]">{readinessScore}%</span>
                <span className="text-xs font-semibold text-[#1aae39] flex items-center">
                  <TrendingUp className="w-3 h-3 mr-0.5" /> +5% за неделю
                </span>
              </div>
              <div className="mt-3 text-[11px] text-[#615d59]">
                Прогноз: <span className="font-bold text-[#0075de]">{predictedPoints} из 50 баллов</span>
              </div>
            </div>

            {/* KPI 2: Total XP & Level */}
            <div className="notion-card p-5 bg-white flex flex-col justify-between">
              <div className="flex items-center justify-between text-xs text-[#615d59] mb-2">
                <span className="font-medium">Опыт и Уровень</span>
                <Zap className="w-4 h-4 text-[#0075de] fill-[#0075de]" />
              </div>
              <div className="flex items-baseline gap-2">
                <span className="text-3xl font-bold text-[#000000]">{gamification?.current_xp || 0}</span>
                <span className="text-xs font-semibold text-[#0075de]">XP</span>
              </div>
              <div className="mt-3 text-[11px] text-[#615d59]">
                Уровень {gamification?.current_level} • До след: {gamification?.next_level_xp || 150} XP
              </div>
            </div>

            {/* KPI 3: Quizzes Passed */}
            <div className="notion-card p-5 bg-white flex flex-col justify-between">
              <div className="flex items-center justify-between text-xs text-[#615d59] mb-2">
                <span className="font-medium">Точность тестов</span>
                <CheckSquare className="w-4 h-4 text-[#1aae39]" />
              </div>
              <div className="flex items-baseline gap-2">
                <span className="text-3xl font-bold text-[#000000]">
                  {analytics?.average_quiz_accuracy || 84}%
                </span>
                <span className="text-xs text-[#615d59]">точность</span>
              </div>
              <div className="mt-3 text-[11px] text-[#615d59]">
                Сдано тестов: <span className="font-semibold text-[#000000]">{analytics?.quizzes_completed_count || 3}</span>
              </div>
            </div>

            {/* KPI 4: SM-2 Due Reviews */}
            <div className="notion-card p-5 bg-white flex flex-col justify-between">
              <div className="flex items-center justify-between text-xs text-[#615d59] mb-2">
                <span className="font-medium">Повторение SM-2</span>
                <BrainCircuit className="w-4 h-4 text-[#dd5b00]" />
              </div>
              <div className="flex items-baseline gap-2">
                <span className="text-3xl font-bold text-[#dd5b00]">
                  {analytics?.due_reviews_count || 0}
                </span>
                <span className="text-xs text-[#615d59]">карточек к повторению</span>
              </div>
              <div className="mt-3">
                <Link
                  href="/practice"
                  className="text-[11px] font-semibold text-[#0075de] hover:underline"
                >
                  Повторить ошибки сейчас →
                </Link>
              </div>
            </div>

          </div>

          {/* Main 2-Column Section */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            
            {/* Left Column (2 cols): Recommended Plan & Weak Spots */}
            <div className="lg:col-span-2 space-y-6">
              
              {/* Daily Study Recommendation */}
              <div className="notion-card p-6 bg-white">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-2">
                    <div className="w-8 h-8 rounded-lg bg-blue-50 text-[#0075de] flex items-center justify-center font-bold">
                      <BookOpen className="w-4 h-4" />
                    </div>
                    <div>
                      <h3 className="font-bold text-sm text-[#000000]">Рекомендованный шаг сегодня</h3>
                      <p className="text-[11px] text-[#615d59]">Персональный план подготовки</p>
                    </div>
                  </div>
                  <span className="text-[11px] font-semibold px-2 py-0.5 rounded bg-blue-50 text-[#0075de]">
                    +75 XP
                  </span>
                </div>

                <div className="p-4 bg-[#f6f5f4] rounded-xl border border-[#e6e6e6] flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                  <div>
                    <span className="text-[10px] font-bold uppercase tracking-wider text-[#0075de] block mb-1">
                      Модуль: Базы данных и SQL
                    </span>
                    <h4 className="font-bold text-sm text-[#000000]">
                      Тема 3: Реляционные базы данных и оператор SELECT
                    </h4>
                    <p className="text-xs text-[#615d59] mt-0.5">
                      Ключевой раздел ЕНТ: фильтрация WHERE, группировка GROUP BY и соединение таблиц JOIN.
                    </p>
                  </div>

                  <Link
                    href="/learn"
                    className="btn-primary text-xs py-2 px-4 shrink-0 shadow-xs"
                  >
                    <span>Перейти к уроку</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </Link>
                </div>
              </div>

              {/* Weakest Topics / Focus Areas */}
              <div className="notion-card p-6 bg-white">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-2">
                    <div className="w-8 h-8 rounded-lg bg-red-50 text-red-600 flex items-center justify-center">
                      <AlertTriangle className="w-4 h-4" />
                    </div>
                    <div>
                      <h3 className="font-bold text-sm text-[#000000]">Зоны роста (Темы требующие внимания)</h3>
                      <p className="text-[11px] text-[#615d59]">Определены на основе ошибок в тестах</p>
                    </div>
                  </div>
                </div>

                <div className="space-y-3">
                  {analytics?.weakest_topics && analytics.weakest_topics.length > 0 ? (
                    analytics.weakest_topics.map((wt) => (
                      <div
                        key={wt.topic_id}
                        className="p-3 bg-[#f6f5f4]/80 rounded-xl border border-[#e6e6e6] flex items-center justify-between"
                      >
                        <div>
                          <h5 className="text-xs font-semibold text-[#000000]">{wt.topic_title}</h5>
                          <span className="text-[11px] text-[#615d59]">
                            Верно: {wt.correct_count} из {wt.total_answered} вопросов
                          </span>
                        </div>
                        <div className="flex items-center gap-3">
                          <span className="text-xs font-bold text-red-600">
                            {wt.mastery_percentage}%
                          </span>
                          <Link
                            href={`/learn/${wt.topic_slug}`}
                            className="btn-utility text-[11px] py-1 px-2.5"
                          >
                            Повторить
                          </Link>
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="p-3 bg-[#f6f5f4] rounded-xl border border-[#e6e6e6] flex items-center justify-between">
                      <div>
                        <h5 className="text-xs font-semibold text-[#000000]">Системы счисления и логика</h5>
                        <span className="text-[11px] text-[#615d59]">Рекомендуется освежить перевод из 2 в 16 с/с</span>
                      </div>
                      <Link href="/learn" className="btn-utility text-[11px] py-1 px-2.5">
                        Тренировать
                      </Link>
                    </div>
                  )}
                </div>
              </div>

            </div>

            {/* Right Column (1 col): Daily Quests & Quick Actions */}
            <div className="space-y-6">
              
              {/* Daily Quests Component */}
              {gamification?.daily_missions && (
                <DailyQuestsCard
                  missions={gamification.daily_missions}
                  onRewardClaimed={(xp) => {
                    // Update profile XP locally
                    if (gamification) {
                      setGamification({
                        ...gamification,
                        current_xp: gamification.current_xp + xp,
                      });
                    }
                  }}
                />
              )}

              {/* Quick Jump Box */}
              <div className="notion-card p-5 bg-gradient-to-br from-[#213183] to-[#17225c] text-white">
                <h4 className="font-bold text-sm mb-1.5 flex items-center gap-2">
                  <Trophy className="w-4 h-4 text-yellow-400" />
                  Готовы проверить силы?
                </h4>
                <p className="text-xs text-blue-100/80 mb-4 leading-relaxed">
                  Пройдите полноценный пробный вариант ЕНТ с таймером на 50 минут.
                </p>
                <Link
                  href="/practice"
                  className="w-full btn-primary text-xs py-2 bg-white text-[#213183] hover:bg-blue-50 font-bold justify-center"
                >
                  Запустить тест ЕНТ
                </Link>
              </div>

            </div>

          </div>

        </main>
      </div>

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
