"use client";

import React, { useState, useEffect, useCallback } from "react";
import { LocalizedLink as Link } from "@/components/navigation/LocalizedLink";
import { useParams } from "next/navigation";
import { Navbar } from "@/components/layout/Navbar";
import { Sidebar } from "@/components/layout/Sidebar";
import { i18nDict, Locale, localizePath, SUPPORTED_LOCALES } from "@/lib/i18n";
import { fetchApi } from "@/lib/api";
import { NewsArticle, NewsAlert } from "@/types/data_platform";
import {
  Newspaper,
  BellRing,
  ExternalLink,
  ShieldCheck,
  Calendar,
  Search,
  ArrowRight,
  Clock,
} from "lucide-react";

export default function NewsFeedPage() {
  const params = useParams();
  const rawLocale = params?.locale as string;
  const locale: Locale = (SUPPORTED_LOCALES.includes(rawLocale as Locale) ? rawLocale : "kk") as Locale;

  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [newsList, setNewsList] = useState<NewsArticle[]>([]);
  const [alerts, setAlerts] = useState<NewsAlert[]>([]);
  const [category, setCategory] = useState<string>("all");
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [isLoading, setIsLoading] = useState(true);

  const fetchNews = useCallback(async () => {
    setIsLoading(true);
    try {
      const params = new URLSearchParams({ limit: "30" });
      if (category !== "all") params.set("category", category);
      if (searchQuery.trim()) params.set("search", searchQuery.trim());
      const data = await fetchApi<{ items: NewsArticle[] }>(`/news?${params}`, { requiresAuth: false });
      setNewsList(data.items || []);
    } catch (err) {
      console.error("Failed to load news", err);
    } finally {
      setIsLoading(false);
    }
  }, [locale, category, searchQuery]);

  const fetchAlerts = useCallback(async () => {
    try {
      const data = await fetchApi<NewsAlert[]>("/news/alerts", { requiresAuth: false });
      setAlerts(data || []);
    } catch (err) {
      console.error("Failed to load alerts", err);
    }
  }, [locale]);

  useEffect(() => {
    fetchNews();
    fetchAlerts();
  }, [fetchNews, fetchAlerts]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    fetchNews();
  };

  const t = i18nDict[locale] || i18nDict.kk;

  const categories = [
    { key: "all", label: t.news.categories.all },
    { key: "unt", label: t.news.categories.unt },
    { key: "registration", label: t.news.categories.registration },
    { key: "grants", label: t.news.categories.grants },
    { key: "specification", label: t.news.categories.informatics },
  ];

  return (
    <div className="min-h-screen bg-[#fbfbfa] text-[#000000]">
      <Navbar onToggleSidebar={() => setSidebarOpen(!sidebarOpen)} />
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      <main className="lg:pl-64 pt-6 pb-16 px-4 sm:px-8 max-w-6xl mx-auto">
        {/* Page Header */}
        <div className="mb-8">
          <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-[#0075de] mb-2">
            <Newspaper className="w-4 h-4" />
            <span>UNTverse Knowledge & News Hub</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-[#000000]">
            {t.news.title}
          </h1>
          <p className="text-sm text-[#615d59] mt-1.5 max-w-3xl">
            {t.news.subtitle}
          </p>
        </div>

        {/* Breaking News Alerts Banner */}
        {alerts.length > 0 && (
          <div className="mb-8 space-y-3">
            {alerts.map((alert) => (
              <div
                key={alert.id}
                className="relative overflow-hidden rounded-xl border border-red-200 bg-gradient-to-r from-red-50 via-orange-50 to-amber-50 p-4 sm:p-5 shadow-xs"
              >
                <div className="flex items-start gap-3.5">
                  <div className="w-9 h-9 rounded-lg bg-red-600 text-white flex items-center justify-center shrink-0 shadow-sm animate-pulse">
                    <BellRing className="w-5 h-5" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 flex-wrap mb-1">
                      <span className="text-[10px] font-extrabold uppercase tracking-wider bg-red-600 text-white px-2 py-0.5 rounded-full">
                        {t.news.breakingAlert}
                      </span>
                      {alert.published_at && (
                        <span className="text-xs text-[#615d59] flex items-center gap-1">
                          <Clock className="w-3 h-3" />
                          {new Date(alert.published_at).toLocaleDateString(locale === "kk" ? "kk-KZ" : "ru-RU")}
                        </span>
                      )}
                    </div>
                    <h3 className="text-sm sm:text-base font-bold text-red-950">
                      {alert.title}
                    </h3>
                    <p className="text-xs text-red-900/80 mt-1 leading-relaxed">
                      {alert.summary}
                    </p>
                    <div className="mt-3 flex items-center gap-3">
                      <Link
                        href={localizePath(`/news/${alert.id}`, locale)}
                        className="inline-flex items-center gap-1 text-xs font-bold text-red-700 hover:text-red-900"
                      >
                        {t.news.readMore} <ArrowRight className="w-3.5 h-3.5" />
                      </Link>
                      <a
                        href={alert.canonical_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-1 text-xs text-[#615d59] hover:text-[#000000]"
                      >
                        {t.news.sourceAttribution} <ExternalLink className="w-3 h-3" />
                      </a>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Filters & Search Toolbar */}
        <div className="card-warm p-4 mb-8 bg-[#ffffff] border border-[#e6e6e6] rounded-xl flex flex-col md:flex-row items-stretch md:items-center justify-between gap-4">
          {/* Category Tabs */}
          <div className="flex items-center gap-1.5 overflow-x-auto pb-1 md:pb-0 scrollbar-none">
            {categories.map((cat) => (
              <button
                key={cat.key}
                onClick={() => setCategory(cat.key)}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold whitespace-nowrap transition-colors ${
                  category === cat.key
                    ? "bg-[#0075de] text-white shadow-xs"
                    : "text-[#615d59] hover:bg-[#f6f5f4] hover:text-[#000000]"
                }`}
              >
                {cat.label}
              </button>
            ))}
          </div>

          {/* Search Form */}
          <form onSubmit={handleSearchSubmit} className="relative min-w-[240px] flex items-center">
            <Search className="w-4 h-4 text-[#8a8580] absolute left-3 pointer-events-none" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder={t.common.searchPlaceholder}
              className="w-full pl-9 pr-4 py-1.5 bg-[#f6f5f4] border border-[#e6e6e6] rounded-lg text-xs focus:bg-white focus:outline-none focus:border-[#0075de] transition-colors"
            />
          </form>
        </div>

        {/* News Feed Grid */}
        {isLoading ? (
          <div className="text-center py-16">
            <div className="inline-block animate-spin w-8 h-8 border-3 border-[#0075de] border-t-transparent rounded-full mb-3" />
            <p className="text-xs text-[#615d59]">{t.common.loading}</p>
          </div>
        ) : newsList.length === 0 ? (
          <div className="card-warm text-center py-16 bg-[#ffffff] border border-[#e6e6e6] rounded-xl">
            <Newspaper className="w-10 h-10 text-[#8a8580] mx-auto mb-3 opacity-40" />
            <p className="text-sm font-semibold text-[#000000]">{t.news.noNews}</p>
            <p className="text-xs text-[#615d59] mt-1">Жаңалықтар тізімі күн сайын 06:00 және 18:00 уақытында жаңартылады.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            {newsList.map((article) => (
              <article
                key={article.id}
                className="card-warm bg-[#ffffff] border border-[#e6e6e6] hover:border-[#0075de]/40 hover:shadow-md transition-all rounded-xl p-5 flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between gap-2 mb-3">
                    <div className="flex items-center gap-2">
                      <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-blue-50 text-[#0075de] border border-blue-100">
                        {article.category}
                      </span>
                      <span className="inline-flex items-center gap-1 text-[11px] font-medium text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-100">
                        <ShieldCheck className="w-3 h-3" />
                        {article.source_authority === "official_primary"
                          ? (locale === "kk" ? "ҰТО Ресми" : "Официально НЦТ")
                          : (locale === "kk" ? "Верификацияланған" : "Верифицировано")}
                      </span>
                    </div>

                    {article.published_at && (
                      <span className="text-[11px] text-[#8a8580] flex items-center gap-1">
                        <Calendar className="w-3 h-3" />
                        {new Date(article.published_at).toLocaleDateString(
                          locale === "kk" ? "kk-KZ" : "ru-RU"
                        )}
                      </span>
                    )}
                  </div>

                  <Link href={localizePath(`/news/${article.id}`, locale)}>
                    <h2 className="text-base font-bold text-[#000000] hover:text-[#0075de] transition-colors leading-snug line-clamp-2">
                      {article.title}
                    </h2>
                  </Link>

                  <p className="text-xs text-[#615d59] mt-2 leading-relaxed line-clamp-3">
                    {article.summary}
                  </p>
                </div>

                <div className="mt-5 pt-3 border-t border-[#f0efee] flex items-center justify-between">
                  <span className="text-[11px] text-[#8a8580] truncate max-w-[180px]">
                    {article.source_name}
                  </span>

                  <div className="flex items-center gap-3">
                    <a
                      href={article.canonical_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-[#8a8580] hover:text-[#000000] transition-colors p-1"
                      title={t.news.sourceAttribution}
                    >
                      <ExternalLink className="w-3.5 h-3.5" />
                    </a>
                    <Link
                      href={localizePath(`/news/${article.id}`, locale)}
                      className="inline-flex items-center gap-1 text-xs font-bold text-[#0075de] hover:underline"
                    >
                      {t.news.readMore} <ArrowRight className="w-3 h-3" />
                    </Link>
                  </div>
                </div>
              </article>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
