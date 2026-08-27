"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { getClientLocale, localizePath, Locale, SUPPORTED_LOCALES } from "@/lib/i18n";

export const Footer: React.FC = () => {
  const pathname = usePathname();
  const currentPathLocale = (pathname?.split("/")[1] as Locale) || "kk";
  const locale: Locale = SUPPORTED_LOCALES.includes(currentPathLocale)
    ? currentPathLocale
    : getClientLocale();

  return (
    <footer className="w-full bg-[#f6f5f4] border-t border-[#e6e6e6] py-10 px-6 lg:px-12 mt-auto">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-6 text-xs text-[#615d59]">
        <div className="flex flex-col sm:flex-row items-center gap-3">
          <div className="flex items-center gap-2">
            <span className="w-6 h-6 rounded-md bg-[#0075de] text-white font-bold flex items-center justify-center text-xs">
              U
            </span>
            <span className="font-semibold text-[#000000]">UNTverse</span>
          </div>
          <span className="hidden sm:inline text-[#a39e98]">•</span>
          <span>
            {locale === "kk"
              ? "© 2026 Ұлттық бірыңғай тестілеуге дайындалудың интеллектуалды платформасы"
              : "© 2026 Интеллектуальная платформа подготовки к Единому Национальному Тестированию"}
          </span>
        </div>

        <div className="flex items-center gap-6">
          <Link href={localizePath("/learn", locale)} className="hover:text-[#000000] transition-colors">
            {locale === "kk" ? "Оқу бағдарламасы" : "Программа ЕНТ"}
          </Link>
          <Link href={localizePath("/practice", locale)} className="hover:text-[#000000] transition-colors">
            {locale === "kk" ? "Тренажер" : "Тренажер"}
          </Link>
          <Link href={localizePath("/news", locale)} className="hover:text-[#000000] transition-colors">
            {locale === "kk" ? "Жаңалықтар" : "Новости"}
          </Link>
          <Link href={localizePath("/unt", locale)} className="hover:text-[#000000] transition-colors">
            {locale === "kk" ? "Ережелер 2026" : "Правила 2026"}
          </Link>
          <Link href={localizePath("/leaderboard", locale)} className="hover:text-[#000000] transition-colors">
            {locale === "kk" ? "Көшбасшылар" : "Рейтинг"}
          </Link>
        </div>
      </div>
    </footer>
  );
};
