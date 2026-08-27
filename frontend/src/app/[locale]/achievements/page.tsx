"use client";

import React, { useState, useEffect } from "react";
import { Navbar } from "@/components/layout/Navbar";
import { Sidebar } from "@/components/layout/Sidebar";
import { Footer } from "@/components/layout/Footer";
import { fetchApi } from "@/lib/api";
import { Achievement } from "@/types/gamification";
import { Award, Lock, CheckCircle2, Zap, Sparkles } from "lucide-react";

export default function AchievementsPage() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [achievements, setAchievements] = useState<Achievement[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadAchievements = async () => {
      try {
        const data = await fetchApi<Achievement[]>("/gamification/achievements");
        setAchievements(data);
      } catch (err) {
        console.error("Failed to load achievements", err);
      } finally {
        setLoading(false);
      }
    };
    loadAchievements();
  }, []);

  const unlockedCount = achievements.filter((a) => a.is_unlocked).length;

  return (
    <div className="min-h-screen flex flex-col bg-[#f6f5f4]">
      <Navbar onToggleSidebar={() => setSidebarOpen(!sidebarOpen)} />

      <div className="flex-1 flex max-w-7xl w-full mx-auto">
        <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

        <main className="flex-1 lg:pl-64 p-4 sm:p-6 lg:p-8 space-y-8 max-w-5xl">
          
          <div className="bg-white border border-[#e6e6e6] rounded-2xl p-6 sm:p-8 shadow-xs flex flex-col sm:flex-row sm:items-center justify-between gap-6">
            <div>
              <span className="eyebrow text-[#0075de] block mb-1 font-semibold">
                Зал славы
              </span>
              <h1 className="heading-1 text-[#000000] mb-2">Достижения и значки</h1>
              <p className="text-xs sm:text-sm text-[#615d59] max-w-xl leading-relaxed">
                Открывайте редкие бейджи за точность в тестах, непрерывные стрики и безупречное решение задач по коду.
              </p>
            </div>

            <div className="p-4 bg-[#f6f5f4] rounded-xl border border-[#e6e6e6] text-center shrink-0">
              <div className="text-2xl font-bold text-[#0075de]">
                {unlockedCount} / {achievements.length}
              </div>
              <div className="text-[11px] text-[#615d59] font-medium mt-0.5">
                Разблокировано
              </div>
            </div>
          </div>

          {loading ? (
            <div className="p-12 text-center text-xs text-[#615d59]">
              Загрузка достижений...
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
              {achievements.map((ach) => (
                <div
                  key={ach.id}
                  className={`notion-card p-6 flex flex-col justify-between transition-all ${
                    ach.is_unlocked
                      ? "bg-white border-blue-200/80 shadow-xs"
                      : "bg-[#f6f5f4]/50 opacity-70 grayscale-50"
                  }`}
                >
                  <div>
                    <div className="flex items-center justify-between mb-4">
                      <div
                        className={`w-12 h-12 rounded-2xl flex items-center justify-center text-xl shadow-xs border ${
                          ach.is_unlocked
                            ? "bg-blue-50 text-[#0075de] border-blue-200"
                            : "bg-stone-200 text-stone-500 border-stone-300"
                        }`}
                      >
                        {ach.is_unlocked ? (
                          <Award className="w-6 h-6 text-[#0075de]" />
                        ) : (
                          <Lock className="w-5 h-5 text-stone-400" />
                        )}
                      </div>

                      <span className="text-xs font-bold text-[#0075de] bg-blue-50 px-2 py-0.5 rounded-full border border-blue-200/50">
                        +{ach.xp_reward} XP
                      </span>
                    </div>

                    <h3 className="font-bold text-sm text-[#000000] mb-1.5">{ach.title}</h3>
                    <p className="text-xs text-[#615d59] leading-relaxed mb-4">
                      {ach.description}
                    </p>
                  </div>

                  <div className="pt-3 border-t border-[#e6e6e6] flex items-center justify-between text-[11px]">
                    <span className="font-semibold uppercase tracking-wider text-[#a39e98]">
                      {ach.category}
                    </span>
                    {ach.is_unlocked ? (
                      <span className="inline-flex items-center gap-1 text-[#1aae39] font-bold">
                        <CheckCircle2 className="w-3.5 h-3.5" />
                        Открыто
                      </span>
                    ) : (
                      <span className="text-stone-500 font-medium">Закрыто</span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}

        </main>
      </div>

      <Footer />
    </div>
  );
}
