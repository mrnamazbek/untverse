"use client";

import React, { useState } from "react";
import { DailyMission } from "@/types/gamification";
import { fetchApi } from "@/lib/api";
import { Target, CheckCircle2, Gift, Zap } from "lucide-react";

interface DailyQuestsCardProps {
  missions: DailyMission[];
  onRewardClaimed?: (xp: number) => void;
}

export const DailyQuestsCard: React.FC<DailyQuestsCardProps> = ({
  missions,
  onRewardClaimed,
}) => {
  const [claimingId, setClaimingId] = useState<number | null>(null);
  const [localMissions, setLocalMissions] = useState(missions);

  const handleClaim = async (missionId: number) => {
    try {
      setClaimingId(missionId);
      const res = await fetchApi<{ message: string; xp_reward: number }>(
        `/gamification/missions/${missionId}/claim`,
        { method: "POST" }
      );
      
      setLocalMissions((prev) =>
        prev.map((m) => (m.id === missionId ? { ...m, is_claimed: true } : m))
      );

      if (onRewardClaimed) {
        onRewardClaimed(res.xp_reward);
      }
    } catch (err: any) {
      alert(err.message);
    } finally {
      setClaimingId(null);
    }
  };

  return (
    <div className="notion-card p-5">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-orange-100 text-[#dd5b00] flex items-center justify-center">
            <Target className="w-4 h-4" />
          </div>
          <div>
            <h3 className="font-bold text-sm text-[#000000]">Ежедневные квесты</h3>
            <p className="text-[11px] text-[#615d59]">Обновляются каждые 24 часа</p>
          </div>
        </div>
        <span className="text-xs font-semibold px-2 py-0.5 rounded bg-[#f6f5f4] text-[#615d59] border border-[#e6e6e6]">
          {localMissions.filter((m) => m.is_completed).length}/{localMissions.length}
        </span>
      </div>

      <div className="space-y-3">
        {localMissions.map((m) => {
          const progressPct = Math.min(100, Math.round((m.current_progress / m.target_count) * 100));

          return (
            <div
              key={m.id}
              className="p-3 bg-[#f6f5f4]/70 border border-[#e6e6e6] rounded-xl flex flex-col gap-2 transition-all hover:bg-[#f6f5f4]"
            >
              <div className="flex items-start justify-between gap-2">
                <div>
                  <h4 className="text-xs font-semibold text-[#000000]">{m.title}</h4>
                  <p className="text-[11px] text-[#615d59] mt-0.5">{m.description}</p>
                </div>

                <div className="flex items-center gap-1 shrink-0 text-xs font-bold text-[#0075de] bg-blue-50 px-2 py-0.5 rounded-full border border-blue-200/50">
                  <Zap className="w-3 h-3 fill-[#0075de]" />
                  <span>+{m.xp_reward} XP</span>
                </div>
              </div>

              {/* Progress Bar & Claim */}
              <div className="flex items-center gap-3 mt-1">
                <div className="flex-1 h-2 bg-white border border-[#e6e6e6] rounded-full overflow-hidden">
                  <div
                    className={`h-full transition-all duration-300 ${
                      m.is_completed ? "bg-[#1aae39]" : "bg-[#0075de]"
                    }`}
                    style={{ width: `${progressPct}%` }}
                  />
                </div>

                <span className="text-[11px] font-medium text-[#615d59] shrink-0">
                  {m.current_progress}/{m.target_count}
                </span>

                {m.is_completed && !m.is_claimed && (
                  <button
                    onClick={() => handleClaim(m.id)}
                    disabled={claimingId === m.id}
                    className="btn-primary text-xs py-1 px-3 bg-[#1aae39] hover:bg-[#158f2e]"
                  >
                    <Gift className="w-3 h-3" />
                    <span>Забрать</span>
                  </button>
                )}

                {m.is_claimed && (
                  <span className="inline-flex items-center gap-1 text-[11px] text-[#1aae39] font-medium">
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    Получено
                  </span>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
