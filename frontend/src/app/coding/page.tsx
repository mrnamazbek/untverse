"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { Navbar } from "@/components/layout/Navbar";
import { Sidebar } from "@/components/layout/Sidebar";
import { Footer } from "@/components/layout/Footer";
import { fetchApi } from "@/lib/api";
import { CodingTask } from "@/types/learning";
import {
  Code2,
  CheckCircle2,
  Zap,
  ArrowRight,
  Terminal,
  Filter,
} from "lucide-react";

export default function CodingTasksPage() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [tasks, setTasks] = useState<CodingTask[]>([]);
  const [filterDifficulty, setFilterDifficulty] = useState<string>("all");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadTasks = async () => {
      try {
        const data = await fetchApi<CodingTask[]>("/coding/tasks");
        setTasks(data);
      } catch (err) {
        console.error("Failed to load coding tasks", err);
      } finally {
        setLoading(false);
      }
    };
    loadTasks();
  }, []);

  const filteredTasks = tasks.filter((t) => {
    if (filterDifficulty === "all") return true;
    return t.difficulty === filterDifficulty;
  });

  const getDifficultyBadge = (difficulty: string) => {
    if (difficulty === "easy")
      return "bg-green-50 text-[#1aae39] border-green-200";
    if (difficulty === "hard")
      return "bg-red-50 text-red-700 border-red-200";
    return "bg-amber-50 text-amber-800 border-amber-200";
  };

  const getDifficultyLabel = (difficulty: string) => {
    if (difficulty === "easy") return "Легкий";
    if (difficulty === "hard") return "Сложный";
    return "Средний";
  };

  return (
    <div className="min-h-screen flex flex-col bg-[#f6f5f4]">
      <Navbar onToggleSidebar={() => setSidebarOpen(!sidebarOpen)} />

      <div className="flex-1 flex max-w-7xl w-full mx-auto">
        <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

        <main className="flex-1 lg:pl-64 p-4 sm:p-6 lg:p-8 space-y-8 max-w-5xl">
          
          {/* Header Banner */}
          <div className="bg-white border border-[#e6e6e6] rounded-2xl p-6 sm:p-8 shadow-xs">
            <div className="flex items-center gap-2 text-[#0075de] font-bold text-xs uppercase tracking-wider mb-2">
              <Code2 className="w-4 h-4" />
              <span>Практический тренажер Python</span>
            </div>
            <h1 className="heading-1 text-[#000000] mb-2">
              Задачи по программированию для ЕНТ
            </h1>
            <p className="text-xs sm:text-sm text-[#615d59] max-w-2xl leading-relaxed">
              Решайте алгоритмические задачи из реальных вариантов ЕНТ: от базовых циклов и срезов строк до бинарного поиска и вложенных структур данных.
            </p>
          </div>

          {/* Difficulty Filter Bar */}
          <div className="flex items-center justify-between gap-4 flex-wrap">
            <div className="flex items-center gap-2">
              <span className="text-xs font-semibold text-[#615d59]">Сложность:</span>
              {["all", "easy", "medium", "hard"].map((diff) => (
                <button
                  key={diff}
                  onClick={() => setFilterDifficulty(diff)}
                  className={`btn-utility text-xs py-1.5 px-3 ${
                    filterDifficulty === diff
                      ? "bg-[#0075de] text-white border-[#0075de] font-semibold"
                      : ""
                  }`}
                >
                  {diff === "all" && "Все задачи"}
                  {diff === "easy" && "Легкие"}
                  {diff === "medium" && "Средние"}
                  {diff === "hard" && "Сложные"}
                </button>
              ))}
            </div>

            <span className="text-xs text-[#615d59] font-medium">
              Найдено: {filteredTasks.length} {filteredTasks.length === 1 ? "задача" : "задач"}
            </span>
          </div>

          {/* Tasks List */}
          {loading ? (
            <div className="p-12 text-center text-xs text-[#615d59]">
              Загрузка задач...
            </div>
          ) : (
            <div className="space-y-3">
              {filteredTasks.map((task) => (
                <div
                  key={task.id}
                  className="notion-card p-5 bg-white flex flex-col sm:flex-row sm:items-center justify-between gap-4 group"
                >
                  <div className="space-y-1.5">
                    <div className="flex items-center gap-2.5">
                      <span
                        className={`text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full border ${getDifficultyBadge(
                          task.difficulty
                        )}`}
                      >
                        {getDifficultyLabel(task.difficulty)}
                      </span>

                      {task.is_solved_by_user && (
                        <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-[#1aae39] bg-green-50 px-2 py-0.5 rounded-full border border-green-200">
                          <CheckCircle2 className="w-3.5 h-3.5" />
                          Решено
                        </span>
                      )}
                    </div>

                    <h3 className="font-bold text-sm text-[#000000] group-hover:text-[#0075de] transition-colors">
                      {task.title}
                    </h3>
                    <p className="text-xs text-[#615d59] line-clamp-1">
                      {task.description}
                    </p>
                  </div>

                  <div className="flex items-center gap-4 shrink-0">
                    <div className="flex items-center gap-1 text-xs font-bold text-[#0075de] bg-blue-50 px-2.5 py-1 rounded-full border border-blue-200/50">
                      <Zap className="w-3.5 h-3.5 fill-[#0075de]" />
                      <span>+{task.xp_reward} XP</span>
                    </div>

                    <Link
                      href={`/coding/${task.id}`}
                      className="btn-primary text-xs py-1.5 px-4 shadow-xs"
                    >
                      <span>Решать</span>
                      <ArrowRight className="w-3.5 h-3.5" />
                    </Link>
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
