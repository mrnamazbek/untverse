"use client";

import React, { useState, Suspense } from "react";
import { LocalizedLink as Link } from "@/components/navigation/LocalizedLink";
import { useRouter, useSearchParams, useParams } from "next/navigation";
import { Navbar } from "@/components/layout/Navbar";
import { Footer } from "@/components/layout/Footer";
import { GoogleButton } from "@/components/auth/GoogleButton";
import { useAuth } from "@/context/AuthContext";
import { getClientLocale, i18nDict, Locale, localizePath, SUPPORTED_LOCALES } from "@/lib/i18n";
import { LogIn, AlertCircle, ArrowRight, ShieldCheck, Loader2 } from "lucide-react";

function LoginForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const params = useParams();
  const { login } = useAuth();

  const currentLocaleParam = params?.locale as Locale | undefined;
  const locale: Locale =
    currentLocaleParam && SUPPORTED_LOCALES.includes(currentLocaleParam)
      ? currentLocaleParam
      : getClientLocale();

  const t = i18nDict[locale] || i18nDict.kk;

  const redirectTo = searchParams?.get("redirect_to") || searchParams?.get("next") || "/dashboard";

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      await login({ email, password });
      router.push(localizePath(redirectTo, locale));
    } catch (err: any) {
      setError(err.message || t.errors.AUTH_INVALID_CREDENTIALS);
    } finally {
      setLoading(false);
    }
  };

  const handleQuickDemo = (demoEmail: string, demoPass: string) => {
    setEmail(demoEmail);
    setPassword(demoPass);
    setError(null);
  };

  return (
    <div className="max-w-md w-full notion-card-elevated p-8 bg-white border border-[#e6e6e6] rounded-2xl shadow-sm">
      <div className="text-center mb-6">
        <div className="w-12 h-12 rounded-xl bg-blue-50 text-[#0075de] flex items-center justify-center mx-auto mb-3 border border-blue-200 shadow-xs">
          <LogIn className="w-6 h-6" />
        </div>
        <h1 className="heading-2 text-[#000000] mb-1.5">{t.auth.loginTitle}</h1>
        <p className="text-xs text-[#615d59]">{t.auth.loginSubtitle}</p>
      </div>

      {error && (
        <div className="p-3.5 bg-red-50 border border-red-200 text-red-700 text-xs rounded-xl flex items-start gap-2.5 mb-5 animate-in fade-in duration-200">
          <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
          <span className="leading-relaxed">{error}</span>
        </div>
      )}

      {/* Google Sign-In Button */}
      <div className="space-y-3 mb-6">
        <GoogleButton
          locale={locale}
          redirectTo={redirectTo}
          mode="signin"
          onError={(err) => setError(err.message)}
        />
        <div className="flex items-center justify-center gap-1.5 text-[11px] text-[#8a8580]">
          <ShieldCheck className="w-3.5 h-3.5 text-[#1aae39]" />
          <span>{t.oauth.secureAuthBadge}</span>
        </div>
      </div>

      {/* Divider */}
      <div className="relative my-6 text-center">
        <div className="absolute inset-0 flex items-center">
          <div className="w-full border-t border-[#e6e6e6]" />
        </div>
        <div className="relative flex justify-center text-xs uppercase">
          <span className="bg-white px-3 text-[#a39e98] font-medium tracking-wider">
            {t.auth.orDivider}
          </span>
        </div>
      </div>

      {/* Email / Password Form */}
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-xs font-semibold text-[#31302e] mb-1">
            {t.auth.emailLabel}
          </label>
          <input
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder={t.auth.emailPlaceholder}
            className="w-full px-3.5 py-2.5 bg-white border border-[#d8d5d1] rounded-xl text-sm focus:outline-none focus:border-[#0075de] focus:ring-2 focus:ring-blue-100 transition-all text-[#31302e]"
          />
        </div>

        <div>
          <label className="block text-xs font-semibold text-[#31302e] mb-1">
            {t.auth.passwordLabel}
          </label>
          <input
            type="password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder={t.auth.passwordPlaceholder}
            className="w-full px-3.5 py-2.5 bg-white border border-[#d8d5d1] rounded-xl text-sm focus:outline-none focus:border-[#0075de] focus:ring-2 focus:ring-blue-100 transition-all text-[#31302e]"
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className="btn-primary w-full py-2.5 text-sm font-semibold shadow-xs mt-2"
        >
          {loading ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              <span>{t.auth.loggingIn}</span>
            </>
          ) : (
            <>
              <span>{t.auth.loginButton}</span>
              <ArrowRight className="w-4 h-4" />
            </>
          )}
        </button>
      </form>

      {/* Quick Demo Fill Buttons */}
      <div className="mt-6 pt-6 border-t border-[#e6e6e6]">
        <div className="text-[11px] font-semibold text-[#a39e98] uppercase tracking-wider mb-2.5 text-center">
          {t.auth.quickDemoTitle}
        </div>
        <div className="grid grid-cols-2 gap-2">
          <button
            type="button"
            onClick={() => handleQuickDemo("student@unt-informatics.kz", "student12345")}
            className="btn-utility text-[11px] justify-center py-1.5"
          >
            {t.auth.demoStudent}
          </button>
          <button
            type="button"
            onClick={() => handleQuickDemo("admin@unt-informatics.kz", "admin12345")}
            className="btn-utility text-[11px] justify-center py-1.5 text-[#0075de]"
          >
            {t.auth.demoAdmin}
          </button>
        </div>
      </div>

      <div className="text-center mt-6 text-xs text-[#615d59]">
        {t.auth.noAccountPrompt}{" "}
        <Link
          href={`/register${redirectTo !== "/dashboard" ? `?redirect_to=${encodeURIComponent(redirectTo)}` : ""}`}
          className="text-[#0075de] font-semibold hover:underline"
        >
          {t.auth.registerLink}
        </Link>
      </div>
    </div>
  );
}

export default function LoginPage() {
  return (
    <div className="min-h-screen flex flex-col bg-[#f6f5f4]">
      <Navbar />

      <main className="flex-1 flex items-center justify-center p-6">
        <Suspense
          fallback={
            <div className="max-w-md w-full p-8 bg-white border border-[#e6e6e6] rounded-2xl flex items-center justify-center">
              <Loader2 className="w-6 h-6 animate-spin text-[#0075de]" />
            </div>
          }
        >
          <LoginForm />
        </Suspense>
      </main>

      <Footer />
    </div>
  );
}
