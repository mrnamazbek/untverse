"use client";

import React, { Suspense } from "react";
import { LocalizedLink as Link } from "@/components/navigation/LocalizedLink";
import { useSearchParams, useParams } from "next/navigation";
import { Navbar } from "@/components/layout/Navbar";
import { Footer } from "@/components/layout/Footer";
import {
  getClientLocale,
  i18nDict,
  Locale,
  SUPPORTED_LOCALES,
  getLocalizedAuthError,
} from "@/lib/i18n";
import { ShieldAlert, ArrowLeft, RefreshCw, Home, HelpCircle } from "lucide-react";

function AuthErrorCard() {
  const searchParams = useSearchParams();
  const params = useParams();

  const currentLocaleParam = params?.locale as Locale | undefined;
  const locale: Locale =
    currentLocaleParam && SUPPORTED_LOCALES.includes(currentLocaleParam)
      ? currentLocaleParam
      : getClientLocale();

  const t = i18nDict[locale] || i18nDict.kk;

  const code = searchParams.get("code") || searchParams.get("error");
  const rawMessage = searchParams.get("message") || searchParams.get("error_description");
  const redirectTo = searchParams.get("redirect_to") || "/dashboard";

  const resolvedErrorMessage = getLocalizedAuthError(
    code || undefined,
    locale,
    rawMessage || undefined
  );

  const retryUrl = `/login${
    redirectTo !== "/dashboard" ? `?redirect_to=${encodeURIComponent(redirectTo)}` : ""
  }`;

  return (
    <div className="max-w-md w-full notion-card-elevated p-8 bg-white border border-[#e6e6e6] rounded-2xl shadow-sm">
      <div className="text-center mb-6">
        <div className="w-14 h-14 rounded-2xl bg-red-50 text-red-600 flex items-center justify-center mx-auto mb-3 border border-red-200 shadow-xs">
          <ShieldAlert className="w-7 h-7" />
        </div>
        <h1 className="heading-2 text-[#000000] mb-1.5">{t.oauth.errorTitle}</h1>
        <p className="text-xs text-[#615d59]">{t.oauth.errorSubtitle}</p>
      </div>

      <div className="p-4 bg-red-50/70 border border-red-200 text-red-800 rounded-xl mb-6 space-y-2">
        <p className="text-xs font-medium leading-relaxed">{resolvedErrorMessage}</p>

        {code && (
          <div className="flex items-center gap-1.5 pt-1 text-[10px] text-red-600/80 font-mono">
            <span className="uppercase tracking-wider">Код:</span>
            <span className="bg-red-100/80 px-1.5 py-0.5 rounded font-semibold">{code}</span>
          </div>
        )}
      </div>

      {code === "AUTH_PASSWORD_NOT_SET" && (
        <div className="p-3.5 bg-blue-50 border border-blue-200 text-[#0075de] text-xs rounded-xl flex items-start gap-2.5 mb-6">
          <HelpCircle className="w-4 h-4 shrink-0 mt-0.5" />
          <span className="leading-relaxed">
            {locale === "kk"
              ? "Бұл аккаунт Google арқылы тіркелген. Кіру үшін Google батырмасын пайдаланыңыз."
              : locale === "en"
              ? "This account was registered via Google. Please use the Google Sign-In button."
              : "Данный аккаунт зарегистрирован через Google. Пожалуйста, используйте кнопку Google для входа."}
          </span>
        </div>
      )}

      {code === "AUTH_SESSION_REUSE_DETECTED" && (
        <div className="p-3.5 bg-amber-50 border border-amber-200 text-amber-900 text-xs rounded-xl flex items-start gap-2.5 mb-6">
          <HelpCircle className="w-4 h-4 shrink-0 mt-0.5" />
          <span className="leading-relaxed">
            {locale === "kk"
              ? "Қауіпсіздік мақсатында барлық сессиялар жабылды. Жүйеге қайта кіріңіз."
              : locale === "en"
              ? "For security purposes, all sessions were revoked. Please log in again."
              : "В целях безопасности все активные сессии были завершены. Выполните повторный вход."}
          </span>
        </div>
      )}

      <div className="space-y-2.5">
        <Link
          href={retryUrl}
          className="btn-primary w-full py-2.5 text-xs font-semibold shadow-xs justify-center gap-2"
        >
          <RefreshCw className="w-4 h-4" />
          <span>{t.oauth.retryButton}</span>
        </Link>

        <Link
          href="/"
          className="btn-utility w-full py-2.5 text-xs font-medium justify-center gap-2"
        >
          <Home className="w-4 h-4 text-[#615d59]" />
          <span>{t.oauth.homeButton}</span>
        </Link>
      </div>
    </div>
  );
}

export default function AuthErrorPage() {
  return (
    <div className="min-h-screen flex flex-col bg-[#f6f5f4]">
      <Navbar />

      <main className="flex-1 flex items-center justify-center p-6">
        <Suspense
          fallback={
            <div className="max-w-md w-full p-8 bg-white border border-[#e6e6e6] rounded-2xl flex items-center justify-center">
              <span className="text-xs text-[#615d59]">Жүктелуде...</span>
            </div>
          }
        >
          <AuthErrorCard />
        </Suspense>
      </main>

      <Footer />
    </div>
  );
}
