"use client";

import React, { useState, useEffect } from "react";
import { Navbar } from "@/components/layout/Navbar";
import { Sidebar } from "@/components/layout/Sidebar";
import { Footer } from "@/components/layout/Footer";
import { fetchApi, setPassword as setPasswordApi } from "@/lib/api";
import { getAuth, updateLocalProfile } from "@/lib/auth";
import { getClientLocale, i18nDict, Locale, SUPPORTED_LOCALES } from "@/lib/i18n";
import { User, Target, Save, CheckCircle2, Lock, Shield, KeyRound, AlertCircle, Loader2 } from "lucide-react";
import { useParams } from "next/navigation";

export default function SettingsPage() {
  const params = useParams();
  const currentLocaleParam = params?.locale as Locale | undefined;
  const locale: Locale =
    currentLocaleParam && SUPPORTED_LOCALES.includes(currentLocaleParam)
      ? currentLocaleParam
      : getClientLocale();

  const t = i18nDict[locale] || i18nDict.kk;

  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [displayName, setDisplayName] = useState("");
  const [bio, setBio] = useState("");
  const [targetScore, setTargetScore] = useState(50);
  const [saved, setSaved] = useState(false);
  const [saving, setSaving] = useState(false);

  // Security / Password State
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [passwordSaving, setPasswordSaving] = useState(false);
  const [passwordSuccess, setPasswordSuccess] = useState(false);
  const [passwordError, setPasswordError] = useState<string | null>(null);

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

  const handleSetPassword = async (e: React.FormEvent) => {
    e.preventDefault();
    setPasswordError(null);
    setPasswordSuccess(false);

    if (newPassword.length < 8) {
      setPasswordError(
        locale === "kk"
          ? "Құпиясөз кемінде 8 таңбадан тұруы керек"
          : locale === "en"
          ? "Password must be at least 8 characters"
          : "Пароль должен содержать не менее 8 символов"
      );
      return;
    }

    if (newPassword !== confirmPassword) {
      setPasswordError(
        locale === "kk"
          ? "Құпиясөздер сәйкес келмейді"
          : locale === "en"
          ? "Passwords do not match"
          : "Пароли не совпадают"
      );
      return;
    }

    setPasswordSaving(true);
    try {
      await setPasswordApi(newPassword);
      setPasswordSuccess(true);
      setNewPassword("");
      setConfirmPassword("");
      setTimeout(() => setPasswordSuccess(false), 4000);
    } catch (err: any) {
      setPasswordError(err.message || "Ошибка при установке пароля");
    } finally {
      setPasswordSaving(false);
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
              {locale === "kk" ? "Жеке мәліметтер" : locale === "en" ? "Profile data" : "Личные данные"}
            </span>
            <h1 className="heading-1 text-[#000000] mb-2">{t.nav.settings}</h1>
            <p className="text-xs sm:text-sm text-[#615d59]">
              {locale === "kk"
                ? "Көрсетілетін есімді, ҰБТ мақсатын және қауіпсіздік параметрлерін басқарыңыз"
                : locale === "en"
                ? "Manage your display name, target score, and security credentials"
                : "Управляйте отображаемым именем, целью на ЕНТ и параметрами безопасности"}
            </p>
          </div>

          {/* Profile Form */}
          <div className="notion-card p-6 sm:p-8 bg-white border border-[#e6e6e6] rounded-2xl shadow-xs">
            {saved && (
              <div className="p-3.5 bg-green-50 border border-green-200 text-green-800 text-xs rounded-xl flex items-center gap-2 mb-6 animate-in fade-in duration-200">
                <CheckCircle2 className="w-4 h-4 text-[#1aae39]" />
                <span>
                  {locale === "kk"
                    ? "Баптаулар сәтті сақталды!"
                    : locale === "en"
                    ? "Settings successfully saved!"
                    : "Настройки успешно сохранены!"}
                </span>
              </div>
            )}

            <form onSubmit={handleSave} className="space-y-6">
              <div>
                <label className="block text-xs font-semibold text-[#31302e] mb-1.5">
                  {t.auth.displayNameLabel}
                </label>
                <input
                  type="text"
                  required
                  value={displayName}
                  onChange={(e) => setDisplayName(e.target.value)}
                  className="w-full px-3.5 py-2.5 bg-white border border-[#d8d5d1] rounded-xl text-sm focus:outline-none focus:border-[#0075de] focus:ring-2 focus:ring-blue-100 transition-all text-[#31302e]"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-[#31302e] mb-1.5">
                  {locale === "kk" ? "Өзіңіз туралы / Мамандық арманыңыз" : locale === "en" ? "About you / Dream University" : "О себе / Мечта о специальности"}
                </label>
                <textarea
                  value={bio}
                  onChange={(e) => setBio(e.target.value)}
                  placeholder="Software Engineering, Astana IT University / IITU..."
                  className="w-full px-3.5 py-2.5 bg-white border border-[#d8d5d1] rounded-xl text-sm focus:outline-none focus:border-[#0075de] focus:ring-2 focus:ring-blue-100 transition-all h-24 text-[#31302e]"
                />
              </div>

              <div className="p-4 bg-[#f6f5f4] rounded-xl border border-[#e6e6e6]">
                <div className="flex items-center justify-between text-xs font-semibold mb-2">
                  <span className="flex items-center gap-1.5 text-[#31302e]">
                    <Target className="w-4 h-4 text-[#0075de]" />
                    {t.auth.targetScoreLabel}:
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
                className="btn-primary py-2.5 px-6 text-xs font-semibold shadow-xs flex items-center gap-2"
              >
                {saving ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>{locale === "kk" ? "Сақталуда..." : locale === "en" ? "Saving..." : "Сохранение..."}</span>
                  </>
                ) : (
                  <>
                    <Save className="w-4 h-4" />
                    <span>{locale === "kk" ? "Өзгерістерді сақтау" : locale === "en" ? "Save changes" : "Сохранить изменения"}</span>
                  </>
                )}
              </button>
            </form>
          </div>

          {/* Security & Password Management Card */}
          <div className="notion-card p-6 sm:p-8 bg-white border border-[#e6e6e6] rounded-2xl shadow-xs space-y-6">
            <div className="flex items-center gap-3 border-b border-[#e6e6e6] pb-4">
              <div className="w-10 h-10 rounded-xl bg-blue-50 text-[#0075de] flex items-center justify-center border border-blue-200">
                <KeyRound className="w-5 h-5" />
              </div>
              <div>
                <h2 className="heading-3 text-[#000000]">{t.auth.setPasswordTitle}</h2>
                <p className="text-xs text-[#615d59]">{t.auth.setPasswordSubtitle}</p>
              </div>
            </div>

            {passwordSuccess && (
              <div className="p-3.5 bg-green-50 border border-green-200 text-green-800 text-xs rounded-xl flex items-center gap-2 animate-in fade-in duration-200">
                <CheckCircle2 className="w-4 h-4 text-[#1aae39] shrink-0" />
                <span>{t.auth.passwordSetSuccess}</span>
              </div>
            )}

            {passwordError && (
              <div className="p-3.5 bg-red-50 border border-red-200 text-red-700 text-xs rounded-xl flex items-center gap-2 animate-in fade-in duration-200">
                <AlertCircle className="w-4 h-4 shrink-0" />
                <span>{passwordError}</span>
              </div>
            )}

            <form onSubmit={handleSetPassword} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-[#31302e] mb-1.5">
                  {t.auth.newPasswordLabel}
                </label>
                <input
                  type="password"
                  required
                  minLength={8}
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  placeholder={t.auth.newPasswordPlaceholder}
                  className="w-full px-3.5 py-2.5 bg-white border border-[#d8d5d1] rounded-xl text-sm focus:outline-none focus:border-[#0075de] focus:ring-2 focus:ring-blue-100 transition-all text-[#31302e]"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-[#31302e] mb-1.5">
                  {locale === "kk" ? "Құпиясөзді растау" : locale === "en" ? "Confirm password" : "Подтверждение пароля"}
                </label>
                <input
                  type="password"
                  required
                  minLength={8}
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  placeholder={t.auth.newPasswordPlaceholder}
                  className="w-full px-3.5 py-2.5 bg-white border border-[#d8d5d1] rounded-xl text-sm focus:outline-none focus:border-[#0075de] focus:ring-2 focus:ring-blue-100 transition-all text-[#31302e]"
                />
              </div>

              <button
                type="submit"
                disabled={passwordSaving}
                className="btn-utility py-2.5 px-6 text-xs font-semibold shadow-xs flex items-center gap-2 hover:bg-[#f6f5f4]"
              >
                {passwordSaving ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin text-[#0075de]" />
                    <span>{locale === "kk" ? "Орнатылуда..." : locale === "en" ? "Saving..." : "Установка..."}</span>
                  </>
                ) : (
                  <>
                    <Lock className="w-4 h-4 text-[#0075de]" />
                    <span>{t.auth.setPasswordButton}</span>
                  </>
                )}
              </button>
            </form>
          </div>

        </main>
      </div>

      <Footer />
    </div>
  );
}
