"use client";

import React, { useEffect, useState } from "react";
import { Clock, AlertTriangle } from "lucide-react";
import { formatTime } from "@/lib/utils";

interface QuizTimerProps {
  initialSeconds: number;
  onTimeExpired: () => void;
  onTick?: (elapsedSeconds: number) => void;
}

export const QuizTimer: React.FC<QuizTimerProps> = ({
  initialSeconds,
  onTimeExpired,
  onTick,
}) => {
  const [secondsLeft, setSecondsLeft] = useState(initialSeconds);
  const [elapsed, setElapsed] = useState(0);

  useEffect(() => {
    if (secondsLeft <= 0) {
      onTimeExpired();
      return;
    }

    const timer = setInterval(() => {
      setSecondsLeft((prev) => {
        if (prev <= 1) {
          clearInterval(timer);
          onTimeExpired();
          return 0;
        }
        return prev - 1;
      });

      setElapsed((prev) => {
        const next = prev + 1;
        if (onTick) onTick(next);
        return next;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [secondsLeft, onTimeExpired, onTick]);

  const isLow = secondsLeft <= 60;

  return (
    <div
      className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-mono font-bold transition-colors ${
        isLow
          ? "bg-red-100 text-red-700 border border-red-300 animate-pulse"
          : "bg-[#f6f5f4] text-[#31302e] border border-[#e6e6e6]"
      }`}
    >
      {isLow ? <AlertTriangle className="w-3.5 h-3.5" /> : <Clock className="w-3.5 h-3.5 text-[#615d59]" />}
      <span>{formatTime(secondsLeft)}</span>
    </div>
  );
};
