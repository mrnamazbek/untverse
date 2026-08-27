"use client";

import React, { useState, useEffect } from "react";
import { LocalizedLink as Link } from "@/components/navigation/LocalizedLink";
import { useParams, useRouter } from "next/navigation";
import { Navbar } from "@/components/layout/Navbar";
import { Sidebar } from "@/components/layout/Sidebar";
import { Footer } from "@/components/layout/Footer";
import { fetchApi } from "@/lib/api";
import { Topic, Quiz, CodingTask } from "@/types/learning";
import {
  BookOpen,
  CheckCircle2,
  PlayCircle,
  HelpCircle,
  Code2,
  ArrowLeft,
  ArrowRight,
  Zap,
  Clock,
} from "lucide-react";

export default function TopicDetailPage() {
  const params = useParams();
  const router = useRouter();
  const topicSlug = params?.topicSlug as string;

  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [topic, setTopic] = useState<Topic | null>(null);
  const [quizzes, setQuizzes] = useState<Quiz[]>([]);
  const [tasks, setTasks] = useState<CodingTask[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!topicSlug) return;

    const loadTopicData = async () => {
      try {
        const topicData = await fetchApi<Topic>(`/courses/topics/${topicSlug}`);
        setTopic(topicData);

        // Fetch related quizzes and tasks for this topic
        const [quizList, taskList] = await Promise.all([
          fetchApi<Quiz[]>(`/quizzes?topic_id=${topicData.id}`).catch(() => []),
          fetchApi<CodingTask[]>(`/coding/tasks?topic_id=${topicData.id}`).catch(() => []),
        ]);
        setQuizzes(quizList);
        setTasks(taskList);
      } catch (err) {
        console.error("Failed to load topic details", err);
      } finally {
        setLoading(false);
      }
    };

    loadTopicData();
  }, [topicSlug]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#f6f5f4]">
        <div className="w-8 h-8 border-3 border-[#0075de] border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (!topic) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-[#f6f5f4] p-6 text-center">
        <h2 className="heading-2 mb-2">Тема не найдена</h2>
        <Link href="/learn" className="btn-primary text-xs">
          Вернуться к темам
        </Link>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col bg-[#f6f5f4]">
      <Navbar onToggleSidebar={() => setSidebarOpen(!sidebarOpen)} />

      <div className="flex-1 flex max-w-7xl w-full mx-auto">
        <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

        <main className="flex-1 lg:pl-64 p-4 sm:p-6 lg:p-8 space-y-8 max-w-5xl">
          
          {/* Back Navigation */}
          <div>
            <Link
              href="/learn"
              className="inline-flex items-center gap-1.5 text-xs font-semibold text-[#615d59] hover:text-[#000000] transition-colors"
            >
              <ArrowLeft className="w-4 h-4" />
              <span>Назад ко всем темам</span>
            </Link>
          </div>

          {/* Topic Hero Card */}
          <div className="bg-white border border-[#e6e6e6] rounded-2xl p-6 sm:p-8 shadow-xs">
            <div className="flex items-center justify-between gap-4 mb-3">
              <span className="text-[11px] font-bold uppercase tracking-wider px-2.5 py-0.5 rounded-full bg-blue-50 text-[#0075de] border border-blue-200/50">
                Модуль ЕНТ
              </span>
              <div className="flex items-center gap-1.5 text-xs font-bold text-[#0075de] bg-blue-50 px-3 py-1 rounded-full border border-blue-200/50">
                <Zap className="w-3.5 h-3.5 fill-[#0075de]" />
                <span>+{topic.xp_reward} XP за модуль</span>
              </div>
            </div>

            <h1 className="heading-1 text-[#000000] mb-3">{topic.title}</h1>
            <p className="text-xs sm:text-sm text-[#615d59] max-w-2xl leading-relaxed mb-6">
              {topic.description}
            </p>

            <div className="flex items-center gap-4 text-xs text-[#615d59] pt-4 border-t border-[#e6e6e6]">
              <span className="flex items-center gap-1.5">
                <Clock className="w-3.5 h-3.5" />
                ~{topic.est_minutes} минут на изучение
              </span>
              <span>•</span>
              <span className="flex items-center gap-1.5">
                <BookOpen className="w-3.5 h-3.5" />
                {topic.lessons?.length || 0} теоретических уроков
              </span>
            </div>
          </div>

          {/* Lessons List */}
          <section className="space-y-4">
            <h2 className="heading-3 text-[#000000]">Теоретические уроки раздела</h2>

            <div className="space-y-3">
              {topic.lessons && topic.lessons.length > 0 ? (
                topic.lessons.map((lesson, idx) => (
                  <div
                    key={lesson.id}
                    className="notion-card p-4 sm:p-5 flex items-center justify-between gap-4 bg-white"
                  >
                    <div className="flex items-center gap-3.5">
                      <div className="w-8 h-8 rounded-full bg-blue-50 text-[#0075de] font-bold text-xs flex items-center justify-center shrink-0 border border-blue-200/50">
                        {idx + 1}
                      </div>
                      <div>
                        <h3 className="font-bold text-sm text-[#000000]">{lesson.title}</h3>
                        <p className="text-[11px] text-[#615d59] mt-0.5 line-clamp-1">
                          {lesson.summary || "Изучение ключевых понятий и примеров задач ЕНТ"}
                        </p>
                      </div>
                    </div>

                    <div className="flex items-center gap-3 shrink-0">
                      <span className="hidden sm:inline text-xs font-semibold text-[#0075de]">
                        +{lesson.xp_reward} XP
                      </span>
                      <Link
                        href={`/lesson/${lesson.id}`}
                        className="btn-primary text-xs py-1.5 px-3.5 shadow-xs"
                      >
                        <PlayCircle className="w-3.5 h-3.5" />
                        <span>Читать урок</span>
                      </Link>
                    </div>
                  </div>
                ))
              ) : (
                <div className="p-8 text-center text-xs text-[#615d59] notion-card">
                  Уроки в этом модуле готовятся к публикации.
                </div>
              )}
            </div>
          </section>

          {/* Quizzes & Practice Section */}
          <section className="space-y-4">
            <h2 className="heading-3 text-[#000000]">Тестирование и закрепление знаний</h2>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {quizzes.length > 0 ? (
                quizzes.map((q) => (
                  <div key={q.id} className="notion-card p-5 bg-white flex flex-col justify-between">
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-amber-50 text-amber-800 border border-amber-200">
                          Тест по теме
                        </span>
                        <span className="text-xs font-bold text-[#0075de]">+{q.xp_reward} XP</span>
                      </div>
                      <h4 className="font-bold text-sm text-[#000000] mb-1">{q.title}</h4>
                      <p className="text-xs text-[#615d59] mb-4">{q.description}</p>
                    </div>

                    <Link
                      href={`/quiz/${q.id}`}
                      className="btn-primary text-xs py-2 justify-center shadow-xs"
                    >
                      <HelpCircle className="w-3.5 h-3.5" />
                      <span>Пройти тест</span>
                    </Link>
                  </div>
                ))
              ) : (
                <div className="notion-card p-5 bg-white flex flex-col justify-between">
                  <div>
                    <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-blue-50 text-[#0075de] mb-2 inline-block">
                      Тест по теме
                    </span>
                    <h4 className="font-bold text-sm text-[#000000] mb-1">
                      Проверочный тест: {topic.title}
                    </h4>
                    <p className="text-xs text-[#615d59] mb-4">
                      10 тестовых вопросов формата ЕНТ для закрепления материала.
                    </p>
                  </div>
                  <Link
                    href={`/practice`}
                    className="btn-primary text-xs py-2 justify-center shadow-xs"
                  >
                    <span>Перейти к тесту</span>
                  </Link>
                </div>
              )}

              {/* Coding Tasks Card if any */}
              <div className="notion-card p-5 bg-[#213183] text-white flex flex-col justify-between">
                <div>
                  <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-white/20 text-white mb-2 inline-block">
                    Практика Python
                  </span>
                  <h4 className="font-bold text-sm mb-1">
                    Интерактивные задачи по коду
                  </h4>
                  <p className="text-xs text-blue-100/80 mb-4">
                    Напишите алгоритм решения реальной задачи ЕНТ в онлайн-песочнице.
                  </p>
                </div>
                <Link
                  href="/coding"
                  className="btn-secondary text-xs py-2 justify-center bg-white text-[#213183] hover:bg-blue-50 font-bold"
                >
                  <Code2 className="w-3.5 h-3.5 text-[#213183]" />
                  <span>Открыть задачи</span>
                </Link>
              </div>
            </div>
          </section>

        </main>
      </div>

      <Footer />
    </div>
  );
}
