"use client";

import React, { useState } from "react";
import { LocalizedLink as Link } from "@/components/navigation/LocalizedLink";
import { useRouter } from "next/navigation";
import { Navbar } from "@/components/layout/Navbar";
import { Footer } from "@/components/layout/Footer";
import { fetchApi } from "@/lib/api";
import { saveAuth } from "@/lib/auth";
import { AuthResponse } from "@/types/api";
import { getClientLocale, localizePath } from "@/lib/i18n";
import { LogIn, AlertCircle, Sparkles, ArrowRight } from "lucide-react";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const data = await fetchApi<AuthResponse>("/auth/login", {
        method: "POST",
        requiresAuth: false,
        body: JSON.stringify({ email, password }),
      });

      saveAuth(data);
      router.push(localizePath("/dashboard", getClientLocale()));
    } catch (err: any) {
      setError(err.message || "Неверный логин или пароль");
    } finally {
      setLoading(false);
    }
  };

  const handleQuickDemo = (demoEmail: string) => {
    setEmail(demoEmail);
    setPassword("password123");
  };

  return (
    <div className="min-h-screen flex flex-col bg-[#f6f5f4]">
      <Navbar />

      <main className="flex-1 flex items-center justify-center p-6">
        <div className="max-w-md w-full notion-card-elevated p-8 bg-white">
          <div className="text-center mb-8">
            <div className="w-12 h-12 rounded-xl bg-blue-50 text-[#0075de] flex items-center justify-center mx-auto mb-3 border border-blue-200">
              <LogIn className="w-6 h-6" />
            </div>
            <h1 className="heading-2 text-[#000000] mb-1.5">Вход в аккаунт</h1>
            <p className="text-xs text-[#615d59]">
              Продолжите подготовку к ЕНТ и сохраняйте свой стрик
            </p>
          </div>

          {error && (
            <div className="p-3.5 bg-red-50 border border-red-200 text-red-700 text-xs rounded-xl flex items-center gap-2 mb-6">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-[#31302e] mb-1">
                Email адрес
              </label>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="student@example.com"
                className="w-full px-3.5 py-2.5 bg-white border border-[#d8d5d1] rounded-xl text-sm focus:outline-none focus:border-[#0075de] focus:ring-2 focus:ring-blue-100 transition-all"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-[#31302e] mb-1">
                Пароль
              </label>
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full px-3.5 py-2.5 bg-white border border-[#d8d5d1] rounded-xl text-sm focus:outline-none focus:border-[#0075de] focus:ring-2 focus:ring-blue-100 transition-all"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="btn-primary w-full py-2.5 text-sm font-semibold shadow-xs mt-2"
            >
              <span>{loading ? "Авторизация..." : "Войти в систему"}</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </form>

          {/* Quick Demo Fill Buttons */}
          <div className="mt-6 pt-6 border-t border-[#e6e6e6]">
            <div className="text-[11px] font-semibold text-[#a39e98] uppercase tracking-wider mb-2.5 text-center">
              Быстрый вход для тестирования:
            </div>
            <div className="grid grid-cols-2 gap-2">
              <button
                type="button"
                onClick={() => {
                  setEmail("student@unt-informatics.kz");
                  setPassword("student12345");
                }}
                className="btn-utility text-[11px] justify-center py-1.5"
              >
                Ученик (student@...)
              </button>
              <button
                type="button"
                onClick={() => {
                  setEmail("admin@unt-informatics.kz");
                  setPassword("admin12345");
                }}
                className="btn-utility text-[11px] justify-center py-1.5 text-[#0075de]"
              >
                Администратор
              </button>
            </div>
          </div>

          <div className="text-center mt-6 text-xs text-[#615d59]">
            Еще нет аккаунта?{" "}
            <Link href="/register" className="text-[#0075de] font-semibold hover:underline">
              Зарегистрироваться
            </Link>
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
}
