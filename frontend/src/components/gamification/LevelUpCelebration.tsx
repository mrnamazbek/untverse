"use client";

import React, { useEffect } from "react";
import confetti from "canvas-confetti";
import { Zap, Award, X, Sparkles } from "lucide-react";

interface LevelUpCelebrationProps {
  newLevel: number;
  xpEarned: number;
  onClose: () => void;
}

export const LevelUpCelebration: React.FC<LevelUpCelebrationProps> = ({
  newLevel,
  xpEarned,
  onClose,
}) => {
  useEffect(() => {
    // Fire festive confetti cannon
    const duration = 2.5 * 1000;
    const end = Date.now() + duration;

    const frame = () => {
      confetti({
        particleCount: 4,
        angle: 60,
        spread: 55,
        origin: { x: 0 },
        colors: ["#0075de", "#ff64c8", "#62aef0", "#dd5b00", "#1aae39"]
      });
      confetti({
        particleCount: 4,
        angle: 120,
        spread: 55,
        origin: { x: 1 },
        colors: ["#0075de", "#ff64c8", "#62aef0", "#dd5b00", "#1aae39"]
      });

      if (Date.now() < end) {
        requestAnimationFrame(frame);
      }
    };
    frame();
  }, []);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-xs animate-in fade-in duration-200">
      <div className="bg-white border border-[#e6e6e6] rounded-2xl shadow-2xl p-8 max-w-md w-full text-center relative overflow-hidden">
        {/* Glow circle background */}
        <div className="absolute -top-12 -left-12 w-40 h-40 bg-blue-100/50 rounded-full blur-2xl pointer-events-none" />
        <div className="absolute -bottom-12 -right-12 w-40 h-40 bg-purple-100/50 rounded-full blur-2xl pointer-events-none" />

        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-[#a39e98] hover:text-[#000000] p-1 rounded-lg hover:bg-[#f6f5f4] transition-colors"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="w-20 h-20 mx-auto mb-4 rounded-2xl bg-gradient-to-tr from-[#0075de] to-[#62aef0] flex items-center justify-center text-white shadow-lg shadow-blue-500/20">
          <Award className="w-10 h-10 animate-bounce" />
        </div>

        <div className="inline-flex items-center gap-1 px-3 py-1 bg-amber-50 border border-amber-200 rounded-full text-xs font-semibold text-amber-800 mb-2">
          <Sparkles className="w-3.5 h-3.5 fill-amber-500" />
          <span>Новый уровень достигнут!</span>
        </div>

        <h2 className="text-2xl font-bold text-[#000000] tracking-tight mb-2">
          Поздравляем! Уровень {newLevel}
        </h2>

        <p className="text-sm text-[#615d59] mb-6">
          Вы успешно заработали <span className="font-bold text-[#0075de]">+{xpEarned} XP</span> и поднялись на новую ступень мастерства в подготовке к ЕНТ.
        </p>

        <button
          onClick={onClose}
          className="btn-primary w-full py-2.5 text-sm font-semibold shadow-md"
        >
          Продолжить обучение
        </button>
      </div>
    </div>
  );
};
