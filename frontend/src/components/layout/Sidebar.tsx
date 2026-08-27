"use client";

import React from "react";
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
} from "lucide-react";
import { getAuth } from "@/lib/auth";
import { AuthResponse } from "@/types/api";

interface SidebarProps {
  isOpen?: boolean;
  onClose?: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ isOpen, onClose }) => {
  const pathname = usePathname();
  const [auth, setAuth] = React.useState<AuthResponse | null>(null);

  React.useEffect(() => {
    setAuth(getAuth());
    const handleStorage = () => setAuth(getAuth());
    window.addEventListener("storage", handleStorage);
    return () => window.removeEventListener("storage", handleStorage);
  }, []);

  const navigationItems = [
    { name: "Дашборд", href: "/dashboard", icon: LayoutDashboard },
    { name: "Обучение и Темы", href: "/learn", icon: BookOpen },
    { name: "Тренажер ЕНТ", href: "/practice", icon: CheckSquare },
    { name: "Задачи Python", href: "/coding", icon: Code2 },
    { name: "Ежедневные квесты", href: "/missions", icon: Target },
    { name: "Лидерборд", href: "/leaderboard", icon: Trophy },
    { name: "Достижения", href: "/achievements", icon: Award },
    { name: "Аналитика ЕНТ", href: "/profile", icon: BarChart3 },
    { name: "Настройки", href: "/settings", icon: Settings },
  ];

  if (auth?.role === "admin") {
    navigationItems.push({ name: "Администрирование", href: "/admin", icon: ShieldAlert });
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
        className={`fixed top-14 left-0 bottom-0 z-30 w-64 bg-[#f6f5f4] border-r border-[#e6e6e6] p-4 flex flex-col justify-between transition-transform duration-200 ease-in-out lg:translate-x-0 ${
          isOpen ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        <div className="space-y-6 overflow-y-auto">
          {/* Quick Progress Banner */}
          {auth && (
            <div className="p-3 bg-white border border-[#e6e6e6] rounded-xl shadow-xs">
              <div className="flex items-center justify-between text-xs mb-1.5">
                <span className="font-semibold text-[#000000]">Уровень {auth.current_level}</span>
                <span className="text-[#615d59] font-medium">{auth.total_xp} XP</span>
              </div>
              <div className="w-full h-2 bg-[#f6f5f4] rounded-full overflow-hidden border border-[#e6e6e6]">
                <div
                  className="h-full bg-[#0075de] rounded-full transition-all duration-500"
                  style={{ width: `${Math.min(100, (auth.total_xp % 300) / 3)}%` }}
                />
              </div>
              <div className="mt-2 flex items-center justify-between text-[11px] text-[#615d59]">
                <div className="flex items-center gap-1 text-[#dd5b00]">
                  <Flame className="w-3.5 h-3.5 fill-[#dd5b00]" />
                  <span>Стрик: {auth.streak_count} дн.</span>
                </div>
                <span className="truncate max-w-[110px]">{auth.rank_title}</span>
              </div>
            </div>
          )}

          {/* Navigation Links */}
          <nav className="space-y-1">
            <div className="px-3 py-1 text-[11px] font-semibold text-[#a39e98] uppercase tracking-wider">
              Навигация
            </div>
            {navigationItems.map((item) => {
              const Icon = item.icon;
              const isActive = pathname === item.href || (item.href !== "/dashboard" && pathname.startsWith(item.href));

              return (
                <Link
                  key={item.href}
                  href={item.href}
                  onClick={onClose}
                  className={`flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-all ${
                    isActive
                      ? "bg-white text-[#0075de] shadow-xs font-semibold border border-[#e6e6e6]"
                      : "text-[#31302e] hover:bg-white/60 hover:text-[#000000]"
                  }`}
                >
                  <Icon className={`w-4 h-4 ${isActive ? "text-[#0075de]" : "text-[#615d59]"}`} />
                  <span>{item.name}</span>
                </Link>
              );
            })}
          </nav>
        </div>

        {/* Bottom Banner / Motivation */}
        <div className="pt-4 border-t border-[#e6e6e6]">
          <div className="p-3 bg-blue-50/70 border border-blue-200/60 rounded-xl text-xs">
            <div className="flex items-center gap-1.5 text-[#0075de] font-semibold mb-1">
              <Zap className="w-3.5 h-3.5 fill-[#0075de]" />
              <span>Цель ЕНТ: 50/50</span>
            </div>
            <p className="text-[11px] text-[#31302e] leading-relaxed">
              Регулярные занятия по 20 минут в день увеличивают средний балл на 35%.
            </p>
          </div>
        </div>
      </aside>
    </>
  );
};
