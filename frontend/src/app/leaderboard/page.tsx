"use client";

import React, { useState, useEffect } from "react";
import { Navbar } from "@/components/layout/Navbar";
import { Sidebar } from "@/components/layout/Sidebar";
import { Footer } from "@/components/layout/Footer";
import { fetchApi } from "@/lib/api";
import { LeaderboardEntry } from "@/types/gamification";
import { Trophy, Medal, Flame, Zap, Crown } from "lucide-react";

export default function LeaderboardPage() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [leaderboard, setLeaderboard] = useState<LeaderboardEntry[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadLeaderboard = async () => {
      try {
        const data = await fetchApi<LeaderboardEntry[]>("/gamification/leaderboard?limit=50");
        setLeaderboard(data);
      } catch (err) {
        console.error("Failed to load leaderboard", err);
      } finally {
        setLoading(false);
      }
    };
    loadLeaderboard();
  }, []);

  return (
    <div className="min-h-screen flex flex-col bg-[#f6f5f4]">
      <Navbar onToggleSidebar={() => setSidebarOpen(!sidebarOpen)} />

      <div className="flex-1 flex max-w-7xl w-full mx-auto">
        <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

        <main className="flex-1 lg:pl-64 p-4 sm:p-6 lg:p-8 space-y-8 max-w-5xl">
          
          <div className="bg-[#213183] text-white rounded-2xl p-6 sm:p-8 shadow-xs relative overflow-hidden">
            <div className="relative z-10">
              <span className="text-[11px] font-bold uppercase tracking-wider px-2.5 py-0.5 rounded-full bg-white/20 text-white mb-2 inline-block">
                Рейтинг Казахстана
              </span>
              <h1 className="heading-1 text-white mb-2">Таблица лидеров ЕНТ</h1>
              <p className="text-xs sm:text-sm text-blue-100/90 max-w-xl leading-relaxed">
                Топ абитуриентов, набравших максимальное количество опыта (XP) и сохранивших непрерывную серию занятий.
              </p>
            </div>
          </div>

          {/* Top 3 Podium Cards */}
          {leaderboard.length >= 3 && (
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-2">
              {/* #2 Silver */}
              <div className="notion-card p-5 bg-white text-center flex flex-col justify-between order-2 sm:order-1 sm:mt-6 border-stone-300">
                <div>
                  <div className="w-12 h-12 rounded-full bg-stone-100 text-stone-600 font-bold flex items-center justify-center mx-auto mb-2 border border-stone-300">
                    <Medal className="w-6 h-6" />
                  </div>
                  <span className="text-xs font-bold text-[#615d59]">#2 Место</span>
                  <h3 className="font-bold text-sm text-[#000000] mt-1">{leaderboard[1].display_name}</h3>
                  <div className="text-[11px] text-[#615d59]">{leaderboard[1].rank_title}</div>
                </div>
                <div className="mt-4 pt-3 border-t border-[#e6e6e6] text-xs font-bold text-[#0075de]">
                  {leaderboard[1].total_xp} XP
                </div>
              </div>

              {/* #1 Gold */}
              <div className="notion-card-elevated p-6 bg-amber-50/50 border-amber-300 text-center flex flex-col justify-between order-1 sm:order-2 shadow-lg">
                <div>
                  <div className="w-14 h-14 rounded-full bg-gradient-to-tr from-amber-400 to-yellow-300 text-amber-950 font-bold flex items-center justify-center mx-auto mb-2 shadow-md">
                    <Crown className="w-8 h-8" />
                  </div>
                  <span className="text-xs font-bold text-amber-800">#1 Чемпион</span>
                  <h3 className="font-bold text-base text-[#000000] mt-1">{leaderboard[0].display_name}</h3>
                  <div className="text-[11px] text-amber-900 font-medium">{leaderboard[0].rank_title}</div>
                </div>
                <div className="mt-4 pt-3 border-t border-amber-200 text-sm font-bold text-amber-900">
                  {leaderboard[0].total_xp} XP
                </div>
              </div>

              {/* #3 Bronze */}
              <div className="notion-card p-5 bg-white text-center flex flex-col justify-between order-3 sm:order-3 sm:mt-8 border-amber-200">
                <div>
                  <div className="w-12 h-12 rounded-full bg-orange-50 text-[#793400] font-bold flex items-center justify-center mx-auto mb-2 border border-orange-200">
                    <Medal className="w-6 h-6" />
                  </div>
                  <span className="text-xs font-bold text-[#793400]">#3 Место</span>
                  <h3 className="font-bold text-sm text-[#000000] mt-1">{leaderboard[2].display_name}</h3>
                  <div className="text-[11px] text-[#615d59]">{leaderboard[2].rank_title}</div>
                </div>
                <div className="mt-4 pt-3 border-t border-[#e6e6e6] text-xs font-bold text-[#0075de]">
                  {leaderboard[2].total_xp} XP
                </div>
              </div>
            </div>
          )}

          {/* Full Table */}
          <div className="notion-card bg-white overflow-hidden">
            <div className="p-4 border-b border-[#e6e6e6] font-bold text-xs text-[#000000]">
              Полный список участников ({leaderboard.length})
            </div>

            {loading ? (
              <div className="p-12 text-center text-xs text-[#615d59]">
                Загрузка таблицы...
              </div>
            ) : (
              <div className="divide-y divide-[#e6e6e6]">
                {leaderboard.map((entry) => (
                  <div
                    key={entry.user_id}
                    className="p-4 flex items-center justify-between gap-4 hover:bg-[#f6f5f4] transition-colors"
                  >
                    <div className="flex items-center gap-3.5">
                      <span className="w-7 text-center font-bold text-xs text-[#615d59]">
                        {entry.rank}
                      </span>

                      <div className="w-8 h-8 rounded-full bg-blue-50 border border-blue-200 text-[#0075de] font-bold text-xs flex items-center justify-center">
                        {entry.display_name.charAt(0).toUpperCase()}
                      </div>

                      <div>
                        <div className="font-bold text-xs sm:text-sm text-[#000000]">
                          {entry.display_name}
                        </div>
                        <div className="text-[11px] text-[#615d59]">
                          Уровень {entry.level} • {entry.rank_title}
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center gap-4 text-xs font-mono">
                      <div className="flex items-center gap-1 text-[#dd5b00]">
                        <Flame className="w-3.5 h-3.5 fill-[#dd5b00]" />
                        <span>{entry.streak_count} дн.</span>
                      </div>

                      <div className="font-bold text-[#0075de] text-right min-w-[70px]">
                        {entry.total_xp} XP
                      </div>
                    </div>
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
