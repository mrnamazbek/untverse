"use client";

import React, { useState, useEffect, useCallback } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { Navbar } from "@/components/layout/Navbar";
import { Sidebar } from "@/components/layout/Sidebar";
import { i18nDict, Locale, localizePath, SUPPORTED_LOCALES } from "@/lib/i18n";
import { NewsArticle } from "@/types/data_platform";
import {
  ArrowLeft,
  Calendar,
  ShieldCheck,
  ExternalLink,
} from "lucide-react";

export default function NewsDetailPage() {
  const params = useParams();
  const rawLocale = params?.locale as string;
  const locale: Locale = (SUPPORTED_LOCALES.includes(rawLocale as Locale) ? rawLocale : "kk") as Locale;
  const articleId = params?.id as string;

  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [article, setArticle] = useState<NewsArticle | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const fetchArticle = useCallback(async () => {
    if (!articleId) return;
    setIsLoading(true);
    try {
      const res = await fetch(`/api/v1/news/${articleId}?locale=${locale}`);
      if (res.ok) {
        const data = await res.json();
        setArticle(data);
      }
    } catch (err) {
      console.error("Failed to load article detail", err);
    } finally {
      setIsLoading(false);
    }
  }, [articleId, locale]);

  useEffect(() => {
    fetchArticle();
  }, [fetchArticle]);

  const t = i18nDict[locale] || i18nDict.kk;

  return (
    <div className="min-h-screen bg-[#fbfbfa] text-[#000000]">
      <Navbar onToggleSidebar={() => setSidebarOpen(!sidebarOpen)} />
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      <main className="lg:pl-64 pt-6 pb-20 px-4 sm:px-8 max-w-4xl mx-auto">
        {/* Back navigation */}
        <div className="mb-6">
          <Link
            href={localizePath("/news", locale)}
            className="inline-flex items-center gap-1.5 text-xs font-semibold text-[#615d59] hover:text-[#000000] transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>{locale === "kk" ? "Барлық жаңалықтарға оралу" : "Назад ко всем новостям"}</span>
          </Link>
        </div>

        {isLoading ? (
          <div className="text-center py-20">
            <div className="inline-block animate-spin w-8 h-8 border-3 border-[#0075de] border-t-transparent rounded-full mb-3" />
            <p className="text-xs text-[#615d59]">{t.common.loading}</p>
          </div>
        ) : !article ? (
          <div className="card-warm text-center py-16 bg-white border border-[#e6e6e6] rounded-xl">
            <p className="text-sm font-semibold">{t.news.noNews}</p>
          </div>
        ) : (
          <article className="card-warm bg-white border border-[#e6e6e6] rounded-2xl p-6 sm:p-10 shadow-xs">
            {/* Header Metadata */}
            <div className="flex flex-wrap items-center justify-between gap-3 pb-6 border-b border-[#f0efee] mb-6">
              <div className="flex items-center gap-2 flex-wrap">
                <span className="text-[11px] font-bold uppercase tracking-wider px-2.5 py-1 rounded bg-blue-50 text-[#0075de] border border-blue-100">
                  {article.category}
                </span>
                <span className="inline-flex items-center gap-1 text-xs font-semibold text-emerald-700 bg-emerald-50 px-2.5 py-1 rounded border border-emerald-100">
                  <ShieldCheck className="w-3.5 h-3.5" />
                  {article.source_name}
                </span>
              </div>

              {article.published_at && (
                <div className="flex items-center gap-1.5 text-xs text-[#8a8580]">
                  <Calendar className="w-3.5 h-3.5" />
                  <span>
                    {new Date(article.published_at).toLocaleDateString(
                      locale === "kk" ? "kk-KZ" : "ru-RU",
                      { year: "numeric", month: "long", day: "numeric" }
                    )}
                  </span>
                </div>
              )}
            </div>

            {/* Title & Summary */}
            <h1 className="text-xl sm:text-3xl font-extrabold tracking-tight text-[#000000] leading-tight mb-4">
              {article.title}
            </h1>

            <div className="p-4 rounded-xl bg-[#f6f5f4] border-l-4 border-[#0075de] mb-8 text-sm sm:text-base text-[#31302e] font-medium leading-relaxed">
              {article.summary}
            </div>

            {/* Body Content */}
            <div className="prose prose-neutral max-w-none text-sm sm:text-base leading-relaxed text-[#1a1a19] space-y-4">
              {article.content ? (
                article.content.split("\n\n").map((para, i) => (
                  <p key={i}>{para}</p>
                ))
              ) : (
                <p>{article.summary}</p>
              )}
            </div>

            {/* Provenance and Verification Footer */}
            <div className="mt-10 pt-6 border-t border-[#f0efee] bg-slate-50/70 -mx-6 sm:-mx-10 -mb-6 sm:-mb-10 p-6 sm:p-8 rounded-b-2xl">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div className="space-y-1">
                  <p className="text-xs font-bold text-[#000000] flex items-center gap-1.5">
                    <ShieldCheck className="w-4 h-4 text-[#0075de]" />
                    <span>{locale === "kk" ? "Тексерілген мемлекеттік дереккөз" : "Верифицированный государственный источник"}</span>
                  </p>
                  <p className="text-[11px] text-[#615d59]">
                    {article.source_authority === "official_primary"
                      ? "ҚР ҰТО және ҒЖБМ ресми порталынан автоматты сүзгіден өтті."
                      : "Ресми мәліметтер негізінде дайындалған."}
                  </p>
                </div>

                <a
                  href={article.canonical_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="btn-primary inline-flex items-center justify-center gap-2 text-xs py-2 px-4 shadow-xs"
                >
                  <span>{locale === "kk" ? "Түпнұсқаны көру" : "Оригинал источника"}</span>
                  <ExternalLink className="w-3.5 h-3.5" />
                </a>
              </div>
            </div>
          </article>
        )}
      </main>
    </div>
  );
}
