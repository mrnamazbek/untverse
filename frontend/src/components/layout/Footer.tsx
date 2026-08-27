import React from "react";
import Link from "next/link";

export const Footer: React.FC = () => {
  return (
    <footer className="w-full bg-[#f6f5f4] border-t border-[#e6e6e6] py-10 px-6 lg:px-12 mt-auto">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-6 text-xs text-[#615d59]">
        <div className="flex flex-col sm:flex-row items-center gap-3">
          <div className="flex items-center gap-2">
            <span className="w-6 h-6 rounded-md bg-[#0075de] text-white font-bold flex items-center justify-center text-xs">
              U
            </span>
            <span className="font-semibold text-[#000000]">ЕНТ Информатика</span>
          </div>
          <span className="hidden sm:inline text-[#a39e98]">•</span>
          <span>© 2026 Образовательная платформа подготовки к Единому Национальному Тестированию</span>
        </div>

        <div className="flex items-center gap-6">
          <Link href="/learn" className="hover:text-[#000000] transition-colors">
            Программа ЕНТ
          </Link>
          <Link href="/practice" className="hover:text-[#000000] transition-colors">
            Тренажер
          </Link>
          <Link href="/leaderboard" className="hover:text-[#000000] transition-colors">
            Рейтинг
          </Link>
          <Link href="/profile" className="hover:text-[#000000] transition-colors">
            Аналитика
          </Link>
        </div>
      </div>
    </footer>
  );
};
