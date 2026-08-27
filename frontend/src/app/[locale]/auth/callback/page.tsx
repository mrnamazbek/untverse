"use client";

import React, { useEffect, useState, useRef, Suspense } from "react";
import { useRouter, useSearchParams, useParams } from "next/navigation";
import { useAuth } from "@/context/AuthContext";
import { getMe as getMeApi, handleGoogleCallback as handleGoogleCallbackApi } from "@/lib/api";
import { saveAuth, saveUser, userToAuthSession, getAuth } from "@/lib/auth";
import { getClientLocale, i18nDict, Locale, localizePath, SUPPORTED_LOCALES } from "@/lib/i18n";
import { Loader2, Sparkles, CheckCircle2, Shield } from "lucide-react";

function CallbackHandler() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const params = useParams();
  const { refreshUserState } = useAuth();

  const currentLocaleParam = params?.locale as Locale | undefined;
  const locale: Locale =
    currentLocaleParam && SUPPORTED_LOCALES.includes(currentLocaleParam)
      ? currentLocaleParam
      : getClientLocale();

  const t = i18nDict[locale] || i18nDict.kk;

  const [statusMessage, setStatusMessage] = useState<string>(t.oauth.authenticating);
  const [isSuccess, setIsSuccess] = useState<boolean>(false);
  const processedRef = useRef<boolean>(false);

  useEffect(() => {
    // Avoid double processing in React StrictMode
    if (processedRef.current) return;
    processedRef.current = true;

    const processAuth = async () => {
      const code = searchParams.get("code");
      const state = searchParams.get("state");
      const errorParam = searchParams.get("error");
      const errorDesc = searchParams.get("error_description");
      const redirectToParam = searchParams.get("redirect_to") || "/dashboard";

      // 1. Google returned an error
      if (errorParam) {
        const errorUrl = `/${locale}/auth/error?code=${encodeURIComponent(
          errorParam
        )}&message=${encodeURIComponent(errorDesc || errorParam)}&redirect_to=${encodeURIComponent(
          redirectToParam
        )}`;
        router.replace(localizePath(errorUrl, locale));
        return;
      }

      try {
        let destination = redirectToParam;

        // 2. Client-side Code + State exchange (SPA flow)
        if (code && state) {
          setStatusMessage(t.oauth.authenticating);
          const loginResp = await handleGoogleCallbackApi(code, state);
          saveAuth(loginResp);

          if (loginResp.redirect_to) {
            destination = loginResp.redirect_to;
          }
        }

        // 3. Sync full user profile via /auth/me (works for both SPA and Backend 307 Cookie redirect)
        setStatusMessage(t.oauth.callbackPreparing);
        const currentUser = await getMeApi();
        if (currentUser) {
          saveUser(currentUser);
          const currentAuth = getAuth();
          const syncedAuth = userToAuthSession(currentUser, currentAuth);
          saveAuth(syncedAuth);
          await refreshUserState();
        }

        setIsSuccess(true);
        setStatusMessage(t.oauth.callbackSuccess);

        // 4. Smooth redirect to target destination
        setTimeout(() => {
          router.replace(localizePath(destination, locale));
        }, 600);
      } catch (err: any) {
        console.error("OAuth Callback error:", err);
        const code = err.code || "AUTH_OAUTH_CODE_EXCHANGE_FAILED";
        const message = err.message || "Ошибка авторизации Google";
        const errorUrl = `/${locale}/auth/error?code=${encodeURIComponent(
          code
        )}&message=${encodeURIComponent(message)}&redirect_to=${encodeURIComponent(
          redirectToParam
        )}`;
        router.replace(localizePath(errorUrl, locale));
      }
    };

    processAuth();
  }, [searchParams, router, locale, t, refreshUserState]);

  return (
    <div className="max-w-md w-full notion-card-elevated p-8 bg-white border border-[#e6e6e6] rounded-2xl shadow-sm text-center">
      <div className="w-16 h-16 rounded-2xl bg-blue-50 text-[#0075de] flex items-center justify-center mx-auto mb-4 border border-blue-200 shadow-xs relative">
        {isSuccess ? (
          <CheckCircle2 className="w-8 h-8 text-[#1aae39] animate-in zoom-in-75 duration-300" />
        ) : (
          <Loader2 className="w-8 h-8 text-[#0075de] animate-spin" />
        )}
        <div className="absolute -top-1 -right-1 w-5 h-5 rounded-full bg-[#0075de] text-white flex items-center justify-center shadow-xs">
          <Sparkles className="w-3 h-3" />
        </div>
      </div>

      <h1 className="heading-2 text-[#000000] mb-2">
        {isSuccess ? t.oauth.callbackTitle : t.oauth.googleSignIn}
      </h1>

      <p className="text-xs text-[#615d59] leading-relaxed mb-6">
        {statusMessage}
      </p>

      {/* Progress Bar */}
      <div className="w-full bg-[#f6f5f4] rounded-full h-1.5 overflow-hidden mb-4 border border-[#e6e6e6]">
        <div
          className={`h-full transition-all duration-700 ease-out ${
            isSuccess ? "bg-[#1aae39] w-full" : "bg-[#0075de] w-3/4 animate-pulse"
          }`}
        />
      </div>

      <div className="flex items-center justify-center gap-1.5 text-[11px] text-[#8a8580] pt-2 border-t border-[#e6e6e6]">
        <Shield className="w-3.5 h-3.5 text-[#0075de]" />
        <span>{t.oauth.secureAuthBadge}</span>
      </div>
    </div>
  );
}

export default function AuthCallbackPage() {
  return (
    <div className="min-h-screen flex items-center justify-center p-6 bg-[#f6f5f4]">
      <Suspense
        fallback={
          <div className="max-w-md w-full p-8 bg-white border border-[#e6e6e6] rounded-2xl flex flex-col items-center justify-center text-center">
            <Loader2 className="w-8 h-8 animate-spin text-[#0075de] mb-3" />
            <p className="text-xs text-[#615d59]">Авторизация...</p>
          </div>
        }
      >
        <CallbackHandler />
      </Suspense>
    </div>
  );
}
