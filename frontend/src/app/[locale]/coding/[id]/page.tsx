"use client";

import React, { useState, useEffect } from "react";
import { LocalizedLink as Link } from "@/components/navigation/LocalizedLink";
import { useParams } from "next/navigation";
import { Navbar } from "@/components/layout/Navbar";
import { Footer } from "@/components/layout/Footer";
import { fetchApi } from "@/lib/api";
import { CodingTask, CodeRunResult } from "@/types/learning";
import { CodeEditor } from "@/components/coding/CodeEditor";
import { TestCaseRunner } from "@/components/coding/TestCaseRunner";
import { ContentRenderer } from "@/components/content/ContentRenderer";
import { Locale, SUPPORTED_LOCALES } from "@/lib/i18n";
import { LevelUpCelebration } from "@/components/gamification/LevelUpCelebration";
import {
  ArrowLeft,
  Code2,
  Zap,
  CheckCircle2,
  Clock,
  HardDrive,
  Info,
} from "lucide-react";

export default function CodingIdePage() {
  const params = useParams();
  const taskId = params?.id as string;
  const rawLocale = params?.locale as string;
  const locale: Locale = SUPPORTED_LOCALES.includes(rawLocale as Locale) ? rawLocale as Locale : "kk";

  const [task, setTask] = useState<CodingTask | null>(null);
  const [code, setCode] = useState("");
  const [running, setRunning] = useState(false);
  const [runResult, setRunResult] = useState<CodeRunResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [celebration, setCelebration] = useState<{ newLevel: number; xp: number } | null>(null);

  useEffect(() => {
    if (!taskId) return;

    const loadTask = async () => {
      try {
        const data = await fetchApi<CodingTask>(`/coding/tasks/${taskId}`);
        setTask(data);
        setCode(data.starter_code || "# Пишите ваше решение здесь\n");
      } catch (err) {
        console.error("Failed to load task", err);
      } finally {
        setLoading(false);
      }
    };

    loadTask();
  }, [taskId]);

  const handleRunCode = async () => {
    if (!task || running) return;
    setRunning(true);

    try {
      const result = await fetchApi<CodeRunResult>(`/coding/tasks/${task.id}/run`, {
        method: "POST",
        body: JSON.stringify({ source_code: code }),
      });

      setRunResult(result);

      if (result.leveled_up) {
        setCelebration({
          newLevel: result.new_level,
          xp: result.xp_earned,
        });
      }
    } catch (err: any) {
      alert(err.message || "Ошибка при выполнении кода");
    } finally {
      setRunning(false);
    }
  };

  const handleResetCode = () => {
    if (task) {
      setCode(task.starter_code);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#f6f5f4]">
        <div className="w-8 h-8 border-3 border-[#0075de] border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (!task) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-[#f6f5f4] p-6 text-center">
        <h2 className="heading-2 mb-2">Задача не найдена</h2>
        <Link href="/coding" className="btn-primary text-xs">
          Вернуться к каталогу задач
        </Link>
      </div>
    );
  }

  const sampleTestCases = task.test_cases?.filter((tc) => !tc.is_hidden) || [];

  return (
    <div className="min-h-screen flex flex-col bg-[#f6f5f4]">
      <Navbar />

      <main className="max-w-7xl mx-auto w-full px-4 sm:px-6 py-6 flex-1 space-y-6">
        
        {/* Navigation & Header */}
        <div className="flex items-center justify-between gap-4">
          <Link
            href="/coding"
            className="inline-flex items-center gap-1.5 text-xs font-semibold text-[#615d59] hover:text-[#000000] transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Назад ко всем задачам</span>
          </Link>

          <div className="flex items-center gap-3">
            <div className="flex items-center gap-1.5 text-xs font-bold text-[#0075de] bg-blue-50 px-3 py-1 rounded-full border border-blue-200/50">
              <Zap className="w-3.5 h-3.5 fill-[#0075de]" />
              <span>+{task.xp_reward} XP</span>
            </div>
          </div>
        </div>

        {/* 2-Column Split Workspace */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          
          {/* Left Column: Problem Description (5 cols) */}
          <div className="lg:col-span-5 space-y-5">
            <div className="notion-card p-6 bg-white space-y-6">
              <div>
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-[10px] font-bold uppercase tracking-wider px-2.5 py-0.5 rounded-full bg-blue-50 text-[#0075de] border border-blue-200/50">
                    Python Задача ЕНТ
                  </span>
                  <span className="text-xs text-[#a39e98]">•</span>
                  <span className="text-xs font-semibold text-[#615d59]">
                    {task.difficulty === "easy" ? "Легкий уровень" : task.difficulty === "hard" ? "Сложный уровень" : "Средний уровень"}
                  </span>
                </div>
                <h1 className="heading-2 text-[#000000]">{task.title}</h1>
              </div>

              {/* Description Body */}
              <ContentRenderer content={task.description} locale={locale} />

              {/* Sample Test Cases Table */}
              {sampleTestCases.length > 0 && (
                <div className="space-y-3 pt-4 border-t border-[#e6e6e6]">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-[#a39e98]">
                    Примеры входных и выходных данных:
                  </h4>

                  <div className="space-y-3">
                    {sampleTestCases.map((tc, idx) => (
                      <div
                        key={idx}
                        className="p-3 bg-[#f6f5f4] rounded-xl border border-[#e6e6e6] text-xs font-mono space-y-2"
                      >
                        <div>
                          <span className="text-[10px] font-sans font-bold text-[#615d59] uppercase block">
                            Ввод:
                          </span>
                          <div className="p-2 bg-white rounded border border-[#e6e6e6] text-[#000000]">
                            {tc.input_data || "<пустой ввод>"}
                          </div>
                        </div>

                        <div>
                          <span className="text-[10px] font-sans font-bold text-[#615d59] uppercase block">
                            Вывод:
                          </span>
                          <div className="p-2 bg-white rounded border border-[#e6e6e6] text-[#000000]">
                            {tc.expected_output}
                          </div>
                        </div>

                        {tc.explanation && (
                          <div className="text-[11px] font-sans text-[#615d59] italic pt-1">
                            Пояснение: {tc.explanation}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Limits */}
              <div className="flex items-center gap-4 text-xs text-[#a39e98] pt-4 border-t border-[#e6e6e6]">
                <span className="flex items-center gap-1">
                  <Clock className="w-3.5 h-3.5" />
                  Лимит: {task.time_limit_seconds} сек.
                </span>
                <span className="flex items-center gap-1">
                  <HardDrive className="w-3.5 h-3.5" />
                  Память: {task.memory_limit_mb} МБ
                </span>
              </div>
            </div>
          </div>

          {/* Right Column: Code Editor & Test Case Runner (7 cols) */}
          <div className="lg:col-span-7 space-y-5">
            <CodeEditor
              code={code}
              onChange={setCode}
              onRun={handleRunCode}
              onReset={handleResetCode}
              isRunning={running}
            />

            <TestCaseRunner result={runResult} isRunning={running} />
          </div>

        </div>

      </main>

      {celebration && (
        <LevelUpCelebration
          newLevel={celebration.newLevel}
          xpEarned={celebration.xp}
          onClose={() => setCelebration(null)}
        />
      )}

      <Footer />
    </div>
  );
}
