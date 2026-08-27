"use client";

import React, { useState } from "react";
import { initGoogleOAuth } from "@/lib/api";
import { getClientLocale, i18nDict, Locale, SUPPORTED_LOCALES } from "@/lib/i18n";
import { Loader2 } from "lucide-react";

export interface GoogleButtonProps {
  locale?: Locale;
  redirectTo?: string;
  mode?: "signin" | "signup";
  className?: string;
  disabled?: boolean;
  label?: string;
  onClick?: () => void;
  onError?: (error: Error) => void;
}

export const GoogleIcon: React.FC<{ className?: string }> = ({ className = "w-5 h-5" }) => (
  <svg
    className={className}
    viewBox="0 0 24 24"
    aria-hidden="true"
    focusable="false"
  >
    <path
      fill="#4285F4"
      d="M23.745 12.27c0-.7-.06-1.4-.19-2.07H12v4.51h6.6c-.29 1.52-1.14 2.82-2.4 3.68v3.05h3.88c2.27-2.09 3.66-5.17 3.66-9.17z"
    />
    <path
      fill="#34A853"
      d="M12 24c3.24 0 5.95-1.08 7.93-2.91l-3.88-3.05c-1.08.72-2.45 1.16-4.05 1.16-3.12 0-5.77-2.1-6.72-4.93H1.25v3.15C3.26 21.36 7.34 24 12 24z"
    />
    <path
      fill="#FBBC05"
      d="M5.28 14.27c-.25-.72-.38-1.49-.38-2.27s.13-1.55.38-2.27V6.58H1.25C.45 8.16 0 9.98 0 12s.45 3.84 1.25 5.42l4.03-3.15z"
    />
    <path
      fill="#EA4335"
      d="M12 4.75c1.77 0 3.35.61 4.6 1.8l3.42-3.42C17.95 1.19 15.24 0 12 0 7.34 0 3.26 2.64 1.25 6.58l4.03 3.15c.95-2.83 3.6-4.98 6.72-4.98z"
    />
  </svg>
);

export const GoogleButton: React.FC<GoogleButtonProps> = ({
  locale: propLocale,
  redirectTo = "/dashboard",
  mode = "signin",
  className = "",
  disabled = false,
  label: customLabel,
  onClick,
  onError,
}) => {
  const [loading, setLoading] = useState(false);

  const activeLocale: Locale =
    propLocale && SUPPORTED_LOCALES.includes(propLocale)
      ? propLocale
      : getClientLocale();

  const t = i18nDict[activeLocale] || i18nDict.kk;

  const defaultText =
    mode === "signup" ? t.oauth.googleSignUp : t.oauth.googleSignIn;
  const buttonText = customLabel || defaultText;
  const loadingText = t.oauth.connectingGoogle;

  const handleClick = async (e: React.MouseEvent<HTMLButtonElement>) => {
    e.preventDefault();
    if (disabled || loading) return;

    onClick?.();
    setLoading(true);

    try {
      const response = await initGoogleOAuth(activeLocale, redirectTo);
      if (response && response.authorization_url) {
        // Smoothly redirect browser to Google Identity Service authorization URL
        window.location.href = response.authorization_url;
      } else {
        throw new Error("Не удалось получить URL авторизации Google");
      }
    } catch (err: any) {
      setLoading(false);
      const errorObj = err instanceof Error ? err : new Error(String(err));
      onError?.(errorObj);
    }
  };

  return (
    <button
      type="button"
      onClick={handleClick}
      disabled={disabled || loading}
      aria-busy={loading}
      aria-label={loading ? loadingText : buttonText}
      className={`relative w-full flex items-center justify-center gap-3 px-4 py-2.5 bg-white hover:bg-[#faf9f8] active:bg-[#f3f2f0] text-[#1f1f1f] font-medium text-sm rounded-xl border border-[#dadce0] hover:border-[#c4c7c5] shadow-xs hover:shadow-sm transition-all duration-150 focus:outline-none focus:ring-2 focus:ring-blue-100 focus:border-[#4285F4] disabled:opacity-60 disabled:cursor-not-allowed cursor-pointer ${className}`}
    >
      {loading ? (
        <>
          <Loader2 className="w-5 h-5 text-[#4285F4] animate-spin shrink-0" />
          <span className="truncate">{loadingText}</span>
        </>
      ) : (
        <>
          <GoogleIcon className="w-5 h-5 shrink-0" />
          <span className="truncate">{buttonText}</span>
        </>
      )}
    </button>
  );
};
