"use client";

import React, { useState, useEffect } from "react";
import { LocalizedLink as Link } from "@/components/navigation/LocalizedLink";
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
  Zap,
  Newspaper,
  BookMarked,
} from "lucide-react";
import { getAuth } from "@/lib/auth";
import { AuthResponse } from "@/types/api";
import {
  getClientLocale,
  localizePath,
  i18nDict,
  Locale,
  SUPPORTED_LOCALES,
} from "@/lib/i18n";

interface SidebarProps {
  isOpen?: boolean;
  onClose?: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ isOpen, onClose }) => {
  const pathname = usePathname();
  const [auth, setAuth] = useState<AuthResponse | null>(null);

  // Derive active locale from URL pathname
  const currentPathLocale = (pathname.split("/")[1] as Locale) || "kk";
  const activeLocale: Locale = SUPPORTED_LOCALES.includes(currentPathLocale)
    ? currentPathLocale
    : getClientLocale();

  useEffect(() => {
    const userAuth = getAuth();
    if (userAuth) setAuth(userAuth);

    const handleStorage = () => setAuth(getAuth());
    window.addEventListener("storage", handleStorage);
    window.addEventListener("unt_auth_change", handleStorage);
    return () => {
      window.removeEventListener("storage", handleStorage);
      window.removeEventListener("unt_auth_change", handleStorage);
    };
  }, []);


  const t = i18nDict[activeLocale] || i18nDict.kk;

  const rawNavigationItems = [
    { name: t.nav.dashboard, rawHref: "/dashboard", icon: LayoutDashboard },
    { name: t.nav.learn, rawHref: "/learn", icon: BookOpen },
    { name: t.nav.practice, rawHref: "/practice", icon: CheckSquare },
    { name: t.nav.coding, rawHref: "/coding", icon: Code2 },
    { name: t.nav.news, rawHref: "/news", icon: Newspaper, badge: activeLocale === "kk" ? "Жаңа" : activeLocale === "en" ? "Live" : "Новое" },
    { name: t.nav.untInfo, rawHref: "/unt", icon: BookMarked },
    { name: t.nav.missions, rawHref: "/missions", icon: Target },
    { name: t.nav.leaderboard, rawHref: "/leaderboard", icon: Trophy },
    { name: t.nav.achievements, rawHref: "/achievements", icon: Award },
    { name: t.nav.profile, rawHref: "/profile", icon: BarChart3 },
    { name: t.nav.settings, rawHref: "/settings", icon: Settings },
  ];

  if (auth?.role === "admin") {
    rawNavigationItems.push({ name: t.nav.admin, rawHref: "/admin", icon: ShieldAlert, badge: undefined });
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
                <span>{(auth.current_level || 1) * 200} XP {activeLocale === "kk" ? "мақсат" : activeLocale === "en" ? "goal" : "цель"}</span>
              </div>
            </div>
          )}

          {/* Navigation Links */}
          <nav className="space-y-1">
            <div className="text-[10px] font-bold text-[#a39e98] uppercase tracking-wider px-3 mb-2">
              {activeLocale === "kk" ? "Негізгі бөлімдер" : activeLocale === "en" ? "Main menu" : "Основное меню"}
            </div>
            {rawNavigationItems.map((item) => {
              const localizedHref = localizePath(item.rawHref, activeLocale);
              const isActive =
                pathname === localizedHref ||
                (item.rawHref !== "/" && pathname.startsWith(localizedHref));
              const Icon = item.icon;

              return (
                <Link
                  key={item.rawHref}
                  href={localizedHref}
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
              <span>{activeLocale === "kk" ? "ҰБТ 50/50 Мақсаты" : activeLocale === "en" ? "UNT 50/50 goal" : "Цель ЕНТ 50/50"}</span>
            </div>
            <p className="text-[11px] text-[#615d59] leading-relaxed">
              {activeLocale === "kk"
                ? "Информатикадан толық 50 балл жинап, IT грантын жеңіп алыңыз!"
                : activeLocale === "en"
                  ? "Earn all 50 Informatics points and compete for an IT grant."
                  : "Наберите максимальные 50 баллов по информатике и выиграйте грант!"}
            </p>
          </div>
        </div>
      </aside>
    </>
  );
};
