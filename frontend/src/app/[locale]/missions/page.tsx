"use client";

import React, { useState, useEffect } from "react";
import { Navbar } from "@/components/layout/Navbar";
import { Sidebar } from "@/components/layout/Sidebar";
import { Footer } from "@/components/layout/Footer";
import { fetchApi } from "@/lib/api";
import { DailyMission } from "@/types/gamification";
import { Target, Zap, Gift, CheckCircle2, Clock } from "lucide-react";

export default function MissionsPage() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [missions, setMissions] = useState<DailyMission[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadMissions = async () => {
      try {
        const data = await fetchApi<DailyMission[]>("/gamification/missions");
        setMissions(data);
      } catch (err) {
        console.error("Failed to load missions", err);
      } finally {
        setLoading(false);
      }
    };
    loadMissions();
  }, []);

  const handleClaim = async (missionId: number) => {
    try {
      await fetchApi(`/gamification/missions/${missionId}/claim`, { method: "POST" });
      setMissions((prev) =>
        prev.map((m) => (m.id === missionId ? { ...m, is_claimed: true } : m))
      );
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
          
          <div className="bg-white border border-[#e6e6e6] rounded-2xl p-6 sm:p-8 shadow-xs">
            <span className="eyebrow text-[#0075de] block mb-1 font-semibold">
              Ежедневная активность
            </span>
            <h1 className="heading-1 text-[#000000] mb-2">Квесты и награды</h1>
            <p className="text-xs sm:text-sm text-[#615d59] max-w-2xl leading-relaxed">
              Выполняйте ежедневные задания для ускоренного набора опыта (XP), поддержания ударного стрика и получения эксклюзивных ачивок.
            </p>
          </div>

          <div className="space-y-4">
            {loading ? (
              <div className="p-12 text-center text-xs text-[#615d59]">
                Загрузка миссий...
              </div>
            ) : (
              missions.map((mission) => {
                const progressPct = Math.min(
                  100,
                  Math.round((mission.current_progress / mission.target_count) * 100)
                );

                return (
                  <div
                    key={mission.id}
                    className="notion-card p-5 bg-white flex flex-col sm:flex-row sm:items-center justify-between gap-4"
                  >
                    <div className="flex items-start gap-4">
                      <div className="w-10 h-10 rounded-xl bg-orange-50 text-[#dd5b00] border border-orange-200 flex items-center justify-center shrink-0">
                        <Target className="w-5 h-5" />
                      </div>
                      <div>
                        <h3 className="font-bold text-sm text-[#000000]">{mission.title}</h3>
                        <p className="text-xs text-[#615d59] mt-0.5">{mission.description}</p>
                        
                        <div className="mt-3 flex items-center gap-3 w-48 sm:w-64">
                          <div className="flex-1 h-2 bg-[#f6f5f4] rounded-full overflow-hidden border border-[#e6e6e6]">
                            <div
                              className="h-full bg-[#0075de] transition-all duration-300"
                              style={{ width: `${progressPct}%` }}
                            />
                          </div>
                          <span className="text-[11px] font-semibold text-[#615d59]">
                            {mission.current_progress}/{mission.target_count}
                          </span>
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center gap-4 shrink-0 sm:self-center">
                      <div className="flex items-center gap-1 text-xs font-bold text-[#0075de] bg-blue-50 px-3 py-1 rounded-full border border-blue-200/50">
                        <Zap className="w-3.5 h-3.5 fill-[#0075de]" />
                        <span>+{mission.xp_reward} XP</span>
                      </div>

                      {mission.is_completed && !mission.is_claimed && (
                        <button
                          onClick={() => handleClaim(mission.id)}
                          className="btn-primary text-xs py-1.5 px-4 bg-[#1aae39] hover:bg-[#158f2e]"
                        >
                          <Gift className="w-3.5 h-3.5" />
                          <span>Забрать награду</span>
                        </button>
                      )}

                      {mission.is_claimed && (
                        <span className="inline-flex items-center gap-1 text-xs text-[#1aae39] font-semibold">
                          <CheckCircle2 className="w-4 h-4" />
                          Получено
                        </span>
                      )}
                    </div>
                  </div>
                );
              })
            )}
          </div>

        </main>
      </div>

      <Footer />
    </div>
  );
}
