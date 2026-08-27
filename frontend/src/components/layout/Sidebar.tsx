"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  BookOpen,
  CheckSquare,
  Code2,
  Target,
  Trophy,
  BarChart3,
  Award,
  Settings,
  ShieldAlert,
  Flame,
  Zap,
  Newspaper,
  BookMarked,
} from "lucide-react";
import { getAuth } from "@/lib/auth";
import { AuthResponse } from "@/types/api";
import { getClientLocale, i18nDict, Locale } from "@/lib/i18n";

interface SidebarProps {
  isOpen?: boolean;
  onClose?: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ isOpen, onClose }) => {
  const pathname = usePathname();
  const [auth, setAuth] = useState<AuthResponse | null>(null);
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

  const t = i18nDict[locale] || i18nDict.kk;

  const navigationItems = [
    { name: t.nav.dashboard, href: "/dashboard", icon: LayoutDashboard },
    { name: t.nav.learn, href: "/learn", icon: BookOpen },
    { name: t.nav.practice, href: "/practice", icon: CheckSquare },
    { name: t.nav.coding, href: "/coding", icon: Code2 },
    { name: t.nav.news, href: "/news", icon: Newspaper, badge: "Live" },
    { name: t.nav.untInfo, href: "/unt", icon: BookMarked },
    { name: t.nav.missions, href: "/missions", icon: Target },
    { name: t.nav.leaderboard, href: "/leaderboard", icon: Trophy },
    { name: t.nav.achievements, href: "/achievements", icon: Award },
    { name: t.nav.profile, href: "/profile", icon: BarChart3 },
    { name: t.nav.settings, href: "/settings", icon: Settings },
  ];

  if (auth?.role === "admin") {
    navigationItems.push({ name: t.nav.admin, href: "/admin", icon: ShieldAlert, badge: undefined });
  }

  return (
    <>
      {/* Mobile Backdrop */}
      {isOpen && (
        <div
          onClick={onClose}
          className="fixed inset-0 bg-black/20 backdrop-blur-xs z-30 lg:hidden"
        />
      )}

      <aside
        className={`fixed top-[57px] bottom-0 left-0 z-30 w-64 bg-[#fbfbfa] border-r border-[#e6e6e6] transition-transform duration-200 ease-in-out lg:translate-x-0 overflow-y-auto flex flex-col justify-between ${
          isOpen ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        <div className="p-4 space-y-6">
          {/* Level Progress Card */}
          {auth && (
            <div className="card-warm p-3.5 border border-[#e6e6e6] bg-[#ffffff]">
              <div className="flex items-center justify-between text-xs mb-1.5">
                <span className="font-semibold text-[#000000]">{auth.rank_title}</span>
                <span className="text-[#0075de] font-bold">{t.common.level} {auth.current_level}</span>
              </div>
              <div className="w-full bg-[#f6f5f4] rounded-full h-1.5 overflow-hidden">
                <div
                  className="bg-[#0075de] h-full rounded-full transition-all duration-300"
                  style={{
                    width: `${Math.min(100, ((auth.total_xp % 200) / 200) * 100)}%`,
                  }}
                />
              </div>
              <div className="flex justify-between items-center mt-1.5 text-[10px] text-[#615d59]">
                <span>{auth.total_xp} XP</span>
                <span>{(auth.current_level || 1) * 200} XP мақсат</span>
              </div>
            </div>
          )}

          {/* Navigation Links */}
          <nav className="space-y-1">
            <div className="text-[10px] font-bold text-[#a39e98] uppercase tracking-wider px-3 mb-2">
              {locale === "kk" ? "Негізгі бөлімдер" : "Основное меню"}
            </div>
            {navigationItems.map((item) => {
              const isActive = pathname === item.href || (item.href !== "/" && pathname.startsWith(item.href));
              const Icon = item.icon;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  onClick={onClose}
                  className={`flex items-center justify-between px-3 py-2 rounded-lg text-xs font-medium transition-all ${
                    isActive
                      ? "bg-[#ffffff] text-[#0075de] font-semibold border border-[#e6e6e6] shadow-xs"
                      : "text-[#615d59] hover:text-[#000000] hover:bg-[#f0efee]"
                  }`}
                >
                  <div className="flex items-center gap-2.5">
                    <Icon className={`w-4 h-4 ${isActive ? "text-[#0075de]" : "text-[#8a8580]"}`} />
                    <span>{item.name}</span>
                  </div>
                  {item.badge && (
                    <span className="text-[9px] font-bold uppercase tracking-wider px-1.5 py-0.5 rounded bg-blue-100 text-[#0075de]">
                      {item.badge}
                    </span>
                  )}
                </Link>
              );
            })}
          </nav>
        </div>

        {/* Sidebar Footer Info */}
        <div className="p-4 border-t border-[#e6e6e6] bg-[#fbfbfa]">
          <div className="card-warm p-3 bg-gradient-to-br from-blue-50 to-indigo-50/40 border border-blue-100">
            <div className="flex items-center gap-2 text-xs font-bold text-[#213183] mb-1">
              <Zap className="w-3.5 h-3.5 text-[#0075de]" />
              <span>{locale === "kk" ? "ҰБТ 50/50 Мақсаты" : "Цель ЕНТ 50/50"}</span>
            </div>
            <p className="text-[11px] text-[#615d59] leading-relaxed">
              {locale === "kk"
                ? "Информатикадан толық 50 балл жинап, IT грантын жеңіп алыңыз!"
                : "Наберите максимальные 50 баллов по Информатике и выиграйте грант!"}
            </p>
          </div>
        </div>
      </aside>
    </>
  );
};
