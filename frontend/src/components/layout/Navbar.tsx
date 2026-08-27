"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { getAuth, clearAuth } from "@/lib/auth";
import { AuthResponse } from "@/types/api";
import { getClientLocale, setClientLocale, i18nDict, Locale } from "@/lib/i18n";
import {
  Flame,
  Zap,
  User,
  LogOut,
  Shield,
  Award,
  Menu,
  Globe,
  Newspaper,
  BookMarked,
} from "lucide-react";

interface NavbarProps {
  onToggleSidebar?: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({ onToggleSidebar }) => {
  const router = useRouter();
  const [auth, setAuth] = useState<AuthResponse | null>(null);
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [locale, setLocale] = useState<Locale>("kk");

  useEffect(() => {
    setAuth(getAuth());
    setLocale(getClientLocale());

    const handleStorage = () => setAuth(getAuth());
    const handleLocale = () => setLocale(getClientLocale());

    window.addEventListener("storage", handleStorage);
    window.addEventListener("localeChange", handleLocale);

    return () => {
      window.removeEventListener("storage", handleStorage);
      window.removeEventListener("localeChange", handleLocale);
    };
  }, []);

  const handleLanguageChange = (newLocale: Locale) => {
    setClientLocale(newLocale);
    setLocale(newLocale);
  };

  const handleLogout = () => {
    clearAuth();
    setAuth(null);
    router.push("/login");
  };

  const t = i18nDict[locale] || i18nDict.kk;

  return (
    <header className="sticky top-0 z-40 w-full bg-[#ffffff] border-b border-[#e6e6e6] px-4 lg:px-8 py-2.5 transition-all">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        <div className="flex items-center gap-3">
          {onToggleSidebar && (
            <button
              onClick={onToggleSidebar}
              className="lg:hidden p-2 text-[#31302e] hover:bg-[#f6f5f4] rounded-md transition-colors"
              aria-label="Мәзірді ашу / Переключить меню"
            >
              <Menu className="w-5 h-5" />
            </button>
          )}

          <Link href="/" className="flex items-center gap-2.5 group">
            <div className="w-8 h-8 rounded-lg bg-[#0075de] flex items-center justify-center text-white font-bold text-base shadow-sm group-hover:scale-105 transition-transform">
              U
            </div>
            <div className="flex flex-col">
              <span className="font-bold text-base tracking-tight text-[#000000] leading-none">
                UNTverse
              </span>
              <span className="text-[11px] text-[#615d59] font-medium tracking-wide">
                ҰБТ / ЕНТ Информатика 50/50
              </span>
            </div>
          </Link>

          {/* Quick Header Nav Links */}
          <nav className="hidden md:flex items-center gap-1 ml-4 pl-4 border-l border-[#e6e6e6]">
            <Link
              href="/news"
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium text-[#615d59] hover:text-[#000000] hover:bg-[#f6f5f4] transition-colors"
            >
              <Newspaper className="w-3.5 h-3.5 text-[#0075de]" />
              <span>{t.nav.news}</span>
            </Link>
            <Link
              href="/unt"
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium text-[#615d59] hover:text-[#000000] hover:bg-[#f6f5f4] transition-colors"
            >
              <BookMarked className="w-3.5 h-3.5 text-[#9d34da]" />
              <span>{t.nav.untInfo}</span>
            </Link>
          </nav>
        </div>

        <div className="flex items-center gap-2 sm:gap-3">
          {/* Language Switcher Pill */}
          <div className="flex items-center bg-[#f6f5f4] border border-[#e6e6e6] rounded-full p-0.5 text-[11px] font-semibold text-[#615d59]">
            <button
              onClick={() => handleLanguageChange("kk")}
              className={`px-2 py-0.5 rounded-full transition-colors ${
                locale === "kk"
                  ? "bg-[#0075de] text-white shadow-xs"
                  : "hover:text-[#000000]"
              }`}
              title="Қазақ тілі"
            >
              ҚАЗ
            </button>
            <button
              onClick={() => handleLanguageChange("ru")}
              className={`px-2 py-0.5 rounded-full transition-colors ${
                locale === "ru"
                  ? "bg-[#0075de] text-white shadow-xs"
                  : "hover:text-[#000000]"
              }`}
              title="Русский язык"
            >
              РУС
            </button>
            <button
              onClick={() => handleLanguageChange("en")}
              className={`px-2 py-0.5 rounded-full transition-colors ${
                locale === "en"
                  ? "bg-[#0075de] text-white shadow-xs"
                  : "hover:text-[#000000]"
              }`}
              title="English"
            >
              ENG
            </button>
          </div>

          {auth ? (
            <div className="flex items-center gap-2 sm:gap-3">
              {/* Streak Counter */}
              <div className="flex items-center gap-1.5 px-2.5 py-1 bg-[#fff5eb] border border-[#ffd8b2] rounded-full text-xs font-semibold text-[#dd5b00]">
                <Flame className="w-3.5 h-3.5 fill-[#dd5b00]" />
                <span>{auth.streak_count || 0} {locale === "kk" ? "күн" : "дн"}</span>
              </div>

              {/* XP & Level Indicator */}
              <div className="hidden sm:flex items-center gap-2 px-3 py-1 bg-[#f6f5f4] border border-[#e6e6e6] rounded-full text-xs font-medium text-[#31302e]">
                <Zap className="w-3.5 h-3.5 text-[#0075de] fill-[#0075de]" />
                <span>{auth.total_xp || 0} XP</span>
                <span className="text-[#a39e98]">•</span>
                <span className="text-[#0075de] font-semibold">{t.common.level} {auth.current_level || 1}</span>
              </div>

              {/* Profile Dropdown Trigger */}
              <div className="relative">
                <button
                  onClick={() => setIsMenuOpen(!isMenuOpen)}
                  className="flex items-center gap-2 p-1 pl-1.5 pr-2.5 rounded-full hover:bg-[#f6f5f4] border border-[#e6e6e6] transition-colors"
                >
                  <div className="w-6 h-6 rounded-full bg-[#0075de]/10 border border-[#0075de]/30 text-[#0075de] flex items-center justify-center font-bold text-xs">
                    {auth.display_name ? auth.display_name.charAt(0).toUpperCase() : "U"}
                  </div>
                  <span className="text-xs font-medium text-[#31302e] hidden md:inline max-w-[110px] truncate">
                    {auth.display_name}
                  </span>
                </button>

                {isMenuOpen && (
                  <div className="absolute right-0 mt-2 w-56 bg-white border border-[#e6e6e6] rounded-xl shadow-lg py-2 z-50 animate-in fade-in slide-in-from-top-2 duration-150">
                    <div className="px-4 py-2 border-b border-[#e6e6e6] mb-1">
                      <p className="text-xs font-semibold text-[#000000] truncate">{auth.display_name}</p>
                      <p className="text-[11px] text-[#615d59] truncate">{auth.email}</p>
                      <div className="mt-1.5 inline-block text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded bg-blue-50 text-[#0075de]">
                        {auth.rank_title}
                      </div>
                    </div>

                    <Link
                      href="/profile"
                      onClick={() => setIsMenuOpen(false)}
                      className="flex items-center gap-2.5 px-4 py-2 text-xs text-[#31302e] hover:bg-[#f6f5f4] transition-colors"
                    >
                      <User className="w-4 h-4 text-[#615d59]" />
                      {t.nav.profile}
                    </Link>

                    <Link
                      href="/achievements"
                      onClick={() => setIsMenuOpen(false)}
                      className="flex items-center gap-2.5 px-4 py-2 text-xs text-[#31302e] hover:bg-[#f6f5f4] transition-colors"
                    >
                      <Award className="w-4 h-4 text-[#615d59]" />
                      {t.nav.achievements}
                    </Link>

                    {auth.role === "admin" && (
                      <Link
                        href="/admin"
                        onClick={() => setIsMenuOpen(false)}
                        className="flex items-center gap-2.5 px-4 py-2 text-xs text-[#0075de] font-semibold hover:bg-blue-50 transition-colors"
                      >
                        <Shield className="w-4 h-4 text-[#0075de]" />
                        {t.nav.admin}
                      </Link>
                    )}

                    <div className="border-t border-[#e6e6e6] mt-1 pt-1">
                      <button
                        onClick={handleLogout}
                        className="w-full flex items-center gap-2.5 px-4 py-2 text-xs text-red-600 hover:bg-red-50 transition-colors"
                      >
                        <LogOut className="w-4 h-4" />
                        {t.nav.logout}
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="flex items-center gap-2">
              <Link href="/login" className="btn-utility text-xs py-1.5 px-3">
                {t.nav.login}
              </Link>
              <Link href="/register" className="btn-primary text-xs py-1.5 px-3.5">
                {t.nav.register}
              </Link>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};
