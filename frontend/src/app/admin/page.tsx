"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Navbar } from "@/components/layout/Navbar";
import { Sidebar } from "@/components/layout/Sidebar";
import { Footer } from "@/components/layout/Footer";
import { fetchApi } from "@/lib/api";
import { getAuth } from "@/lib/auth";
import {
  ShieldAlert,
  Users,
  Award,
  BookOpen,
  PlusCircle,
  BarChart,
  CheckCircle2,
  Code2,
  HelpCircle,
} from "lucide-react";

export default function AdminPage() {
  const router = useRouter();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [analytics, setAnalytics] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  // Form states
  const [topicTitle, setTopicTitle] = useState("");
  const [topicSlug, setTopicSlug] = useState("");
  const [topicDesc, setTopicDesc] = useState("");
  const [message, setMessage] = useState<string | null>(null);

  useEffect(() => {
    const auth = getAuth();
    if (!auth || auth.role !== "admin") {
      router.push("/dashboard");
      return;
    }

    const loadAdminData = async () => {
      try {
        const data = await fetchApi("/admin/analytics");
        setAnalytics(data);
      } catch (err) {
        console.error("Failed to load admin analytics", err);
      } finally {
        setLoading(false);
      }
    };

    loadAdminData();
  }, [router]);

  const handleCreateTopic = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await fetchApi("/admin/topics", {
        method: "POST",
        body: JSON.stringify({
          course_id: 1,
          title: topicTitle,
          slug: topicSlug || topicTitle.toLowerCase().replace(/\s+/g, "-"),
          description: topicDesc,
          est_minutes: 30,
          xp_reward: 100,
        }),
      });

      setMessage("Новая тема успешно добавлена в учебный план ЕНТ!");
      setTopicTitle("");
      setTopicSlug("");
      setTopicDesc("");
      setTimeout(() => setMessage(null), 3000);
    } catch (err: any) {
      alert(err.message || "Ошибка добавления темы");
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-[#f6f5f4]">
      <Navbar onToggleSidebar={() => setSidebarOpen(!sidebarOpen)} />

      <div className="flex-1 flex max-w-7xl w-full mx-auto">
        <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

        <main className="flex-1 lg:pl-64 p-4 sm:p-6 lg:p-8 space-y-8 max-w-5xl">
          
          <div className="bg-[#213183] text-white rounded-2xl p-6 sm:p-8 shadow-xs flex items-center justify-between">
            <div>
              <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-white/20 text-white text-[11px] font-bold uppercase tracking-wider mb-2">
                <ShieldAlert className="w-3.5 h-3.5" />
                <span>Панель управления курсом</span>
              </div>
              <h1 className="heading-1 text-white mb-2">Администратор ЕНТ</h1>
              <p className="text-xs sm:text-sm text-blue-100/90 max-w-xl leading-relaxed">
                Анализ успеваемости потока учеников, статистика сложных вопросов и управление базой заданий.
              </p>
            </div>
          </div>

          {/* Admin KPI Stats */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="notion-card p-5 bg-white">
              <div className="flex items-center justify-between text-xs text-[#615d59] mb-2">
                <span>Всего учеников</span>
                <Users className="w-4 h-4 text-[#0075de]" />
              </div>
              <div className="text-2xl font-bold text-[#000000]">
                {analytics?.total_students || 12}
              </div>
              <div className="text-[11px] text-[#615d59] mt-1">активных аккаунтов</div>
            </div>

            <div className="notion-card p-5 bg-white">
              <div className="flex items-center justify-between text-xs text-[#615d59] mb-2">
                <span>Средний балл тестов</span>
                <BarChart className="w-4 h-4 text-[#1aae39]" />
              </div>
              <div className="text-2xl font-bold text-[#000000]">
                {analytics?.average_quiz_score || 82.5}%
              </div>
              <div className="text-[11px] text-[#615d59] mt-1">по всем попыткам</div>
            </div>

            <div className="notion-card p-5 bg-white">
              <div className="flex items-center justify-between text-xs text-[#615d59] mb-2">
                <span>Пройдено тестов</span>
                <HelpCircle className="w-4 h-4 text-[#dd5b00]" />
              </div>
              <div className="text-2xl font-bold text-[#000000]">
                {analytics?.total_quiz_attempts || 45}
              </div>
              <div className="text-[11px] text-[#615d59] mt-1">завершенных сессий</div>
            </div>

            <div className="notion-card p-5 bg-white">
              <div className="flex items-center justify-between text-xs text-[#615d59] mb-2">
                <span>Средний опыт</span>
                <Award className="w-4 h-4 text-purple-600" />
              </div>
              <div className="text-2xl font-bold text-[#000000]">
                {analytics?.average_student_xp || 320} XP
              </div>
              <div className="text-[11px] text-[#615d59] mt-1">на одного ученика</div>
            </div>
          </div>

          {/* Create Content Form */}
          <div className="notion-card p-6 sm:p-8 bg-white space-y-6">
            <div>
              <h2 className="heading-3 text-[#000000]">Добавить новую тему в программу</h2>
              <p className="text-xs text-[#615d59]">
                Создание нового модуля курса подготовки к ЕНТ
              </p>
            </div>

            {message && (
              <div className="p-3.5 bg-green-50 border border-green-200 text-green-800 text-xs rounded-xl flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-[#1aae39]" />
                <span>{message}</span>
              </div>
            )}

            <form onSubmit={handleCreateTopic} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-[#31302e] mb-1">
                  Название темы (например: «Графы и поиск кратчайшего пути»)
                </label>
                <input
                  type="text"
                  required
                  value={topicTitle}
                  onChange={(e) => setTopicTitle(e.target.value)}
                  className="w-full px-3.5 py-2.5 bg-white border border-[#d8d5d1] rounded-xl text-sm focus:outline-none focus:border-[#0075de] transition-all"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-[#31302e] mb-1">
                  Slug URL (например: graph-algorithms)
                </label>
                <input
                  type="text"
                  value={topicSlug}
                  onChange={(e) => setTopicSlug(e.target.value)}
                  placeholder="Оставьте пустым для автогенерации"
                  className="w-full px-3.5 py-2.5 bg-white border border-[#d8d5d1] rounded-xl text-sm focus:outline-none focus:border-[#0075de] transition-all font-mono"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-[#31302e] mb-1">
                  Краткое описание темы и требований ЕНТ
                </label>
                <textarea
                  required
                  value={topicDesc}
                  onChange={(e) => setTopicDesc(e.target.value)}
                  className="w-full px-3.5 py-2.5 bg-white border border-[#d8d5d1] rounded-xl text-sm focus:outline-none focus:border-[#0075de] transition-all h-20"
                />
              </div>

              <button
                type="submit"
                className="btn-primary text-xs py-2 px-5 shadow-xs"
              >
                <PlusCircle className="w-4 h-4" />
                <span>Опубликовать тему</span>
              </button>
            </form>
          </div>

        </main>
      </div>

      <Footer />
    </div>
  );
}
