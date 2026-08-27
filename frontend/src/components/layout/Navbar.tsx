"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { getAuth, clearAuth } from "@/lib/auth";
import { AuthResponse } from "@/types/api";
import { Flame, Zap, User, LogOut, Shield, Award, Sparkles, Menu, X } from "lucide-react";

interface NavbarProps {
  onToggleSidebar?: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({ onToggleSidebar }) => {
  const router = useRouter();
  const [auth, setAuth] = useState<AuthResponse | null>(null);
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  useEffect(() => {
    setAuth(getAuth());
    const handleStorage = () => setAuth(getAuth());
    window.addEventListener("storage", handleStorage);
    return () => window.removeEventListener("storage", handleStorage);
  }, []);

  const handleLogout = () => {
    clearAuth();
    setAuth(null);
    router.push("/login");
  };

  return (
    <header className="sticky top-0 z-40 w-full bg-[#ffffff] border-b border-[#e6e6e6] px-4 lg:px-8 py-3 transition-all">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        <div className="flex items-center gap-3">
          {onToggleSidebar && (
            <button
              onClick={onToggleSidebar}
              className="lg:hidden p-2 text-[#31302e] hover:bg-[#f6f5f4] rounded-md transition-colors"
              aria-label="Переключить меню"
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
                ЕНТ Информатика
              </span>
              <span className="text-[11px] text-[#615d59] font-medium tracking-wide">
                Платформа подготовки 50/50
              </span>
            </div>
          </Link>
        </div>

        {auth ? (
          <div className="flex items-center gap-3 md:gap-5">
            {/* Streak Counter */}
            <div className="flex items-center gap-1.5 px-3 py-1 bg-[#fff5eb] border border-[#ffd8b2] rounded-full text-xs font-semibold text-[#dd5b00]">
              <Flame className="w-4 h-4 fill-[#dd5b00]" />
              <span>{auth.streak_count || 0} дней</span>
            </div>

            {/* XP & Level Indicator */}
            <div className="hidden sm:flex items-center gap-2 px-3 py-1 bg-[#f6f5f4] border border-[#e6e6e6] rounded-full text-xs font-medium text-[#31302e]">
              <Zap className="w-4 h-4 text-[#0075de] fill-[#0075de]" />
              <span>{auth.total_xp || 0} XP</span>
              <span className="text-[#a39e98]">•</span>
              <span className="text-[#0075de] font-semibold">Уровень {auth.current_level || 1}</span>
            </div>

            {/* Profile Dropdown Trigger */}
            <div className="relative">
              <button
                onClick={() => setIsMenuOpen(!isMenuOpen)}
                className="flex items-center gap-2 p-1 pl-2 pr-2.5 rounded-full hover:bg-[#f6f5f4] border border-[#e6e6e6] transition-colors"
              >
                <div className="w-7 h-7 rounded-full bg-[#0075de]/10 border border-[#0075de]/30 text-[#0075de] flex items-center justify-center font-bold text-xs">
                  {auth.display_name ? auth.display_name.charAt(0).toUpperCase() : "U"}
                </div>
                <span className="text-xs font-medium text-[#31302e] hidden md:inline max-w-[120px] truncate">
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
                    Мой Профиль
                  </Link>

                  <Link
                    href="/achievements"
                    onClick={() => setIsMenuOpen(false)}
                    className="flex items-center gap-2.5 px-4 py-2 text-xs text-[#31302e] hover:bg-[#f6f5f4] transition-colors"
                  >
                    <Award className="w-4 h-4 text-[#615d59]" />
                    Достижения
                  </Link>

                  {auth.role === "admin" && (
                    <Link
                      href="/admin"
                      onClick={() => setIsMenuOpen(false)}
                      className="flex items-center gap-2.5 px-4 py-2 text-xs text-[#0075de] font-semibold hover:bg-blue-50 transition-colors"
                    >
                      <Shield className="w-4 h-4 text-[#0075de]" />
                      Панель администратора
                    </Link>
                  )}

                  <div className="border-t border-[#e6e6e6] my-1" />

                  <button
                    onClick={handleLogout}
                    className="w-full flex items-center gap-2.5 px-4 py-2 text-xs text-red-600 hover:bg-red-50 transition-colors text-left"
                  >
                    <LogOut className="w-4 h-4 text-red-500" />
                    Выйти из аккаунта
                  </button>
                </div>
              )}
            </div>
          </div>
        ) : (
          <div className="flex items-center gap-3">
            <Link
              href="/login"
              className="text-xs font-medium text-[#31302e] hover:text-[#000000] px-3 py-1.5 transition-colors"
            >
              Войти
            </Link>
            <Link
              href="/register"
              className="btn-primary text-xs py-1.5 px-4 shadow-sm"
            >
              Начать подготовку
            </Link>
          </div>
        )}
      </div>
    </header>
  );
};
