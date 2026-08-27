"use client";

import React, { useState, useEffect } from "react";
import { LocalizedLink as Link } from "@/components/navigation/LocalizedLink";
import { Navbar } from "@/components/layout/Navbar";
import { Sidebar } from "@/components/layout/Sidebar";
import { Footer } from "@/components/layout/Footer";
import { fetchApi } from "@/lib/api";
import { Course } from "@/types/learning";
import {
  BookOpen,
  CheckCircle2,
  Lock,
  ArrowRight,
  Code2,
  Database,
  Cpu,
  Shield,
  Network,
  BrainCircuit,
  Zap,
} from "lucide-react";

export default function LearnPage() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [courses, setCourses] = useState<Course[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadCourses = async () => {
      try {
        const data = await fetchApi<Course[]>("/courses", { requiresAuth: false });
        setCourses(data);
      } catch (err) {
        console.error("Failed to load courses", err);
      } finally {
        setLoading(false);
      }
    };
    loadCourses();
  }, []);

  const getTopicIcon = (slug: string) => {
    if (slug.includes("logic") || slug.includes("number")) return Cpu;
    if (slug.includes("python")) return Code2;
    if (slug.includes("sql") || slug.includes("database")) return Database;
    if (slug.includes("network")) return Network;
    if (slug.includes("security")) return Shield;
    return BrainCircuit;
  };

  return (
    <div className="min-h-screen flex flex-col bg-[#f6f5f4]">
      <Navbar onToggleSidebar={() => setSidebarOpen(!sidebarOpen)} />

      <div className="flex-1 flex max-w-7xl w-full mx-auto">
        <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

        <main className="flex-1 lg:pl-64 p-4 sm:p-6 lg:p-8 space-y-8 max-w-5xl">
          
          {/* Header */}
          <div className="bg-white border border-[#e6e6e6] rounded-2xl p-6 shadow-xs">
            <span className="eyebrow text-[#0075de] block mb-1 font-semibold">Учебная программа</span>
            <h1 className="heading-1 text-[#000000] mb-2">
              Карта подготовки к ЕНТ по Информатике
            </h1>
            <p className="text-xs sm:text-sm text-[#615d59] max-w-2xl leading-relaxed">
              Все темы структурированы по требованиям Национального центра тестирования (НЦТ) РК. 
              Проходите уроки, решайте тесты по разделам и повышайте уровень мастерства.
            </p>
          </div>

          {/* Topics Roadmap List */}
          {loading ? (
            <div className="p-12 text-center text-xs text-[#615d59]">
              Загрузка учебных модулей...
            </div>
          ) : (
            <div className="space-y-8">
              {courses.map((course) => (
                <div key={course.id} className="space-y-4">
                  <div className="flex items-center gap-2">
                    <BookOpen className="w-5 h-5 text-[#0075de]" />
                    <h2 className="heading-2 text-[#000000]">{course.title}</h2>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {course.topics.map((topic, index) => {
                      const Icon = getTopicIcon(topic.slug);
                      const mastery = topic.user_mastery_percentage || 0;

                      return (
                        <div
                          key={topic.id}
                          className="notion-card p-5 flex flex-col justify-between group"
                        >
                          <div>
                            <div className="flex items-center justify-between mb-3">
                              <div className="flex items-center gap-2.5">
                                <div className="w-9 h-9 rounded-lg bg-blue-50 text-[#0075de] border border-blue-200/60 flex items-center justify-center">
                                  <Icon className="w-4 h-4" />
                                </div>
                                <div>
                                  <span className="text-[10px] font-bold text-[#a39e98] uppercase tracking-wider">
                                    Модуль {index + 1}
                                  </span>
                                  <h3 className="font-bold text-sm text-[#000000] group-hover:text-[#0075de] transition-colors leading-snug">
                                    {topic.title}
                                  </h3>
                                </div>
                              </div>

                              <div className="flex items-center gap-1 text-[11px] font-semibold text-[#0075de] bg-blue-50/80 px-2 py-0.5 rounded-md">
                                <Zap className="w-3 h-3 fill-[#0075de]" />
                                <span>+{topic.xp_reward} XP</span>
                              </div>
                            </div>

                            <p className="text-xs text-[#615d59] leading-relaxed mb-4 line-clamp-2">
                              {topic.description}
                            </p>
                          </div>

                          <div className="pt-3 border-t border-[#e6e6e6] space-y-3">
                            <div className="flex items-center justify-between text-[11px] text-[#615d59]">
                              <span>
                                {topic.lessons_count || 3} уроков • {topic.quizzes_count || 1} тест
                              </span>
                              <span className="font-semibold text-[#000000]">
                                Освоено: {mastery}%
                              </span>
                            </div>

                            <div className="w-full h-1.5 bg-[#f6f5f4] rounded-full overflow-hidden border border-[#e6e6e6]">
                              <div
                                className="h-full bg-[#0075de] transition-all duration-300"
                                style={{ width: `${mastery}%` }}
                              />
                            </div>

                            <Link
                              href={`/learn/${topic.slug}`}
                              className="btn-secondary w-full text-xs py-2 justify-center group-hover:bg-[#0075de] group-hover:text-white group-hover:border-[#0075de] transition-all"
                            >
                              <span>Открыть раздел</span>
                              <ArrowRight className="w-3.5 h-3.5" />
                            </Link>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              ))}
            </div>
          )}

        </main>
      </div>

      <Footer />
    </div>
  );
}
