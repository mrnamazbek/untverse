"use client";

import React, { useState, useEffect, useCallback } from "react";
import { LocalizedLink as Link } from "@/components/navigation/LocalizedLink";
import { useParams } from "next/navigation";
import { Navbar } from "@/components/layout/Navbar";
import { Sidebar } from "@/components/layout/Sidebar";
import { i18nDict, Locale, localizePath, SUPPORTED_LOCALES } from "@/lib/i18n";
import { fetchApi } from "@/lib/api";
import { CurrentUntRule, ExamSpecification } from "@/types/data_platform";
import {
  BookMarked,
  Calendar,
  ChevronDown,
  ChevronUp,
  Cpu,
  ArrowRight,
} from "lucide-react";

export default function UntKnowledgePage() {
  const params = useParams();
  const rawLocale = params?.locale as string;
  const locale: Locale = (SUPPORTED_LOCALES.includes(rawLocale as Locale) ? rawLocale : "kk") as Locale;

  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [rules, setRules] = useState<CurrentUntRule | null>(null);
  const [specifications, setSpecifications] = useState<ExamSpecification[]>([]);
  const [expandedSection, setExpandedSection] = useState<string | null>("CS-4");
  const [isLoading, setIsLoading] = useState(true);

  const fetchData = useCallback(async () => {
    setIsLoading(true);
    try {
      const [rules, specifications] = await Promise.all([
        fetchApi<CurrentUntRule>("/unt/current", { requiresAuth: false }),
        fetchApi<ExamSpecification[]>("/unt/specifications", { requiresAuth: false }),
      ]);
      setRules(rules);
      setSpecifications(specifications);
    } catch (err) {
      console.error("Failed to load UNT specs", err);
    } finally {
      setIsLoading(false);
    }
  }, [locale]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const t = i18nDict[locale] || i18nDict.kk;
  const activeSpec = specifications[0];

  return (
    <div className="min-h-screen bg-[#fbfbfa] text-[#000000]">
      <Navbar onToggleSidebar={() => setSidebarOpen(!sidebarOpen)} />
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      <main className="lg:pl-64 pt-6 pb-20 px-4 sm:px-8 max-w-6xl mx-auto">
        {/* Page Header */}
        <div className="mb-8">
          <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-[#9d34da] mb-2">
            <BookMarked className="w-4 h-4" />
            <span>ҰТО Ресми Ережелер Базасы</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-[#000000]">
            {t.untKnowledge.title}
          </h1>
          <p className="text-sm text-[#615d59] mt-1.5 max-w-3xl">
            {t.untKnowledge.subtitle}
          </p>
        </div>

        {isLoading ? (
          <div className="text-center py-20">
            <div className="inline-block animate-spin w-8 h-8 border-3 border-[#0075de] border-t-transparent rounded-full mb-3" />
            <p className="text-xs text-[#615d59]">{t.common.loading}</p>
          </div>
        ) : (
          <div className="space-y-10">
            {/* Core Exam Metrics Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="card-warm bg-white border border-[#e6e6e6] p-4 rounded-xl">
                <div className="text-xs font-semibold text-[#615d59] mb-1">
                  {locale === "kk" ? "Сұрақтар саны" : "Количество вопросов"}
                </div>
                <div className="text-2xl font-black text-[#000000]">120 сұрақ</div>
                <div className="text-[11px] text-[#0075de] font-medium mt-1">
                  Информатика: 50 сұрақ
                </div>
              </div>

              <div className="card-warm bg-white border border-[#e6e6e6] p-4 rounded-xl">
                <div className="text-xs font-semibold text-[#615d59] mb-1">
                  {locale === "kk" ? "Максималды балл" : "Максимальный балл"}
                </div>
                <div className="text-2xl font-black text-[#0075de]">140 балл</div>
                <div className="text-[11px] text-emerald-600 font-medium mt-1">
                  Информатика: 50 балл
                </div>
              </div>

              <div className="card-warm bg-white border border-[#e6e6e6] p-4 rounded-xl">
                <div className="text-xs font-semibold text-[#615d59] mb-1">
                  {locale === "kk" ? "Емтихан ұзақтығы" : "Длительность"}
                </div>
                <div className="text-2xl font-black text-[#000000]">240 минут</div>
                <div className="text-[11px] text-[#615d59] font-medium mt-1">
                  4 сағат толық уақыт
                </div>
              </div>

              <div className="card-warm bg-white border border-[#e6e6e6] p-4 rounded-xl">
                <div className="text-xs font-semibold text-[#615d59] mb-1">
                  {locale === "kk" ? "Шекті балл" : "Пороговый балл"}
                </div>
                <div className="text-2xl font-black text-amber-600">50 балл</div>
                <div className="text-[11px] text-[#615d59] font-medium mt-1">
                  Әр пәннен кемі 5 балл
                </div>
              </div>
            </div>

            {/* Profile Combination & Grants Section */}
            <div className="card-warm bg-gradient-to-r from-blue-900 to-indigo-900 text-white rounded-2xl p-6 sm:p-8 shadow-sm">
              <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
                <div>
                  <span className="text-[10px] font-extrabold uppercase tracking-wider bg-white/20 text-white px-2.5 py-1 rounded-full">
                    IT және Компьютерлік ғылымдар профилі
                  </span>
                  <h2 className="text-xl sm:text-2xl font-black mt-3">
                    Математика + Информатика (В057, В058, В059)
                  </h2>
                  <p className="text-xs sm:text-sm text-blue-100/90 mt-2 max-w-2xl leading-relaxed">
                    Қазақстанның жетекші университеттерінде (МУИТ, АТУ, ҚБТУ, СДУ, Satbayev University) ақпараттық технологиялар грантына түсу үшін 120-дан кем емес бәсекелі балл жинау ұсынылады.
                  </p>
                </div>
                <div className="bg-white/10 backdrop-blur-md rounded-xl p-4 border border-white/20 shrink-0 text-center sm:text-left">
                  <div className="text-xs text-blue-200 uppercase font-semibold">Грант диапазоны</div>
                  <div className="text-2xl sm:text-3xl font-black text-amber-300 mt-0.5">115 — 138 балл</div>
                  <div className="text-[11px] text-blue-200 mt-1">Квоталар мен басымдықтарды ескере отырып</div>
                </div>
              </div>
            </div>

            {/* 2026 Testing Periods Timeline */}
            <div>
              <h2 className="text-lg font-bold text-[#000000] mb-4 flex items-center gap-2">
                <Calendar className="w-5 h-5 text-[#0075de]" />
                <span>{locale === "kk" ? "2026 жылғы ҰБТ кезеңдері" : "Периоды сдачи ЕНТ 2026"}</span>
              </h2>

              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                {rules?.testing_periods?.map((p, idx) => (
                  <div
                    key={idx}
                    className={`card-warm p-4 rounded-xl border ${
                      p.purpose.includes("грант") || p.purpose.includes("Грант")
                        ? "bg-blue-50/50 border-[#0075de]/30"
                        : "bg-white border-[#e6e6e6]"
                    }`}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-xs font-bold text-[#0075de]">{p.period}</span>
                      <span className="text-[10px] font-semibold uppercase px-2 py-0.5 rounded bg-[#f6f5f4] text-[#615d59]">
                        {p.type}
                      </span>
                    </div>
                    <div className="text-sm font-bold text-[#000000]">{p.dates}</div>
                    <p className="text-xs text-[#615d59] mt-2 leading-relaxed">{p.purpose}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Informatics Specification Sections & 24 Topics Accordion */}
            {activeSpec && (
              <div>
                <div className="flex items-center justify-between gap-4 mb-4">
                  <div>
                    <h2 className="text-lg font-bold text-[#000000] flex items-center gap-2">
                      <Cpu className="w-5 h-5 text-[#9d34da]" />
                      <span>{t.untKnowledge.specifications} (Нұсқа {activeSpec.version})</span>
                    </h2>
                    <p className="text-xs text-[#615d59] mt-1">
                      Барлығы 6 бөлім және 24 таксономиялық тақырып (ҰТО бекіткен)
                    </p>
                  </div>
                  <Link
                    href={localizePath("/practice", locale)}
                    className="btn-primary inline-flex items-center gap-1.5 text-xs py-2 px-3.5"
                  >
                    <span>{locale === "kk" ? "Тренажерде жаттығу" : "Тренироваться"}</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </Link>
                </div>

                <div className="space-y-3">
                  {activeSpec.sections.map((section) => {
                    const isExpanded = expandedSection === section.code;
                    return (
                      <div
                        key={section.id}
                        className="card-warm bg-white border border-[#e6e6e6] rounded-xl overflow-hidden"
                      >
                        <button
                          onClick={() => setExpandedSection(isExpanded ? null : section.code)}
                          className="w-full px-5 py-4 flex items-center justify-between text-left hover:bg-[#fbfbfa] transition-colors"
                        >
                          <div className="flex items-center gap-3">
                            <span className="w-10 h-7 rounded bg-purple-100 text-[#9d34da] font-extrabold text-xs flex items-center justify-center shrink-0">
                              {section.code}
                            </span>
                            <div>
                              <h3 className="text-sm font-bold text-[#000000]">
                                {section.title}
                              </h3>
                              <p className="text-xs text-[#615d59] mt-0.5">
                                {section.question_count_est} сұрақ ({section.weight_percentage}% үлес) • {section.topics.length} тақырып
                              </p>
                            </div>
                          </div>

                          <div className="text-[#8a8580]">
                            {isExpanded ? (
                              <ChevronUp className="w-4 h-4" />
                            ) : (
                              <ChevronDown className="w-4 h-4" />
                            )}
                          </div>
                        </button>

                        {isExpanded && (
                          <div className="px-5 pb-5 pt-2 border-t border-[#f0efee] bg-[#fafaf9]">
                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 mt-2">
                              {section.topics.map((topic) => (
                                <div
                                  key={topic.id}
                                  className="p-3 bg-white border border-[#e6e6e6] rounded-lg flex items-start gap-2.5 shadow-2xs"
                                >
                                  <span className="text-[10px] font-bold text-[#9d34da] bg-purple-50 px-1.5 py-0.5 rounded shrink-0">
                                    {topic.code}
                                  </span>
                                  <div>
                                    <h4 className="text-xs font-semibold text-[#000000]">
                                      {topic.title}
                                    </h4>
                                    {topic.learning_objectives && (
                                      <p className="text-[11px] text-[#615d59] mt-1">
                                        {String(topic.learning_objectives.learning_objective || "")}
                                      </p>
                                    )}
                                  </div>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}
