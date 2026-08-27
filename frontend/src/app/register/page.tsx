"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Navbar } from "@/components/layout/Navbar";
import { Footer } from "@/components/layout/Footer";
import { fetchApi } from "@/lib/api";
import { saveAuth } from "@/lib/auth";
import { AuthResponse } from "@/types/api";
import { UserPlus, AlertCircle, Sparkles, ArrowRight, Target } from "lucide-react";

export default function RegisterPage() {
  const router = useRouter();
  const [displayName, setDisplayName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [targetScore, setTargetScore] = useState(50);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const data = await fetchApi<AuthResponse>("/auth/register", {
        method: "POST",
        requiresAuth: false,
        body: JSON.stringify({
          display_name: displayName,
          email,
          password,
          role: "student",
        }),
      });

      saveAuth(data);
      router.push("/dashboard");
    } catch (err: any) {
      setError(err.message || "Ошибка при регистрации");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-[#f6f5f4]">
      <Navbar />

      <main className="flex-1 flex items-center justify-center p-6">
        <div className="max-w-md w-full notion-card-elevated p-8 bg-white">
          <div className="text-center mb-8">
            <div className="w-12 h-12 rounded-xl bg-blue-50 text-[#0075de] flex items-center justify-center mx-auto mb-3 border border-blue-200">
              <UserPlus className="w-6 h-6" />
            </div>
            <h1 className="heading-2 text-[#000000] mb-1.5">Регистрация в системе</h1>
            <p className="text-xs text-[#615d59]">
              Создайте профиль и начните путь к 50 баллам на ЕНТ
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
                Ваше имя или никнейм
              </label>
              <input
                type="text"
                required
                value={displayName}
                onChange={(e) => setDisplayName(e.target.value)}
                placeholder="Алихан Нурланов"
                className="w-full px-3.5 py-2.5 bg-white border border-[#d8d5d1] rounded-xl text-sm focus:outline-none focus:border-[#0075de] focus:ring-2 focus:ring-blue-100 transition-all"
              />
            </div>

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
                Пароль (от 6 символов)
              </label>
              <input
                type="password"
                required
                minLength={6}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full px-3.5 py-2.5 bg-white border border-[#d8d5d1] rounded-xl text-sm focus:outline-none focus:border-[#0075de] focus:ring-2 focus:ring-blue-100 transition-all"
              />
            </div>

            {/* Target Score Selector */}
            <div className="p-3 bg-[#f6f5f4] rounded-xl border border-[#e6e6e6]">
              <div className="flex items-center justify-between text-xs font-semibold mb-2">
                <span className="flex items-center gap-1.5 text-[#31302e]">
                  <Target className="w-3.5 h-3.5 text-[#0075de]" />
                  Целевой балл на ЕНТ:
                </span>
                <span className="text-[#0075de] font-bold">{targetScore} / 50</span>
              </div>
              <input
                type="range"
                min="30"
                max="50"
                value={targetScore}
                onChange={(e) => setTargetScore(Number(e.target.value))}
                className="w-full h-2 bg-white rounded-lg appearance-none cursor-pointer accent-[#0075de]"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="btn-primary w-full py-2.5 text-sm font-semibold shadow-xs mt-2"
            >
              <span>{loading ? "Создание аккаунта..." : "Создать аккаунт"}</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </form>

          <div className="text-center mt-6 text-xs text-[#615d59]">
            Уже зарегистрированы?{" "}
            <Link href="/login" className="text-[#0075de] font-semibold hover:underline">
              Войти в систему
            </Link>
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
}
