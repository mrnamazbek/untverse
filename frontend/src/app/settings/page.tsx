"use client";

import React, { useState, useEffect } from "react";
import { Navbar } from "@/components/layout/Navbar";
import { Sidebar } from "@/components/layout/Sidebar";
import { Footer } from "@/components/layout/Footer";
import { fetchApi } from "@/lib/api";
import { getAuth, updateLocalProfile } from "@/lib/auth";
import { User, Target, Save, CheckCircle2 } from "lucide-react";

export default function SettingsPage() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [displayName, setDisplayName] = useState("");
  const [bio, setBio] = useState("");
  const [targetScore, setTargetScore] = useState(50);
  const [saved, setSaved] = useState(false);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    const auth = getAuth();
    if (auth) {
      setDisplayName(auth.display_name || "");
    }
  }, []);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setSaved(false);

    try {
      await fetchApi("/users/me/profile", {
        method: "PUT",
        body: JSON.stringify({
          display_name: displayName,
          bio,
          target_unt_score: targetScore,
        }),
      });

      updateLocalProfile({ display_name: displayName });
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } catch (err: any) {
      alert(err.message || "Ошибка сохранения настроек");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-[#f6f5f4]">
      <Navbar onToggleSidebar={() => setSidebarOpen(!sidebarOpen)} />

      <div className="flex-1 flex max-w-7xl w-full mx-auto">
        <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

        <main className="flex-1 lg:pl-64 p-4 sm:p-6 lg:p-8 space-y-8 max-w-3xl">
          
          <div className="bg-white border border-[#e6e6e6] rounded-2xl p-6 sm:p-8 shadow-xs">
            <span className="eyebrow text-[#0075de] block mb-1 font-semibold">
              Личные данные
            </span>
            <h1 className="heading-1 text-[#000000] mb-2">Настройки аккаунта</h1>
            <p className="text-xs sm:text-sm text-[#615d59]">
              Управляйте отображаемым именем и вашей целью на ЕНТ
            </p>
          </div>

          <div className="notion-card p-6 sm:p-8 bg-white">
            {saved && (
              <div className="p-3.5 bg-green-50 border border-green-200 text-green-800 text-xs rounded-xl flex items-center gap-2 mb-6">
                <CheckCircle2 className="w-4 h-4 text-[#1aae39]" />
                <span>Настройки успешно сохранены!</span>
              </div>
            )}

            <form onSubmit={handleSave} className="space-y-6">
              <div>
                <label className="block text-xs font-semibold text-[#31302e] mb-1.5">
                  Отображаемое имя (в рейтинге и профиле)
                </label>
                <input
                  type="text"
                  required
                  value={displayName}
                  onChange={(e) => setDisplayName(e.target.value)}
                  className="w-full px-3.5 py-2.5 bg-white border border-[#d8d5d1] rounded-xl text-sm focus:outline-none focus:border-[#0075de] focus:ring-2 focus:ring-blue-100 transition-all"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-[#31302e] mb-1.5">
                  О себе / Мечта о специальности
                </label>
                <textarea
                  value={bio}
                  onChange={(e) => setBio(e.target.value)}
                  placeholder="Поступаю на Software Engineering в Астана IT / МУИТ..."
                  className="w-full px-3.5 py-2.5 bg-white border border-[#d8d5d1] rounded-xl text-sm focus:outline-none focus:border-[#0075de] focus:ring-2 focus:ring-blue-100 transition-all h-24"
                />
              </div>

              <div className="p-4 bg-[#f6f5f4] rounded-xl border border-[#e6e6e6]">
                <div className="flex items-center justify-between text-xs font-semibold mb-2">
                  <span className="flex items-center gap-1.5 text-[#31302e]">
                    <Target className="w-4 h-4 text-[#0075de]" />
                    Целевой результат на ЕНТ:
                  </span>
                  <span className="text-sm font-bold text-[#0075de]">{targetScore} / 50</span>
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
                disabled={saving}
                className="btn-primary py-2.5 px-6 text-xs font-semibold shadow-xs"
              >
                <Save className="w-4 h-4" />
                <span>{saving ? "Сохранение..." : "Сохранить изменения"}</span>
              </button>
            </form>
          </div>

        </main>
      </div>

      <Footer />
    </div>
  );
}
