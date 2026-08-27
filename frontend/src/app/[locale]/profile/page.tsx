"use client";

import React, { useState, useEffect } from "react";
import { Navbar } from "@/components/layout/Navbar";
import { Sidebar } from "@/components/layout/Sidebar";
import { Footer } from "@/components/layout/Footer";
import { fetchApi } from "@/lib/api";
import { getAuth } from "@/lib/auth";
import { StudentDashboardAnalytics, MistakeLogItem } from "@/types/analytics";
import { GamificationProfile } from "@/types/gamification";
import {
  User,
  Target,
  BarChart3,
  TrendingUp,
  BrainCircuit,
  AlertCircle,
  Clock,
  CheckCircle2,
  Zap,
} from "lucide-react";

export default function ProfileAnalyticsPage() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [analytics, setAnalytics] = useState<StudentDashboardAnalytics | null>(null);
  const [gamification, setGamification] = useState<GamificationProfile | null>(null);
  const [mistakes, setMistakes] = useState<MistakeLogItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadProfileData = async () => {
      try {
        const [dashData, gameData, mistakeList] = await Promise.all([
          fetchApi<StudentDashboardAnalytics>("/analytics/dashboard"),
          fetchApi<GamificationProfile>("/gamification/profile"),
          fetchApi<MistakeLogItem[]>("/analytics/mistakes").catch(() => []),
        ]);
        setAnalytics(dashData);
        setGamification(gameData);
        setMistakes(mistakeList);
      } catch (err) {
        console.error("Failed to load analytics", err);
      } finally {
        setLoading(false);
      }
    };
    loadProfileData();
  }, []);

  const readiness = analytics?.unt_readiness_score || 75;
  const predictedScore = Math.round((readiness / 100) * 50);

  return (
    <div className="min-h-screen flex flex-col bg-[#f6f5f4]">
      <Navbar onToggleSidebar={() => setSidebarOpen(!sidebarOpen)} />

      <div className="flex-1 flex max-w-7xl w-full mx-auto">
        <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

        <main className="flex-1 lg:pl-64 p-4 sm:p-6 lg:p-8 space-y-8 max-w-5xl">
          
          {/* User Profile Card */}
          <div className="bg-white border border-[#e6e6e6] rounded-2xl p-6 sm:p-8 shadow-xs flex flex-col sm:flex-row sm:items-center justify-between gap-6">
            <div className="flex items-center gap-4">
              <div className="w-16 h-16 rounded-2xl bg-[#0075de] text-white flex items-center justify-center font-bold text-2xl shadow-md">
                {gamification?.display_name ? gamification.display_name.charAt(0).toUpperCase() : "U"}
              </div>
              <div>
                <div className="inline-block text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded bg-blue-50 text-[#0075de] mb-1">
                  {gamification?.rank_title || "Исследователь Информатики"}
                </div>
                <h1 className="heading-2 text-[#000000]">{gamification?.display_name || "Ученик"}</h1>
                <p className="text-xs text-[#615d59]">
                  Уровень {gamification?.current_level || 1} • {gamification?.current_xp || 0} XP накоплено
                </p>
              </div>
            </div>

            {/* Target vs Predicted score */}
            <div className="p-4 bg-[#f6f5f4] rounded-xl border border-[#e6e6e6] flex items-center gap-6">
              <div>
                <span className="text-[10px] uppercase font-bold text-[#a39e98] block">
                  Прогноз ЕНТ:
                </span>
                <span className="text-2xl font-bold text-[#0075de] font-mono">
                  {predictedScore} <span className="text-xs text-[#615d59]">/ 50</span>
                </span>
              </div>
              <div className="w-px h-8 bg-[#e6e6e6]" />
              <div>
                <span className="text-[10px] uppercase font-bold text-[#a39e98] block">
                  Целевой балл:
                </span>
                <span className="text-2xl font-bold text-[#1aae39] font-mono">
                  50 <span className="text-xs text-[#615d59]">/ 50</span>
                </span>
              </div>
            </div>
          </div>

          {/* Topic Mastery Breakdown */}
          <div className="notion-card p-6 sm:p-8 bg-white space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="heading-3 text-[#000000]">Матрица готовности по темам ЕНТ</h2>
                <p className="text-xs text-[#615d59]">
                  Процент освоения рассчитывается на основе точности решения тестов и задач по коду
                </p>
              </div>
            </div>

            <div className="space-y-4">
              {analytics?.all_topic_masteries && analytics.all_topic_masteries.length > 0 ? (
                analytics.all_topic_masteries.map((tm) => (
                  <div key={tm.topic_id} className="space-y-1.5">
                    <div className="flex items-center justify-between text-xs font-semibold">
                      <span className="text-[#000000]">{tm.topic_title}</span>
                      <span className="text-[#0075de]">{tm.mastery_percentage}%</span>
                    </div>
                    <div className="w-full h-2 bg-[#f6f5f4] rounded-full overflow-hidden border border-[#e6e6e6]">
                      <div
                        className="h-full bg-[#0075de] rounded-full transition-all duration-500"
                        style={{ width: `${tm.mastery_percentage}%` }}
                      />
                    </div>
                  </div>
                ))
              ) : (
                [
                  { title: "Системы счисления и логика", pct: 85 },
                  { title: "Программирование на Python", pct: 72 },
                  { title: "Базы данных и SQL", pct: 90 },
                  { title: "Компьютерные сети и Интернет", pct: 60 },
                  { title: "Информационная безопасность", pct: 80 },
                  { title: "Алгоритмы и структуры данных", pct: 68 },
                ].map((item, idx) => (
                  <div key={idx} className="space-y-1.5">
                    <div className="flex items-center justify-between text-xs font-semibold">
                      <span className="text-[#000000]">{item.title}</span>
                      <span className="text-[#0075de]">{item.pct}%</span>
                    </div>
                    <div className="w-full h-2 bg-[#f6f5f4] rounded-full overflow-hidden border border-[#e6e6e6]">
                      <div
                        className="h-full bg-[#0075de] rounded-full"
                        style={{ width: `${item.pct}%` }}
                      />
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Mistakes Log Review List */}
          <div className="notion-card p-6 sm:p-8 bg-white space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="heading-3 text-[#000000]">Журнал ошибок</h2>
                <p className="text-xs text-[#615d59]">
                  Вопросы, в которых вы допускали ошибки при прохождении тестов
                </p>
              </div>
              <span className="text-xs font-bold text-red-600 bg-red-50 px-2.5 py-1 rounded-full border border-red-200">
                {mistakes.length} записей
              </span>
            </div>

            {mistakes.length === 0 ? (
              <div className="p-8 text-center text-xs text-[#615d59] border border-dashed rounded-xl">
                Отлично! Все допущенные ранее ошибки успешно отработаны и закрыты в SM-2.
              </div>
            ) : (
              <div className="divide-y divide-[#e6e6e6]">
                {mistakes.map((m) => (
                  <div key={m.id} className="py-3.5 space-y-1.5">
                    <div className="flex items-center justify-between">
                      <span className="text-[11px] font-bold text-red-600">
                        Ошибок: {m.error_count}
                      </span>
                      <span className="text-[10px] text-[#a39e98]">
                        {new Date(m.last_mistake_at).toLocaleDateString("ru-RU")}
                      </span>
                    </div>
                    <p className="text-xs font-medium text-[#000000]">{m.question_text}</p>
                    {m.explanation && (
                      <p className="text-[11px] text-[#615d59] bg-[#f6f5f4] p-2 rounded-lg">
                        {m.explanation}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>

        </main>
      </div>

      <Footer />
    </div>
  );
}
